"""
SCDA API router
===============

Thin HTTP layer over :class:`laniakea.intelligence.scda_manager.ScdaManager`.

The router is shared with the unified API at ``laniakea.api.main`` via
:meth:`set_shared_manager` so that state created by one is visible from the
other.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from laniakea.intelligence.scda_manager import ScdaManager, get_scda_manager


router = APIRouter(prefix="/scda", tags=["SCDA"])


# --- Pydantic models --------------------------------------------------------
class ScdaCreateRequest(BaseModel):
    identity: str = Field(..., min_length=1, max_length=128)


class ScdaSolveRequest(BaseModel):
    identity: str = Field(..., min_length=1, max_length=128)
    problem_difficulty: float = Field(..., ge=0.0, le=1.0)
    solution_quality: float = Field(..., ge=0.0, le=1.0)
    is_valid: bool = True


class ScdaPassiveRequest(BaseModel):
    identity: str = Field(..., min_length=1, max_length=128)


# --- Shared singleton accessor ---------------------------------------------
_shared: Optional[ScdaManager] = None


def set_shared_manager(manager: ScdaManager) -> None:
    """Register the shared :class:`ScdaManager` instance.

    Called by ``laniakea.api.main`` after the subsystem is initialised.
    """
    global _shared
    _shared = manager


def _manager() -> ScdaManager:
    global _shared
    if _shared is None:
        _shared = get_scda_manager()
    return _shared


# --- Routes -----------------------------------------------------------------
@router.get("/identities", summary="List all known SCDA identities")
def list_identities() -> List[str]:
    return _manager().list_identities()


@router.get("/states", summary="List the state of every known SCDA")
def list_states() -> List[Dict[str, Any]]:
    return _manager().all_states()


@router.get("/leaderboard", summary="Top SCDAs by complexity index")
def leaderboard(top_n: int = 10) -> List[Dict[str, Any]]:
    top_n = max(1, min(top_n, 100))
    return _manager().leaderboard(top_n=top_n)


@router.post("/create", summary="Create a new SCDA (idempotent on identity)")
def create_scda(req: ScdaCreateRequest) -> Dict[str, Any]:
    scda = _manager().create(req.identity)
    return {"message": "SCDA ready", "state": _manager().all_states()[-1]}


@router.get("/state/{identity}", summary="Fetch a single SCDA state")
def get_state(identity: str) -> Dict[str, Any]:
    scda = _manager().get(identity)
    if scda is None:
        raise HTTPException(status_code=404, detail=f"SCDA {identity!r} not found")
    return {
        "identity": scda.identity,
        "complexity_index": scda.complexity_index,
        "genetic_diversity": scda.dna.calculate_genetic_diversity(),
        "energy": scda.energy,
        "knowledge_count": len(scda.knowledge_vector),
        "problem_queue_size": len(scda.problem_queue),
        "knowledge_vector_8d": _manager().compute_knowledge_vector(identity),
    }


@router.post("/solve", summary="Attempt to solve a hard problem for an SCDA")
def attempt_solve(req: ScdaSolveRequest) -> Dict[str, Any]:
    if not 0.0 <= req.problem_difficulty <= 1.0:
        raise HTTPException(status_code=400, detail="problem_difficulty must be in [0, 1]")
    if not 0.0 <= req.solution_quality <= 1.0:
        raise HTTPException(status_code=400, detail="solution_quality must be in [0, 1]")
    return _manager().attempt_solve(
        identity=req.identity,
        problem_difficulty=req.problem_difficulty,
        solution_quality=req.solution_quality,
        is_valid=req.is_valid,
    )


@router.post("/passive", summary="Run the SCDA's passive update tick")
def passive_update(req: ScdaPassiveRequest) -> Dict[str, Any]:
    return _manager().passive_update(req.identity)


@router.get("/knowledge-vector/{identity}", summary="Get the SCDA's 8D knowledge vector")
def get_knowledge_vector(identity: str) -> Dict[str, Any]:
    scda = _manager().get(identity)
    if scda is None:
        raise HTTPException(status_code=404, detail=f"SCDA {identity!r} not found")
    return {
        "identity": scda.identity,
        "knowledge_vector_8d": _manager().compute_knowledge_vector(identity),
    }
