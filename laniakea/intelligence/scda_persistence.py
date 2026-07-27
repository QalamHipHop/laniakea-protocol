"""
Laniakea Protocol — SCDA disk persistence
==========================================

Optional JSON-on-disk snapshot layer for :class:`ScdaManager`. The manager
itself stays in-memory (fast) but every mutation is mirrored to a JSON
file so SCDAs survive process restarts (dev / single-node Render deploy).

Design notes
------------
* Writes are debounced (default 1s) to avoid hammering the disk when many
  small mutations land in the same request burst (e.g. a breeding loop).
* Writes are atomic (``os.replace`` on a temp file) so a crash mid-write
  cannot corrupt the snapshot.
* Loading is best-effort — a corrupt or missing file is treated as "empty
  registry" and logged as a warning, never as a fatal error.
* The persistence layer is opt-in: ``install_persistence()`` wires it into
  the singleton returned by ``get_scda_manager()``. The default behaviour
  (no install) matches the original in-memory manager, so this is fully
  backwards compatible.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .scda_manager import ScdaManager, get_scda_manager

logger = logging.getLogger("laniakea.intelligence.scda_persistence")

# Default snapshot location — honour an env override so Render persistent
# disks / Docker volumes can be mounted without code changes.
_DEFAULT_PATH = os.getenv(
    "LANIAKEA_SCDA_SNAPSHOT",
    str(Path(__file__).resolve().parents[2] / "data" / "scda_snapshot.json"),
)


class ScdaPersistence:
    """JSON snapshot layer for :class:`ScdaManager`."""

    def __init__(
        self,
        manager: ScdaManager,
        path: str = _DEFAULT_PATH,
        debounce_seconds: float = 1.0,
    ) -> None:
        self._manager = manager
        self._path = Path(path)
        self._debounce = debounce_seconds
        self._lock = threading.RLock()
        self._timer: Optional[threading.Timer] = None
        self._closed = False

    # -- public API --------------------------------------------------------
    def install(self) -> None:
        """Load any existing snapshot and arm auto-save."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning("Cannot create snapshot dir %s: %s", self._path.parent, exc)
        self.load()
        # Wrap the mutating methods so any state change schedules a save.
        for name in ("create", "register", "delete"):
            self._wrap(name)
        # passive_update + attempt_solve also mutate SCDA fields, so we hook
        # into the underlying model's mutation by re-saving after each call.
        for name in ("passive_update", "attempt_solve"):
            self._wrap(name)
        logger.info(
            "SCDA persistence installed → %s (debounce=%.2fs)",
            self._path,
            self._debounce,
        )

    def load(self) -> int:
        """Load snapshot from disk into the manager. Returns count loaded."""
        if not self._path.exists():
            logger.info("No SCDA snapshot at %s — starting empty.", self._path)
            return 0
        try:
            with self._path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Corrupt SCDA snapshot ignored: %s", exc)
            return 0

        scdas = payload.get("scdas") or {}
        loaded = 0
        with self._manager._lock:  # type: ignore[attr-defined]
            for identity, blob in scdas.items():
                try:
                    scda = self._manager._scdas.get(identity)  # type: ignore[attr-defined]
                    if scda is None:
                        from .scda_model import SingleCellDigitalAccount

                        scda = SingleCellDigitalAccount(identity=identity)
                        self._manager._scdas[identity] = scda  # type: ignore[attr-defined]
                    self._restore_scda(scda, blob)
                    loaded += 1
                except Exception as exc:  # pragma: no cover - defensive
                    logger.warning("Failed to restore SCDA %s: %s", identity, exc)
        logger.info("Loaded %d SCDAs from %s", loaded, self._path)
        return loaded

    def save_now(self) -> None:
        """Flush the current state to disk immediately (synchronous)."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            self._do_save()

    def flush(self) -> None:
        """Alias used at shutdown."""
        self.save_now()

    # -- internals ---------------------------------------------------------
    def _schedule(self) -> None:
        if self._closed:
            return
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce, self._do_save)
            self._timer.daemon = True
            self._timer.start()

    def _do_save(self) -> None:
        with self._manager._lock:  # type: ignore[attr-defined]
            payload: Dict[str, Any] = {
                "version": 1,
                "saved_at": time.time(),
                "scdas": {
                    ident: self._snapshot_scda(scda)
                    for ident, scda in self._manager._scdas.items()  # type: ignore[attr-defined]
                },
            }
        tmp = self._path.with_suffix(self._path.suffix + ".tmp")
        try:
            with tmp.open("w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, default=str)
            os.replace(tmp, self._path)
        except OSError as exc:  # pragma: no cover - defensive
            logger.warning("SCDA snapshot save failed: %s", exc)
        else:
            logger.debug("SCDA snapshot saved (%d entries)", len(payload["scdas"]))

    def _snapshot_scda(self, scda: Any) -> Dict[str, Any]:
        """Read public state off a SCDA without going through Pydantic."""
        return {
            "identity": scda.identity,
            "complexity_index": float(getattr(scda, "complexity_index", 0.0)),
            "energy": float(getattr(scda, "energy", 0.0)),
            "generation": int(getattr(scda, "generation", 0)),
            "tier": int(getattr(scda, "tier", 0)),
            "dna": getattr(scda, "dna", None),
            "knowledge_vector": dict(getattr(scda, "knowledge_vector", {}) or {}),
            "problem_queue": list(getattr(scda, "problem_queue", []) or []),
            "stats": dict(getattr(scda, "stats", {}) or {}),
        }

    def _restore_scda(self, scda: Any, blob: Dict[str, Any]) -> None:
        """Apply a snapshot blob onto an existing SCDA instance."""
        if "complexity_index" in blob:
            scda.complexity_index = float(blob["complexity_index"])
        if "energy" in blob:
            scda.energy = float(blob["energy"])
        if "generation" in blob:
            scda.generation = int(blob["generation"])
        if "tier" in blob:
            scda.tier = int(blob["tier"])
        if "dna" in blob and blob["dna"] is not None:
            scda.dna = blob["dna"]
        if "knowledge_vector" in blob:
            scda.knowledge_vector = dict(blob["knowledge_vector"] or {})
        if "problem_queue" in blob:
            scda.problem_queue = list(blob["problem_queue"] or [])
        if "stats" in blob:
            scda.stats = dict(blob["stats"] or {})

    def _wrap(self, name: str) -> None:
        """Wrap ``ScdaManager.<name>`` so it triggers a debounced save."""
        original = getattr(self._manager, name)
        if getattr(original, "_persistence_wrapped", False):
            return
        persistence = self

        def wrapped(*args: Any, **kwargs: Any) -> Any:
            try:
                return original(*args, **kwargs)
            finally:
                persistence._schedule()

        wrapped.__name__ = getattr(original, "__name__", name)
        wrapped._persistence_wrapped = True  # type: ignore[attr-defined]
        setattr(self._manager, name, wrapped)


_persistence: Optional[ScdaPersistence] = None
_persistence_lock = threading.Lock()


def install_persistence(
    path: Optional[str] = None,
    debounce_seconds: float = 1.0,
) -> ScdaPersistence:
    """Install disk persistence on the singleton SCDA manager (idempotent)."""
    global _persistence
    with _persistence_lock:
        if _persistence is not None:
            return _persistence
        manager = get_scda_manager()
        _persistence = ScdaPersistence(
            manager,
            path=path or _DEFAULT_PATH,
            debounce_seconds=debounce_seconds,
        )
        _persistence.install()
        return _persistence


def get_persistence() -> Optional[ScdaPersistence]:
    return _persistence
