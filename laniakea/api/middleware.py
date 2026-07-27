"""
Laniakea Protocol — API Middleware Stack
=========================================

Production-grade middleware components for the unified FastAPI surface:

* :class:`RequestIDMiddleware` — adds a unique ``X-Request-ID`` to every
  request/response so logs, audit trails, and client-side debugging can
  correlate calls across the whole stack.
* :class:`SecurityHeadersMiddleware` — emits the standard hardening
  headers (``X-Content-Type-Options``, ``X-Frame-Options``,
  ``Referrer-Policy``, ``Permissions-Policy``,
  ``Strict-Transport-Security``).
* :class:`RateLimitMiddleware` — per-process, per-IP sliding window
  rate limiter. Defaults to a generous 600 req/min to avoid breaking
  the WebSocket gateway but is configurable through ``RATE_LIMIT_PER_MIN``.
* :class:`DeprecationMiddleware` — adds ``X-Deprecation-Notice`` /
  ``Sunset`` / ``Link`` headers to known legacy paths so SDK
  consumers can migrate.

The middleware are intentionally simple and dependency-free so they
boot on the minimal Render image.
"""

from __future__ import annotations

import os
import time
import uuid
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


# --- Request ID ------------------------------------------------------------
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a stable request ID to every request/response pair.

    The header is exposed both as ``X-Request-ID`` (read by most SDKs)
    and stored on ``request.state.request_id`` so handlers / audit
    loggers can use it without re-parsing headers.
    """

    HEADER_IN = "X-Request-ID"
    HEADER_OUT = "X-Request-ID"

    async def dispatch(self, request: Request, call_next) -> Response:
        incoming = request.headers.get(self.HEADER_IN)
        rid = incoming if incoming else f"lk-{uuid.uuid4().hex[:16]}"
        request.state.request_id = rid
        request.state.request_start = time.perf_counter()
        response = await call_next(request)
        response.headers[self.HEADER_OUT] = rid
        # Add a measured latency header — handy for client-side tracing.
        elapsed_ms = (time.perf_counter() - request.state.request_start) * 1000.0
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response


# --- Security headers ------------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Emit baseline hardening headers on every response."""

    DEFAULTS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "X-Laniakea-Protocol": "LaniakeA/1.0.0-Unified",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for k, v in self.DEFAULTS.items():
            # Don't override a header the application deliberately set.
            if k not in response.headers:
                response.headers[k] = v
        # Only emit HSTS when explicitly enabled (e.g. when serving over HTTPS).
        if os.getenv("ENABLE_HSTS", "false").lower() in ("1", "true", "yes"):
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response


# --- Per-IP rate limiter ---------------------------------------------------
class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple sliding-window per-IP rate limiter.

    Tracks timestamps in a deque per remote address. The window is
    ``RATE_LIMIT_WINDOW_SEC`` (default 60s) and the cap is
    ``RATE_LIMIT_PER_MIN`` (default 600). Health / metrics / docs paths
    are exempt so monitoring tooling is never throttled.
    """

    EXEMPT_PREFIXES = (
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/ws/",  # WebSocket upgrades are long-lived
    )

    def __init__(self, app) -> None:
        super().__init__(app)
        self.window_sec = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
        self.limit = int(os.getenv("RATE_LIMIT_PER_MIN", "600"))
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)

    def _client_key(self, request: Request) -> str:
        # Prefer the first X-Forwarded-For hop (Render sets it).
        xff = request.headers.get("X-Forwarded-For")
        if xff:
            return xff.split(",")[0].strip()
        return (request.client.host if request.client else "unknown") or "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            return await call_next(request)
        key = self._client_key(request)
        now = time.monotonic()
        bucket = self._buckets[key]
        # Drop stale entries
        cutoff = now - self.window_sec
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.limit:
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": self.limit,
                    "window_seconds": self.window_sec,
                    "path": path,
                },
                headers={
                    "Retry-After": str(self.window_sec),
                    "X-RateLimit-Limit": str(self.limit),
                    "X-RateLimit-Remaining": "0",
                },
            )
        bucket.append(now)
        response = await call_next(request)
        remaining = max(0, self.limit - len(bucket))
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


# --- Deprecation notices ---------------------------------------------------
class DeprecationMiddleware(BaseHTTPMiddleware):
    """Flag known legacy paths so SDK consumers get a deprecation hint.

    Currently only the dash-form ``/knowledge-market/*`` is mapped to the
    canonical underscore form ``/knowledge_market/*`` because the dash
    variant was a historical alias and is kept only for backward
    compatibility.
    """

    LEGACY: Dict[str, Tuple[str, str]] = {
        "/knowledge-market": (
            "/knowledge_market",
            "Use the canonical underscore form `/knowledge_market/*`",
        ),
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        path = request.url.path
        for legacy_prefix, (canonical, notice) in self.LEGACY.items():
            if path.startswith(legacy_prefix):
                response.headers["Deprecation"] = "true"
                response.headers["X-Deprecation-Notice"] = notice
                response.headers["Link"] = f'<{canonical}>; rel="successor-version"'
                break
        return response


# --- Aggregate registry ----------------------------------------------------
def install_default_middleware(app) -> None:
    """Install the full Laniakea middleware stack on a FastAPI app.

    Order matters: outermost middleware runs first, so we install:

    1. Security headers (outer — applies to every response, even errors).
    2. Deprecation notices (outer — flag legacy paths).
    3. Rate limiter (early — reject before expensive work).
    4. Request ID (inner — so business handlers can read ``state.request_id``).
    """
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(DeprecationMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
