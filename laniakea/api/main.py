"""
Laniakea Protocol - Unified API
================================

The unified FastAPI surface that wires together every core subsystem of the
Laniakea protocol. This module is intentionally defensive: every optional /
heavy import is wrapped so that a missing dependency (e.g. ``openai``) does
not take the entire API down.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- Core utilities ---------------------------------------------------------
from laniakea.core.config import settings
from laniakea.utils.logger import setup_logger

# --- Subsystem imports (wrapped so a single broken module cannot kill boot) -
def _safe_import(module: str, attr: str) -> Any:
    """Return ``module.attr`` or a stub if the import fails."""
    try:
        return getattr(__import__(module, fromlist=[attr]), attr)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Optional subsystem unavailable: %s (%s)", module, exc)
        return None


logger = setup_logger("laniakea.api")

# --- Core systems -----------------------------------------------------------
from laniakea.blockchain.core import Blockchain  # noqa: E402
from laniakea.consensus.poa import ProofOfAuthority  # noqa: E402
from laniakea.crosschain.bridge import Bridge  # noqa: E402
from laniakea.quantum.processor import QuantumProcessor, QuantumCircuit  # noqa: E402
from laniakea.governance.dao import DAO  # noqa: E402
from laniakea.marketplace.nft import Marketplace  # noqa: E402
from laniakea.simulation.cosmic import CosmicSimulator, CosmicEntity  # noqa: E402
from laniakea.dashboard.metrics import ProtocolMetrics  # noqa: E402
from laniakea.achievements.system import AchievementSystem  # noqa: E402
from laniakea.ai.model import AIModel  # noqa: E402
from laniakea.defi.swap import DecentralizedExchange, LiquidityPool  # noqa: E402

# Diplomacy lives in ``governance.metaverse_diplomacy`` (legacy reference was
# ``laniakea.diplomacy.core`` which never existed in this repo).
try:  # pragma: no cover - defensive
    from laniakea.governance.metaverse_diplomacy import (
        DiplomacySystem,
        get_diplomacy_system,
    )
except Exception:  # pragma: no cover
    DiplomacySystem = None  # type: ignore[assignment]
    get_diplomacy_system = None  # type: ignore[assignment]
    logger.warning("DiplomacySystem unavailable - diplomacy endpoints will be disabled")

# KnowledgeMarket used to live at ``laniakea.knowledge_market.core`` in the
# MVP plan. The real implementation is in
# ``laniakea.marketplace.knowledge_market`` so we shim it.
try:  # pragma: no cover - defensive
    from laniakea.marketplace.knowledge_market import (
        KnowledgeMarketplace as KnowledgeMarket,
        get_marketplace as get_knowledge_market,
    )
except Exception:  # pragma: no cover
    KnowledgeMarket = None  # type: ignore[assignment]
    get_knowledge_market = None  # type: ignore[assignment]
    logger.warning("KnowledgeMarket unavailable - knowledge-market endpoints will be disabled")

# SCDA subsystem
try:
    from laniakea.intelligence.scda_manager import get_scda_manager
except Exception:  # pragma: no cover - defensive
    get_scda_manager = None  # type: ignore[assignment]
    logger.warning("SCDA manager unavailable - SCDA endpoints will be disabled")


# --- App bootstrap ----------------------------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "The unified API for the Laniakea Protocol, integrating all core "
        "modules: blockchain, cross-chain bridge, quantum simulation, "
        "governance, marketplace, simulation, dashboard, achievements, AI, "
        "DeFi, diplomacy and knowledge market."
    ),
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# --- CORS middleware -------------------------------------------------------
_cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "*")
_cors_origins = [o.strip() for o in _cors_origins_env.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCDA disk persistence (best-effort, opt-in) ---------------------------
# Loads any existing SCDA snapshot from disk and arms an auto-save hook so
# SCDAs survive process restarts. Disabled automatically if a custom path
# is set to /dev/null or the data dir is not writable.
try:
    _scda_persist_path = os.getenv("LANIAKEA_SCDA_SNAPSHOT", "")
    if _scda_persist_path and _scda_persist_path != "/dev/null":
        from laniakea.intelligence.scda_persistence import install_persistence

        install_persistence(path=_scda_persist_path)
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("SCDA persistence install failed: %s", exc)

# --- Laniakea middleware stack (request-id, security headers, rate-limit) -
try:
    from laniakea.api.middleware import install_default_middleware
    install_default_middleware(app)
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("Laniakea middleware stack unavailable: %s", exc)


# --- Global exception handler ---------------------------------------------
@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Convert unhandled exceptions into a uniform JSON error response.

    This prevents FastAPI from returning its default 500 with HTML/empty
    body and gives the client a stable contract to parse.
    """
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": exc.__class__.__name__,
            "message": str(exc),
            "path": request.url.path,
        },
    )


# --- Request-counter middleware ---------------------------------------------
_request_count = {"total": 0, "by_path": {}}


@app.middleware("http")
async def _request_counter_middleware(request: Request, call_next):
    """Lightweight per-route request counter for /observability endpoints."""
    _request_count["total"] += 1
    bucket = _request_count["by_path"]
    bucket[request.url.path] = bucket.get(request.url.path, 0) + 1
    response = await call_next(request)
    return response


@app.get("/discovery", tags=["System"])
def discovery() -> Dict[str, Any]:
    """Return a machine-readable index of every HTTP route in the API."""
    out = []
    for r in app.routes:
        path = getattr(r, "path", None)
        if not path:
            continue
        methods = getattr(r, "methods", None) or set()
        out.append({
            "path": path,
            "methods": sorted(methods) if methods else [],
            "tags": getattr(r, "tags", []) or [],
            "name": getattr(r, "name", None),
        })
    return {"count": len(out), "routes": out}


@app.get("/observability/requests", tags=["Observability"])
def request_stats() -> Dict[str, Any]:
    """Return the in-process request counter (useful for live-traffic checks)."""
    top = sorted(
        _request_count["by_path"].items(), key=lambda kv: -kv[1]
    )[:20]
    return {
        "total": _request_count["total"],
        "top_paths": [{"path": p, "count": c} for p, c in top],
    }

# --- Initialise subsystems --------------------------------------------------
laniakea_chain = Blockchain()
laniakea_consensus = ProofOfAuthority(settings.AUTHORITIES)
laniakea_bridge = Bridge(supported_chains=settings.SUPPORTED_CHAINS)
laniakea_quantum = QuantumProcessor(max_qubits=settings.MAX_QUBITS)
laniakea_dao = DAO(total_supply=settings.TOTAL_TOKEN_SUPPLY)
laniakea_marketplace = Marketplace()
laniakea_simulator = CosmicSimulator(time_step=settings.SIMULATION_TIME_STEP)
laniakea_metrics = ProtocolMetrics()
laniakea_achievements = AchievementSystem()
laniakea_ai = AIModel("LANA_KE_001")
laniakea_dex = DecentralizedExchange()
laniakea_diplomacy = get_diplomacy_system() if get_diplomacy_system is not None else None
laniakea_knowledge_market = get_knowledge_market() if get_knowledge_market is not None else None
laniakea_scda_manager = get_scda_manager() if get_scda_manager is not None else None

# Seed the cosmic simulator with two example entities.
laniakea_simulator.add_entity(
    CosmicEntity("Laniakea_Core", "Galaxy", [0.0, 0.0, 0.0], 1.0e42)
)
laniakea_simulator.add_entity(
    CosmicEntity("Milky_Way", "Galaxy", [1.0e22, 0.0, 0.0], 1.5e42)
)

# --- Genesis SCDA seed (opt-in, non-destructive) ---------------------------
# If the SCDA registry is empty AND genesis seeding is enabled via the
# ``LANIAKEA_GENESIS_SEED`` env var, create a small set of named SCDAs so
# the dashboards have something to render on first boot. This mirrors the
# cosmic-simulator seeding above and is a no-op when the registry already
# contains identities (e.g. loaded from a snapshot).
try:
    _genesis_enabled = os.getenv("LANIAKEA_GENESIS_SEED", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if (
        _genesis_enabled
        and laniakea_scda_manager is not None
        and not laniakea_scda_manager.list_identities()
    ):
        _GENESIS_SCDAS = [
            "Qalam-Origin",
            "Cosmos-One",
            "Nebula-Prime",
            "Andromeda-Seed",
            "Aurora-Zero",
        ]
        for _ident in _GENESIS_SCDAS:
            laniakea_scda_manager.create(_ident)
        logger.info(
            "Genesis SCDA seed created %d identities: %s",
            len(_GENESIS_SCDAS),
            ", ".join(_GENESIS_SCDAS),
        )
except Exception as _exc:  # pragma: no cover - defensive
    logger.warning("Genesis SCDA seed failed: %s", _exc)

logger.info(
    "Laniakea Protocol v%s initialised. Diplomacy=%s, KnowledgeMarket=%s",
    settings.PROJECT_VERSION,
    laniakea_diplomacy is not None,
    laniakea_knowledge_market is not None,
)


# --- Pydantic models --------------------------------------------------------
class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float


class BlockResponse(BaseModel):
    index: int
    timestamp: float
    transactions: List[Dict[str, Any]]
    proof: Any
    previous_hash: str


class BridgeTransfer(BaseModel):
    source_chain: str
    target_chain: str
    asset: str
    amount: float
    sender: str
    recipient: str


class AIQuery(BaseModel):
    prompt: str


class SwapRequest(BaseModel):
    token_in: str
    token_out: str
    amount_in: float


class QuantumJob(BaseModel):
    num_qubits: int
    gates: List[Dict[str, Any]]


class NFTMint(BaseModel):
    owner: str
    metadata_uri: str
    asset_type: str


class ProposalCreate(BaseModel):
    title: str
    description: str
    proposer: str


class VoteCast(BaseModel):
    voter_address: str
    vote_type: str  # "for" or "against"


class KnowledgeTokenizeRequest(BaseModel):
    owner_scda_id: str
    scda_knowledge_vector: List[float]
    complexity_index: float
    knowledge_type: Optional[str] = "General"


class KnowledgeListRequest(BaseModel):
    asset_id: str
    price: float


class KnowledgeBuyRequest(BaseModel):
    asset_id: str
    buyer_scda_id: str


class DiplomacyAllianceRequest(BaseModel):
    name: str
    founder_scda_id: str
    members: List[str]
    initial_knowledge_vectors: Optional[Dict[str, List[float]]] = None


class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = None


# --- Optional API routers ---------------------------------------------------
# Knowledge market router
try:
    from laniakea.api.knowledge_market_api import router as knowledge_market_router
    app.include_router(knowledge_market_router, tags=["Knowledge Market"])
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("knowledge_market_api router not loaded: %s", exc)
    knowledge_market_router = None

try:
    from laniakea.api.diplomacy_api import router as diplomacy_router
    # Share the DiplomacySystem instance with the router so that the state
    # is consistent across /diplomacy/alliance and /diplomacy/alliances.
    try:
        from laniakea.api import diplomacy_api as _diplomacy_api
        if laniakea_diplomacy is not None:
            _diplomacy_api.set_shared_diplomacy(laniakea_diplomacy)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Could not share DiplomacySystem instance: %s", exc)
    app.include_router(diplomacy_router, tags=["Diplomacy"])
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("diplomacy_api router not loaded: %s", exc)
    diplomacy_router = None

try:
    from laniakea.api.llm_api import router as llm_router
    app.include_router(llm_router, tags=["LLM Integration"])
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("llm_api router not loaded: %s", exc)
    llm_router = None

try:
    from laniakea.api.scda_api import router as scda_router, set_shared_manager as _set_scda
    if laniakea_scda_manager is not None:
        _set_scda(laniakea_scda_manager)
    app.include_router(scda_router, tags=["SCDA"])
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("scda_api router not loaded: %s", exc)
    scda_router = None

try:
    from laniakea.api.scda_integration_api import router as scda_integration_router
    app.include_router(scda_integration_router, tags=["SCDA Integration"])
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("scda_integration_api router not loaded: %s", exc)
    scda_integration_router = None

try:
    from laniakea.api.observability_api import router as observability_router
    app.include_router(observability_router, tags=["Observability"])
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("observability_api router not loaded: %s", exc)
    observability_router = None

# Web3 wallet integration (SIWE auth + wallet<->SCDA binding)
try:
    from laniakea.api.web3_api import router as web3_router
    app.include_router(web3_router)
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("web3_api router not loaded: %s", exc)
    web3_router = None

# SCDA breeding system
try:
    from laniakea.api.breeding_api import router as breeding_router
    app.include_router(breeding_router)
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("breeding_api router not loaded: %s", exc)
    breeding_router = None

# Governance v2 (proposal lifecycle + delegation + treasury)
try:
    from laniakea.api.governance_api import router as governance_router
    app.include_router(governance_router)
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("governance_api router not loaded: %s", exc)
    governance_router = None

# Self-evolution API: HTTP surface over laniakea.intelligence.self_evolution.
# The engine already exists; this just exposes /evolution/{status,scan,suggest,improve,log}.
try:
    from laniakea.api.self_evolution_api import router as self_evolution_router
    app.include_router(self_evolution_router, tags=["Self-Evolution"])
    logger.info("Self-Evolution API mounted at /evolution")
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("self_evolution_api router not loaded: %s", exc)
    self_evolution_router = None


# --- WebSocket Manager (optional, lazy-loaded) ----------------------------
_websocket_manager = None
try:
    from laniakea.websocket.websocket_manager import WebSocketManager
    _websocket_manager = WebSocketManager()
    logger.info("WebSocketManager initialised")
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("WebSocketManager unavailable: %s", exc)


# --- System endpoints -------------------------------------------------------
@app.get("/", tags=["System"])
def read_root() -> Dict[str, Any]:
    """Root endpoint that returns a welcome message and a feature inventory."""
    logger.info("Root endpoint accessed.")
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} Unified API",
        "version": settings.PROJECT_VERSION,
        "environment": settings.DEPLOYMENT_ENV,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "health": "/health",
        "status": "/core/status",
        "subsystems": {
            "blockchain": True,
            "consensus": True,
            "crosschain": True,
            "quantum": True,
            "governance": True,
            "marketplace": True,
            "simulation": True,
            "dashboard": True,
            "achievements": True,
            "ai": True,
            "defi": True,
            "diplomacy": laniakea_diplomacy is not None,
            "knowledge_market": laniakea_knowledge_market is not None,
            "scda": laniakea_scda_manager is not None,
        },
    }


@app.on_event("startup")
async def _on_startup() -> None:
    """Capture service start time so /health can report uptime."""
    import time as _t
    app.state.start_time = _t.time()
    logger.info("Laniakea API startup complete (v%s)", settings.PROJECT_VERSION)


@app.get("/health", tags=["System"])
def healthcheck() -> Dict[str, Any]:
    """Liveness/readiness probe with uptime. Used by Render / Kubernetes."""
    import time as _t
    start = getattr(app.state, "start_time", _t.time())
    return {
        "status": "ok",
        "version": settings.PROJECT_VERSION,
        "uptime_seconds": round(_t.time() - start, 3),
        "environment": settings.DEPLOYMENT_ENV,
    }


# --- Blockchain endpoints ---------------------------------------------------
@app.get("/blockchain/info", tags=["Blockchain"])
def blockchain_info() -> Dict[str, Any]:
    """Return chain summary (length, latest block hash, pending tx count)."""
    return {
        "length": len(laniakea_chain.chain),
        "latest_hash": laniakea_chain.last_block.hash if hasattr(laniakea_chain, "last_block") else None,
        "pending_transactions": len(getattr(laniakea_chain, "current_transactions", [])),
    }


@app.get("/blockchain/chain", response_model=List[BlockResponse], tags=["Blockchain"])
def full_chain() -> List[Dict[str, Any]]:
    return [block.to_dict() for block in laniakea_chain.chain]


@app.post("/blockchain/transactions/new", tags=["Blockchain"])
def new_transaction(tx: Transaction) -> Dict[str, Any]:
    index = laniakea_chain.new_transaction(tx.sender, tx.recipient, tx.amount)
    logger.info("New transaction from %s to %s queued for block %s", tx.sender, tx.recipient, index)
    return {"message": f"Transaction will be added to Block {index}"}


@app.post("/blockchain/mine", tags=["Blockchain"])
def mine_block(authority_address: Optional[str] = None) -> Dict[str, Any]:
    if not settings.AUTHORITIES:
        logger.error("Cannot mine: No authorities defined in settings.")
        raise HTTPException(status_code=503, detail="Service Unavailable: No mining authorities configured.")

    if authority_address is None:
        authority_address = settings.AUTHORITIES[0]
    if authority_address not in settings.AUTHORITIES:
        logger.warning("Unauthorized mine attempt by %s.", authority_address)
        raise HTTPException(status_code=403, detail="Not a recognized authority.")

    new_block = laniakea_consensus.sign_block(laniakea_chain, authority_address)
    logger.info("New block %s forged by %s.", new_block.index, authority_address)

    laniakea_metrics.update_metric("latest_block_height", new_block.index)
    laniakea_metrics.update_metric(
        "total_transactions",
        laniakea_metrics.metrics["total_transactions"] + len(new_block.transactions),
    )
    laniakea_achievements.update_user_progress(
        authority_address, "blockchain.blocks_mined", new_block.index
    )

    return {"message": "New Block Forged", "block": new_block.to_dict()}


# --- Cross-chain endpoints --------------------------------------------------
@app.get("/crosschain/supported", tags=["Cross-Chain"])
def crosschain_supported() -> Dict[str, Any]:
    """Return supported cross-chain routes and the bridge instance stats."""
    try:
        supported = list(laniakea_bridge.supported_chains or [])
    except Exception:
        supported = list(getattr(settings, "SUPPORTED_CHAINS", []))
    return {
        "supported_chains": supported,
        "active_transfers": len(getattr(laniakea_bridge, "pending_transactions", {})),
        "completed_transfers": len(getattr(laniakea_bridge, "completed_transactions", {})),
    }


@app.post("/crosschain/transfer/initiate", tags=["Cross-Chain"])
def initiate_cross_chain_transfer(transfer: BridgeTransfer) -> Dict[str, Any]:
    try:
        tx = laniakea_bridge.initiate_transfer(
            transfer.source_chain,
            transfer.target_chain,
            transfer.asset,
            transfer.amount,
            transfer.sender,
            transfer.recipient,
        )
        logger.info("Cross-chain transfer initiated: %s", tx.tx_id)
        laniakea_achievements.update_user_progress(
            transfer.sender,
            "crosschain.transfers_completed",
            len(laniakea_bridge.completed_transactions) + 1,
        )
        return {"message": "Transfer initiated successfully", "tx_id": tx.tx_id}
    except ValueError as exc:
        logger.error("Cross-chain initiation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/crosschain/transfer/complete/{tx_id}", tags=["Cross-Chain"])
def complete_cross_chain_transfer(tx_id: str) -> Dict[str, Any]:
    try:
        tx = laniakea_bridge.complete_transfer(tx_id)
        logger.info("Cross-chain transfer completed: %s", tx.tx_id)
        return {"message": "Transfer completed successfully", "tx": tx.to_dict()}
    except ValueError as exc:
        logger.error("Cross-chain completion failed for %s: %s", tx_id, exc)
        raise HTTPException(status_code=404, detail=str(exc))


# --- Quantum endpoints ------------------------------------------------------
@app.post("/quantum/job/submit", tags=["Quantum"])
def submit_quantum_job(job: QuantumJob) -> Dict[str, Any]:
    try:
        qc = laniakea_quantum.create_circuit(job.num_qubits)
        for gate in job.gates:
            gate_type = gate.get("type", "").lower()
            target = int(gate.get("target", 0))
            if gate_type == "h":
                qc.h_gate(target)
            elif gate_type == "x":
                qc.x_gate(target)
            else:
                raise ValueError(f"Unsupported gate type: {gate_type}")

        laniakea_quantum.submit_job(qc)
        laniakea_metrics.update_metric("quantum_job_queue_size", len(laniakea_quantum.job_queue))
        laniakea_achievements.update_user_progress(
            "System", "quantum.jobs_submitted", len(laniakea_quantum.job_queue)
        )
        logger.info("Quantum job submitted with %s qubits.", job.num_qubits)
        return {"message": "Quantum job submitted", "queue_size": len(laniakea_quantum.job_queue)}
    except ValueError as exc:
        logger.error("Quantum job submission failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/quantum/job/process", tags=["Quantum"])
def process_quantum_job() -> Dict[str, Any]:
    result = laniakea_quantum.process_next_job()
    laniakea_metrics.update_metric("quantum_job_queue_size", len(laniakea_quantum.job_queue))
    if result is None:
        logger.info("No pending quantum jobs to process.")
        return {"message": "No pending quantum jobs"}
    logger.info("Quantum job processed. Result: %s", result)
    return {"message": "Quantum job processed", "result": result}


# --- Governance endpoints ---------------------------------------------------
@app.get("/governance/proposals", tags=["Governance"])
def list_proposals() -> List[Dict[str, Any]]:
    """List all DAO proposals (active + finalized)."""
    out: List[Dict[str, Any]] = []
    for proposal in laniakea_dao.proposals.values():
        out.append({
            "proposal_id": proposal.proposal_id,
            "title": proposal.title,
            "description": proposal.description,
            "proposer": proposal.proposer,
            "status": proposal.status,
            "votes_for": getattr(proposal, "votes_for", 0),
            "votes_against": getattr(proposal, "votes_against", 0),
            "voter_count": len(getattr(proposal, "voters", [])),
        })
    return out


@app.get("/governance/proposals/{proposal_id}", tags=["Governance"])
def get_proposal(proposal_id: int) -> Dict[str, Any]:
    """Return full details for a single proposal."""
    proposal = laniakea_dao.proposals.get(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail=f"Proposal {proposal_id} not found")
    return {
        "proposal_id": proposal.proposal_id,
        "title": proposal.title,
        "description": proposal.description,
        "proposer": proposal.proposer,
        "status": proposal.status,
        "votes_for": getattr(proposal, "votes_for", 0),
        "votes_against": getattr(proposal, "votes_against", 0),
        "voters": list(getattr(proposal, "voters", [])),
        "vote_types": getattr(proposal, "vote_types", {}),
    }


@app.post("/governance/proposals/new", tags=["Governance"])
def create_proposal(prop: ProposalCreate) -> Dict[str, Any]:
    proposal = laniakea_dao.create_proposal(prop.title, prop.description, prop.proposer)
    logger.info("New DAO proposal created by %s: %s", prop.proposer, prop.title)
    return {"message": "Proposal created", "proposal_id": proposal.proposal_id}


@app.post("/governance/proposals/{proposal_id}/vote", tags=["Governance"])
def cast_vote(proposal_id: int, vote: VoteCast) -> Dict[str, Any]:
    try:
        laniakea_dao.vote(proposal_id, vote.voter_address, vote.vote_type)
        progress = laniakea_dao.proposals[proposal_id].voters
        laniakea_achievements.update_user_progress(
            vote.voter_address, "governance.votes_cast", len(progress)
        )
        logger.info("Vote cast by %s on proposal %s.", vote.voter_address, proposal_id)
        return {"message": "Vote cast successfully"}
    except ValueError as exc:
        logger.error("Vote failed on proposal %s: %s", proposal_id, exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/governance/proposals/{proposal_id}/finalize", tags=["Governance"])
def finalize_proposal(proposal_id: int) -> Dict[str, Any]:
    try:
        laniakea_dao.finalize_proposal(proposal_id)
        status = laniakea_dao.proposals[proposal_id].status
        logger.info("Proposal %s finalized with status: %s", proposal_id, status)
        return {"message": f"Proposal {proposal_id} finalized", "status": status}
    except ValueError as exc:
        logger.error("Finalization failed for proposal %s: %s", proposal_id, exc)
        raise HTTPException(status_code=404, detail=str(exc))


# --- Marketplace (NFT) endpoints --------------------------------------------
@app.post("/marketplace/nft/mint", tags=["Marketplace"])
def mint_nft(nft_data: NFTMint) -> Dict[str, Any]:
    nft = laniakea_marketplace.mint_nft(nft_data.owner, nft_data.metadata_uri, nft_data.asset_type)
    logger.info("NFT %s minted for %s.", nft.token_id, nft_data.owner)
    return {"message": "NFT minted successfully", "token_id": nft.token_id}


@app.post("/marketplace/nft/{token_id}/list", tags=["Marketplace"])
def list_nft(token_id: str, price: float) -> Dict[str, Any]:
    try:
        laniakea_marketplace.list_nft(token_id, price)
        logger.info("NFT %s listed for sale at %s LANA.", token_id, price)
        return {"message": f"NFT {token_id} listed for {price}"}
    except ValueError as exc:
        logger.error("NFT listing failed for %s: %s", token_id, exc)
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/marketplace/nft/{token_id}/buy", tags=["Marketplace"])
def buy_nft(token_id: str, buyer: str) -> Dict[str, Any]:
    try:
        nft = laniakea_marketplace.buy_nft(token_id, buyer)
        logger.info("NFT %s purchased by %s.", token_id, buyer)
        return {"message": f"NFT {token_id} purchased by {buyer}", "new_owner": nft.owner}
    except ValueError as exc:
        logger.error("NFT purchase failed for %s: %s", token_id, exc)
        raise HTTPException(status_code=400, detail=str(exc))


# --- Simulation endpoints ---------------------------------------------------
@app.post("/simulation/step", tags=["Simulation"])
def step_simulation() -> Dict[str, Any]:
    laniakea_simulator.step_simulation()
    laniakea_achievements.update_user_progress(
        "System",
        "simulation.steps_run",
        int(laniakea_simulator.current_time / laniakea_simulator.time_step),
    )
    logger.info("Cosmic simulation stepped. Current time: %s", laniakea_simulator.current_time)
    return {
        "message": "Simulation advanced one step",
        "current_time": laniakea_simulator.current_time,
    }


@app.get("/simulation/entities", tags=["Simulation"])
def get_simulation_entities() -> List[Dict[str, Any]]:
    return [entity.to_dict() for entity in laniakea_simulator.entities]


# --- Dashboard endpoints ----------------------------------------------------
@app.get("/dashboard/metrics", tags=["Dashboard"])
def get_metrics() -> Dict[str, Any]:
    return laniakea_metrics.get_all_metrics()


@app.get("/dashboard/history/{key}", tags=["Dashboard"])
def get_metric_history(key: str) -> List[Dict[str, Any]]:
    history = laniakea_metrics.get_metric_history(key)
    if not history:
        raise HTTPException(status_code=404, detail="Metric history not found.")
    return history


# --- Achievements endpoints -------------------------------------------------
@app.get("/achievements/all", tags=["Achievements"])
def get_all_achievements() -> List[Dict[str, Any]]:
    return [ach.to_dict() for ach in laniakea_achievements.achievements.values()]


@app.get("/achievements/user/{user_id}", tags=["Achievements"])
def get_user_achievements(user_id: str) -> Dict[str, Any]:
    progress = laniakea_achievements.user_progress.get(user_id, {})
    if not progress:
        raise HTTPException(status_code=404, detail="User not found or no progress recorded.")
    return progress


@app.get("/achievements/catalog", tags=["Achievements"])
def achievements_catalog() -> Dict[str, Any]:
    """Return all available achievements + total user-progress entries."""
    return {
        "total_achievements": len(laniakea_achievements.achievements),
        "users_tracked": len(laniakea_achievements.user_progress),
        "achievements": [a.to_dict() for a in laniakea_achievements.achievements.values()],
    }


# --- Core / status endpoints ------------------------------------------------
@app.get("/version", tags=["System"])
def version() -> Dict[str, Any]:
    """Return protocol & build metadata (also exposed at /)."""
    return {
        "protocol_version": settings.PROJECT_VERSION,
        "project_name": settings.PROJECT_NAME,
        "environment": settings.DEPLOYMENT_ENV,
    }


@app.get("/token/info", tags=["Token"])
def token_info() -> Dict[str, Any]:
    """Return LAN token economic parameters."""
    return {
        "symbol": getattr(settings, "TOKEN_SYMBOL", "LAN"),
        "name": getattr(settings, "TOKEN_NAME", "Laniakea"),
        "total_supply": getattr(settings, "TOTAL_TOKEN_SUPPLY", None),
        "inflation_rate": getattr(settings, "TOKEN_INFLATION_RATE", None),
        "burn_rate": getattr(settings, "TOKEN_BURN_RATE", None),
        "staking_apy": getattr(settings, "STAKING_APY", None),
        "decimals": getattr(settings, "TOKEN_DECIMALS", 18),
    }


@app.get("/core/status", tags=["Core"])
def core_status() -> Dict[str, Any]:
    return {
        "status": "Operational",
        "protocol_version": settings.PROJECT_VERSION,
        "chain_length": len(laniakea_chain.chain),
        "dao_proposals": len(laniakea_dao.proposals),
        "quantum_queue": len(laniakea_quantum.job_queue),
        "ai_model_version": laniakea_ai.version,
        "ai_performance": getattr(laniakea_ai, "performance_score", 0.0),
        "dex_pools": len(laniakea_dex.pools),
        "scda_identities": len(laniakea_scda_manager.list_identities()) if laniakea_scda_manager else 0,
        "knowledge_market_listed": (
            len(laniakea_knowledge_market.assets) if laniakea_knowledge_market else 0
        ),
        "diplomacy_alliances": (
            len(laniakea_diplomacy.alliances) if laniakea_diplomacy else 0
        ),
    }


# --- AI endpoints -----------------------------------------------------------
@app.post("/ai/query", tags=["AI"])
def query_ai_model(query: AIQuery) -> Dict[str, Any]:
    result = laniakea_ai.query(query.prompt)
    logger.info("AI Model queried. Confidence: %.2f", result["confidence"])
    return result


@app.post("/ai/train", tags=["AI"])
def train_ai_model(data_size: int) -> Dict[str, Any]:
    laniakea_ai.train(data_size)
    logger.info("AI Model trained with %s data units.", data_size)
    return {
        "message": "AI Model training simulated successfully",
        "new_score": laniakea_ai.performance_score,
    }


# --- Cosmic overview endpoint ----------------------------------------------
@app.get("/cosmic/overview", tags=["Cosmic"])
def cosmic_overview() -> Dict[str, Any]:
    """Aggregate, real-time snapshot of every live subsystem.

    Returns a single payload that the Cosmic UI dashboard consumes to render
    the unified hypercube state. Designed to be safe even when an optional
    subsystem (e.g. diplomacy, knowledge market) is unavailable.
    """
    identities = (
        laniakea_scda_manager.list_identities() if laniakea_scda_manager else []
    )

    # Total SCDA complexity / energy for the radar chart.
    # The SCDA manager does not expose ``get_state(identity)`` — the canonical
    # way to read a single SCDA is ``manager.get(identity).get_state()``.
    # We use the manager-level aggregators when available for efficiency.
    total_complexity = 0.0
    total_energy = 0.0
    if laniakea_scda_manager is not None:
        for ident in identities:
            scda_obj = laniakea_scda_manager.get(ident)
            if scda_obj is None:
                continue
            state = scda_obj.get_state()
            total_complexity += float(
                getattr(state, "complexity_index", 0.0) or 0.0
            )
            total_energy += float(getattr(state, "energy", 0.0) or 0.0)

    return {
        "protocol": {
            "name": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "environment": os.getenv("NODE_ENV", "development"),
            "status": "Operational",
        },
        "blockchain": {
            "chain_length": len(laniakea_chain.chain),
            "latest_hash": laniakea_chain.chain[-1].hash if laniakea_chain.chain else None,
            "difficulty": getattr(laniakea_chain, "difficulty", 4),
        },
        "consensus": {
            "authority": (
                laniakea_consensus.authority
                if hasattr(laniakea_consensus, "authority")
                else "laniakea-authority"
            ),
            "validators": len(getattr(laniakea_consensus, "validators", []) or []),
        },
        "defi": {
            "pools": len(laniakea_dex.pools),
            "pool_names": list(laniakea_dex.pools.keys()),
        },
        "governance": {
            "proposals": len(laniakea_dao.proposals),
        },
        "quantum": {
            "queue": len(laniakea_quantum.job_queue),
        },
        "ai": {
            "version": laniakea_ai.version,
            "performance": getattr(laniakea_ai, "performance_score", 0.0),
        },
        "scda": {
            "identities": len(identities),
            "total_complexity": total_complexity,
            "total_energy": total_energy,
        },
        "diplomacy": {
            "alliances": (
                len(laniakea_diplomacy.alliances) if laniakea_diplomacy else 0
            ),
            "available": laniakea_diplomacy is not None,
        },
        "knowledge_market": {
            "listed": (
                len(laniakea_knowledge_market.assets) if laniakea_knowledge_market else 0
            ),
            "available": laniakea_knowledge_market is not None,
        },
        "metaverse": {
            "entities": len(laniakea_simulator.entities),
        },
    }


# --- DeFi endpoints ---------------------------------------------------------
@app.get("/defi/pools", tags=["DeFi"])
def get_all_pools() -> Dict[str, Any]:
    return {
        name: {
            "reserve_x": pool.reserve_x,
            "reserve_y": pool.reserve_y,
            "token_x": pool.token_x,
            "token_y": pool.token_y,
        }
        for name, pool in laniakea_dex.pools.items()
    }


@app.post("/defi/swap", tags=["DeFi"])
def perform_swap(swap_request: SwapRequest) -> Dict[str, Any]:
    try:
        pool = laniakea_dex.get_pool(swap_request.token_in, swap_request.token_out)
        result = pool.swap(swap_request.token_in, swap_request.amount_in)
        logger.info(
            "Swap performed: %s %s -> %.4f %s",
            swap_request.amount_in,
            swap_request.token_in,
            result["amount_out"],
            swap_request.token_out,
        )
        return result
    except ValueError as exc:
        logger.error("Swap failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))


# --- Direct knowledge-market endpoints (in addition to the optional router) -
@app.post("/knowledge_market/tokenize", tags=["Knowledge Market"])
def knowledge_market_tokenize(req: KnowledgeTokenizeRequest) -> Dict[str, Any]:
    if laniakea_knowledge_market is None:
        raise HTTPException(status_code=503, detail="Knowledge market subsystem unavailable.")
    try:
        asset = laniakea_knowledge_market.tokenize_knowledge(
            req.owner_scda_id,
            req.scda_knowledge_vector,
            req.complexity_index,
            req.knowledge_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": "Knowledge tokenised", "asset": asset.to_dict()}


@app.get("/knowledge_market/listed", tags=["Knowledge Market"])
def knowledge_market_listed() -> List[Dict[str, Any]]:
    if laniakea_knowledge_market is None:
        return []
    return laniakea_knowledge_market.get_listed_assets()


@app.get("/knowledge_market/stats", tags=["Knowledge Market"])
def knowledge_market_stats() -> Dict[str, Any]:
    """Aggregate stats for the knowledge marketplace."""
    if laniakea_knowledge_market is None:
        raise HTTPException(status_code=503, detail="Knowledge market unavailable")
    assets = laniakea_knowledge_market.assets
    listed = [a for a in assets.values() if getattr(a, "is_listed", False)]
    return {
        "total_assets": len(assets),
        "listed_assets": len(listed),
        "total_volume": getattr(laniakea_knowledge_market, "total_volume", 0.0),
        "asset_types": list({
            getattr(a, "knowledge_type", "General") for a in assets.values()
        }),
    }


@app.post("/knowledge_market/list", tags=["Knowledge Market"])
def knowledge_market_list(req: KnowledgeListRequest) -> Dict[str, Any]:
    if laniakea_knowledge_market is None:
        raise HTTPException(status_code=503, detail="Knowledge market subsystem unavailable.")
    try:
        laniakea_knowledge_market.list_asset(req.asset_id, req.price)
        return {"message": f"Asset {req.asset_id} listed for {req.price}"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/knowledge_market/buy", tags=["Knowledge Market"])
def knowledge_market_buy(req: KnowledgeBuyRequest) -> Dict[str, Any]:
    if laniakea_knowledge_market is None:
        raise HTTPException(status_code=503, detail="Knowledge market subsystem unavailable.")
    try:
        tx = laniakea_knowledge_market.buy_asset(req.asset_id, req.buyer_scda_id)
        return {"message": "Asset purchased", "tx_id": tx.tx_id, "new_owner": req.buyer_scda_id}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/knowledge_market/asset/{asset_id}", tags=["Knowledge Market"])
def knowledge_market_asset(asset_id: str) -> Dict[str, Any]:
    if laniakea_knowledge_market is None:
        raise HTTPException(status_code=503, detail="Knowledge market subsystem unavailable.")
    try:
        return laniakea_knowledge_market.get_asset_details(asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/knowledge_market/types", tags=["Knowledge Market"])
def knowledge_market_types() -> Dict[str, Any]:
    """Return canonical knowledge types + supported scientific domains.

    Two catalogues are exposed:

    * ``types`` – the asset-type enum used by :func:`tokenize` to
      categorise a knowledge asset (e.g. ``Algorithm``, ``Discovery``).
    * ``domains`` – the 8 canonical scientific domains used by the
      8D knowledge vector (Physics, Biology, …) – matches the
      README / white-paper block-equation section.
    """
    try:
        from laniakea.marketplace.knowledge_market import (
            KnowledgeType,
            KNOWLEDGE_DOMAINS,
        )
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=503,
            detail=f"Knowledge type catalog unavailable: {exc}",
        )
    return {
        "types": [{"name": t.name, "value": t.value} for t in KnowledgeType],
        "domains": list(KNOWLEDGE_DOMAINS),
        "type_count": len(list(KnowledgeType)),
        "domain_count": len(KNOWLEDGE_DOMAINS),
    }


# --- Direct diplomacy endpoints --------------------------------------------
@app.post("/diplomacy/alliance", tags=["Diplomacy"])
def diplomacy_create_alliance(req: DiplomacyAllianceRequest) -> Dict[str, Any]:
    if laniakea_diplomacy is None:
        raise HTTPException(status_code=503, detail="Diplomacy subsystem unavailable.")
    # Build a default 8D knowledge vector per member if not provided so that
    # the signature of DiplomacySystem.create_alliance is always satisfied.
    member_ids = [req.founder_scda_id] + [m for m in req.members if m != req.founder_scda_id]
    vectors = req.initial_knowledge_vectors or {
        scda_id: [0.5] * 8 for scda_id in member_ids
    }
    # Ensure every member has a vector so the average is well-defined.
    for scda_id in member_ids:
        vectors.setdefault(scda_id, [0.5] * 8)
    alliance = laniakea_diplomacy.create_alliance(
        req.name,
        req.founder_scda_id,
        member_ids,
        vectors,
    )
    return {"message": "Alliance created", "alliance": alliance.to_dict()}


@app.get("/diplomacy/alliances", tags=["Diplomacy"])
def diplomacy_list_alliances() -> List[Dict[str, Any]]:
    if laniakea_diplomacy is None:
        return []
    return [a.to_dict() for a in laniakea_diplomacy.alliances.values()]


@app.get("/diplomacy/stats", tags=["Diplomacy"])
def diplomacy_stats() -> Dict[str, Any]:
    """Aggregate stats for the diplomacy subsystem."""
    if laniakea_diplomacy is None:
        raise HTTPException(status_code=503, detail="Diplomacy unavailable")
    alliances = laniakea_diplomacy.alliances
    return {
        "total_alliances": len(alliances),
        "total_members": sum(len(a.members) for a in alliances.values()),
        "alliance_names": [a.name for a in alliances.values()],
    }


# --- Direct LLM endpoints (used as a fallback when llm_api router is absent) -
@app.post("/llm/generate", tags=["LLM Integration"])
def llm_generate(req: LLMRequest) -> Dict[str, Any]:
    """Simulated LLM endpoint - returns a deterministic stub when no real
    model is wired in. Real implementations should override this router."""
    return {
        "model": req.model or "laniakea-stub-1.0",
        "prompt": req.prompt,
        "completion": (
            "[stub] No upstream LLM configured for this deployment. "
            "The LaniakeA protocol answer would normally be computed here."
        ),
    }


# --- Direct SCDA endpoints (fallback when scda_api router is unavailable) ----
class ScdaCreateBody(BaseModel):
    identity: str


class ScdaSolveBody(BaseModel):
    identity: str
    problem_difficulty: float
    solution_quality: float
    is_valid: bool = True


class ScdaPassiveBody(BaseModel):
    identity: str


@app.get("/scda/identities", tags=["SCDA"])
def scda_identities() -> List[str]:
    if laniakea_scda_manager is None:
        return []
    return laniakea_scda_manager.list_identities()


@app.get("/scda/states", tags=["SCDA"])
def scda_states() -> List[Dict[str, Any]]:
    if laniakea_scda_manager is None:
        return []
    return laniakea_scda_manager.all_states()


@app.get("/scda/leaderboard", tags=["SCDA"])
def scda_leaderboard(top_n: int = 10) -> List[Dict[str, Any]]:
    if laniakea_scda_manager is None:
        return []
    top_n = max(1, min(top_n, 100))
    return laniakea_scda_manager.leaderboard(top_n=top_n)


@app.post("/scda/create", tags=["SCDA"])
def scda_create(body: ScdaCreateBody) -> Dict[str, Any]:
    if laniakea_scda_manager is None:
        raise HTTPException(status_code=503, detail="SCDA subsystem unavailable.")
    laniakea_scda_manager.create(body.identity)
    return {"message": f"SCDA {body.identity!r} ready", "identity": body.identity}


@app.get("/scda/state/{identity}", tags=["SCDA"])
def scda_state(identity: str) -> Dict[str, Any]:
    if laniakea_scda_manager is None:
        raise HTTPException(status_code=503, detail="SCDA subsystem unavailable.")
    scda = laniakea_scda_manager.get(identity)
    if scda is None:
        raise HTTPException(status_code=404, detail=f"SCDA {identity!r} not found")
    return {
        "identity": scda.identity,
        "complexity_index": scda.complexity_index,
        "genetic_diversity": scda.dna.calculate_genetic_diversity(),
        "energy": scda.energy,
        "knowledge_count": len(scda.knowledge_vector),
        "problem_queue_size": len(scda.problem_queue),
        "knowledge_vector_8d": laniakea_scda_manager.compute_knowledge_vector(identity),
    }


@app.post("/scda/solve", tags=["SCDA"])
def scda_solve(body: ScdaSolveBody) -> Dict[str, Any]:
    if laniakea_scda_manager is None:
        raise HTTPException(status_code=503, detail="SCDA subsystem unavailable.")
    if not 0.0 <= body.problem_difficulty <= 1.0:
        raise HTTPException(status_code=400, detail="problem_difficulty must be in [0, 1]")
    if not 0.0 <= body.solution_quality <= 1.0:
        raise HTTPException(status_code=400, detail="solution_quality must be in [0, 1]")
    return laniakea_scda_manager.attempt_solve(
        body.identity, body.problem_difficulty, body.solution_quality, body.is_valid,
    )


@app.post("/scda/passive", tags=["SCDA"])
def scda_passive(body: ScdaPassiveBody) -> Dict[str, Any]:
    if laniakea_scda_manager is None:
        raise HTTPException(status_code=503, detail="SCDA subsystem unavailable.")
    return laniakea_scda_manager.passive_update(body.identity)


@app.get("/scda/leaderboard/{top_n}", tags=["SCDA"])
def scda_leaderboard_path(top_n: int) -> List[Dict[str, Any]]:
    """Path-based version of the leaderboard for systems that block query params."""
    if laniakea_scda_manager is None:
        return []
    top_n = max(1, min(top_n, 100))
    return laniakea_scda_manager.leaderboard(top_n=top_n)


@app.get("/scda/identities/{identity}/knowledge", tags=["SCDA"])
def scda_knowledge(identity: str) -> Dict[str, Any]:
    """Return the SCDA knowledge-vector + DNA gene snapshot."""
    if laniakea_scda_manager is None:
        raise HTTPException(status_code=503, detail="SCDA subsystem unavailable.")
    scda = laniakea_scda_manager.get(identity)
    if scda is None:
        raise HTTPException(status_code=404, detail=f"SCDA {identity!r} not found")
    return {
        "identity": identity,
        "knowledge_vector_8d": laniakea_scda_manager.compute_knowledge_vector(identity),
        "knowledge_count": len(scda.knowledge_vector),
        "genetic_diversity": scda.dna.calculate_genetic_diversity(),
        "genes": [g.to_dict() if hasattr(g, "to_dict") else {"name": g.name, "strength": g.strength, "domain": g.domain.value if hasattr(g.domain, "value") else str(g.domain)} for g in scda.dna.genes],
        "complexity_index": scda.complexity_index,
        "energy": scda.energy,
    }


@app.get("/scda/summary", tags=["SCDA"])
def scda_summary() -> Dict[str, Any]:
    """Aggregate metrics across all SCDAs (complexity, energy, count)."""
    if laniakea_scda_manager is None:
        return {"scda_available": False, "identities": [], "total": 0}
    states = laniakea_scda_manager.all_states()
    return {
        "scda_available": True,
        "total": len(states),
        "identities": [s["identity"] for s in states],
        "total_complexity": laniakea_scda_manager.total_complexity(),
        "total_energy": laniakea_scda_manager.total_energy(),
        "states": states,
    }


@app.delete("/scda/{identity}", tags=["SCDA"])
def scda_delete(identity: str) -> Dict[str, Any]:
    """Remove a SCDA from the in-memory registry (does not persist)."""
    if laniakea_scda_manager is None:
        raise HTTPException(status_code=503, detail="SCDA subsystem unavailable.")
    removed = laniakea_scda_manager.delete(identity)
    if not removed:
        raise HTTPException(status_code=404, detail=f"SCDA {identity!r} not found")
    return {"message": f"SCDA {identity!r} removed", "identity": identity}


# --- WebSocket endpoints -----------------------------------------------------
try:
    from fastapi import WebSocket, WebSocketDisconnect
    from laniakea.websocket.websocket_manager import ConnectionType

    @app.websocket("/ws/{connection_type}/{connection_id}")
    async def websocket_endpoint(websocket: WebSocket, connection_type: str, connection_id: str):
        """Laniakea WebSocket gateway.

        Supported connection types: blockchain, tasks, notifications,
        marketplace, dashboard, collaboration, chat, space_explorer,
        governance. The endpoint broadcasts chain/simulation/SCDA updates.
        """
        if _websocket_manager is None:
            await websocket.close(code=1011)
            return
        # Map string to enum, default to dashboard
        try:
            ctype = ConnectionType(connection_type)
        except ValueError:
            ctype = ConnectionType.DASHBOARD

        await _websocket_manager.connect(websocket, connection_id, ctype)
        try:
            while True:
                msg = await websocket.receive_text()
                # Echo back as acknowledgement + a periodic system update
                _websocket_manager.connection_stats["messages_received"] += 1
                await websocket.send_json({
                    "type": "ack",
                    "connection_id": connection_id,
                    "echo": msg,
                    "server_time": time.time(),
                })
        except WebSocketDisconnect:
            _websocket_manager.disconnect(connection_id)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("WebSocket %s closed: %s", connection_id, exc)
            _websocket_manager.disconnect(connection_id)


    @app.get("/ws/stats", tags=["WebSocket"])
    def websocket_stats() -> Dict[str, Any]:
        """Return live WebSocket connection statistics."""
        if _websocket_manager is None:
            return {"websocket_available": False}
        return {
            "websocket_available": True,
            "stats": _websocket_manager.connection_stats,
            "active_connections": len(_websocket_manager.active_connections),
        }
except Exception as exc:  # pragma: no cover - defensive
    logger.warning("WebSocket routes unavailable: %s", exc)
