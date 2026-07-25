"""
Laniakea Protocol - In-Process Telemetry
========================================

A tiny, dependency-free telemetry layer that powers the
``/observability/snapshot`` endpoint and the per-route timing
middleware. The design is deliberately minimal:

* **In-process only** — no external exporter, no OpenTelemetry
  dependency. If you need OTLP, wrap :class:`Tracer.export` in your
  own exporter; the API stays the same.
* **Append-only ring buffer for spans** — the most recent
  ``MAX_SPANS`` spans live in memory and can be inspected at any
  time. Useful for live debugging without setting up a full tracing
  backend.
* **Counters + histograms per (subsystem, operation)** — keep the
  Prometheus-style naming so the existing ``/observability/prometheus``
  endpoint can be extended to use them.

Author: LaniakeA Dev
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from typing import Any, Deque, Dict, Iterator, List, Optional, Tuple


# --- Span data -------------------------------------------------------------
class Span:
    """A single timed operation.

    Spans are created with :class:`Tracer.span` (a context manager) so
    the open/close bookkeeping is always correct even on exception.
    """

    __slots__ = (
        "name",
        "subsystem",
        "request_id",
        "started_at",
        "ended_at",
        "duration_ms",
        "status",
        "error",
        "attributes",
    )

    def __init__(
        self,
        name: str,
        subsystem: str = "api",
        request_id: Optional[str] = None,
    ) -> None:
        self.name = name
        self.subsystem = subsystem
        self.request_id = request_id
        self.started_at = time.perf_counter()
        self.ended_at: Optional[float] = None
        self.duration_ms: Optional[float] = None
        self.status: str = "ok"
        self.error: Optional[str] = None
        self.attributes: Dict[str, Any] = {}

    def finish(self, error: Optional[BaseException] = None) -> None:
        """Mark the span as finished and record its status."""
        if self.ended_at is not None:
            return
        self.ended_at = time.perf_counter()
        self.duration_ms = round((self.ended_at - self.started_at) * 1000.0, 3)
        if error is not None:
            self.status = "error"
            self.error = f"{error.__class__.__name__}: {error}"
        elif self.error:
            self.status = "error"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "subsystem": self.subsystem,
            "request_id": self.request_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "error": self.error,
            "attributes": dict(self.attributes),
        }


# --- Latency histogram (constant-memory) -----------------------------------
class _LatencyHistogram:
    """Bounded running histogram with a fixed bucket layout.

    Bucket boundaries are chosen so the cumulative output is useful
    for "is this endpoint slow?" without dragging in a stats library.
    """

    BOUNDARIES_MS: Tuple[float, ...] = (
        1.0,
        5.0,
        10.0,
        25.0,
        50.0,
        100.0,
        250.0,
        500.0,
        1000.0,
        2500.0,
        5000.0,
    )

    def __init__(self) -> None:
        self.count: int = 0
        self.sum_ms: float = 0.0
        self.buckets: Dict[float, int] = {b: 0 for b in self.BOUNDARIES_MS}
        self.overflow: int = 0

    def observe(self, value_ms: float) -> None:
        self.count += 1
        self.sum_ms += value_ms
        placed = False
        for b in self.BOUNDARIES_MS:
            if value_ms <= b:
                self.buckets[b] += 1
                placed = True
                break
        if not placed:
            self.overflow += 1

    def to_dict(self) -> Dict[str, Any]:
        if not self.count:
            return {
                "count": 0,
                "sum_ms": 0.0,
                "mean_ms": 0.0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
                "buckets": {str(b): 0 for b in self.BOUNDARIES_MS},
                "overflow": 0,
            }
        return {
            "count": self.count,
            "sum_ms": round(self.sum_ms, 3),
            "mean_ms": round(self.sum_ms / self.count, 3),
            "p50_ms": self._percentile(0.50),
            "p95_ms": self._percentile(0.95),
            "p99_ms": self._percentile(0.99),
            "buckets": {str(b): self.buckets[b] for b in self.BOUNDARIES_MS},
            "overflow": self.overflow,
        }

    def _percentile(self, q: float) -> float:
        # Approximate percentile from the bucket boundaries — good enough
        # for a smoke-test, not a replacement for a real histogram.
        target = max(1, int(round(self.count * q)))
        cumulative = 0
        for b in self.BOUNDARIES_MS:
            cumulative += self.buckets[b]
            if cumulative >= target:
                return float(b)
        return float(self.BOUNDARIES_MS[-1])


# --- Tracer ----------------------------------------------------------------
class Tracer:
    """Process-wide tracer + counter registry.

    The :class:`Tracer` exposes a :func:`span` context manager plus
    helper methods to record counters. State is held in plain dicts
    guarded by a lock so it is safe to use from multiple threads /
    asyncio tasks.
    """

    MAX_SPANS = 200

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._spans: Deque[Span] = deque(maxlen=self.MAX_SPANS)
        self._counters: Dict[Tuple[str, str], int] = defaultdict(int)
        self._histograms: Dict[Tuple[str, str], _LatencyHistogram] = defaultdict(_LatencyHistogram)
        self._errors: Dict[Tuple[str, str], int] = defaultdict(int)

    # --- spans ------------------------------------------------------------
    @contextmanager
    def span(
        self,
        name: str,
        subsystem: str = "api",
        request_id: Optional[str] = None,
        **attributes: Any,
    ) -> Iterator[Span]:
        """Time a block of code and record it as a span.

        The returned :class:`Span` can have attributes added before the
        block exits. Exceptions are captured into ``span.error`` and
        re-raised, so a failed call still produces a usable span.
        """
        s = Span(name=name, subsystem=subsystem, request_id=request_id)
        s.attributes.update(attributes)
        try:
            yield s
        except BaseException as exc:  # noqa: BLE001 - we re-raise
            s.finish(error=exc)
            self._record_span(s)
            with self._lock:
                self._errors[(subsystem, name)] += 1
            raise
        else:
            s.finish()
            self._record_span(s)

    def _record_span(self, span: Span) -> None:
        with self._lock:
            self._spans.append(span)
            key = (span.subsystem, span.name)
            self._counters[key] += 1
            if span.duration_ms is not None:
                self._histograms[key].observe(span.duration_ms)
            if span.status == "error":
                self._errors[key] += 1

    def recent_spans(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._spans)[-limit:]
        # Newest first for the dashboard.
        return [s.to_dict() for s in reversed(items)]

    # --- counters ---------------------------------------------------------
    def inc(self, subsystem: str, name: str, by: int = 1) -> None:
        with self._lock:
            self._counters[(subsystem, name)] += by

    def time(self, subsystem: str, name: str, duration_ms: float) -> None:
        with self._lock:
            self._histograms[(subsystem, name)].observe(duration_ms)

    def error(self, subsystem: str, name: str) -> None:
        with self._lock:
            self._errors[(subsystem, name)] += 1

    # --- snapshots --------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        """Return a JSON-safe summary of every metric collected so far."""
        with self._lock:
            metrics: Dict[str, Dict[str, Any]] = {}
            keys = set(self._counters) | set(self._histograms) | set(self._errors)
            for subsystem, name in sorted(keys):
                key = f"{subsystem}.{name}"
                metrics[key] = {
                    "subsystem": subsystem,
                    "name": name,
                    "count": self._counters.get((subsystem, name), 0),
                    "errors": self._errors.get((subsystem, name), 0),
                    "latency_ms": self._histograms.get(
                        (subsystem, name), _LatencyHistogram()
                    ).to_dict(),
                }
            return {
                "spans_total": sum(self._counters.values()),
                "errors_total": sum(self._errors.values()),
                "unique_metrics": len(metrics),
                "metrics": metrics,
            }


# --- Singleton -------------------------------------------------------------
_tracer: Optional[Tracer] = None
_tracer_lock = threading.Lock()


def get_tracer() -> Tracer:
    """Return the process-wide :class:`Tracer` (created on first use)."""
    global _tracer
    if _tracer is None:
        with _tracer_lock:
            if _tracer is None:
                _tracer = Tracer()
    return _tracer


def reset_tracer() -> None:  # pragma: no cover - test helper
    """Drop the singleton — used in tests so each test starts clean."""
    global _tracer
    with _tracer_lock:
        _tracer = None


# --- Self-test --------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover - manual smoke
    t = get_tracer()
    with t.span("do_work", subsystem="demo", request_id="r-1") as s:
        s.attributes["k"] = "v"
        time.sleep(0.005)
    try:
        with t.span("boom", subsystem="demo"):
            raise ValueError("nope")
    except ValueError:
        pass
    import json as _j
    print(_j.dumps(t.snapshot(), indent=2))
