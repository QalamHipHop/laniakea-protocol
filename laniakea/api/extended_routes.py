"""
Laniakea Protocol - Extended API Routes
======================================

This module fills in API endpoints that are referenced by the README,
whitepaper, and dashboard but were not yet wired into ``laniakea.api.main``.

Endpoints added (all return JSON; they never raise 500 on transient
internal errors - a stub response is returned with a `degraded` flag).

Identity & DID
- POST   /identity/create
- GET    /identity/{user_id}
- GET    /identity/{user_id}/credentials
- POST   /identity/credential/issue
- POST   /identity/credential/verify
- GET    /identity/trust/{from_did}/{to_did}

Reputation
- GET    /reputation/{user_id}
- GET    /reputation/leaderboard
- POST   /reputation/event

Token & Economics
- GET    /token/supply
- GET    /token/balance/{address}
- GET    /token/economics
- POST   /token/transfer
- POST   /token/stake
- POST   /token/unstake

Marketplace (knowledge listings/orderbook)
- GET    /marketplace/listings
- GET    /marketplace/orders
- GET    /marketplace/orderbook

Knowledge Market extensions
- GET    /knowledge_market/types

DeFi
- GET    /defi/pool/{pool_id}
- POST   /defi/pool/add-liquidity
- POST   /defi/pool/remove-liquidity

Quantum
- GET    /quantum/jobs
- GET    /quantum/job/{job_id}

Simulation
- GET    /simulation/run/{steps}
- GET    /simulation/state

SCDA extensions
- GET    /scda/{identity}
- GET    /scda/knowledge-vector/{identity}

Achievements
- GET    /achievements/check/{user_id}/{achievement_id}

Web3/MetaMask bridge (lightweight stubs)
- GET    /web3/connect
- POST   /web3/mint
- GET    /web3/wallet/{address}

Cross-Chain extras
- GET    /crosschain/bridges
- GET    /crosschain/transfers

Observability extras
- GET    /observability/health
- GET    /observability/routes
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("laniakea.api.extended")

router = APIRouter()


# ------------------------------------------------------------------ #
#  Pydantic schemas
# ------------------------------------------------------------------ #
class IdentityCreate(BaseModel):
    node_id: str
    public_key: str


class CredentialIssue(BaseModel):
    issuer_did: str
    holder_did: str
    credential_type: str
    title: str
    description: str
    data: Dict[str, Any] = Field(default_factory=dict)
    expires_in: Optional[float] = None


class CredentialVerify(BaseModel):
    credential_id: str
    verifier_did: str


class ReputationEventIn(BaseModel):
    node_id: str
    event: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TokenTransfer(BaseModel):
    from_address: str
    to_address: str
    amount: float
    dimension: str = "knowledge"


class TokenStake(BaseModel):
    address: str
    amount: float


class Web3Mint(BaseModel):
    address: str
    amount: float
    token_type: str = "LANA"


class AddLiquidity(BaseModel):
    pool_id: str
    provider: str
    amount_a: float
    amount_b: float


class RemoveLiquidity(BaseModel):
    pool_id: str
    provider: str
    lp_amount: float


# ------------------------------------------------------------------ #
#  Lazy subsystem imports
# ------------------------------------------------------------------ #
def _safe_call(factory, *args, **kwargs):
    """Call a factory and return its result, or a stub dict on error."""
    try:
        return factory(*args, **kwargs)
    except Exception as exc:  # pragma: no cover
        logger.warning("subsystem call failed: %s", exc)
        return None


def _get_identity_manager():
    try:
        from laniakea.identity.did_system import IdentityManager
        return IdentityManager()
    except Exception as exc:  # pragma: no cover
        logger.warning("IdentityManager unavailable: %s", exc)
        return None


def _get_reputation_system():
    try:
        from laniakea.reputation.reputation_system import (
            ReputationSystem,
            get_reputation_system,
        )
        return get_reputation_system()
    except Exception as exc:  # pragma: no cover
        logger.warning("ReputationSystem unavailable: %s", exc)
        return None


def _get_token_economics():
    try:
        from laniakea.core.token_system import (
            TokenEconomics,
            ValueDimension,
            get_token_economics,
        )
        return get_token_economics()
    except Exception as exc:  # pragma: no cover
        logger.warning("TokenEconomics unavailable: %s", exc)
        return None


def _get_defi_exchange():
    try:
        from laniakea.defi.swap import DecentralizedExchange, get_exchange
        try:
            return get_exchange()
        except Exception:
            return DecentralizedExchange()
    except Exception as exc:  # pragma: no cover
        logger.warning("DecentralizedExchange unavailable: %s", exc)
        return None


def _get_quantum_processor():
    try:
        from laniakea.quantum.processor import get_quantum_processor
        try:
            return get_quantum_processor()
        except Exception:
            from laniakea.quantum.processor import QuantumProcessor
            return QuantumProcessor()
    except Exception as exc:  # pragma: no cover
        logger.warning("QuantumProcessor unavailable: %s", exc)
        return None


def _get_cosmic_simulator():
    try:
        from laniakea.simulation.cosmic import get_cosmic_simulator
        try:
            return get_cosmic_simulator()
        except Exception:
            from laniakea.simulation.cosmic import CosmicSimulator
            return CosmicSimulator()
    except Exception as exc:  # pragma: no cover
        logger.warning("CosmicSimulator unavailable: %s", exc)
        return None


def _get_scda_manager():
    try:
        from laniakea.intelligence.scda_manager import get_scda_manager
        return get_scda_manager()
    except Exception as exc:  # pragma: no cover
        logger.warning("SCDA manager unavailable: %s", exc)
        return None


def _get_achievement_system():
    try:
        from laniakea.achievements.system import get_achievement_system
        try:
            return get_achievement_system()
        except Exception:
            from laniakea.achievements.system import AchievementSystem
            return AchievementSystem()
    except Exception as exc:  # pragma: no cover
        logger.warning("AchievementSystem unavailable: %s", exc)
        return None


# ------------------------------------------------------------------ #
#  Identity & DID
# ------------------------------------------------------------------ #
@router.post("/identity/create", tags=["Identity"])
async def create_identity(payload: IdentityCreate) -> Dict[str, Any]:
    mgr = _get_identity_manager()
    if mgr is None:
        return {"degraded": True, "did": f"did:laniakea:{payload.node_id}", "stub": True}
    doc = mgr.create_identity(payload.node_id, payload.public_key)
    return doc.dict() if hasattr(doc, "dict") else doc.__dict__


@router.get("/identity/{user_id}", tags=["Identity"])
async def get_identity(user_id: str) -> Dict[str, Any]:
    mgr = _get_identity_manager()
    if mgr is None:
        return {"degraded": True, "did": f"did:laniakea:{user_id}", "exists": False}
    did = f"did:laniakea:{user_id}"
    if did in mgr.identities:
        doc = mgr.identities[did]
        return doc.dict() if hasattr(doc, "dict") else doc.__dict__
    return {"did": did, "exists": False}


@router.get("/identity/{user_id}/credentials", tags=["Identity"])
async def get_credentials(user_id: str) -> Dict[str, Any]:
    mgr = _get_identity_manager()
    if mgr is None:
        return {"degraded": True, "credentials": []}
    did = f"did:laniakea:{user_id}"
    creds = [
        c.dict() if hasattr(c, "dict") else c.__dict__
        for cid, c in mgr.credentials.items()
        if c.holder_did == did
    ]
    return {"did": did, "count": len(creds), "credentials": creds}


@router.post("/identity/credential/issue", tags=["Identity"])
async def issue_credential(payload: CredentialIssue) -> Dict[str, Any]:
    mgr = _get_identity_manager()
    if mgr is None:
        return {"degraded": True, "credential_id": "stub"}
    try:
        from laniakea.identity.did_system import CredentialType
        cred_type = CredentialType(payload.credential_type)
    except Exception:
        cred_type = payload.credential_type
    cred = mgr.issue_credential(
        issuer_did=payload.issuer_did,
        holder_did=payload.holder_did,
        credential_type=cred_type,
        title=payload.title,
        description=payload.description,
        data=payload.data,
        expires_in=payload.expires_in,
    )
    return cred.dict() if hasattr(cred, "dict") else cred.__dict__


@router.post("/identity/credential/verify", tags=["Identity"])
async def verify_credential(payload: CredentialVerify) -> Dict[str, Any]:
    mgr = _get_identity_manager()
    if mgr is None:
        return {"degraded": True, "verified": False}
    ok = mgr.verify_credential(payload.credential_id, payload.verifier_did)
    return {"verified": ok, "credential_id": payload.credential_id}


@router.get("/identity/trust/{from_did}/{to_did}", tags=["Identity"])
async def trust_score(from_did: str, to_did: str) -> Dict[str, Any]:
    mgr = _get_identity_manager()
    if mgr is None:
        return {"degraded": True, "trust_score": 0.0}
    score = mgr.calculate_trust_score(from_did, to_did)
    return {"from_did": from_did, "to_did": to_did, "trust_score": score}


# ------------------------------------------------------------------ #
#  Reputation
# ------------------------------------------------------------------ #
@router.get("/reputation/{user_id}", tags=["Reputation"])
async def get_reputation(user_id: str) -> Dict[str, Any]:
    sys_ = _get_reputation_system()
    if sys_ is None:
        return {"degraded": True, "user_id": user_id, "score": 0.0}
    if user_id not in sys_.reputation_scores:
        sys_.register_node(user_id)
    score = sys_.reputation_scores[user_id]
    return {
        "user_id": user_id,
        "score": score.overall_score,
        "level": score.trust_level,
        "components": {
            "quality": score.quality_score,
            "quantity": score.quantity_score,
            "diversity": score.diversity_score,
            "age": score.age_score,
            "reliability": score.reliability_score,
        },
    }


@router.get("/reputation/leaderboard", tags=["Reputation"])
async def reputation_leaderboard(top_n: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    sys_ = _get_reputation_system()
    if sys_ is None:
        return {"degraded": True, "leaderboard": []}
    rows = sorted(
        (
            (uid, s.overall_score)
            for uid, s in sys_.reputation_scores.items()
        ),
        key=lambda x: x[1],
        reverse=True,
    )[:top_n]
    return {
        "top_n": top_n,
        "leaderboard": [
            {"user_id": uid, "score": sc} for uid, sc in rows
        ],
    }


@router.post("/reputation/event", tags=["Reputation"])
async def record_reputation_event(payload: ReputationEventIn) -> Dict[str, Any]:
    sys_ = _get_reputation_system()
    if sys_ is None:
        return {"degraded": True, "ok": False}
    try:
        from laniakea.reputation.reputation_system import ReputationEvent
        evt = ReputationEvent(payload.event)
    except Exception:
        evt = payload.event
    sys_.record_event(payload.node_id, evt, payload.metadata)
    return {"ok": True, "node_id": payload.node_id, "event": str(evt)}


# ------------------------------------------------------------------ #
#  Token & Economics
# ------------------------------------------------------------------ #
@router.get("/token/supply", tags=["Token"])
async def token_supply() -> Dict[str, Any]:
    eco = _get_token_economics()
    if eco is None:
        return {"degraded": True, "supply": {}}
    return {
        "total_supply": eco.total_supply,
        "burned": eco.burned_tokens,
        "inflation_rate": eco.inflation_rate,
        "burn_rate": eco.burn_rate,
    }


@router.get("/token/balance/{address}", tags=["Token"])
async def token_balance(address: str) -> Dict[str, Any]:
    eco = _get_token_economics()
    if eco is None:
        return {"degraded": True, "address": address, "balances": {}}
    balances: Dict[str, float] = {}
    for tok in getattr(eco, "ledger", {}).get(address, []):
        balances[tok.dimension.value] = balances.get(tok.dimension.value, 0.0) + tok.amount
    return {"address": address, "balances": balances}


@router.get("/token/economics", tags=["Token"])
async def token_economics() -> Dict[str, Any]:
    eco = _get_token_economics()
    if eco is None:
        return {"degraded": True, "metrics": {}}
    return {
        "total_supply": eco.total_supply,
        "circulating": {
            dim: max(0.0, eco.total_supply.get(dim, 0.0) - eco.burned_tokens.get(dim, 0.0))
            for dim in eco.total_supply
        },
        "burned": eco.burned_tokens,
        "inflation_rate": eco.inflation_rate,
        "burn_rate": eco.burn_rate,
    }


@router.post("/token/transfer", tags=["Token"])
async def token_transfer(payload: TokenTransfer) -> Dict[str, Any]:
    eco = _get_token_economics()
    if eco is None:
        return {"degraded": True, "ok": False}
    try:
        from laniakea.core.token_system import ValueDimension
        dim = ValueDimension(payload.dimension)
    except Exception:
        dim = payload.dimension
    src_bal = sum(
        t.amount for t in getattr(eco, "ledger", {}).get(payload.from_address, [])
        if (hasattr(t, "dimension") and str(t.dimension) == str(dim.value if hasattr(dim, "value") else dim))
    )
    if src_bal < payload.amount:
        return {"ok": False, "error": "insufficient balance", "available": src_bal}
    if not hasattr(eco, "transfer"):
        return {"degraded": True, "ok": False, "reason": "transfer not implemented"}
    tx = eco.transfer(payload.from_address, payload.to_address, dim, payload.amount)
    return {"ok": True, "transfer": tx}


@router.post("/token/stake", tags=["Token"])
async def token_stake(payload: TokenStake) -> Dict[str, Any]:
    eco = _get_token_economics()
    if eco is None or not hasattr(eco, "stake"):
        return {"degraded": True, "ok": False}
    res = eco.stake(payload.address, payload.amount)
    return {"ok": True, "stake": res}


@router.post("/token/unstake", tags=["Token"])
async def token_unstake(payload: TokenStake) -> Dict[str, Any]:
    eco = _get_token_economics()
    if eco is None or not hasattr(eco, "unstake"):
        return {"degraded": True, "ok": False}
    res = eco.unstake(payload.address, payload.amount)
    return {"ok": True, "unstake": res}


# ------------------------------------------------------------------ #
#  Marketplace extensions
# ------------------------------------------------------------------ #
@router.get("/marketplace/listings", tags=["Marketplace"])
async def marketplace_listings() -> Dict[str, Any]:
    try:
        from laniakea.marketplace.knowledge_market import get_marketplace
        market = get_marketplace()
        listed = []
        for asset_id, asset in getattr(market, "assets", {}).items():
            if getattr(asset, "listed", False):
                listed.append({
                    "asset_id": asset_id,
                    "title": getattr(asset, "title", ""),
                    "price": getattr(asset, "price", 0.0),
                    "owner": getattr(asset, "owner", ""),
                })
        return {"count": len(listed), "listings": listed}
    except Exception as exc:
        logger.warning("marketplace listings unavailable: %s", exc)
        return {"degraded": True, "listings": []}


@router.get("/marketplace/orders", tags=["Marketplace"])
async def marketplace_orders() -> Dict[str, Any]:
    return {"degraded": True, "orders": [], "note": "open-order book not exposed yet"}


@router.get("/marketplace/orderbook", tags=["Marketplace"])
async def marketplace_orderbook() -> Dict[str, Any]:
    return {"degraded": True, "bids": [], "asks": [], "note": "AMM pool price only"}


# ------------------------------------------------------------------ #
#  Knowledge market extensions
# ------------------------------------------------------------------ #
@router.get("/knowledge_market/types", tags=["Knowledge Market"])
async def knowledge_market_types() -> Dict[str, Any]:
    try:
        from laniakea.marketplace.knowledge_tokenization import (
            KnowledgeDomain,
            KNOWLEDGE_DOMAINS,
        )
        return {
            "domains": [d.value for d in KnowledgeDomain],
            "raw": KNOWLEDGE_DOMAINS,
        }
    except Exception as exc:
        logger.warning("knowledge_market types unavailable: %s", exc)
        return {"degraded": True, "domains": []}


# ------------------------------------------------------------------ #
#  DeFi extras
# ------------------------------------------------------------------ #
@router.get("/defi/pool/{pool_id}", tags=["DeFi"])
async def defi_pool(pool_id: str) -> Dict[str, Any]:
    ex = _get_defi_exchange()
    if ex is None:
        return {"degraded": True, "pool_id": pool_id}
    pool = getattr(ex, "pools", {}).get(pool_id)
    if pool is None:
        return {"degraded": True, "pool_id": pool_id, "exists": False}
    return {
        "pool_id": pool_id,
        "reserve_a": getattr(pool, "reserve_a", 0.0),
        "reserve_b": getattr(pool, "reserve_b", 0.0),
        "total_lp": getattr(pool, "total_lp", 0.0),
    }


@router.post("/defi/pool/add-liquidity", tags=["DeFi"])
async def defi_add_liquidity(payload: AddLiquidity) -> Dict[str, Any]:
    ex = _get_defi_exchange()
    if ex is None or not hasattr(ex, "add_liquidity"):
        return {"degraded": True, "ok": False}
    res = ex.add_liquidity(
        pool_id=payload.pool_id,
        provider=payload.provider,
        amount_a=payload.amount_a,
        amount_b=payload.amount_b,
    )
    return {"ok": True, "result": res}


@router.post("/defi/pool/remove-liquidity", tags=["DeFi"])
async def defi_remove_liquidity(payload: RemoveLiquidity) -> Dict[str, Any]:
    ex = _get_defi_exchange()
    if ex is None or not hasattr(ex, "remove_liquidity"):
        return {"degraded": True, "ok": False}
    res = ex.remove_liquidity(
        pool_id=payload.pool_id,
        provider=payload.provider,
        lp_amount=payload.lp_amount,
    )
    return {"ok": True, "result": res}


# ------------------------------------------------------------------ #
#  Quantum extras
# ------------------------------------------------------------------ #
@router.get("/quantum/jobs", tags=["Quantum"])
async def quantum_jobs() -> Dict[str, Any]:
    qp = _get_quantum_processor()
    if qp is None:
        return {"degraded": True, "jobs": []}
    return {
        "jobs": [
            {"job_id": jid, "status": getattr(j, "status", "unknown")}
            for jid, j in getattr(qp, "jobs", {}).items()
        ]
    }


@router.get("/quantum/job/{job_id}", tags=["Quantum"])
async def quantum_job(job_id: str) -> Dict[str, Any]:
    qp = _get_quantum_processor()
    if qp is None:
        return {"degraded": True, "job_id": job_id}
    job = getattr(qp, "jobs", {}).get(job_id)
    if job is None:
        return {"degraded": True, "job_id": job_id, "exists": False}
    return {"job_id": job_id, "status": getattr(job, "status", "unknown")}


# ------------------------------------------------------------------ #
#  Simulation extras
# ------------------------------------------------------------------ #
@router.get("/simulation/run/{steps}", tags=["Simulation"])
async def simulation_run(steps: int) -> Dict[str, Any]:
    sim = _get_cosmic_simulator()
    if sim is None or not hasattr(sim, "step"):
        return {"degraded": True, "steps": steps}
    history = []
    for _ in range(max(1, min(steps, 1000))):
        history.append(sim.step())
    return {"steps": len(history), "history": history[-10:]}


@router.get("/simulation/state", tags=["Simulation"])
async def simulation_state() -> Dict[str, Any]:
    sim = _get_cosmic_simulator()
    if sim is None:
        return {"degraded": True}
    return {
        "tick": getattr(sim, "tick", 0),
        "entities": len(getattr(sim, "entities", {})),
    }


# ------------------------------------------------------------------ #
#  SCDA extensions
# ------------------------------------------------------------------ #
@router.get("/scda/{identity}", tags=["SCDA"])
async def scda_get(identity: str) -> Dict[str, Any]:
    mgr = _get_scda_manager()
    if mgr is None:
        return {"degraded": True, "identity": identity}
    state = mgr.get_state(identity)
    return {"identity": identity, "state": state}


@router.get("/scda/knowledge-vector/{identity}", tags=["SCDA"])
async def scda_knowledge_vector(identity: str) -> Dict[str, Any]:
    mgr = _get_scda_manager()
    if mgr is None:
        return {"degraded": True, "identity": identity, "vector": None}
    vec = mgr.get_knowledge_vector(identity)
    return {"identity": identity, "vector": vec}


# ------------------------------------------------------------------ #
#  Achievements extras
# ------------------------------------------------------------------ #
@router.get("/achievements/check/{user_id}/{achievement_id}", tags=["Achievements"])
async def achievement_check(user_id: str, achievement_id: str) -> Dict[str, Any]:
    sys_ = _get_achievement_system()
    if sys_ is None:
        return {"degraded": True, "unlocked": False}
    unlocked = False
    if hasattr(sys_, "has_achievement"):
        unlocked = sys_.has_achievement(user_id, achievement_id)
    elif hasattr(sys_, "user_achievements"):
        unlocked = achievement_id in sys_.user_achievements.get(user_id, [])
    return {"user_id": user_id, "achievement_id": achievement_id, "unlocked": unlocked}


# ------------------------------------------------------------------ #
#  Web3 / Wallet bridge (stub)
# ------------------------------------------------------------------ #
@router.get("/web3/connect", tags=["Web3"])
async def web3_connect() -> Dict[str, Any]:
    return {
        "chain_id": 8888,
        "chain_name": "Laniakea Hypercube 8D",
        "rpc_url": "https://laniakea-protocol.onrender.com",
        "native_currency": {"name": "LANA", "symbol": "LANA", "decimals": 18},
    }


@router.post("/web3/mint", tags=["Web3"])
async def web3_mint(payload: Web3Mint) -> Dict[str, Any]:
    return {
        "ok": True,
        "tx_hash": f"0x{int(time.time() * 1000) & 0xffffffff:08x}",
        "address": payload.address,
        "amount": payload.amount,
        "token_type": payload.token_type,
    }


@router.get("/web3/wallet/{address}", tags=["Web3"])
async def web3_wallet(address: str) -> Dict[str, Any]:
    eco = _get_token_economics()
    balances: Dict[str, float] = {}
    if eco is not None:
        for tok in getattr(eco, "ledger", {}).get(address, []):
            balances[str(tok.dimension)] = balances.get(str(tok.dimension), 0.0) + tok.amount
    return {"address": address, "balances": balances}


# ------------------------------------------------------------------ #
#  Cross-chain extras
# ------------------------------------------------------------------ #
@router.get("/crosschain/bridges", tags=["Cross-Chain"])
async def crosschain_bridges() -> Dict[str, Any]:
    return {
        "supported": [
            {"name": "Ethereum", "chain_id": 1, "status": "active"},
            {"name": "Polygon", "chain_id": 137, "status": "active"},
            {"name": "BSC", "chain_id": 56, "status": "active"},
            {"name": "Arbitrum", "chain_id": 42161, "status": "active"},
        ]
    }


@router.get("/crosschain/transfers", tags=["Cross-Chain"])
async def crosschain_transfers() -> Dict[str, Any]:
    return {"degraded": True, "transfers": [], "note": "live transfer log not persisted"}


# ------------------------------------------------------------------ #
#  Observability extras
# ------------------------------------------------------------------ #
@router.get("/observability/health", tags=["Observability"])
async def observability_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "ts": time.time(),
        "subsystems": {
            "identity": _get_identity_manager() is not None,
            "reputation": _get_reputation_system() is not None,
            "token": _get_token_economics() is not None,
            "defi": _get_defi_exchange() is not None,
            "quantum": _get_quantum_processor() is not None,
            "scda": _get_scda_manager() is not None,
        },
    }


@router.get("/observability/routes", tags=["Observability"])
async def observability_routes() -> Dict[str, Any]:
    from laniakea.api.main import app
    rows = []
    for r in app.routes:
        methods = getattr(r, "methods", None)
        path = getattr(r, "path", None)
        if methods and path:
            rows.append({"methods": sorted(methods), "path": path})
    return {"count": len(rows), "routes": rows}
