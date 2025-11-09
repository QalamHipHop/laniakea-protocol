"""
LaniakeA Protocol - 8-Dimensional Blockchain
Version: 0.0.01 (Master Rebuild)
Copyright © 2025 LaniakeA Protocol. All Rights Reserved.
"""

__version__ = "0.0.01"
__author__ = "LaniakeA Team"
__description__ = "Cosmic Computational Superprotocol - 8D Blockchain for Collective Intelligence"
__license__ = "MIT"
__tagline__ = "The Cosmic Evolution Engine"

from laniakea.core.hypercube_blockchain import (
    HypercubeBlockchain,
    HyperBlock,
    HyperTransaction,
    DIMENSIONS
)

from laniakea.utils.logger import setup_logger, get_logger
from laniakea.utils.config import get_config, Config

__all__ = [
    'HypercubeBlockchain',
    'HyperBlock',
    'HyperTransaction',
    'DIMENSIONS',
    'setup_logger',
    'get_logger',
    'get_config',
    'Config',
    '__version__',
]
