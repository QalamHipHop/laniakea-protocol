"""Laniakea Protocol — Self-Evolution API
=====================================

HTTP surface over :mod:`laniakea.intelligence.self_evolution`. The engine
itself has existed for a while; this router is the missing API so that
the agent gateway (and external operators) can:

* see the engine's current state (``GET /evolution/status``)
* trigger a full project scan (``POST /evolution/scan``)
* ask the LLM for improvement suggestions (``POST /evolution/suggest``)
* apply a suggestion to a single file (``POST /evolution/improve``)
* read the tail of ``evolution_log.json`` (``GET /evolution/log``)

Every endpoint is defensive: if the engine fails to import (e.g. on
Render with a transient dependency issue) we surface a 503 instead of
taking the whole API down.
"""

from __future__ import annotations

import asyncio
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("laniakea.api.self_evolution")

router = APIRouter(prefix="/evolution", tags=["Self-Evolution"])

# ---------------------------------------------------------------------------
# Engine singleton (lazy)
# ---------------------------------------------------------------------------

_engine_singleton: Optional[Any] = None
_engine_lock = asyncio.Lock()


async def get_engine() -> Any:
    """Return a cached :class:`SelfEvolutionEngine` or build one on first use.

    The engine is heavy (it loads ``ValueVector`` + ``HashModernityEngine``
    and the AI API wrapper), so we only construct it the first time a
    request actually needs it.
    """
    global _engine_singleton
    if _engine_singleton is not None:
        return _engine_singleton
    async with _engine_lock:
        if _engine_singleton is not None:
            return _engine_singleton
        try:
            from laniakea.intelligence.self_evolution import SelfEvolutionEngine
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=503,
                detail=f"Self-evolution engine unavailable: {exc}",
            ) from exc
        _engine_singleton = SelfEvolutionEngine(project_root=".")
        logger.info("SelfEvolutionEngine initialised for /evolution API")
        return _engine_singleton


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ScanResponse(BaseModel):
    version: str
    timestamp: str
    total_files: int
    total_lines: int
    avg_complexity: float
    total_value_created: float
    top_files: List[Dict[str, Any]] = Field(default_factory=list)


class SuggestResponse(BaseModel):
    version: str
    timestamp: str
    suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)


class ImproveRequest(BaseModel):
    filepath: str
    suggestion: Dict[str, Any]
    confirm: bool = False
    backup: bool = True


class ImproveResponse(BaseModel):
    filepath: str
    applied: bool
    backup_path: Optional[str] = None
    error: Optional[str] = None
    timestamp: str


class StatusResponse(BaseModel):
    engine_version: str
    last_scan: Optional[Dict[str, Any]] = None
    last_suggestions: List[Dict[str, Any]] = Field(default_factory=list)
    evolution_log_path: str
    evolution_log_entries: int
    project_root: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _project_root() -> Path:
    """Return the project root used by the engine."""
    return Path(".").resolve()


def _evolution_log_path() -> Path:
    return _project_root() / "evolution_log.json"


def _read_evolution_log(limit: int = 10) -> List[Dict[str, Any]]:
    """Return the last ``limit`` entries from ``evolution_log.json``.

    The on-disk format is a JSON array of reports; each report may itself
    contain ``suggestions`` and ``applied_improvements``. We flatten the
    newest entries so the API consumer sees a chronological list.
    """
    p = _evolution_log_path()
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read evolution_log.json: %s", exc)
        return []
    if not isinstance(data, list):
        return []
    return data[-limit:]


def _backup_file(path: Path) -> Path:
    """Copy ``path`` to ``.evolution_backup/<ts>/<relative>`` and return it."""
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    backup_root = _project_root() / ".evolution_backup" / ts
    backup_root.mkdir(parents=True, exist_ok=True)
    dest = backup_root / path.name
    shutil.copy2(path, dest)
    return dest


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/status", response_model=StatusResponse, summary="Self-evolution engine state")
async def evolution_status() -> StatusResponse:
    """Return engine version + tail of the evolution log so operators can
    see whether the last scan succeeded and what was suggested.
    """
    engine = await get_engine()
    log = _read_evolution_log(limit=5)
    last_scan: Optional[Dict[str, Any]] = None
    last_suggestions: List[Dict[str, Any]] = []
    if log:
        newest = log[-1]
        if isinstance(newest, dict):
            stats = newest.get("project_stats")
            if isinstance(stats, dict):
                last_scan = {
                    "version": newest.get("version"),
                    "timestamp": newest.get("timestamp"),
                    "total_files": stats.get("total_files"),
                    "total_lines": stats.get("total_lines"),
                    "avg_complexity": stats.get("avg_complexity"),
                    "total_value_created": stats.get("total_value_created"),
                }
            suggestions_block = newest.get("suggestions")
            if isinstance(suggestions_block, list):
                last_suggestions = suggestions_block
    return StatusResponse(
        engine_version=getattr(engine, "version", "unknown"),
        last_scan=last_scan,
        last_suggestions=last_suggestions,
        evolution_log_path=str(_evolution_log_path()),
        evolution_log_entries=len(_read_evolution_log(limit=10_000)),
        project_root=str(_project_root()),
    )


@router.post("/scan", response_model=ScanResponse, summary="Full project scan")
async def evolution_scan(top_n: int = Query(10, ge=1, le=100)) -> ScanResponse:
    """Synchronously scan the whole project tree and return aggregate stats.

    The engine's own ``scan_project`` is async; we just call it. The
    top-N files are returned sorted by complexity so an operator can
    see the hot spots without opening the full report.
    """
    engine = await get_engine()
    try:
        stats = await engine.scan_project()
    except Exception as exc:
        logger.exception("scan_project failed")
        raise HTTPException(status_code=500, detail=f"Scan failed: {exc}") from exc

    files = stats.get("files") or []
    sorted_files = sorted(
        files, key=lambda f: f.get("complexity_score", 0), reverse=True
    )
    top = [
        {
            "filepath": f.get("filepath"),
            "lines": f.get("lines"),
            "complexity_score": f.get("complexity_score"),
            "functions": f.get("functions"),
            "classes": f.get("classes"),
        }
        for f in sorted_files[:top_n]
    ]
    return ScanResponse(
        version=stats.get("version", "unknown"),
        timestamp=stats.get("timestamp", datetime.utcnow().isoformat()),
        total_files=stats.get("total_files", 0),
        total_lines=stats.get("total_lines", 0),
        avg_complexity=float(stats.get("avg_complexity", 0.0)),
        total_value_created=float(stats.get("total_value_created", 0.0)),
        top_files=top,
    )


@router.post(
    "/suggest",
    response_model=SuggestResponse,
    summary="Ask the LLM for improvement suggestions on hot-spot files",
)
async def evolution_suggest() -> SuggestResponse:
    """Run ``scan_project`` + ``suggest_improvements`` and return the
    raw LLM suggestions. The engine appends the report to
    ``evolution_log.json`` as a side effect, so ``/evolution/log`` will
    reflect the new entry immediately after this call.
    """
    engine = await get_engine()
    try:
        stats = await engine.scan_project()
        suggestions = await engine.suggest_improvements(stats)
    except Exception as exc:
        logger.exception("evolution_suggest failed")
        raise HTTPException(status_code=500, detail=f"Suggest failed: {exc}") from exc

    clean: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    for item in suggestions or []:
        if not isinstance(item, dict):
            continue
        if "error" in item:
            errors.append(item)
        else:
            clean.append(item)

    return SuggestResponse(
        version=getattr(engine, "version", "unknown"),
        timestamp=datetime.utcnow().isoformat(),
        suggestions=clean,
        errors=errors,
    )


@router.post(
    "/improve",
    response_model=ImproveResponse,
    summary="Apply one suggestion to one file (requires confirm=true)",
)
async def evolution_improve(req: ImproveRequest) -> ImproveResponse:
    """Apply a single suggestion to a single file.

    Safety rails:
    * ``confirm`` must be ``true`` or we refuse — the agent gateway
      and any human operator must opt in.
    * By default we copy the file to ``.evolution_backup/<ts>/`` before
      writing. If the LLM returns broken code, the original is safe.
    * We only touch files that live under the project root.
    """
    if not req.confirm:
        raise HTTPException(
            status_code=400,
            detail="confirm=true is required to apply an improvement.",
        )
    target = Path(req.filepath).resolve()
    root = _project_root()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Refusing to touch files outside project root: {req.filepath}",
        ) from exc
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {req.filepath}")

    engine = await get_engine()
    backup_path: Optional[str] = None
    if req.backup:
        try:
            backup_path = str(_backup_file(target))
        except OSError as exc:
            raise HTTPException(
                status_code=500, detail=f"Backup failed: {exc}"
            ) from exc

    try:
        applied = await engine.auto_improve_code(str(target), req.suggestion)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("auto_improve_code failed for %s", target)
        return ImproveResponse(
            filepath=str(target),
            applied=False,
            backup_path=backup_path,
            error=f"{type(exc).__name__}: {exc}",
            timestamp=datetime.utcnow().isoformat(),
        )

    return ImproveResponse(
        filepath=str(target),
        applied=bool(applied),
        backup_path=backup_path,
        error=None if applied else "engine reported applied=false",
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/log", summary="Tail of evolution_log.json")
async def evolution_log(limit: int = Query(5, ge=1, le=100)) -> Dict[str, Any]:
    """Return the last ``limit`` evolution reports."""
    entries = _read_evolution_log(limit=limit)
    return {
        "path": str(_evolution_log_path()),
        "count": len(entries),
        "entries": entries,
    }
