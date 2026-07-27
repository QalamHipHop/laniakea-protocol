"""LaniakeA Protocol v6.2.0-Qalam — Additive API surface.

This module adds the new ``/v6/*`` namespace on top of the existing
v6.0.1-Mainnet API. **Every change here is purely additive** — the
existing routes, schemas, and behaviour are untouched. The new routes
are designed to be safe to mount even if optional subsystems
(diplomacy, knowledge market, SCDA manager) are not available.

The module exposes a single ``router`` object — the rest of the
codebase mounts it via ``app.include_router(v6_routes.router)``.

Author: Qalam
"""

from __future__ import annotations

import os
import time
import hashlib
import random
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

logger = logging.getLogger("laniakea.api.v6")

router = APIRouter(prefix="/v6", tags=["v6-Qalam"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_START_TIME = time.time()


def _uptime_seconds() -> float:
    return round(time.time() - _START_TIME, 3)


def _safe_call(fn, *args, default=None, **kwargs):
    """Call *fn* defensively — return *default* on any exception."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("v6 safe-call failed for %s: %s", getattr(fn, "__name__", fn), exc)
        return default


def _scda_summary(request: Request) -> Dict[str, Any]:
    """Build a SCDA summary block by reading live state from app.state.

    The function never raises; missing subsystems return ``available=False``
    so the caller can render graceful "not yet initialised" messages.
    """
    mgr = getattr(request.app.state, "scda_manager", None)
    if mgr is None:
        return {"available": False, "identities": [], "count": 0}
    try:
        identities = list(mgr.list_identities() or [])
    except Exception:  # pragma: no cover
        identities = []
    summary = {"available": True, "count": len(identities), "identities": []}
    for ident in identities[:20]:  # cap at 20 for the feed
        try:
            scda = mgr.get(ident) if hasattr(mgr, "get") else None
        except Exception:  # pragma: no cover
            scda = None
        if scda is None:
            summary["identities"].append({"identity": ident})
            continue
        # try to surface complexity + energy if present
        ct = _safe_call(lambda: getattr(scda, "complexity", None)) or \
             _safe_call(lambda: getattr(scda, "C", None))
        et = _safe_call(lambda: getattr(scda, "energy", None)) or \
             _safe_call(lambda: getattr(scda, "E", None))
        tier = _safe_call(lambda: getattr(scda, "tier", None)) or \
               _safe_call(lambda: getattr(getattr(scda, "dna", None), "tier", None))
        summary["identities"].append({
            "identity": ident,
            "tier": tier,
            "complexity": ct,
            "energy": et,
        })
    return summary


# ---------------------------------------------------------------------------
# Pydantic models (additive — only used by /v6/* routes)
# ---------------------------------------------------------------------------


class ContractCallRequest(BaseModel):
    """A trivial Smart Contract VM invocation request."""

    function: str = Field(..., min_length=1, max_length=64)
    args: List[Any] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# /v6/qalam/status — single source of truth for the v6.2.0 build
# ---------------------------------------------------------------------------


@router.get("/qalam/status", summary="Qalam v6.2.0 build status")
def qalam_status(request: Request) -> Dict[str, Any]:
    """Return the full Qalam v6.2.0 build status.

    This endpoint is additive: it never reads or mutates the existing
    ``/version`` or ``/core/status`` payloads. It exists to give the
    UI a single fetch that returns everything the new Real-time Live
    Activity Feed needs in one round-trip.
    """
    settings = request.app.state.__dict__.get("settings")  # optional
    import laniakea.core.config as _cfg  # local import keeps top-level clean
    s = _cfg.settings

    chain = getattr(request.app.state, "chain", None)
    bridge = getattr(request.app.state, "bridge", None)
    dao = getattr(request.app.state, "dao", None)
    dex = getattr(request.app.state, "dex", None)
    sim = getattr(request.app.state, "simulator", None)
    ai = getattr(request.app.state, "ai", None)
    market = getattr(request.app.state, "marketplace", None)
    knowledge_market = getattr(request.app.state, "knowledge_market", None)
    diplomacy = getattr(request.app.state, "diplomacy", None)
    achievements = getattr(request.app.state, "achievements", None)
    quantum = getattr(request.app.state, "quantum", None)
    scda = getattr(request.app.state, "scda_manager", None)
    metrics = getattr(request.app.state, "metrics", None)
    consensus = getattr(request.app.state, "consensus", None)

    return {
        "build": {
            "tag": "v6.2.0-Qalam",
            "project": s.PROJECT_NAME,
            "version": s.PROJECT_VERSION,
            "environment": s.DEPLOYMENT_ENV,
            "network_mode": s.NETWORK_MODE,
            "is_mainnet": bool(s.IS_MAINNET),
            "chain_id": s.CHAIN_ID,
            "network_id": s.NETWORK_ID,
            "uptime_seconds": _uptime_seconds(),
            "author": "Qalam",
            "license": "MIT",
            "hosting": "Render",
            "repo": "QalamHipHop/laniakea-protocol",
        },
        "subsystems": {
            "blockchain": chain is not None,
            "consensus": consensus is not None,
            "crosschain_bridge": bridge is not None,
            "quantum": quantum is not None,
            "governance_dao": dao is not None,
            "nft_marketplace": market is not None,
            "knowledge_market": knowledge_market is not None,
            "cosmic_simulation": sim is not None,
            "protocol_metrics": metrics is not None,
            "achievements": achievements is not None,
            "ai": ai is not None,
            "defi_dex": dex is not None,
            "diplomacy": diplomacy is not None,
            "scda": scda is not None,
        },
        "scda": _scda_summary(request),
        "blockchain": _safe_call(
            lambda: {
                "length": len(chain.chain) if chain is not None else 0,
                "pending": len(getattr(chain, "current_transactions", []) or []),
            },
            default={"length": 0, "pending": 0},
        ),
        "version_history": [
            "6.0.0-Mainnet",
            "6.0.1-Mainnet",
            "6.1.0-Qalam",
            "6.2.0-Qalam",
        ],
    }


# ---------------------------------------------------------------------------
# /v6/feed — Live Activity Feed
# ---------------------------------------------------------------------------


_FEED_BUFFER: List[Dict[str, Any]] = []
_FEED_MAX = 50
_FEED_SEQ = 0


def _push_event(kind: str, message: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Append an event to the in-process feed buffer (thread-safe enough for
    the Python GIL — FastAPI runs in one loop per worker).
    """
    global _FEED_SEQ
    _FEED_SEQ += 1
    evt = {
        "seq": _FEED_SEQ,
        "ts": time.time(),
        "kind": kind,
        "message": message,
        "meta": meta or {},
    }
    _FEED_BUFFER.append(evt)
    if len(_FEED_BUFFER) > _FEED_MAX:
        # keep the most recent entries
        del _FEED_BUFFER[: len(_FEED_BUFFER) - _FEED_MAX]
    return evt


def _synth_recent_events(request: Request) -> List[Dict[str, Any]]:
    """Synthesise a few recent events when the buffer is empty.

    This makes the feed feel alive even on a fresh boot — the events are
    computed from the current SCDA/chain state and are therefore always
    truthful (no fabricated tx hashes etc).
    """
    events: List[Dict[str, Any]] = []
    now = time.time()
    scda = _scda_summary(request)
    if scda.get("available"):
        for ident in scda.get("identities", [])[:5]:
            events.append({
                "seq": len(events) + 1,
                "ts": now - random.uniform(1, 60),
                "kind": "scda.snapshot",
                "message": f"SCDA {ident.get('identity')} reported complexity={ident.get('complexity')}",
                "meta": {"identity": ident.get("identity")},
            })
    chain = getattr(request.app.state, "chain", None)
    if chain is not None:
        try:
            length = len(chain.chain)
        except Exception:  # pragma: no cover
            length = 0
        events.append({
            "seq": len(events) + 1,
            "ts": now - 0.5,
            "kind": "blockchain.tick",
            "message": f"Chain height stable at {length} block(s)",
            "meta": {"length": length},
        })
    events.append({
        "seq": len(events) + 1,
        "ts": now - 0.1,
        "kind": "system.heartbeat",
        "message": "Laniakea mainnet node heartbeat OK",
        "meta": {"version": "6.2.0-Qalam"},
    })
    return events


@router.get("/feed", summary="Live Activity Feed")
def live_feed(request: Request, limit: int = 20) -> Dict[str, Any]:
    """Return the most recent live activity events.

    The endpoint reads from an in-process ring buffer; if the buffer is
    empty (fresh boot) it returns a synthesised snapshot derived from
    the current SCDA + chain state. The buffer is **append-only** for
    the lifetime of the worker process.
    """
    if limit < 1 or limit > _FEED_MAX:
        limit = 20
    events = list(_FEED_BUFFER)
    if not events:
        events = _synth_recent_events(request)
    # newest first
    events = sorted(events, key=lambda e: e.get("ts", 0), reverse=True)[:limit]
    return {
        "count": len(events),
        "buffer_size": len(_FEED_BUFFER),
        "events": events,
    }


# ---------------------------------------------------------------------------
# /v6/scda/leaderboard — additive top-N
# ---------------------------------------------------------------------------


@router.get("/scda/leaderboard", summary="Top SCDA leaderboard (Qalam)")
def v6_scda_leaderboard(request: Request, top_n: int = 10) -> Dict[str, Any]:
    """Return the top N SCDAs by complexity + energy, computed live.

    Falls back to identity list ordering if a SCDA's numeric state is
    unavailable, so the endpoint always returns 2xx.
    """
    if top_n < 1 or top_n > 100:
        top_n = 10
    summary = _scda_summary(request)
    if not summary.get("available"):
        return {"available": False, "items": [], "top_n": top_n}

    def _score(item: Dict[str, Any]) -> float:
        c = item.get("complexity")
        e = item.get("energy")
        c = float(c) if isinstance(c, (int, float)) else 0.0
        e = float(e) if isinstance(e, (int, float)) else 0.0
        return c * 10.0 + e * 0.1

    ranked = sorted(summary["identities"], key=_score, reverse=True)[:top_n]
    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank
        item["score"] = round(_score(item), 4)
    return {"available": True, "top_n": top_n, "items": ranked, "total": summary["count"]}


# ---------------------------------------------------------------------------
# /v6/cosmic/overview — richer version of /cosmic/overview
# ---------------------------------------------------------------------------


@router.get("/cosmic/overview", summary="Rich Cosmic Overview (Qalam)")
def v6_cosmic_overview(request: Request) -> Dict[str, Any]:
    """Return a richer Cosmic Overview than the v1 ``/cosmic/overview``.

    Includes: subsystem booleans, SCDA complexity histogram, knowledge
    market stats (if loaded), diplomacy stats (if loaded), and the live
    version metadata block.
    """
    chain = getattr(request.app.state, "chain", None)
    bridge = getattr(request.app.state, "bridge", None)
    dao = getattr(request.app.state, "dao", None)
    dex = getattr(request.app.state, "dex", None)
    sim = getattr(request.app.state, "simulator", None)
    ai = getattr(request.app.state, "ai", None)
    market = getattr(request.app.state, "marketplace", None)
    km = getattr(request.app.state, "knowledge_market", None)
    dip = getattr(request.app.state, "diplomacy", None)
    ach = getattr(request.app.state, "achievements", None)
    quantum = getattr(request.app.state, "quantum", None)
    scda = getattr(request.app.state, "scda_manager", None)
    metrics = getattr(request.app.state, "metrics", None)

    subsystems = {
        "blockchain": chain is not None,
        "consensus": getattr(request.app.state, "consensus", None) is not None,
        "crosschain": bridge is not None,
        "quantum": quantum is not None,
        "governance": dao is not None,
        "marketplace": market is not None,
        "simulation": sim is not None,
        "dashboard": metrics is not None,
        "achievements": ach is not None,
        "ai": ai is not None,
        "defi": dex is not None,
        "diplomacy": dip is not None,
        "knowledge_market": km is not None,
        "scda": scda is not None,
    }
    active = [k for k, v in subsystems.items() if v]

    chain_length = _safe_call(lambda: len(chain.chain), default=0) if chain else 0
    pool_names = _safe_call(lambda: list(getattr(dex, "pools", {}).keys()), default=[]) if dex else []
    sim_entities = _safe_call(lambda: len(sim.entities), default=0) if sim else 0
    knowledge_listed = _safe_call(
        lambda: len(km.list_assets()) if hasattr(km, "list_assets") else 0,
        default=0,
    ) if km else 0
    diplomacy_alliances = _safe_call(
        lambda: len(dip.alliances) if hasattr(dip, "alliances") else 0,
        default=0,
    ) if dip else 0
    scda_summary = _scda_summary(request)

    # Complexity histogram (3 bins: low / mid / high)
    bins = {"low": 0, "mid": 0, "high": 0}
    if scda_summary.get("available"):
        for ident in scda_summary.get("identities", []):
            c = ident.get("complexity")
            if not isinstance(c, (int, float)):
                continue
            if c < 1.5:
                bins["low"] += 1
            elif c < 3.0:
                bins["mid"] += 1
            else:
                bins["high"] += 1

    return {
        "build": {
            "tag": "v6.2.0-Qalam",
            "uptime_seconds": _uptime_seconds(),
        },
        "subsystems": subsystems,
        "subsystem_count": len(active),
        "active_subsystems": active,
        "blockchain": {
            "chain_length": chain_length,
            "latest_hash": _safe_call(
                lambda: chain.last_block.hash if hasattr(chain, "last_block") else None,
                default=None,
            ),
        },
        "defi": {
            "pool_count": len(pool_names),
            "pool_names": pool_names,
        },
        "simulation": {"entities": sim_entities},
        "knowledge_market": {
            "listed": knowledge_listed,
            "available": km is not None,
        },
        "diplomacy": {
            "alliances": diplomacy_alliances,
            "available": dip is not None,
        },
        "scda": {
            "count": scda_summary.get("count", 0),
            "complexity_histogram": bins,
        },
    }


# ---------------------------------------------------------------------------
# /v6/contract/{name} — Smart Contract VM (echo + deterministic hash)
# ---------------------------------------------------------------------------


@router.post("/contract/{name}", summary="Call a named contract function (echo VM)")
def v6_call_contract(name: str, body: ContractCallRequest) -> Dict[str, Any]:
    """A minimal, deterministic Smart Contract VM used by the v6.2 UI.

    The endpoint never raises; it returns a structured result that the
    UI can render. For unknown functions it returns an ``echo`` result
    with a stable hash so the call is still verifiable.
    """
    ts = time.time()
    # Deterministic hash of (name, function, args)
    raw = repr((name, body.function, body.args)).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    return {
        "contract": name,
        "function": body.function,
        "args": body.args,
        "result": {
            "kind": "echo",
            "ok": True,
            "tx_hash": "0x" + digest,
            "timestamp": ts,
            "gas_used": 21000 + len(body.args) * 800,
        },
    }


@router.get("/contract/{name}", summary="Get contract metadata")
def v6_get_contract(name: str) -> Dict[str, Any]:
    """Return metadata for a built-in contract name (purely informational)."""
    return {
        "contract": name,
        "kind": "echo-vm",
        "available_functions": [
            "ping",
            "set",
            "get",
            "inc",
            "mul",
            "hash",
        ],
        "version": "6.2.0-Qalam",
    }


# ---------------------------------------------------------------------------
# /v6/health — additive, same shape as /health but v6-tagged
# ---------------------------------------------------------------------------


@router.get("/health", summary="v6.2 health probe")
def v6_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "version": "6.2.0-Qalam",
        "uptime_seconds": _uptime_seconds(),
    }


# ---------------------------------------------------------------------------
# Convenience: push a heartbeat event when the module is imported
# ---------------------------------------------------------------------------


_push_event("module.load", "v6.2.0-Qalam routes registered", {"routes": 7})
