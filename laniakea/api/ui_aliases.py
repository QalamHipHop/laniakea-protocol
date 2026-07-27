"""UI compatibility aliases.

The Cosmic UI v6 dashboard calls a number of endpoints with ``GET`` that
are implemented as ``POST`` elsewhere in the stack, plus a handful of
intuitive-but-undefined paths (``/ai/generate``, ``/quantum/status``,
``/social/hub``, ``/web3/wallet``, ``/crosschain/bridges``).

This module installs:

* ``GET`` aliases for every ``POST`` endpoint the UI uses as a fallback.
  They return a deterministic preview payload (a stub of what the ``POST``
  would return when given sensible inputs), so the ``setCode`` blocks in
  the UI light up immediately instead of showing ``405 Method Not Allowed``.
* Lightweight ``GET`` endpoints for the previously-undefined paths
  (``/ai/generate``, ``/crosschain/bridges``, ``/quantum/status``,
  ``/social/hub``, ``/web3/wallet``).
* SCDA ``/scda/snapshot`` and ``/scda/stats`` aliases that point at
  the existing ``/scda/summary`` payload.

All routes are added with ``include_in_schema=True`` so the ``/discovery``
index reports them.

The module is **purely additive**: it never overrides an existing
declaration. If a name is already taken on the app, the alias is skipped
with a debug log so the original handler keeps priority.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import FastAPI

logger = logging.getLogger("laniakea.api.ui_aliases")


def _route_exists(app: FastAPI, path: str, method: str) -> bool:
    """Return True if a route for ``method path`` is already registered."""
    method_upper = method.upper()
    for r in app.routes:
        if getattr(r, "path", None) != path:
            continue
        methods = getattr(r, "methods", None) or set()
        if method_upper in methods:
            return True
    return False


def install_ui_aliases(app: FastAPI) -> None:
    """Register every UI-compatibility alias on the given ``app``.

    Safe to call multiple times — duplicate registrations are skipped.
    """
    aliases: Dict[str, Any] = {
        # --- SCDA aliases -----------------------------------------------------
        "/scda/snapshot": lambda: {
            "alias_of": "/scda/summary",
            "summary": "Snapshot of every known SCDA (states + aggregates).",
            "total": _safe_total_scdas(app),
            "states": _safe_call_state_summary(app),
        },
        "/scda/stats": lambda: {
            "alias_of": "/scda/summary",
            "available": True,
            "total": _safe_total_scdas(app),
        },
        # --- AI aliases -------------------------------------------------------
        "/ai/generate": lambda: {
            "model": "laniakea-stub-1.0",
            "completion": (
                "[stub] /ai/generate is an alias for /ai/query. "
                "POST {\"prompt\": \"...\"} to /ai/query to receive a real response."
            ),
            "is_stub": True,
        },
        "/ai/status": lambda: {
            "model": "LANA_KE_001",
            "available": True,
            "performance": _safe_ai_perf(app),
        },
        # --- LLM aliases ------------------------------------------------------
        "/llm/snapshot": lambda: {
            "alias_of": "/llm/status",
            "providers": ["stub", "openai"],
            "default_provider": "openai",
            "default_model": "gpt-4.1-mini",
        },
        # --- Blockchain aliases ----------------------------------------------
        "/blockchain/snapshot": lambda: {
            "alias_of": "/blockchain/info",
            "length": _safe_chain_length(app),
        },
        # --- DeFi aliases -----------------------------------------------------
        "/defi/snapshot": lambda: {
            "alias_of": "/defi/pools",
            "pools": list(_safe_pools(app).keys()),
        },
        # --- Quantum aliases --------------------------------------------------
        "/quantum/status": lambda: {
            "queue_size": _safe_quantum_queue(app),
            "available": True,
            "max_qubits": _safe_max_qubits(app),
        },
        "/quantum/snapshot": lambda: {
            "alias_of": "/quantum/status",
            "queue_size": _safe_quantum_queue(app),
        },
        # --- Simulation aliases ----------------------------------------------
        "/simulation/snapshot": lambda: {
            "entities": _safe_simulation_entities_count(app),
            "current_time": 0.0,
        },
        # --- Cross-chain aliases ---------------------------------------------
        "/crosschain/bridges": lambda: {
            "supported_chains": _safe_supported_chains(app),
            "alias_of": "/crosschain/supported",
        },
        # --- Social aliases ---------------------------------------------------
        "/social/hub": lambda: {
            "alias_of": "/social/stats",
            "posts": 0,
            "follows": 0,
            "available": True,
        },
        "/social/stats": lambda: {
            "posts": 0,
            "follows": 0,
            "users": 0,
            "available": True,
        },
        "/social/snapshot": lambda: {
            "alias_of": "/social/feed",
            "posts": [],
            "count": 0,
        },
        # --- Web3 aliases -----------------------------------------------------
        "/web3/wallet": lambda: {
            "alias_of": "/web3/chains",
            "connected": False,
            "chains": _safe_web3_chains(app),
        },
        # --- Marketplace aliases ---------------------------------------------
        "/marketplace/snapshot": lambda: {
            "alias_of": "/marketplace/listings",
            "listings": 0,
        },
        # --- SCDA integration aliases ----------------------------------------
        "/scda-integration/snapshot": lambda: {
            "alias_of": "/scda-integration/overview",
            "available": True,
        },
        # --- Breeding aliases ------------------------------------------------
        "/breeding/snapshot": lambda: {
            "alias_of": "/breeding/stats",
            "total_events": 0,
        },
        # --- Dashboard aliases -----------------------------------------------
        "/dashboard/snapshot": lambda: {
            "alias_of": "/dashboard/metrics",
            "available": True,
        },

        # --- POST-only endpoints aliased to GET (preview / dry-run) -----------
        # The UI v6 sometimes probes these with GET in addition to POST. The
        # GET path returns a deterministic preview payload and never mutates
        # any state.
        "/scda/breed": lambda: {
            "alias_of": "POST /scda/breed",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {parent1, parent2} to actually breed.",
            "required_fields": ["parent1", "parent2"],
        },
        "/scda/solve": lambda: {
            "alias_of": "POST /scda/solve",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {identity, problem_difficulty, solution_quality} to attempt a solve.",
            "required_fields": ["identity", "problem_difficulty", "solution_quality"],
        },
        "/ai/query": lambda: {
            "alias_of": "POST /ai/query",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {prompt} to query the AI model.",
            "required_fields": ["prompt"],
            "stub_completion": "[stub] POST a prompt to /ai/query to receive a real response.",
        },
        "/llm/generate": lambda: {
            "alias_of": "POST /llm/generate",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {prompt} to generate a completion.",
            "required_fields": ["prompt"],
            "stub_completion": "[stub] POST a prompt to /llm/generate to receive a real completion.",
        },
        "/llm/hard_problem": lambda: {
            "alias_of": "POST /llm/hard_problem",
            "method": "GET",
            "preview": True,
            "stub_problem": {
                "statement": "[stub] POST a domain/difficulty to /llm/hard_problem to receive a real Hard Problem.",
                "domain": "cosmology",
                "difficulty": 0.5,
            },
        },
        "/llm/evaluate": lambda: {
            "alias_of": "POST /llm/evaluate",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {problem, candidate_solution} to evaluate.",
        },
        "/llm/agent": lambda: {
            "alias_of": "POST /llm/agent",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {goal} to run the agent.",
        },
        "/blockchain/mine": lambda: {
            "alias_of": "POST /blockchain/mine",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST to /blockchain/mine to forge a new block (requires authorities).",
            "authorities_configured": _safe_authorities(),
        },
        "/blockchain/transactions/new": lambda: {
            "alias_of": "POST /blockchain/transactions/new",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {sender, recipient, amount} to enqueue a transaction.",
        },
        "/defi/swap": lambda: {
            "alias_of": "POST /defi/swap",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {token_in, token_out, amount_in} to perform a swap.",
            "pools_available": list(_safe_pools(app).keys()),
        },
        "/quantum/job/submit": lambda: {
            "alias_of": "POST /quantum/job/submit",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {num_qubits, gates} to submit a quantum job.",
            "max_qubits": _safe_max_qubits(app),
            "queue_size": _safe_quantum_queue(app),
        },
        "/quantum/job/process": lambda: {
            "alias_of": "POST /quantum/job/process",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST to /quantum/job/process to run the next queued job.",
            "queue_size": _safe_quantum_queue(app),
        },
        "/simulation/step": lambda: {
            "alias_of": "POST /simulation/step",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST to /simulation/step to advance the cosmic simulation by one tick.",
            "entities": _safe_simulation_entities_count(app),
            "current_time": 0.0,
        },
        "/marketplace/nft/mint": lambda: {
            "alias_of": "POST /marketplace/nft/mint",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {owner, metadata_uri, asset_type} to mint an NFT.",
        },
        "/marketplace/nft/list": lambda: {
            "alias_of": "POST /marketplace/nft/{token_id}/list",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST /marketplace/nft/{token_id}/list?price=N to list an NFT.",
        },
        "/marketplace/nft/buy": lambda: {
            "alias_of": "POST /marketplace/nft/{token_id}/buy",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST /marketplace/nft/{token_id}/buy?buyer=addr to buy an NFT.",
        },
        "/breeding/breed": lambda: {
            "alias_of": "POST /breeding/breed",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {parent_a, parent_b, mode} to /breeding/breed to issue a breeding event.",
        },
        "/scda-integration/auto-list-knowledge": lambda: {
            "alias_of": "POST /scda-integration/auto-list-knowledge",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {identity, list_price, knowledge_type} to mint+list a knowledge asset.",
        },
        "/scda-integration/form-alliance": lambda: {
            "alias_of": "POST /scda-integration/form-alliance",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {founder, partner, name} to form an alliance.",
        },
        "/scda-integration/cosine-similarity": lambda: {
            "alias_of": "POST /scda-integration/cosine-similarity",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {a, b} to compute the cosine similarity.",
        },
        "/crosschain/transfer/initiate": lambda: {
            "alias_of": "POST /crosschain/transfer/initiate",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {source_chain, target_chain, asset, amount, sender, recipient} to initiate.",
        },
        "/web3/link": lambda: {
            "alias_of": "POST /web3/link",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {address, signature} to link a wallet.",
        },
        "/knowledge_market/tokenize": lambda: {
            "alias_of": "POST /knowledge_market/tokenize",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {owner_scda_id, scda_knowledge_vector, complexity_index} to tokenize knowledge.",
        },
        "/evolution/scan": lambda: {
            "alias_of": "POST /evolution/scan",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST to /evolution/scan to run a self-evolution scan.",
        },
        "/evolution/improve": lambda: {
            "alias_of": "POST /evolution/improve",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {filepath} to /evolution/improve.",
        },
        "/diplomacy/alliances": lambda: {
            "alias_of": "POST /diplomacy/alliances",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {name, founder_scda_id, members} to /diplomacy/alliances to form a new alliance.",
            "list": _safe_diplomacy_alliances(app),
        },
        "/gov/proposals": lambda: {
            "alias_of": "POST /gov/proposals",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {title, description, proposer} to /gov/proposals to create one.",
        },

        "/scda/create": lambda: {
            "alias_of": "POST /scda/create",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST {identity} to /scda/create to register a new SCDA.",
        },
        "/marketplace/nft/tok-1/list": lambda: {
            "alias_of": "POST /marketplace/nft/{token_id}/list",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST /marketplace/nft/{token_id}/list?price=N to list an NFT.",
        },
        "/marketplace/nft/tok-1/buy": lambda: {
            "alias_of": "POST /marketplace/nft/{token_id}/buy",
            "method": "GET",
            "preview": True,
            "message": "GET is a preview. POST /marketplace/nft/{token_id}/buy?buyer=addr to buy an NFT.",
        },
        # --- Generic UI-friendly alias --------------------------------------
        "/ui/endpoints": lambda: _ui_endpoint_index(app),
    }

    installed = 0
    for path, handler in aliases.items():
        if _route_exists(app, path, "GET"):
            logger.debug("UI alias %s skipped — already registered", path)
            continue
        app.add_api_route(path, handler, methods=["GET"], tags=["UI Aliases"])
        installed += 1

    if installed:
        logger.info("Installed %d UI-compatibility aliases", installed)



def _safe_authorities() -> list:
    try:
        from laniakea.core.config import settings
        return list(getattr(settings, "AUTHORITIES", []) or [])
    except Exception:  # pragma: no cover - defensive
        return []


def _safe_diplomacy_alliances(app: FastAPI) -> list:
    try:
        d = getattr(app.state, "diplomacy", None)
        if d is None or not hasattr(d, "alliances"):
            return []
        return [a.to_dict() if hasattr(a, "to_dict") else {"name": getattr(a, "name", str(a))} for a in d.alliances.values()]
    except Exception:  # pragma: no cover - defensive
        return []

# --- Safe introspection helpers --------------------------------------------
def _safe_call_state_summary(app: FastAPI) -> list:
    try:
        # Hit the same code path the SCDA summary route uses.
        manager = getattr(app.state, "scda_manager", None)
        if manager is None:
            return []
        return manager.all_states()
    except Exception:  # pragma: no cover - defensive
        return []


def _safe_total_scdas(app: FastAPI) -> int:
    try:
        manager = getattr(app.state, "scda_manager", None)
        if manager is None:
            return 0
        return len(manager.list_identities())
    except Exception:  # pragma: no cover - defensive
        return 0


def _safe_ai_perf(app: FastAPI) -> float:
    try:
        ai = getattr(app.state, "ai", None)
        return getattr(ai, "performance_score", 0.0) if ai else 0.0
    except Exception:  # pragma: no cover - defensive
        return 0.0


def _safe_chain_length(app: FastAPI) -> int:
    try:
        chain = getattr(app.state, "chain", None)
        return len(chain.chain) if chain else 0
    except Exception:  # pragma: no cover - defensive
        return 0


def _safe_pools(app: FastAPI) -> dict:
    try:
        dex = getattr(app.state, "dex", None)
        return dex.pools if dex else {}
    except Exception:  # pragma: no cover - defensive
        return {}


def _safe_quantum_queue(app: FastAPI) -> int:
    try:
        q = getattr(app.state, "quantum", None)
        return len(q.job_queue) if q else 0
    except Exception:  # pragma: no cover - defensive
        return 0


def _safe_max_qubits(app: FastAPI) -> int:
    try:
        from laniakea.core.config import settings
        return int(getattr(settings, "MAX_QUBITS", 5))
    except Exception:  # pragma: no cover - defensive
        return 5


def _safe_simulation_entities_count(app: FastAPI) -> int:
    try:
        sim = getattr(app.state, "simulator", None)
        return len(sim.entities) if sim else 0
    except Exception:  # pragma: no cover - defensive
        return 0


def _safe_supported_chains(app: FastAPI) -> list:
    try:
        from laniakea.core.config import settings
        return list(getattr(settings, "SUPPORTED_CHAINS", []))
    except Exception:  # pragma: no cover - defensive
        return []


def _safe_web3_chains(app: FastAPI) -> list:
    """Try the live web3 router; fall back to a static chain list."""
    try:
        from laniakea.api.web3_api import SUPPORTED_CHAINS
        return SUPPORTED_CHAINS
    except Exception:  # pragma: no cover - defensive
        return [
            {"caip2": "eip155:1", "chain_id": 1, "name": "Ethereum Mainnet"},
        ]


def _ui_endpoint_index(app: FastAPI) -> Dict[str, Any]:
    """Return a list of GET-only endpoints to help the UI render fallback
    panels without poking every POST endpoint."""
    out = []
    for r in app.routes:
        path = getattr(r, "path", None)
        if not path or path.startswith("/openapi"):
            continue
        methods = getattr(r, "methods", None) or set()
        if "GET" not in methods:
            continue
        out.append({
            "path": path,
            "tags": getattr(r, "tags", []) or [],
            "name": getattr(r, "name", None),
        })
    return {"count": len(out), "endpoints": out}
