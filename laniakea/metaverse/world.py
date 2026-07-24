"""
LaniakeA Protocol - Metaverse World (re-export)
================================================

Re-exports the :class:`MetaverseWorld`, :class:`Entity`,
:class:`EntityType` and :class:`Vector3` primitives from
``src/metaverse/world.py`` so that the avatar / region / world layer
referenced by the README (\"Metaverse World + Entity + Avatar + Region\")
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

from src.metaverse.world import (  # noqa: E402
    Entity,
    EntityType,
    MetaverseWorld,
    Vector3,
    Region,
    Avatar,
    SocialSpace,
)

__all__ = [
    "Entity",
    "EntityType",
    "MetaverseWorld",
    "Vector3",
    "Region",
    "Avatar",
    "SocialSpace",
]
