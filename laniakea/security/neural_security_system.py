"""
LaniakeA Protocol - Neural Security System (re-export)
======================================================

Re-exports the bio-inspired / neural-network security layer from
``src/security/neural_security_system.py`` through the canonical
``laniakea.*`` path.

The implementation models a 5-state immune system (Dormant -> Vigilant
-> Active -> Combat -> Quarantine) and uses an online anomaly detector
inspired by the brain's pattern-recognition circuits.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.security.neural_security_system import (  # noqa: E402
    SecurityLevel,
    ThreatType,
    SecurityPattern,
    ImmuneResponse,
    NeuralPatternRecognizer,
    QuantumSecureCommunicator,
    BiologicalImmunitySystem,
    NeuralSecuritySystem,
)

__all__ = [
    "SecurityLevel",
    "ThreatType",
    "SecurityPattern",
    "ImmuneResponse",
    "NeuralPatternRecognizer",
    "QuantumSecureCommunicator",
    "BiologicalImmunitySystem",
    "NeuralSecuritySystem",
]
