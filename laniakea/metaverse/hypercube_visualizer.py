"""
LaniakeA Protocol - 8D Hypercube Visualizer (re-export)
========================================================

Re-exports the original :class:`HypercubeVisualizer` from
``src/metaverse/hypercube_visualizer.py`` so the 8D->3D projection
(used by the Three.js visualizer in ``web/3d-visualization.html`` and
``web/metaverse_8d_visualization.html``) stays importable through the
canonical ``laniakea.*`` path.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.metaverse.hypercube_visualizer import HypercubeVisualizer  # noqa: E402

__all__ = ["HypercubeVisualizer"]
