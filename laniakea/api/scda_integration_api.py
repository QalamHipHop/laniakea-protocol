"""
Laniakea Protocol — SCDA Cross-Subsystem Integration
====================================================

Wires the SCDA registry together with the Diplomacy and Knowledge
Market subsystems so a single HTTP call can:

* create / refresh a SCDA
* mint a KnowledgeAsset from its current knowledge vector
* list that asset on the marketplace
* optionally form an alliance with another SCDA based on the
  cosine similarity of their 8D knowledge vectors

This is the kind of end-to-end workflow that an SDK or a client-side
agent wants to fire when a user reaches a new SCDA tier.

All endpoints are read-/write- thin shims over the existing subsystems
— the heavy lifting lives in :mod:`laniakea.intelligence.scda_manager`,
:mod:`laniakea.marketplace.knowledge_market`, and
:mod:`laniakea.governance.metaverse_diplomacy`.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from laniakea.intelligence.scda_manager import get_scda_manager
from laniakea.marketplace.knowledge_market import get_marketplace
from laniakea.governance.metaverse_diplomacy import get_diplomacy_system


router = APIRouter(prefix="/scda-integration", tags=["SCDA Integration"])


# --- Pydantic models -------------------------------------------------------
class AutoListKnowledgeRequest(BaseModel):
    identity: str = Field(..., min_length=1, max_length=128, description="SCDA identity")
    knowledge_type: str = Field(default="GENERAL", description="Asset type (e.g. ALGORITHM, DISCOVERY)")
    list_price: float = Field(default=0.0, ge=0.0, description="Listing price in LANA; 0 = unlisted")
    complexity_floor: float = Field(default=1.1, ge=1.0, description="Minimum C(t) required to mint")


class FormAllianceRequest(BaseModel):
    founder: str = Field(..., min_length=1, max_length=128)
    partner: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=128)
    min_similarity: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum cosine similarity (0=skip check)")


class CosineSimilarityRequest(BaseModel):
    a: str = Field(..., min_length=1, max_length=128)
    b: str = Field(..., min_length=1, max_length=128)


# --- Helpers ---------------------------------------------------------------
def _cosine(v1: List[float], v2: List[float]) -> float:
    """Compute the cosine similarity between two equal-length vectors.

    Returns ``0.0`` if either vector is zero-length or non-finite. The
    8D knowledge vectors are dense and small, so a pure-Python
    implementation is more than fast enough.
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum((x * y) for x, y in zip(v1, v2))
    n1 = math.sqrt(sum(x * x for x in v1))
    n2 = math.sqrt(sum(y * y for y in v2))
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    return dot / (n1 * n2)


# --- Endpoints -------------------------------------------------------------
@router.post(
    "/auto-list-knowledge",
    summary="Mint + list a KnowledgeAsset from an SCDA's current knowledge vector",
    response_model=Dict[str, Any],
)
def auto_list_knowledge(req: AutoListKnowledgeRequest) -> Dict[str, Any]:
    """End-to-end: read SCDA → mint asset → optionally list.

    The endpoint refuses to mint when the SCDA hasn't accumulated
    enough complexity (default ``C(t) >= 1.1``) to keep the marketplace
    free of low-value assets.
    """
    manager = get_scda_manager()
    scda = manager.get(req.identity)
    if scda is None:
        raise HTTPException(status_code=404, detail=f"SCDA {req.identity!r} not found")
    if scda.complexity_index < req.complexity_floor:
        raise HTTPException(
            status_code=400,
            detail=(
                f"SCDA complexity {scda.complexity_index:.3f} is below "
                f"the {req.complexity_floor} floor"
            ),
        )

    market = get_marketplace()
    if market is None:
        raise HTTPException(status_code=503, detail="Knowledge market unavailable")

    knowledge_vector = manager.compute_knowledge_vector(req.identity)
    asset = market.tokenize_knowledge(
        owner_scda_id=req.identity,
        scda_knowledge_vector=knowledge_vector,
        complexity_index=scda.complexity_index,
        knowledge_type=req.knowledge_type,
    )

    listed = False
    if req.list_price > 0:
        market.list_asset(asset.asset_id, req.list_price)
        listed = True

    return {
        "message": "Knowledge minted" + (" and listed" if listed else ""),
        "asset": asset.to_dict(),
        "scda_state": scda.get_state(),
        "knowledge_vector_8d": knowledge_vector,
        "listed": listed,
    }


@router.post(
    "/form-alliance",
    summary="Form an alliance between two SCDAs using knowledge-vector similarity",
    response_model=Dict[str, Any],
)
def form_alliance(req: FormAllianceRequest) -> Dict[str, Any]:
    """Create an alliance between two SCDAs.

    Optionally gates the alliance on the cosine similarity of the two
    participants' 8D knowledge vectors — useful for "science guild"
    style alliances that want at least some shared domain focus.
    """
    manager = get_scda_manager()
    founder_scda = manager.get(req.founder)
    partner_scda = manager.get(req.partner)
    if founder_scda is None or partner_scda is None:
        missing = [n for n, s in ((req.founder, founder_scda), (req.partner, partner_scda)) if s is None]
        raise HTTPException(
            status_code=404,
            detail=f"Unknown SCDA(s): {', '.join(missing)}",
        )

    vec_a = manager.compute_knowledge_vector(req.founder)
    vec_b = manager.compute_knowledge_vector(req.partner)
    similarity = _cosine(vec_a, vec_b)
    if req.min_similarity > 0 and similarity < req.min_similarity:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cosine similarity {similarity:.3f} is below the "
                f"{req.min_similarity} floor"
            ),
        )

    diplomacy = get_diplomacy_system()
    if diplomacy is None:
        raise HTTPException(status_code=503, detail="Diplomacy subsystem unavailable")

    alliance = diplomacy.create_alliance(
        name=req.name,
        founder_scda_id=req.founder,
        initial_members=[req.founder, req.partner],
        initial_knowledge_vectors={req.founder: vec_a, req.partner: vec_b},
    )
    return {
        "message": f"Alliance '{req.name}' created",
        "alliance": alliance.to_dict(),
        "cosine_similarity": similarity,
    }


@router.post(
    "/cosine-similarity",
    summary="Compute cosine similarity between two SCDAs' 8D knowledge vectors",
    response_model=Dict[str, Any],
)
def cosine_similarity(req: CosineSimilarityRequest) -> Dict[str, Any]:
    """Lightweight vector-similarity probe used by clients to decide
    whether to issue an alliance request via :func:`form_alliance`."""
    manager = get_scda_manager()
    if manager.get(req.a) is None or manager.get(req.b) is None:
        raise HTTPException(status_code=404, detail="One or both SCDAs not found")
    vec_a = manager.compute_knowledge_vector(req.a)
    vec_b = manager.compute_knowledge_vector(req.b)
    sim = _cosine(vec_a, vec_b)
    return {
        "a": req.a,
        "b": req.b,
        "vector_a": vec_a,
        "vector_b": vec_b,
        "cosine_similarity": sim,
    }


@router.get(
    "/overview",
    summary="Cross-subsystem overview (SCDA + market + diplomacy)",
    response_model=Dict[str, Any],
)
def overview() -> Dict[str, Any]:
    """Snapshot of every subsystem wired into SCDA flow — useful for
    dashboards and smoke tests."""
    manager = get_scda_manager()
    market = get_marketplace()
    diplomacy = get_diplomacy_system()
    return {
        "scda": {
            "available": True,
            "total": len(manager.all_states()),
            "total_complexity": manager.total_complexity(),
            "total_energy": manager.total_energy(),
        },
        "knowledge_market": {
            "available": market is not None,
            "total_assets": len(market.assets) if market else 0,
            "listed_assets": sum(1 for a in (market.assets.values() if market else []) if getattr(a, "is_listed", False)),
        },
        "diplomacy": {
            "available": diplomacy is not None,
            "alliances": len(diplomacy.alliances) if diplomacy and hasattr(diplomacy, "alliances") else 0,
        },
    }
