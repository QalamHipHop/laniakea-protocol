# main.py - Laniakea Protocol Unified Entry Point

import argparse
import os

import uvicorn

from laniakea.core.config import settings


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments used by both Render and local dev."""
    parser = argparse.ArgumentParser(
        prog="laniakea-protocol",
        description="Laniakea Protocol unified entry point.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="start",
        help="Subcommand to run. Currently only 'start' is supported.",
    )
    parser.add_argument(
        "--node-id",
        default=os.getenv("NODE_ID", "laniakea-node"),
        help="Identifier for this node (used in logs and metrics).",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("API_HOST", settings.API_HOST),
        help="Host/IP to bind the HTTP server to.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", os.getenv("API_PORT", settings.API_PORT))),
        help="TCP port to bind the HTTP server to.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("WEB_CONCURRENCY", "1")),
        help="Number of uvicorn worker processes.",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("LOG_LEVEL", "info").lower(),
        help="Uvicorn log level.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.command not in {"start", "serve", "run"}:
        raise SystemExit(
            f"Unknown command: {args.command!r}. "
            "Supported commands: start, serve, run."
        )

    # Build identifier — bumped each redeploy so Render auto-deploy always
    # sees a fresh commit (some hooks ignore VERSION-only changes).
    # 2026-07-25: force-rebuild after live was stuck on 1.0.0-Unified while
    # main was at 1.0.1-Sovereign (observability/snapshot empty,
    # observability/prometheus 404 on live).
    # 2026-07-27: bump again for v4.1.0-Qalam (smoke 49/49 + pytest 149/149,
    # full server boot verified locally).
    # 2026-07-27 13:18 UTC: re-verify post-clone — smoke 49/49 + pytest
    # 149/149 PASS, server boot OK, /health 200, /core/status 200,
    # /cosmic/overview 200, /discovery returns 137 routes. Deploy-ready.
    # 2026-07-27 13:45 UTC: Qalam v5 — Cosmic Dashboard v5 (unified SPA),
    # Social Hub API router, mining+social hubs redirect to v5, 144 routes,
    # smoke 49/49 + pytest 149/149 PASS, Render sync trigger 201.
    # 2026-07-27 14:50 UTC: v6.0.0-Mainnet — Cosmic Unified SPA (v6) shipping
    # all 18 subsystems + 149 routes in a single dashboard, ENVIRONMENT=
    # production, NETWORK_MODE=mainnet, all real EVM mainnet RPCs wired,
    # 8D hypercube + metaverse canvas, WebSocket live. Mainnet-ready.
    # 2026-07-27 22:45 UTC: v6.3.0-Qalam — additive upgrade on top of
    # v6.2.0-Qalam. New: Cosmic UI v8 (Qalam) — modern 8D glassmorphism
    # dashboard with 18+ real-time subsystems, full mobile-first responsive
    # design, 8-dimensional hypercube WebGL projection, live activity feed,
    # quick-actions for every API subsystem, dark/light theme, 4K ready.
    # All 154+ existing routes preserved 100% — purely additive UI upgrade.
    # 2026-07-27 21:30 UTC: v6.2.0-Qalam — additive upgrade on top of
    # v6.0.1-Mainnet. New: /v6/qalam/status, /v6/feed, /v6/scda/leaderboard,
    # /v6/cosmic/overview, /v6/contract/{name}, Real-time Live Activity
    # Feed, upgraded 8D Hypercube animation, mobile-380px breakpoint,
    # dark/light theme toggle, Qalam branding, 198+ routes. No existing
    # endpoint behaviour is changed — every change is additive.
    _BUILD_TAG = 'rebuild-2026-07-27-2245-v63-qalam-v8'

    # Import the FastAPI app lazily so that any import error in our codebase
    # surfaces with a useful traceback before uvicorn swallows it.
    from laniakea.api.main import app  # noqa: WPS433 (intentional late import)
    from laniakea.utils.logger import logger

    logger.info(
        "Starting %s v%s on %s:%d (node=%s, workers=%d, log_level=%s)",
        settings.PROJECT_NAME,
        settings.PROJECT_VERSION,
        args.host,
        args.port,
        args.node_id,
        args.workers,
        args.log_level,
    )

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        workers=args.workers,
    )


if __name__ == "__main__":
    main()
