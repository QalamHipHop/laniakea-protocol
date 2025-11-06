"""
LaniakeA Protocol - Unified Blockchain Core
Integrated blockchain system with POV consensus and intelligent features
Version: 3.0.0
"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import logging
from laniakea.core.hypercube_blockchain import HypercubeBlockchain, HyperBlock, HyperTransaction

# The original LaniakeABlockchain class is now deprecated in favor of the 8D Hypercube implementation.
# The main entry point will now use HypercubeBlockchain
LaniakeABlockchain = HypercubeBlockchain
Block = HyperBlock
Transaction = HyperTransaction
