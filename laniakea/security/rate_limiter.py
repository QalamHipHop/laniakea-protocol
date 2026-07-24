"""
LaniakeA Protocol - Rate Limiter (re-export)
==============================================

Re-exports the sliding-window + token-bucket rate-limiter from
``src/security/rate_limiter.py`` so DDoS / brute-force protection
remains accessible through the canonical ``laniakea.*`` path.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.security.rate_limiter import (  # noqa: E402
    RateLimitConfig,
    ClientState,
    RateLimiter,
    get_rate_limiter,
    rate_limit,
)

__all__ = [
    "RateLimitConfig",
    "ClientState",
    "RateLimiter",
    "get_rate_limiter",
    "rate_limit",
]
