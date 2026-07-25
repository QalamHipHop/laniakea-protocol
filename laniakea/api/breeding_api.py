"""API router for SCDA breeding.

Mounts under ``/breeding``. The endpoints accept either the explicit
SCDA identity (when called by a wallet-bound client) or a
``session_id`` from the SIWE auth layer. The actual SCDA objects live
in the global ``ScdaManager`` singleton, so breedings created here
are visible to every other subsystem.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field

from laniakea.intelligence.breeding import (
    BreedingEngine,
    BreedingMode,
    get_breeding_engine,
)
from laniakea.intelligence.scda_manager import get_scda_manager

logger = logging.getLogger("laniakea.api.breeding")

router = APIRouter(prefix="/breeding", tags=["Breeding"])


# ----------------------------------------------------------------------------
# Schemas
# ----------------------------------------------------------------------------


class BreedRequest(BaseModel):
    parent_a: str = Field(..., description="SCDA identity of parent A")
    parent_b: str = Field(..., description="SCDA identity of parent B")
    mode: BreedingMode = BreedingMode.OFF_CHAIN
    contract_id: Optional[str] = None
    mutation_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    offspring_id: Optional[str] = None
    auto_register: bool = Field(
        default=True,
        description="If true, the offspring is added to the SCDA manager.",
    )


class ContractRequest(BaseModel):
    parent_a: str
    parent_b: str
    issued_by: str
    ttl_seconds: int = 7 * 24 * 3600
    signature: Optional[str] = None


class ContractResponse(BaseModel):
    contract_id: str
    parent_a: str
    parent_b: str
    issued_by: str
    issued_at: float
    expires_at: float
    nonce: str


class FindPartnersRequest(BaseModel):
    candidate: str
    max_results: int = Field(default=5, ge=1, le=50)


class PartnerInfo(BaseModel):
    identity: str
    distance: float
    reason: str
    can_breed: bool
    complexity: float
    energy: float
    tier: str


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------


def _engine() -> BreedingEngine:
    return get_breeding_engine()


@router.post("/breed")
async def breed(req: BreedRequest) -> Dict[str, Any]:
    """Run a breeding event between two SCDAs.

    Returns 400 on a pre-flight failure (insufficient energy, tier
    mismatch without a contract, etc). The endpoint is idempotent in
    the sense that a failed pre-flight leaves the parents untouched.
    """
    manager = get_scda_manager()
    pa = manager.get(req.parent_a)
    pb = manager.get(req.parent_b)
    if pa is None or pb is None:
        missing = [n for n, sc in ((req.parent_a, pa), (req.parent_b, pb)) if sc is None]
        raise HTTPException(status_code=404, detail={"missing": missing})
    try:
        outcome = _engine().breed(
            parent_a=pa,
            parent_b=pb,
            mode=req.mode,
            contract_id=req.contract_id,
            mutation_rate=req.mutation_rate,
            offspring_id=req.offspring_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if req.auto_register:
        # Build a new SCDA wrapping the offspring DNA, and add it to
        # the manager so subsequent calls can address it by id.
        from laniakea.intelligence.scda_model import SingleCellDigitalAccount
        from laniakea.intelligence.digital_dna import DigitalDNA
        child = SingleCellDigitalAccount(
            identity=outcome.offspring_id, dna=outcome.offspring_dna
        )
        # Carry over an initial knowledge vector from both parents so
        # the offspring isn't a blank slate.
        for k, v in pa.knowledge_vector.items():
            child.knowledge_vector.setdefault(k, v * 0.5)
        for k, v in pb.knowledge_vector.items():
            child.knowledge_vector[k] = max(child.knowledge_vector.get(k, 0.0), v * 0.5)
        # Bump complexity gently so the child is visibly "alive".
        child.complexity_index = max(1.0, min(pa.complexity_index, pb.complexity_index) * 0.25)
        manager._scdas[outcome.offspring_id] = child
        manager._created_at[outcome.offspring_id] = outcome.timestamp

    return outcome.to_dict()


@router.post("/contract", response_model=ContractResponse)
async def issue_contract(req: ContractRequest) -> ContractResponse:
    c = _engine().issue_contract(
        parent_a=req.parent_a,
        parent_b=req.parent_b,
        issued_by=req.issued_by,
        ttl_seconds=req.ttl_seconds,
        signature=req.signature,
    )
    return ContractResponse(
        contract_id=c.contract_id,
        parent_a=c.parent_a,
        parent_b=c.parent_b,
        issued_by=c.issued_by,
        issued_at=c.issued_at,
        expires_at=c.expires_at,
        nonce=c.nonce,
    )


@router.delete("/contract/{contract_id}")
async def revoke_contract(contract_id: str) -> Dict[str, Any]:
    ok = _engine().revoke_contract(contract_id)
    return {"revoked": ok, "contract_id": contract_id}


@router.get("/contract/{contract_id}")
async def get_contract(contract_id: str) -> Dict[str, Any]:
    c = _engine().get_contract(contract_id)
    if c is None:
        raise HTTPException(status_code=404, detail="contract_not_found")
    return {
        "contract_id": c.contract_id,
        "parent_a": c.parent_a,
        "parent_b": c.parent_b,
        "issued_by": c.issued_by,
        "issued_at": c.issued_at,
        "expires_at": c.expires_at,
        "nonce": c.nonce,
        "used": c.used,
        "valid": c.is_valid(__import__("time").time()),
    }


@router.post("/partners")
async def find_partners(req: FindPartnersRequest) -> Dict[str, Any]:
    manager = get_scda_manager()
    cand = manager.get(req.candidate)
    if cand is None:
        raise HTTPException(status_code=404, detail="candidate_not_found")
    pool = list(manager._scdas.values())
    ranked = _engine().find_partners(cand, pool, max_results=req.max_results)
    out: List[Dict[str, Any]] = []
    for other, dist, reason in ranked:
        ok, _why = _engine().can_breed(cand, other)
        from laniakea.intelligence.breeding import _tier_from_generation
        out.append(
            {
                "identity": other.identity,
                "distance": dist,
                "reason": reason,
                "can_breed": ok,
                "complexity": other.complexity_index,
                "energy": other.energy,
                "tier": _tier_from_generation(other.dna.generation),
            }
        )
    return {"candidate": req.candidate, "partners": out, "count": len(out)}


@router.get("/compatibility")
async def compatibility(a: str = Query(...), b: str = Query(...)) -> Dict[str, Any]:
    manager = get_scda_manager()
    sa = manager.get(a)
    sb = manager.get(b)
    if sa is None or sb is None:
        missing = [n for n, sc in ((a, sa), (b, sb)) if sc is None]
        raise HTTPException(status_code=404, detail={"missing": missing})
    dist = _engine().compatibility(sa, sb)
    ok, reason = _engine().can_breed(sa, sb)
    cost_a, cost_b = _engine().compute_energy_cost(sa, sb)
    return {
        "a": a,
        "b": b,
        "distance": dist,
        "can_breed": ok,
        "reason": reason,
        "energy_cost": {"a": cost_a, "b": cost_b, "total": cost_a + cost_b},
    }


@router.get("/history")
async def breeding_history(limit: int = Query(default=50, ge=1, le=500)) -> Dict[str, Any]:
    rows = [o.to_dict() for o in _engine().history(limit=limit)]
    return {"count": len(rows), "outcomes": rows}


@router.get("/stats")
async def breeding_stats() -> Dict[str, Any]:
    return {
        "total_events": _engine().outcome_count(),
        "config": {
            "base_energy_cost": _engine().config.base_energy_cost,
            "energy_per_complexity": _engine().config.energy_per_complexity,
            "default_mutation_rate": _engine().config.default_mutation_rate,
        },
    }
