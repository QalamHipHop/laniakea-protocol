"""
LaniakeA Protocol - 8-Dimensional Blockchain
Version: 3.0.0
"""

__version__ = "3.0.0"
__author__ = "LaniakeA Team"
__description__ = "8-Dimensional Blockchain with AI Intelligence"

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
