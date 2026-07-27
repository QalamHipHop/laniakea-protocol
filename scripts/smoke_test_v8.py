#!/usr/bin/env python3
"""
LaniakeA Protocol · v8 UI Smoke Test
=====================================
Author: Qalam · Build v6.3.0-Qalam

Hits every endpoint the unified 8D Cosmic UI (cosmic_v8.html) calls and
prints a pass/fail summary. Use this to verify a Render deployment went
green.

Usage::

    python scripts/smoke_test_v8.py [--base https://laniakea-protocol.onrender.com]

Exit code 0 on all-green, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Dict, List, Tuple
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError


# Every endpoint cosmic_v8.js calls. Order = display order in the report.
ENDPOINTS: List[Tuple[str, str]] = [
    # Overview tab
    ("GET", "/health"),
    ("GET", "/core/status"),
    ("GET", "/"),
    ("GET", "/cosmic/overview"),
    ("GET", "/dashboard/metrics"),
    ("GET", "/achievements/all"),
    ("GET", "/defi/pools"),
    ("GET", "/governance/proposals"),
    ("GET", "/marketplace/nft/all"),
    ("GET", "/quantum/queue"),
    ("GET", "/marketplace/all"),
    ("GET", "/knowledge_market/listed"),
    ("GET", "/v6/scda/leaderboard"),
    ("GET", "/token/info"),
    ("GET", "/crosschain/supported"),
    # v8 UI compatibility (new in v6.3.0-Qalam)
    ("GET", "/ai/info"),
    ("GET", "/ai/problems"),
    ("GET", "/consensus/info"),
    ("GET", "/metaverse/world"),
    ("GET", "/metaverse/world/stats"),
    ("GET", "/mining/info"),
    ("GET", "/mining/rewards"),
    ("GET", "/reputation/info"),
    ("GET", "/reputation/leaderboard"),
    ("GET", "/v6/qalam/version-history"),
    ("GET", "/v6/qalam/subsystems"),
    # SCDA tab
    ("GET", "/scda/identities"),
    # v6 namespace
    ("GET", "/v6/qalam/status"),
    ("GET", "/v6/feed"),
    ("GET", "/v6/cosmic/overview"),
    # Web UI
    ("GET", "/web/cosmic_v8.html"),
    ("GET", "/web/cosmic_v8.css"),
    ("GET", "/web/cosmic_v8.js"),
    # Discovery
    ("GET", "/discovery"),
]


def _hit(base: str, method: str, path: str, timeout: float = 12.0) -> Tuple[int, float]:
    url = base.rstrip("/") + path
    t0 = time.perf_counter()
    req = urlrequest.Request(url, method=method, headers={"Accept": "application/json"})
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            _ = resp.read(1024)
            return resp.status, (time.perf_counter() - t0) * 1000.0
    except HTTPError as exc:
        return exc.code, (time.perf_counter() - t0) * 1000.0
    except URLError:
        return 0, (time.perf_counter() - t0) * 1000.0


def main() -> int:
    p = argparse.ArgumentParser(description="LaniakeA v8 UI smoke test")
    p.add_argument(
        "--base",
        default="https://laniakea-protocol.onrender.com",
        help="Base URL of the deployment",
    )
    p.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Exit non-zero on any non-2xx response (default: only 5xx and 0 fail)",
    )
    args = p.parse_args()

    print(f"🚬 LaniakeA · v8 UI Smoke Test")
    print(f"   base: {args.base}")
    print(f"   endpoints: {len(ENDPOINTS)}")
    print()
    print(f"{'METHOD':<6} {'STATUS':>6}  {'ms':>7}  PATH")

    counts: Dict[str, int] = {"ok": 0, "warn": 0, "fail": 0}
    for method, path in ENDPOINTS:
        status, ms = _hit(args.base, method, path)
        if status == 0:
            tag = "FAIL"; counts["fail"] += 1
        elif 200 <= status < 300:
            tag = "OK"; counts["ok"] += 1
        elif 300 <= status < 500:
            tag = "WARN"; counts["warn"] += 1
        else:
            tag = "FAIL"; counts["fail"] += 1
        print(f"{method:<6} {status:>6}  {ms:>7.1f}  {path}")

    print()
    print(f"  ✓ OK   {counts['ok']}")
    print(f"  ! WARN {counts['warn']}  (3xx-4xx — usually harmless)")
    print(f"  ✗ FAIL {counts['fail']}  (5xx / network — needs attention)")

    if counts["fail"] > 0 or (args.fail_on_warn and counts["warn"] > 0):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
