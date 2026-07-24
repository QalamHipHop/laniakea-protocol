"""
LaniakeA Protocol - P2P Network Manager (re-export)
====================================================

Re-exports :class:`P2PManager` from ``src/network/p2p.py`` so the
peer-to-peer transport layer referenced by the README is reachable
through the canonical ``laniakea.*`` path.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.network.p2p import P2PManager  # noqa: E402

__all__ = ["P2PManager"]
