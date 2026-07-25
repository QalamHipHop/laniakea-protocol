"""
Laniakea Protocol — Observability API
=====================================

Exposes the live state of every subsystem in a single, deterministic
JSON payload — used by the dashboard, the live smoke test, and external
monitoring tooling (Grafana, Prometheus federation, Uptime Kuma, etc.).

Two endpoints are provided:

* ``GET /observability/snapshot`` — comprehensive JSON snapshot of all
  subsystems (SCDA, knowledge market, diplomacy, blockchain, DeFi,
  WebSocket, request counters).
* ``GET /observability/prometheus`` — Prometheus text exposition format
  for scraping.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict

from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

from laniakea.intelligence.scda_manager import get_scda_manager
from laniakea.marketplace.knowledge_market import get_marketplace
from laniakea.governance.metaverse_diplomacy import get_diplomacy_system


router = APIRouter(prefix="/observability", tags=["Observability"])


# --- Service-start timestamp (used to compute uptime) ---------------------
_SERVICE_STARTED_AT = time.time()
_VERSION = os.getenv("LANIAKEA_VERSION", "1.0.0-Unified")


def _uptime_seconds() -> float:
    return max(0.0, time.time() - _SERVICE_STARTED_AT)


def _safe_call(fn, default=None):
    try:
        return fn() if fn else default
    except Exception:
        return default


@router.get(
    "/snapshot",
    summary="Full snapshot of every Laniakea subsystem",
    response_model=Dict[str, Any],
)
def observability_snapshot() -> Dict[str, Any]:
    """One-shot JSON snapshot — for dashboards and live smoke tests."""
    manager = _safe_call(get_scda_manager, default=None)
    market = _safe_call(get_marketplace, default=None)
    diplomacy = _safe_call(get_diplomacy_system, default=None)

    scda_payload: Dict[str, Any] = {"available": manager is not None}
    if manager is not None:
        states = manager.all_states()
        scda_payload.update({
            "total": len(states),
            "total_complexity": manager.total_complexity(),
            "total_energy": manager.total_energy(),
            "mean_complexity": (
                manager.total_complexity() / len(states) if states else 0.0
            ),
        })

    market_payload: Dict[str, Any] = {"available": market is not None}
    if market is not None:
        assets = getattr(market, "assets", {}) or {}
        listed = [a for a in assets.values() if getattr(a, "is_listed", False)]
        market_payload.update({
            "total_assets": len(assets),
            "listed_assets": len(listed),
            "total_volume": getattr(market, "total_volume", 0.0),
        })

    diplomacy_payload: Dict[str, Any] = {"available": diplomacy is not None}
    if diplomacy is not None:
        alliances = getattr(diplomacy, "alliances", {}) or {}
        diplomacy_payload.update({
            "alliances": len(alliances),
            "treaties": len(getattr(diplomacy, "treaties", {}) or {}),
        })

    return {
        "service": {
            "name": "laniakea-protocol",
            "version": _VERSION,
            "uptime_seconds": _uptime_seconds(),
            "started_at": _SERVICE_STARTED_AT,
            "now": time.time(),
        },
        "scda": scda_payload,
        "knowledge_market": market_payload,
        "diplomacy": diplomacy_payload,
    }


@router.get(
    "/prometheus",
    summary="Prometheus text-format metrics",
    response_class=PlainTextResponse,
)
def prometheus_metrics() -> Response:
    """Expose the most useful counters in Prometheus text format.

    This is intentionally lightweight: no client library, no histogram
    buckets — just the gauge/counter values that matter for live
    alerting.
    """
    manager = _safe_call(get_scda_manager, default=None)
    market = _safe_call(get_marketplace, default=None)
    diplomacy = _safe_call(get_diplomacy_system, default=None)

    lines = [
        "# HELP laniakea_uptime_seconds Seconds since service start",
        "# TYPE laniakea_uptime_seconds gauge",
        f"laniakea_uptime_seconds {_uptime_seconds():.3f}",
        "",
        "# HELP laniakea_version_info Service version (always 1)",
        "# TYPE laniakea_version_info gauge",
        f'laniakea_version_info{{version="{_VERSION}"}} 1',
        "",
    ]

    if manager is not None:
        states = manager.all_states()
        lines.extend([
            "# HELP laniakea_scda_total Number of SCDAs",
            "# TYPE laniakea_scda_total gauge",
            f"laniakea_scda_total {len(states)}",
            "",
            "# HELP laniakea_scda_complexity_sum Sum of C(t) across all SCDAs",
            "# TYPE laniakea_scda_complexity_sum gauge",
            f"laniakea_scda_complexity_sum {manager.total_complexity():.4f}",
            "",
            "# HELP laniakea_scda_energy_sum Sum of E(t) across all SCDAs",
            "# TYPE laniakea_scda_energy_sum gauge",
            f"laniakea_scda_energy_sum {manager.total_energy():.4f}",
            "",
        ])

    if market is not None:
        assets = getattr(market, "assets", {}) or {}
        listed = sum(1 for a in assets.values() if getattr(a, "is_listed", False))
        lines.extend([
            "# HELP laniakea_market_assets_total Total knowledge assets minted",
            "# TYPE laniakea_market_assets_total gauge",
            f"laniakea_market_assets_total {len(assets)}",
            "",
            "# HELP laniakea_market_listed_total Knowledge assets currently listed",
            "# TYPE laniakea_market_listed_total gauge",
            f"laniakea_market_listed_total {listed}",
            "",
        ])

    if diplomacy is not None:
        alliances = getattr(diplomacy, "alliances", {}) or {}
        lines.extend([
            "# HELP laniakea_diplomacy_alliances_total Total alliances formed",
            "# TYPE laniakea_diplomacy_alliances_total gauge",
            f"laniakea_diplomacy_alliances_total {len(alliances)}",
            "",
        ])

    return PlainTextResponse(
        content="\n".join(lines),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
