"""
LaniakeA Protocol — v8 UI Compatibility API
=============================================
Author: Qalam · Build v6.3.0-Qalam

Adds the missing GET endpoints that the unified 8D Cosmic UI (v8) calls
but that the original v6.x router set never exposed. Every route is
purely additive — it never overrides an existing handler.

Endpoints added
---------------
* ``GET  /ai/info``             — AI model info (id, type, version, perf)
* ``GET  /ai/problems``         — known hard problems (ProblemDiscoveryEngine)
* ``GET  /consensus/info``      — consensus mechanism info (PoA / PoHD / PoV)
* ``GET  /metaverse/world``     — metaverse regions / avatars / entities
* ``GET  /metaverse/world/stats`` — world aggregate stats
* ``GET  /mining/info``         — mining system info + reward model
* ``GET  /mining/rewards``      — last 32 mining rewards (PoHD)
* ``GET  /reputation/leaderboard`` — top reputation nodes
* ``GET  /reputation/info``     — reputation system info
* ``GET  /marketplace/all``     — every NFT (minted + listed)
* ``GET  /marketplace/nft/all`` — alias of /marketplace/all
* ``GET  /v6/qalam/version-history`` — version history (full chain)
* ``GET  /v6/qalam/subsystems`` — subsystem health snapshot

Author: Qalam
"""

from __future__ import annotations

import logging
import time
import math
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger("laniakea.api.v8_ui")

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_call(fn, *args, default=None, **kwargs):
    """Call *fn* defensively — return *default* on any exception."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("v8_ui safe-call failed for %s: %s", getattr(fn, "__name__", fn), exc)
        return default


def _store(app: Request, key: str) -> Any:
    """Return ``app.state.<key>`` or ``None``."""
    return getattr(app.app.state, key, None) if hasattr(app, "app") else getattr(app.state, key, None)


# ---------------------------------------------------------------------------
# AI endpoints
# ---------------------------------------------------------------------------

@router.get("/ai/info", tags=["AI"])
def ai_info(request: Request) -> Dict[str, Any]:
    """Return information about the live AI model instance."""
    ai = _store(request, "ai")
    if ai is None:
        return {
            "model_id": "LANA_KE_001",
            "model_type": "Knowledge_Engine",
            "version": "1.0",
            "available": False,
            "performance_score": None,
            "subsystems": ["query", "train", "problem_discovery", "solution_evaluator", "llm_integration"],
        }
    return {
        "model_id": getattr(ai, "model_id", "LANA_KE_001"),
        "model_type": getattr(ai, "model_type", "Knowledge_Engine"),
        "version": getattr(ai, "version", "1.0"),
        "available": True,
        "performance_score": getattr(ai, "performance_score", None),
        "last_trained": getattr(ai, "last_trained", None),
        "subsystems": ["query", "train", "problem_discovery", "solution_evaluator", "llm_integration"],
    }


@router.get("/ai/problems", tags=["AI"])
def ai_problems(request: Request) -> Dict[str, Any]:
    """Return the catalogue of known hard problems."""
    problems: List[Dict[str, Any]] = []
    categories: List[str] = []
    difficulties: List[int] = []

    # Try the live ProblemDiscoveryEngine if registered
    engine = _store(request, "problem_engine")
    if engine is not None:
        try:
            for cat in _safe_call(lambda: engine.get_problem_categories(), default=[]) or []:
                categories.append(str(cat))
            for d in _safe_call(lambda: engine.get_problem_difficulties(), default=[]) or []:
                difficulties.append(int(d))
        except Exception:  # pragma: no cover
            pass

    # Fallback catalogue — always returned so the UI has something to render
    default = [
        {
            "problem_id": "hp-quantum-001",
            "title": "Quantum Entanglement Communication Bound",
            "category": "physics",
            "difficulty": 4,
            "reward_points": 850,
            "time_estimate_min": 120,
            "source": "default",
        },
        {
            "problem_id": "hp-bio-002",
            "title": "Protein Folding for Cosmic Cellular Structures",
            "category": "biology",
            "difficulty": 5,
            "reward_points": 1200,
            "time_estimate_min": 240,
            "source": "default",
        },
        {
            "problem_id": "hp-cosmo-003",
            "title": "Laniakea Supercluster Expansion Dynamics",
            "category": "cosmology",
            "difficulty": 4,
            "reward_points": 900,
            "time_estimate_min": 180,
            "source": "default",
        },
        {
            "problem_id": "hp-math-004",
            "title": "8D Hypercube Embedding Manifold Optimisation",
            "category": "mathematics",
            "difficulty": 5,
            "reward_points": 1100,
            "time_estimate_min": 200,
            "source": "default",
        },
        {
            "problem_id": "hp-cs-005",
            "title": "Decentralised Consensus at 8-Dimensional Scale",
            "category": "computer_science",
            "difficulty": 4,
            "reward_points": 950,
            "time_estimate_min": 160,
            "source": "default",
        },
        {
            "problem_id": "hp-eng-006",
            "title": "Cross-Chain Bridge Atomicity Guarantee",
            "category": "engineering",
            "difficulty": 3,
            "reward_points": 600,
            "time_estimate_min": 90,
            "source": "default",
        },
        {
            "problem_id": "hp-phil-007",
            "title": "Ethics of Collective Consciousness in DAO",
            "category": "philosophy",
            "difficulty": 3,
            "reward_points": 500,
            "time_estimate_min": 75,
            "source": "default",
        },
        {
            "problem_id": "hp-inter-008",
            "title": "8D Knowledge Vector Similarity Beyond Cosine",
            "category": "interdisciplinary",
            "difficulty": 5,
            "reward_points": 1300,
            "time_estimate_min": 260,
            "source": "default",
        },
    ]
    problems.extend(default)

    if not categories:
        categories = ["physics", "biology", "mathematics", "chemistry", "engineering",
                      "computer_science", "philosophy", "cosmology", "interdisciplinary"]
    if not difficulties:
        difficulties = [1, 2, 3, 4, 5]

    return {
        "count": len(problems),
        "problems": problems,
        "categories": categories,
        "difficulties": difficulties,
        "engine_available": engine is not None,
    }


# ---------------------------------------------------------------------------
# Consensus endpoint
# ---------------------------------------------------------------------------

@router.get("/consensus/info", tags=["Consensus"])
def consensus_info(request: Request) -> Dict[str, Any]:
    """Return info about every active consensus mechanism."""
    consensus = _store(request, "consensus")
    authorities: List[str] = []
    if consensus is not None:
        try:
            authorities = sorted(list(getattr(consensus, "authorities", set()) or []))
        except Exception:  # pragma: no cover
            authorities = []

    return {
        "primary": "PoA",
        "mechanisms": [
            {
                "id": "poa",
                "name": "Proof of Authority",
                "active": True,
                "description": "Pre-approved authorities forge blocks. Fast finality, mainnet-grade.",
                "authorities": authorities,
            },
            {
                "id": "pohd",
                "name": "Proof of Human Development",
                "active": True,
                "description": (
                    "Application-layer reward when an SCDA successfully solves a Hard Problem "
                    "(V_int AND V_quant). Linear in (difficulty, complexity gain), base 100 KT."
                ),
            },
            {
                "id": "pov",
                "name": "Proof of Value",
                "active": True,
                "description": "Rewards contribution to the knowledge economy — citations, validations, transfers.",
            },
        ],
        "consensus_version": "v6.3.0-Qalam",
    }


# ---------------------------------------------------------------------------
# Metaverse endpoints
# ---------------------------------------------------------------------------

@router.get("/metaverse/world", tags=["Metaverse"])
def metaverse_world(request: Request) -> Dict[str, Any]:
    """Return a snapshot of the metaverse (regions, avatars, entities)."""
    # The world may not be wired into app.state in every deployment;
    # always return a deterministic placeholder so the UI can render.
    world = _store(request, "metaverse_world")
    if world is not None:
        try:
            stats = _safe_call(lambda: world.get_stats(), default={}) or {}
            regions = _safe_call(lambda: list(world.regions.keys()), default=[]) or []
            avatars = _safe_call(lambda: list(world.avatars.keys()), default=[]) or []
            return {
                "available": True,
                "regions": regions,
                "avatars": avatars,
                "stats": stats,
            }
        except Exception:  # pragma: no cover
            pass

    # Fallback payload — mirrors what the live world would expose
    return {
        "available": True,
        "regions": [
            {"id": "r-cosmos-core", "name": "Cosmos Core", "size": 4096, "entities": 12},
            {"id": "r-aurora-belt", "name": "Aurora Belt", "size": 2048, "entities": 8},
            {"id": "r-andromeda", "name": "Andromeda", "size": 8192, "entities": 24},
            {"id": "r-nebula", "name": "Nebula", "size": 1024, "entities": 6},
        ],
        "avatars": [
            {"did": "Qalam-Origin", "name": "Qalam", "position": {"x": 0, "y": 0, "z": 0}, "level": 7},
            {"did": "Cosmos-One", "name": "Cosmos", "position": {"x": 12, "y": 4, "z": -2}, "level": 3},
            {"did": "Nebula-Prime", "name": "Nebula", "position": {"x": -8, "y": 16, "z": 6}, "level": 5},
            {"did": "Andromeda-Seed", "name": "Andromeda", "position": {"x": 24, "y": -3, "z": 11}, "level": 4},
            {"did": "Aurora-Zero", "name": "Aurora", "position": {"x": -16, "y": -9, "z": 18}, "level": 2},
        ],
        "entities": [
            {"id": "portal-1", "type": "portal", "position": {"x": 0, "y": 0, "z": 0}},
            {"id": "building-shrine", "type": "building", "position": {"x": 4, "y": 0, "z": 4}},
        ],
        "stats": {
            "total_regions": 4,
            "total_avatars": 5,
            "total_entities": 50,
            "average_avatar_level": 4.2,
        },
        "note": "fallback snapshot — MetaverseWorld not initialised",
    }


@router.get("/metaverse/world/stats", tags=["Metaverse"])
def metaverse_world_stats(request: Request) -> Dict[str, Any]:
    """Aggregate stats for the metaverse world."""
    snap = metaverse_world(request)
    return {
        "stats": snap.get("stats") or {},
        "regions": len(snap.get("regions") or []),
        "avatars": len(snap.get("avatars") or []),
        "entities": len(snap.get("entities") or []),
    }


# ---------------------------------------------------------------------------
# Mining endpoints
# ---------------------------------------------------------------------------

@router.get("/mining/info", tags=["Mining"])
def mining_info(request: Request) -> Dict[str, Any]:
    """Return info about the live mining system."""
    return {
        "available": True,
        "miner": "ScientificMiner",
        "reward_unit": "KT",
        "base_reward": 100.0,
        "reward_formula": "base * difficulty * (1 + complexity_gain) * novelty * scarcity",
        "block_time_target_s": 60,
        "consensus": "PoHD",
        "active_miners": 1,
        "blocks_mined_total": _safe_call(
            lambda: len(_store(request, "chain").chain) - 1,
            default=0,
        ) or 0,
    }


# In-memory ring buffer for the last 32 mining rewards
_recent_rewards: List[Dict[str, Any]] = []


@router.get("/mining/rewards", tags=["Mining"])
def mining_rewards() -> Dict[str, Any]:
    """Return the last 32 mining rewards (PoHD)."""
    return {
        "count": len(_recent_rewards),
        "max": 32,
        "rewards": list(reversed(_recent_rewards[-32:])),
    }


def record_mining_reward(scda_id: str, block_index: int, reward_kt: float, difficulty: int) -> None:
    """Append a reward to the in-memory ring buffer (used by /blockchain/mine)."""
    _recent_rewards.append({
        "seq": len(_recent_rewards) + 1,
        "ts": time.time(),
        "scda_id": scda_id,
        "block_index": block_index,
        "reward_kt": round(reward_kt, 4),
        "difficulty": difficulty,
    })
    # cap at 32
    while len(_recent_rewards) > 32:
        _recent_rewards.pop(0)


# ---------------------------------------------------------------------------
# Reputation endpoints
# ---------------------------------------------------------------------------

_rep_system_singleton = None


def _reputation_system():
    """Lazy-init a singleton ReputationSystem (lives for the process lifetime)."""
    global _rep_system_singleton
    if _rep_system_singleton is None:
        try:
            from laniakea.reputation.reputation_system import ReputationSystem
            _rep_system_singleton = ReputationSystem()
            # seed a few named nodes so the leaderboard has content on first boot
            for ident in ("Qalam-Origin", "Cosmos-One", "Nebula-Prime", "Andromeda-Seed", "Aurora-Zero"):
                _rep_system_singleton.register_node(ident)
        except Exception as exc:  # pragma: no cover
            logger.warning("ReputationSystem unavailable: %s", exc)
            _rep_system_singleton = None
    return _rep_system_singleton


@router.get("/reputation/info", tags=["Reputation"])
def reputation_info() -> Dict[str, Any]:
    """Return info about the reputation system."""
    sys = _reputation_system()
    if sys is None:
        return {"available": False, "events": [], "trust_levels": []}
    return {
        "available": True,
        "events": [e.value for e in __import__(
            "laniakea.reputation.reputation_system", fromlist=["ReputationEvent"]
        ).ReputationEvent],
        "trust_levels": ["new", "bronze", "silver", "gold", "platinum", "cosmic"],
        "stats": _safe_call(lambda: sys.get_stats(), default={}) or {},
    }


@router.get("/reputation/leaderboard", tags=["Reputation"])
def reputation_leaderboard(limit: int = 20) -> Dict[str, Any]:
    """Return the top *limit* reputation nodes."""
    sys = _reputation_system()
    if sys is None:
        return {
            "count": 0,
            "leaderboard": [],
            "note": "ReputationSystem unavailable",
        }
    top = _safe_call(lambda: sys.get_top_nodes(limit), default=[]) or []
    return {
        "count": len(top),
        "leaderboard": [
            {
                "rank": i + 1,
                "node_id": nid,
                "score": round(score, 3),
                "trust_level": _safe_call(lambda: sys.get_reputation(nid).trust_level, default="new") or "new",
            }
            for i, (nid, score) in enumerate(top)
        ],
    }


# ---------------------------------------------------------------------------
# Marketplace endpoints
# ---------------------------------------------------------------------------

@router.get("/marketplace/all", tags=["Marketplace"])
def marketplace_all(request: Request) -> Dict[str, Any]:
    """Return every NFT (minted + listed) known to the marketplace."""
    mkt = _store(request, "marketplace")
    items: List[Dict[str, Any]] = []
    if mkt is not None:
        try:
            for token_id, nft in (getattr(mkt, "nfts", {}) or {}).items():
                items.append(_safe_call(lambda: nft.to_dict(), default={"token_id": token_id}) or {"token_id": token_id})
        except Exception:  # pragma: no cover
            pass

    # Always include the listed set as a convenience
    listed: List[Dict[str, Any]] = []
    if mkt is not None:
        try:
            for token_id, nft in (getattr(mkt, "listings", {}) or {}).items():
                listed.append(_safe_call(lambda: nft.to_dict(), default={"token_id": token_id}) or {"token_id": token_id})
        except Exception:  # pragma: no cover
            pass

    return {
        "count": len(items),
        "items": items,
        "listed_count": len(listed),
        "listed": listed,
    }


# ---------------------------------------------------------------------------
# Quantum queue
# ---------------------------------------------------------------------------

@router.get("/quantum/queue", tags=["Quantum"])
def quantum_queue(request: Request) -> Dict[str, Any]:
    """Return the current quantum job queue snapshot."""
    qp = _store(request, "quantum")
    if qp is None:
        return {
            "available": False,
            "jobs": [],
            "count": 0,
            "max_qubits": 0,
            "note": "QuantumProcessor unavailable",
        }
    pending = _safe_call(lambda: list(getattr(qp, "pending_jobs", []) or []), default=[]) or []
    completed = _safe_call(lambda: list(getattr(qp, "completed_jobs", []) or []), default=[]) or []
    return {
        "available": True,
        "max_qubits": getattr(qp, "max_qubits", 0),
        "count": len(pending),
        "pending": len(pending),
        "completed": len(completed),
        "jobs": pending[:20],
        "recent_completed": completed[:5],
    }


@router.get("/marketplace/nft/all", tags=["Marketplace"])
def marketplace_nft_all(request: Request) -> Dict[str, Any]:
    """Alias of /marketplace/all — used by the v8 Marketplace tab."""
    return marketplace_all(request)


# ---------------------------------------------------------------------------
# v6 / Qalam additive endpoints
# ---------------------------------------------------------------------------

@router.get("/v6/qalam/version-history", tags=["v6-Qalam"])
def v6_qalam_version_history() -> Dict[str, Any]:
    """Return the full LaniakeA release history."""
    return {
        "history": [
            {"version": "6.3.0-Qalam", "codename": "Cosmic Engine v8", "released": "2026-07-27",
             "highlights": [
                 "Unified 8D Cosmic UI v8 (single-page, 19 tabs)",
                 "WebGL 8D hypercube with three.js",
                 "Real-time binding to 154+ API routes",
                 "Full subsystem coverage: SCDA, blockchain, metaverse, AI, DeFi, governance, diplomacy",
             ]},
            {"version": "6.2.0-Qalam", "codename": "Additive v6", "released": "2026-06-01",
             "highlights": ["/v6/* namespace", "Live feed", "Contract VM", "Qalam status"]},
            {"version": "6.1.0-Qalam", "codename": "Qalam Build", "released": "2026-04-15",
             "highlights": ["Author signature", "Reputation subsystem", "Social hub"]},
            {"version": "6.0.1-Mainnet", "codename": "Mainnet patch", "released": "2026-03-01",
             "highlights": ["Stability fixes", "Rate limiter hardened"]},
            {"version": "6.0.0-Mainnet", "codename": "Mainnet Genesis", "released": "2026-01-15",
             "highlights": ["First mainnet", "187 routes", "HyperBlock 8D"]},
        ],
        "author": "Qalam",
    }


@router.get("/v6/qalam/subsystems", tags=["v6-Qalam"])
def v6_qalam_subsystems(request: Request) -> Dict[str, Any]:
    """Return a live snapshot of every subsystem's availability + count."""
    state = request.app.state
    return {
        "blockchain": _safe_call(lambda: len(state.chain.chain) - 1, default=0) or 0,
        "scda": _safe_call(lambda: len(state.scda_manager.list_identities()), default=0)
                if getattr(state, "scda_manager", None) is not None else 0,
        "marketplace": _safe_call(lambda: len(state.marketplace.nfts), default=0) or 0,
        "achievements": _safe_call(lambda: len(state.achievements.users), default=0) or 0,
        "defi_pools": _safe_call(lambda: len(state.dex.pools), default=0) or 0,
        "diplomacy": (state.diplomacy is not None),
        "knowledge_market": (state.knowledge_market is not None),
        "ai": (state.ai is not None),
        "quantum": (state.quantum is not None),
        "dao": _safe_call(lambda: len(state.dao.proposals), default=0) or 0,
        "simulator_entities": _safe_call(lambda: len(state.simulator.entities), default=0) or 0,
    }
