"""
LaniakeA Protocol - 8D SCDA (Vector Form) Re-export
====================================================

The ``src/scda.py`` module is the 8-dimensional vector implementation
referenced by the README's block-equation section. It splits the 8D state
into a 4D Knowledge vector K(t) and a 4D Energy vector E(t) and applies
diminishing-returns decay / cost curves.

This wrapper re-exports the class from the canonical ``laniakea.*`` path
so the README contract (\"the 8D vector K(t).A = D(P).E\") stays consistent.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.scda import DIMENSIONS, SCDA  # noqa: E402

__all__ = ["DIMENSIONS", "SCDA"]
