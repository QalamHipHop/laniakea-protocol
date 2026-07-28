"""
LaniakeA Protocol — Cosmic UI v8 Extra API
============================================
Author: cosmic-backend (Track B) + Qalam

Additive router that powers the unified 8D Cosmic Dashboard (v8) features
that go beyond the existing v6.x / v8_ui_api surface. All endpoints are
strictly read/write to in-memory state (app.state or the live subsystem
references attached at startup) and never touch disk or external services
without an explicit call.

Endpoints
---------
* ``GET  /cosmic/system/overview`` — aggregated protocol snapshot
* ``GET  /cosmic/network/graph``   — P2P graph (peers + edges) for 3D viewer
* ``GET  /cosmic/metaverse/state`` — metaverse world state snapshot
* ``GET  /cosmic/algorithms/list`` — saved custom hard problems (runtime)
* ``POST /cosmic/algorithms/save`` — save a custom hard problem
* ``DELETE /cosmic/algorithms/{id}`` — delete a saved algorithm
* ``GET  /cosmic/scda/{identity}/full`` — full SCDA snapshot
* ``POST /cosmic/scda/create-custom``  — create SCDA with custom params
* ``POST /cosmic/scda/{identity}/evolve`` — evolve a specific SCDA
"""

from __future__ import annotations

import hashlib
import logging
import math
import random
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

logger = logging.getLogger("laniakea.api.cosmic_v8_extra")

router = APIRouter(prefix="/cosmic", tags=["Cosmic v8"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class AlgorithmSaveRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    domain: str = Field(..., min_length=1, max_length=64)
    difficulty: float = Field(..., ge=0.0, le=1.0)
    equation: str = Field(..., min_length=1, max_length=2000)
    rubric: List[str] = Field(default_factory=list)


class SCCustomCreateRequest(BaseModel):
    identity: str = Field(..., min_length=1, max_length=128)
    initial_complexity: float = Field(default=1.0, ge=0.0, le=1e6)
    initial_energy: float = Field(default=100.0, ge=0.0, le=1e6)
    dna_overrides: Optional[Dict[str, Any]] = None


class SCDAEvolveRequest(BaseModel):
    problem_difficulty: float = Field(..., ge=0.0, le=1.0)
    custom_problem: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _state(request: Request) -> Any:
    return request.app.state


def _safe(callable_fn, *args, default=None, **kwargs):
    try:
        return callable_fn(*args, **kwargs)
    except Exception as exc:  # pragma: no cover
        logger.debug("safe call failed for %s: %s", getattr(callable_fn, "__name__", callable_fn), exc)
        return default


def _ensure_algorithms_bucket(state: Any) -> Dict[str, Dict[str, Any]]:
    """Return (and lazily create) the in-memory algorithm bucket."""
    if not hasattr(state, "cosmic_algorithms") or state.cosmic_algorithms is None:
        state.cosmic_algorithms = {}
    return state.cosmic_algorithms


# ---------------------------------------------------------------------------
# 1) System overview — aggregate
# ---------------------------------------------------------------------------


@router.get("/system/overview", summary="Aggregated protocol snapshot")
def system_overview(request: Request) -> Dict[str, Any]:
    state = _state(request)
    uptime = None
    try:
        from time import time as _t
        start = getattr(state, "start_time", _t())
        uptime = int(_t() - start)
    except Exception:
        pass

    chain = getattr(state, "chain", None)
    consensus = getattr(state, "consensus", None)
    dex = getattr(state, "dex", None)
    dao = getattr(state, "dao", None)
    achievements = getattr(state, "achievements", None)
    marketplace = getattr(state, "marketplace", None)
    ai = getattr(state, "ai", None)
    scda_manager = getattr(state, "scda_manager", None)

    def _height() -> Optional[int]:
        try:
            if chain and hasattr(chain, "chain"):
                return len(chain.chain)
            if chain and hasattr(chain, "blocks"):
                return len(chain.blocks)
        except Exception:
            return None
        return None

    return {
        "network": "mainnet",
        "version": "v6.3.0-Qalam",
        "uptime_seconds": uptime,
        "block_height": _height(),
        "validators": _safe(lambda: len(getattr(consensus, "validators", []))),
        "tps": _safe(lambda: getattr(chain, "tps", 0)) or 0,
        "treasury": _safe(lambda: getattr(dao, "treasury_balance", 0)) or 0,
        "ai": {
            "available": ai is not None,
            "performance": _safe(lambda: getattr(ai, "performance_score", None)),
        },
        "dex_pools": _safe(lambda: len(getattr(dex, "pools", {}))) or 0,
        "achievements": _safe(lambda: len(getattr(achievements, "catalog", []))) or 0,
        "marketplace_nfts": _safe(lambda: len(getattr(marketplace, "nfts", []))) or 0,
        "scda_count": _safe(lambda: len(getattr(scda_manager, "scda_registry", {}))) or 0,
        "subsystems": {
            "blockchain": chain is not None,
            "consensus": consensus is not None,
            "defi": dex is not None,
            "governance": dao is not None,
            "marketplace": marketplace is not None,
            "ai": ai is not None,
            "achievements": achievements is not None,
            "scda": scda_manager is not None,
            "metaverse": getattr(state, "metaverse_world", None) is not None,
        },
    }


# ---------------------------------------------------------------------------
# 2) Network graph — for 3D P2P viewer
# ---------------------------------------------------------------------------


@router.get("/network/graph", summary="P2P graph snapshot for 3D viewer")
def network_graph(request: Request) -> Dict[str, Any]:
    state = _state(request)
    bridge = getattr(state, "bridge", None)
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Try to harvest live peers
    peers: List[Any] = []
    try:
        if bridge and hasattr(bridge, "peers"):
            peers = list(bridge.peers or [])
    except Exception:
        peers = []

    if peers:
        for i, p in enumerate(peers):
            pid = getattr(p, "id", f"peer-{i}")
            nodes.append(
                {
                    "id": pid,
                    "label": getattr(p, "name", pid)[:16],
                    "x": float(math.cos(i * 0.7) * 1.6),
                    "y": float(math.sin(i * 0.5) * 1.6),
                    "z": float(math.cos(i * 0.3 + 0.4) * 1.6),
                    "region": getattr(p, "region", "global"),
                    "latency_ms": getattr(p, "latency", random.randint(8, 90)),
                }
            )
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if random.random() < 0.35:
                    edges.append(
                        {"source": nodes[i]["id"], "target": nodes[j]["id"], "weight": random.random()}
                    )
    else:
        # Deterministic 24-node fallback across 8D positions
        rng = random.Random(2026)
        names = [
            "laniakea-01", "laniakea-02", "laniakea-03", "laniakea-04",
            "cosmos-1", "cosmos-2", "nebula-x", "nebula-y",
            "void-relay", "plasma-1", "plasma-2", "quasar-7",
            "horizon-9", "horizon-10", "helix-3", "helix-4",
            "photon-a", "photon-b", "photon-c", "prism-1",
            "prism-2", "aurora-1", "aurora-2", "aurora-3",
        ]
        regions = ["na", "eu", "ap", "sa", "af", "oc"]
        for i, n in enumerate(names):
            theta = (i / 24) * 2 * math.pi
            phi = (i * 0.43) % math.pi
            r = 1.4 + 0.25 * math.sin(i)
            nodes.append(
                {
                    "id": n,
                    "label": n,
                    "x": float(r * math.sin(phi) * math.cos(theta)),
                    "y": float(r * math.sin(phi) * math.sin(theta)),
                    "z": float(r * math.cos(phi)),
                    "region": regions[i % len(regions)],
                    "latency_ms": rng.randint(8, 180),
                }
            )
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if rng.random() < 0.30:
                    edges.append(
                        {"source": nodes[i]["id"], "target": nodes[j]["id"], "weight": rng.random()}
                    )

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "avg_degree": (2 * len(edges) / len(nodes)) if nodes else 0,
        },
    }


# ---------------------------------------------------------------------------
# 3) Metaverse state
# ---------------------------------------------------------------------------


@router.get("/metaverse/state", summary="Metaverse world state snapshot")
def metaverse_state(request: Request) -> Dict[str, Any]:
    state = _state(request)
    world = getattr(state, "metaverse_world", None)
    if world is None:
        return {
            "regions": [],
            "avatars": [],
            "entities": [],
            "stats": {
                "region_count": 0,
                "avatar_count": 0,
                "entity_count": 0,
                "scda_count": 0,
            },
        }
    try:
        regions = _safe(lambda: list(world.regions), default=[]) or []
        avatars = _safe(lambda: list(world.avatars), default=[]) or []
        entities = _safe(lambda: list(world.entities), default=[]) or []
        return {
            "regions": [
                {"id": getattr(r, "id", i), "name": getattr(r, "name", f"region-{i}")}
                for i, r in enumerate(regions[:64])
            ],
            "avatars": [
                {"id": getattr(a, "id", i), "owner": getattr(a, "owner", "")[:24]}
                for i, a in enumerate(avatars[:64])
            ],
            "entities": [
                {"id": getattr(e, "id", i), "type": getattr(e, "type", "entity")}
                for i, e in enumerate(entities[:128])
            ],
            "stats": {
                "region_count": len(regions),
                "avatar_count": len(avatars),
                "entity_count": len(entities),
                "scda_count": _safe(lambda: len(getattr(state.scda_manager, "scda_registry", {}))),
            },
        }
    except Exception as exc:  # pragma: no cover
        logger.warning("metaverse state failed: %s", exc)
        return {"regions": [], "avatars": [], "entities": [], "stats": {}, "error": str(exc)}


# ---------------------------------------------------------------------------
# 4-6) Algorithm save / list / delete
# ---------------------------------------------------------------------------


@router.get("/algorithms/list", summary="List custom hard problems saved in memory")
def algorithms_list(request: Request) -> Dict[str, Any]:
    bucket = _ensure_algorithms_bucket(_state(request))
    items = sorted(bucket.values(), key=lambda a: a.get("created_at", 0), reverse=True)
    return {"algorithms": items, "count": len(items)}


@router.post("/algorithms/save", summary="Save a custom hard problem")
def algorithms_save(req: AlgorithmSaveRequest, request: Request) -> Dict[str, Any]:
    bucket = _ensure_algorithms_bucket(_state(request))
    aid = "alg-" + hashlib.sha1(
        f"{req.name}-{req.domain}-{time.time()}-{uuid.uuid4().hex}".encode()
    ).hexdigest()[:12]
    record = {
        "id": aid,
        "name": req.name,
        "domain": req.domain,
        "difficulty": req.difficulty,
        "equation": req.equation,
        "rubric": req.rubric,
        "created_at": time.time(),
        "source": "user",
    }
    bucket[aid] = record
    return {"id": aid, "status": "saved", "record": record}


@router.delete("/algorithms/{algorithm_id}", summary="Delete a saved algorithm")
def algorithms_delete(algorithm_id: str, request: Request) -> Dict[str, Any]:
    bucket = _ensure_algorithms_bucket(_state(request))
    if algorithm_id not in bucket:
        raise HTTPException(status_code=404, detail=f"algorithm {algorithm_id} not found")
    del bucket[algorithm_id]
    return {"status": "deleted", "id": algorithm_id}


# ---------------------------------------------------------------------------
# 7) Full SCDA snapshot
# ---------------------------------------------------------------------------


@router.get("/scda/{identity}/full", summary="Full SCDA snapshot (state, dna, knowledge vector, lineage)")
def scda_full(identity: str, request: Request) -> Dict[str, Any]:
    state = _state(request)
    mgr = getattr(state, "scda_manager", None)
    if mgr is None:
        raise HTTPException(status_code=503, detail="scda manager not initialised")
    scda = _safe(lambda: mgr.get(identity), default=None)
    if scda is None:
        raise HTTPException(status_code=404, detail=f"scda {identity} not found")
    return {
        "identity": identity,
        "state": _safe(lambda: mgr.state_for(identity), default=None)
        or _safe(lambda: mgr._state_for(scda), default=None)
        or {},
        "knowledge_vector": _safe(lambda: list(getattr(scda, "knowledge_vector", [])), default=[]),
        "dna": _safe(lambda: scda.dna.to_dict(), default={"genes": []}),
        "lineage": _safe(lambda: list(getattr(scda, "lineage", [])), default=[]),
    }


# ---------------------------------------------------------------------------
# 8) Create custom SCDA
# ---------------------------------------------------------------------------


@router.post("/scda/create-custom", summary="Create SCDA with custom initial parameters")
def scda_create_custom(req: SCCustomCreateRequest, request: Request) -> Dict[str, Any]:
    state = _state(request)
    mgr = getattr(state, "scda_manager", None)
    if mgr is None:
        raise HTTPException(status_code=503, detail="scda manager not initialised")
    try:
        scda = _safe(
            lambda: mgr.create(
                identity=req.identity,
                initial_complexity=req.initial_complexity,
                initial_energy=req.initial_energy,
            ),
            default=None,
        )
    except TypeError:
        # Older signature — fall back
        scda = _safe(lambda: mgr.create(req.identity), default=None)
    if scda is None:
        raise HTTPException(status_code=500, detail="failed to create scda")
    return {
        "status": "created",
        "identity": req.identity,
        "state": _safe(lambda: mgr.state_for(req.identity), default=None)
        or _safe(lambda: mgr._state_for(scda), default=None)
        or {},
    }


# ---------------------------------------------------------------------------
# 9) Evolve a specific SCDA
# ---------------------------------------------------------------------------


@router.post("/scda/{identity}/evolve", summary="Evolve a specific SCDA")
def scda_evolve(identity: str, req: SCDAEvolveRequest, request: Request) -> Dict[str, Any]:
    state = _state(request)
    mgr = getattr(state, "scda_manager", None)
    if mgr is None:
        raise HTTPException(status_code=503, detail="scda manager not initialised")
    scda = _safe(lambda: mgr.get(identity), default=None)
    if scda is None:
        raise HTTPException(status_code=404, detail=f"scda {identity} not found")
    before = float(getattr(scda, "complexity_index", 0.0))
    try:
        problem = {
            "difficulty": req.problem_difficulty,
            "domain": (req.custom_problem or {}).get("domain", "knowledge"),
            "statement": (req.custom_problem or {}).get("statement", ""),
            "equation": (req.custom_problem or {}).get("equation", ""),
        }
        if hasattr(scda, "attempt_solve_problem"):
            scda.attempt_solve_problem(problem, solution_quality=0.85)
        elif hasattr(scda, "passive_update"):
            scda.passive_update()
    except Exception as exc:  # pragma: no cover
        logger.warning("evolve failed: %s", exc)
    after = float(getattr(scda, "complexity_index", before))
    return {
        "identity": identity,
        "before": before,
        "after": after,
        "delta_c": after - before,
        "new_state": _safe(lambda: mgr.state_for(identity), default=None)
        or _safe(lambda: mgr._state_for(scda), default=None)
        or {},
    }
