"""Governance v2 API surface.

Exposes the production :class:`GovernanceDAO` over HTTP. The
original ``/dao/*`` routes keep working through a thin compatibility
layer that delegates to :class:`laniakea.governance.dao.DAO`.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from laniakea.governance.dao_v2 import (
    GovernanceDAO,
    ProposalAction,
    ProposalCategory,
    ProposalState,
    ProposalV2,
    Treasury,
    get_governance_dao,
)

logger = logging.getLogger("laniakea.api.governance")

router = APIRouter(prefix="/gov", tags=["Governance v2"])


# ----------------------------------------------------------------------------
# Schemas
# ----------------------------------------------------------------------------


class ActionModel(BaseModel):
    kind: str = Field(..., description="treasury_spend | parameter_update | breeding_contract | text")
    payload: Dict[str, Any] = Field(default_factory=dict)


class CreateProposalRequest(BaseModel):
    title: str
    description: str
    proposer: str
    category: ProposalCategory = ProposalCategory.TEXT
    actions: List[ActionModel] = Field(default_factory=list)
    quorum: Optional[float] = None
    pass_threshold: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class VoteRequest(BaseModel):
    voter: str
    choice: str = Field(..., description="for | against | abstain")


class DelegateRequest(BaseModel):
    delegator: str
    delegate: str
    weight: Optional[int] = None
    lock_seconds: Optional[int] = None


class ParameterUpdateRequest(BaseModel):
    key: str
    value: Any


class TreasuryDepositRequest(BaseModel):
    asset: str
    amount: int
    actor: str
    note: str = ""


class TreasuryWithdrawRequest(BaseModel):
    asset: str
    amount: int
    actor: str
    note: str = ""


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------


def _dao() -> GovernanceDAO:
    return get_governance_dao()


@router.get("/proposals")
async def list_proposals(state: Optional[ProposalState] = None) -> Dict[str, Any]:
    props = _dao().list_proposals(state=state)
    return {
        "count": len(props),
        "proposals": [p.snapshot() for p in props],
    }


@router.post("/proposals")
async def create_proposal(req: CreateProposalRequest) -> Dict[str, Any]:
    try:
        p = _dao().create_proposal(
            title=req.title,
            description=req.description,
            proposer=req.proposer,
            category=req.category,
            actions=[ProposalAction(kind=a.kind, payload=a.payload) for a in req.actions],
            quorum=req.quorum,
            pass_threshold=req.pass_threshold,
            metadata=req.metadata,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return p.snapshot()


@router.post("/proposals/{pid}/submit")
async def submit_proposal(pid: int) -> Dict[str, Any]:
    try:
        p = _dao().submit(pid)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return p.snapshot()


@router.post("/proposals/{pid}/start_voting")
async def start_voting(pid: int) -> Dict[str, Any]:
    try:
        p = _dao().start_voting(pid)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return p.snapshot()


@router.post("/proposals/{pid}/vote")
async def cast_vote(pid: int, req: VoteRequest) -> Dict[str, Any]:
    try:
        v = _dao().vote(pid, req.voter, req.choice)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"proposal_id": pid, "vote": v.__dict__}


@router.post("/proposals/{pid}/close")
async def close_voting(pid: int) -> Dict[str, Any]:
    try:
        p = _dao().close_voting(pid)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return p.snapshot()


@router.post("/proposals/{pid}/execute")
async def execute_proposal(pid: int) -> Dict[str, Any]:
    try:
        out = _dao().execute(pid)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return out


@router.post("/proposals/{pid}/cancel")
async def cancel_proposal(pid: int, actor: str) -> Dict[str, Any]:
    try:
        p = _dao().cancel(pid, actor)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return p.snapshot()


@router.get("/proposals/{pid}")
async def get_proposal(pid: int) -> Dict[str, Any]:
    p = _dao().get_proposal(pid)
    if p is None:
        raise HTTPException(status_code=404, detail="proposal_not_found")
    return p.snapshot()


# -- Delegation --------------------------------------------------------------


@router.post("/delegations")
async def create_delegation(req: DelegateRequest) -> Dict[str, Any]:
    try:
        d = _dao().delegate(
            delegator=req.delegator,
            delegate=req.delegate,
            weight=req.weight,
            lock_seconds=req.lock_seconds,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return d.__dict__


@router.delete("/delegations")
async def revoke_delegation(delegator: str, delegate: str) -> Dict[str, Any]:
    ok = _dao().revoke_delegation(delegator, delegate)
    return {"revoked": ok}


# -- Parameters --------------------------------------------------------------


@router.post("/parameters")
async def set_parameter(req: ParameterUpdateRequest) -> Dict[str, Any]:
    return _dao().set_parameter(req.key, req.value)


@router.get("/parameters")
async def list_parameters() -> Dict[str, Any]:
    return _dao()._parameters


# -- Treasury ----------------------------------------------------------------


@router.get("/treasury")
async def treasury_balances() -> Dict[str, Any]:
    t: Treasury = _dao().treasury
    return {"balances": dict(t.balances)}


@router.post("/treasury/deposit")
async def treasury_deposit(req: TreasuryDepositRequest) -> Dict[str, Any]:
    try:
        bal = _dao().treasury.deposit(req.asset, req.amount, req.actor, req.note)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"asset": req.asset, "balance": bal}


@router.post("/treasury/withdraw")
async def treasury_withdraw(req: TreasuryWithdrawRequest) -> Dict[str, Any]:
    try:
        bal = _dao().treasury.withdraw(req.asset, req.amount, req.actor, note=req.note)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"asset": req.asset, "balance": bal}


@router.get("/treasury/history")
async def treasury_history(limit: int = Query(default=100, ge=1, le=1000)) -> Dict[str, Any]:
    rows = [e.__dict__ for e in _dao().treasury.history(limit=limit)]
    return {"count": len(rows), "events": rows}


# -- Audit -------------------------------------------------------------------


@router.get("/audit")
async def audit_log(limit: int = Query(default=100, ge=1, le=1000)) -> Dict[str, Any]:
    rows = [e.to_dict() for e in _dao().audit.entries(limit=limit)]
    return {"count": len(rows), "events": rows}


@router.get("/stats")
async def gov_stats() -> Dict[str, Any]:
    d = _dao()
    return {
        "proposals": len(d.proposals),
        "delegations": len(d.delegations),
        "treasury": dict(d.treasury.balances),
        "parameters": d._parameters,
        "config": {
            "voting_period_seconds": d.config.voting_period_seconds,
            "voting_delay_seconds": d.config.voting_delay_seconds,
            "execution_delay_seconds": d.config.execution_delay_seconds,
            "default_quorum": d.config.default_quorum,
            "pass_threshold": d.config.pass_threshold,
        },
    }
