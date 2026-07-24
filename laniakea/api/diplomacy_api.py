"""Metaverse Diplomacy API router.

Thin FastAPI wrapper around :class:`laniakea.governance.metaverse_diplomacy.DiplomacySystem`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from laniakea.governance.metaverse_diplomacy import DiplomacySystem


router = APIRouter(prefix="/diplomacy", tags=["Diplomacy"])


# --- Pydantic models --------------------------------------------------------
class AllianceCreateRequest(BaseModel):
    name: str
    founder_scda_id: str
    members: List[str] = Field(default_factory=list)
    knowledge_vectors: Dict[str, List[float]] = Field(default_factory=dict)


# --- Singleton accessor -----------------------------------------------------
_diplomacy: Optional[DiplomacySystem] = None


def _get_diplomacy() -> DiplomacySystem:
    global _diplomacy
    if _diplomacy is None:
        _diplomacy = DiplomacySystem()
    return _diplomacy


# --- Routes -----------------------------------------------------------------
@router.get("/alliances", summary="List all alliances")
def list_alliances() -> List[Dict[str, Any]]:
    return [a.to_dict() for a in _get_diplomacy().alliances.values()]


@router.post("/alliances", summary="Create a new alliance")
def create_alliance(req: AllianceCreateRequest) -> Dict[str, Any]:
    # Always include the founder in the members list.
    members = list(set(req.members + [req.founder_scda_id]))

    # Default to a zero 8D vector for any member that didn't provide one.
    knowledge_vectors = {member: [0.0] * 8 for member in members}
    for scda_id, vec in req.knowledge_vectors.items():
        if scda_id in knowledge_vectors and len(vec) == 8:
            knowledge_vectors[scda_id] = vec

    alliance = _get_diplomacy().create_alliance(
        name=req.name,
        founder_scda_id=req.founder_scda_id,
        initial_members=members,
        initial_knowledge_vectors=knowledge_vectors,
    )
    return {"message": "Alliance created", "alliance": alliance.to_dict()}


@router.get("/alliances/{alliance_id}/reputation", summary="Get the reputation score of an alliance")
def get_alliance_reputation(alliance_id: str) -> Dict[str, Any]:
    try:
        score = _get_diplomacy().get_alliance_reputation(alliance_id)
        return {"alliance_id": alliance_id, "reputation": score}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/alliances/by-member/{scda_id}", summary="Find the alliance a given SCDA belongs to")
def get_alliance_by_member(scda_id: str) -> Dict[str, Any]:
    alliance = _get_diplomacy().get_alliance_by_member(scda_id)
    if alliance is None:
        raise HTTPException(status_code=404, detail=f"No alliance found for SCDA {scda_id}.")
    return alliance.to_dict()
