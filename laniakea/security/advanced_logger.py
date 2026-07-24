"""
LaniakeA Protocol - Advanced Logger & Audit Trail (re-export)
==============================================================

Re-exports the original audit / log subsystem from
``src/security/advanced_logger.py`` so the structured-event, encrypted
log, and audit-trail surface referenced by the README remains
accessible through the canonical ``laniakea.*`` path.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.security.advanced_logger import (  # noqa: E402
    AdvancedLogger,
    LogLevel,
    EventType,
    LogEntry,
    get_logger,
)

__all__ = [
    "AdvancedLogger",
    "LogLevel",
    "EventType",
    "LogEntry",
    "get_logger",
]
