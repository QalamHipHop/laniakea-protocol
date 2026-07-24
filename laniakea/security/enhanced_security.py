"""
LaniakeA Protocol - Enhanced Security (re-export)
==================================================

Re-exports the SecurityLevel / ThreatLevel enums and the
:func:`get_security_manager` accessor from
``src/security/enhanced_security.py`` so the canonical ``laniakea.*``
import path keeps working.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.security.enhanced_security import (  # noqa: E402
    SecurityLevel,
    ThreatLevel,
    SecurityEvent,
    SecurityPolicy,
    EnhancedSecurityManager,
)

__all__ = [
    "SecurityLevel",
    "ThreatLevel",
    "SecurityEvent",
    "SecurityPolicy",
    "EnhancedSecurityManager",
]
