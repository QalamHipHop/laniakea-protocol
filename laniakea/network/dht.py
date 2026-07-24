"""
LaniakeA Protocol - Distributed Hash Table (Kademlia) re-export
================================================================

Re-exports the Kademlia-style DHT (DHTNode, KBucket, RoutingTable,
DistributedHashTable) from ``src/network/dht.py`` so the peer-discovery
layer referenced by the README remains accessible through the canonical
``laniakea.*`` path.
"""

from __future__ import annotations

import os
import sys

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.network.dht import (  # noqa: E402
    DHTNode,
    KBucket,
    RoutingTable,
    KademliaDHT,
    DHTStorage,
    ContentAddressableNetwork,
)

__all__ = [
    "DHTNode",
    "KBucket",
    "RoutingTable",
    "KademliaDHT",
    "DHTStorage",
    "ContentAddressableNetwork",
]
