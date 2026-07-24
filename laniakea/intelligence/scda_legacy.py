"""
LaniakeA Protocol - SCDA Legacy Re-export
==========================================

This module re-exports the legacy :class:`SingleCellDigitalAccount` from
``src/scda_legacy.py`` so that downstream code (and the README which
references the legacy class with constants ``alpha``, ``k1``, ``k2``,
``C(0)``, ``E(0)``) can import it from the canonical ``laniakea.*`` path
without having to know about the legacy ``src/`` directory.

The actual implementation lives in ``src/scda_legacy.py``; this file is
a thin re-export layer. Keeping the legacy class available is important
for:

* backward compatibility with existing API consumers and docs;
* preserving the original evolutionary constants (alpha=1.5, k1=10,
  k2=50, etc.) that the white-paper / scientific model relies on;
* providing a clean, minimal surface for educational / reference use
  distinct from the full DNA-aware ``scda_model.SingleCellDigitalAccount``.
"""

from __future__ import annotations

import os
import sys

# Make sure the repo root is on sys.path so that ``from src.scda_legacy
# import ...`` works regardless of how the interpreter is launched.
_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Re-export the legacy class.
from src.scda_legacy import (  # noqa: E402
    SingleCellDigitalAccount,
    generate_hard_problem,
    validate_solution,
)

# Constants are class-level attributes, not module-level. Expose them as
# module attributes too so the white-paper can refer to them as
# ``scda_legacy.EVOLUTIONARY_RESISTANCE_COEFFICIENT`` without breaking.
EVOLUTIONARY_RESISTANCE_COEFFICIENT = SingleCellDigitalAccount.EVOLUTIONARY_RESISTANCE_COEFFICIENT
INITIAL_COMPLEXITY = SingleCellDigitalAccount.INITIAL_COMPLEXITY
INITIAL_ENERGY = SingleCellDigitalAccount.INITIAL_ENERGY
ENERGY_CONSUMPTION_FACTOR = SingleCellDigitalAccount.ENERGY_CONSUMPTION_FACTOR
ENERGY_REPLENISHMENT_FACTOR = SingleCellDigitalAccount.ENERGY_REPLENISHMENT_FACTOR
PASSIVE_ENERGY_REPLENISHMENT = SingleCellDigitalAccount.PASSIVE_ENERGY_REPLENISHMENT

__all__ = [
    "SingleCellDigitalAccount",
    "generate_hard_problem",
    "validate_solution",
    "EVOLUTIONARY_RESISTANCE_COEFFICIENT",
    "INITIAL_COMPLEXITY",
    "INITIAL_ENERGY",
    "ENERGY_CONSUMPTION_FACTOR",
    "ENERGY_REPLENISHMENT_FACTOR",
    "PASSIVE_ENERGY_REPLENISHMENT",
]
