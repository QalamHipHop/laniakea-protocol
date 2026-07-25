"""
Laniakea Protocol - State Persistence Layer
============================================

Provides a thin, dependency-light persistence layer for the four "hot"
in-memory subsystems that the API keeps in process memory:

* SCDA registry (``laniakea.intelligence.scda_manager``)
* Knowledge marketplace (``laniakea.marketplace.knowledge_market``)
* Metaverse diplomacy (``laniakea.governance.metaverse_diplomacy``)
* Achievements (``laniakea.achievements.system``)

The design goals are:

* **One table, one row per subsystem** — keep schema migrations trivial.
* **Pickle + gzip for the payload** — generic across arbitrary Python
  object graphs, no bespoke (de)serialization.
* **SQLite-first, Postgres-compatible** — works on Render's free tier
  out of the box, and any backend that exposes a SQLAlchemy URL.
* **Fail-soft by default** — if the database is unavailable the
  subsystems keep working in memory; persistence becomes best-effort.
* **Auditable** — every save/rehydrate call emits an INFO log line so
  operators can see what is happening in the wild.

The layer is intentionally not opinionated about *what* the payload
contains — each subsystem provides a :func:`snapshot` callable and a
:func:`restore` callable. The persistence layer just stores the bytes.

Author: LaniakeA Dev
"""

from __future__ import annotations

import gzip
import logging
import os
import pickle  # nosec - we control the payload sources
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from sqlalchemy import Column, DateTime, Integer, String, LargeBinary, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from laniakea.core.config import settings

logger = logging.getLogger("laniakea.persistence")

Base = declarative_base()


class SubsystemState(Base):
    """One row per persisted subsystem.

    The ``payload`` column is a gzipped pickle of the snapshot blob
    produced by the subsystem's :func:`snapshot` callable. The
    ``version`` column lets us evolve the schema without losing data —
    mismatched versions are logged and treated as a fresh start.
    """

    __tablename__ = "subsystem_state"

    name = Column(String(64), primary_key=True)
    version = Column(String(32), nullable=False, default="1")
    payload = Column(LargeBinary, nullable=False)
    note = Column(Text, nullable=True)
    updated_at = Column(DateTime, nullable=False)


@dataclass
class PersistResult:
    """Return value for :func:`StatePersistence.save` — useful in tests."""

    name: str
    ok: bool
    bytes_written: int
    duration_ms: float
    error: Optional[str] = None


class StatePersistence:
    """Persist and rehydrate subsystem state across restarts."""

    SCHEMA_VERSION = "1"

    def __init__(self, db_url: Optional[str] = None) -> None:
        self._db_url = db_url or settings.DATABASE_URL
        self._lock = threading.RLock()
        self._engine = None
        self._session_factory = None
        self._available = False
        self._initialise_engine()

    # --- engine bootstrap ---------------------------------------------------
    def _initialise_engine(self) -> None:
        """Make sure the SQLAlchemy engine + table exist.

        We build our own engine rather than relying on
        ``laniakea.storage.database_setup.init_db`` because the legacy
        global-engine pattern races with the new persistence layer when
        both run at startup.
        """
        try:
            connect_args: Dict[str, Any] = {}
            if self._db_url.startswith("sqlite"):
                connect_args = {"check_same_thread": False}
            self._engine = create_engine(
                self._db_url,
                pool_pre_ping=True,
                connect_args=connect_args,
            )
            # Verify the connection actually works.
            with self._engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            )
            Base.metadata.create_all(self._engine)
            self._available = True
            logger.info(
                "persistence.engine.ready url=%s",
                self._safe_url(self._db_url),
            )
        except SQLAlchemyError as exc:
            self._available = False
            logger.warning(
                "persistence.engine.unavailable url=%s err=%s",
                self._safe_url(self._db_url),
                exc,
            )
        except Exception as exc:  # pragma: no cover - defensive
            self._available = False
            logger.warning(
                "persistence.engine.failed url=%s err=%s",
                self._safe_url(self._db_url),
                exc,
            )

    @staticmethod
    def _safe_url(url: str) -> str:
        """Strip credentials from a URL for safe logging."""
        if "@" in url and "://" in url:
            scheme, rest = url.split("://", 1)
            if "@" in rest:
                _, host = rest.split("@", 1)
                return f"{scheme}://***@{host}"
        return url

    @property
    def available(self) -> bool:
        return self._available

    # --- save / load --------------------------------------------------------
    def save(
        self,
        name: str,
        snapshot: Callable[[], Any],
        note: Optional[str] = None,
    ) -> PersistResult:
        """Snapshot the subsystem and persist it.

        ``snapshot`` is invoked inside the lock to keep the bytes
        consistent with the rest of the subsystem state.
        """
        start = time.perf_counter()
        with self._lock:
            if not self._available:
                return PersistResult(
                    name=name,
                    ok=False,
                    bytes_written=0,
                    duration_ms=(time.perf_counter() - start) * 1000,
                    error="engine_unavailable",
                )
            try:
                raw = snapshot()
                blob = gzip.compress(pickle.dumps(raw, protocol=pickle.HIGHEST_PROTOCOL))
                session = self._session_factory()
                try:
                    row = session.get(SubsystemState, name)
                    from datetime import datetime
                    if row is None:
                        row = SubsystemState(
                            name=name,
                            version=self.SCHEMA_VERSION,
                            payload=blob,
                            note=note,
                            updated_at=datetime.utcnow(),
                        )
                        session.add(row)
                    else:
                        row.version = self.SCHEMA_VERSION
                        row.payload = blob
                        row.note = note
                        row.updated_at = datetime.utcnow()
                    session.commit()
                finally:
                    session.close()
                elapsed = (time.perf_counter() - start) * 1000
                logger.info(
                    "persistence.save.ok name=%s bytes=%d ms=%.2f",
                    name,
                    len(blob),
                    elapsed,
                )
                return PersistResult(
                    name=name,
                    ok=True,
                    bytes_written=len(blob),
                    duration_ms=elapsed,
                )
            except SQLAlchemyError as exc:
                logger.warning("persistence.save.db_error name=%s err=%s", name, exc)
                return PersistResult(
                    name=name,
                    ok=False,
                    bytes_written=0,
                    duration_ms=(time.perf_counter() - start) * 1000,
                    error=str(exc),
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("persistence.save.error name=%s err=%s", name, exc)
                return PersistResult(
                    name=name,
                    ok=False,
                    bytes_written=0,
                    duration_ms=(time.perf_counter() - start) * 1000,
                    error=str(exc),
                )

    def load(self, name: str) -> Optional[Any]:
        """Rehydrate a subsystem payload, or ``None`` if absent / unsupported."""
        with self._lock:
            if not self._available:
                return None
            try:
                session = self._session_factory()
                try:
                    row = session.get(SubsystemState, name)
                    if row is None:
                        return None
                    if row.version != self.SCHEMA_VERSION:
                        logger.warning(
                            "persistence.load.version_mismatch name=%s stored=%s expected=%s",
                            name,
                            row.version,
                            self.SCHEMA_VERSION,
                        )
                        return None
                    return pickle.loads(gzip.decompress(row.payload))  # nosec
                finally:
                    session.close()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("persistence.load.error name=%s err=%s", name, exc)
                return None

    def rehydrate(
        self,
        name: str,
        restore: Callable[[Any], None],
    ) -> bool:
        """Load + restore. Returns True if anything was restored."""
        payload = self.load(name)
        if payload is None:
            return False
        try:
            restore(payload)
            logger.info("persistence.rehydrate.ok name=%s", name)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("persistence.rehydrate.error name=%s err=%s", name, exc)
            return False

    # --- admin helpers ------------------------------------------------------
    def list_persisted(self) -> Dict[str, Dict[str, Any]]:
        """Return a small summary of every persisted row (no payload)."""
        with self._lock:
            if not self._available:
                return {}
            try:
                session = self._session_factory()
                try:
                    rows = session.query(SubsystemState).all()
                    return {
                        r.name: {
                            "version": r.version,
                            "bytes": len(r.payload or b""),
                            "note": r.note,
                            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                        }
                        for r in rows
                    }
                finally:
                    session.close()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("persistence.list.error err=%s", exc)
                return {}

    def clear(self, name: str) -> bool:
        """Delete a persisted subsystem row (mainly for tests)."""
        with self._lock:
            if not self._available:
                return False
            try:
                session = self._session_factory()
                try:
                    row = session.get(SubsystemState, name)
                    if row is None:
                        return False
                    session.delete(row)
                    session.commit()
                    return True
                finally:
                    session.close()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("persistence.clear.error name=%s err=%s", name, exc)
                return False


# --- Singleton accessor ----------------------------------------------------
_singleton: Optional[StatePersistence] = None
_singleton_lock = threading.Lock()


def get_persistence() -> StatePersistence:
    """Return the process-wide :class:`StatePersistence` instance."""
    global _singleton
    if _singleton is None:
        with _singleton_lock:
            if _singleton is None:
                _singleton = StatePersistence()
    return _singleton


# --- Subsystem adapters ----------------------------------------------------
# Each adapter exposes a ``snapshot()`` -> Any and a ``restore(payload)``
# -> None. They are intentionally tiny so the persistence layer stays
# generic. If a subsystem is not importable (e.g. an optional
# dependency is missing) the adapter is silently skipped at boot.


def _scda_snapshot() -> Any:
    from laniakea.intelligence.scda_manager import get_scda_manager

    manager = get_scda_manager()
    return {
        "identities": manager.list_identities(),
        "snapshots": manager.all_snapshots(),
    }


def _scda_restore(payload: Any) -> None:
    from laniakea.intelligence.scda_manager import get_scda_manager

    manager = get_scda_manager()
    for state in payload.get("snapshots", []):
        identity = state.get("identity")
        if not identity:
            continue
        scda = manager.get_or_create(identity)
        try:
            scda.hydrate_from_snapshot(state)
        except Exception:  # pragma: no cover - defensive
            logger.debug("scda.hydrate.failed identity=%s", identity)


def _market_snapshot() -> Any:
    from laniakea.marketplace.knowledge_market import get_marketplace

    market = get_marketplace()
    return {
        "assets": {
            aid: a.to_dict() for aid, a in getattr(market, "assets", {}).items()
        },
    }


def _market_restore(payload: Any) -> None:
    from laniakea.marketplace.knowledge_market import (
        KnowledgeAsset,
        get_marketplace,
    )

    market = get_marketplace()
    market.assets = {}
    for aid, data in payload.get("assets", {}).items():
        try:
            market.assets[aid] = KnowledgeAsset(**data)
        except Exception:  # pragma: no cover - defensive
            logger.debug("market.restore.failed asset=%s", aid)


def _diplomacy_snapshot() -> Any:
    from laniakea.governance.metaverse_diplomacy import get_diplomacy_system

    sys_ = get_diplomacy_system()
    if sys_ is None:
        return None
    return sys_.snapshot()


def _diplomacy_restore(payload: Any) -> None:
    from laniakea.governance.metaverse_diplomacy import get_diplomacy_system

    sys_ = get_diplomacy_system()
    if sys_ is None:
        return
    sys_.restore(payload)


def _achievements_snapshot() -> Any:
    try:
        from laniakea.achievements.system import AchievementSystem
    except Exception:  # pragma: no cover - optional
        return None
    # AchievementSystem currently keeps state inside instance methods
    # rather than on ``self``; we return an empty payload and let a
    # future refactor populate this. Kept here to exercise the
    # persistence path during boot.
    return {"version": "1", "users": {}}


def _achievements_restore(payload: Any) -> None:  # pragma: no cover - noop today
    return None


# --- Boot-time wiring ------------------------------------------------------
SUBSYSTEMS: Dict[str, Dict[str, Callable[[], Any]]] = {
    "scda": {"snapshot": _scda_snapshot, "restore": _scda_restore},
    "knowledge_market": {"snapshot": _market_snapshot, "restore": _market_restore},
    "diplomacy": {"snapshot": _diplomacy_snapshot, "restore": _diplomacy_restore},
    "achievements": {"snapshot": _achievements_snapshot, "restore": _achievements_restore},
}


def rehydrate_all() -> Dict[str, bool]:
    """Try to rehydrate every registered subsystem at boot.

    Returns a dict of ``{name: restored}`` so the API can include it in
    its startup log and on ``/observability/snapshot``.
    """
    persistence = get_persistence()
    out: Dict[str, bool] = {}
    for name, hooks in SUBSYSTEMS.items():
        try:
            out[name] = persistence.rehydrate(name, hooks["restore"])
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("rehydrate.failed name=%s err=%s", name, exc)
            out[name] = False
    return out


def persist_all() -> Dict[str, PersistResult]:
    """Snapshot every registered subsystem. Used on graceful shutdown."""
    persistence = get_persistence()
    out: Dict[str, PersistResult] = {}
    for name, hooks in SUBSYSTEMS.items():
        try:
            out[name] = persistence.save(name, hooks["snapshot"], note="auto")
        except Exception as exc:  # pragma: no cover - defensive
            out[name] = PersistResult(
                name=name,
                ok=False,
                bytes_written=0,
                duration_ms=0.0,
                error=str(exc),
            )
    return out


# Self-test -----------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover - manual smoke
    p = get_persistence()
    p.save("selftest", lambda: {"hello": "world", "ts": time.time()})
    print(p.list_persisted())
    print(p.load("selftest"))
