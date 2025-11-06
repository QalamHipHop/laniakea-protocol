"""
LaniakeA Protocol - Intelligent Blockchain System
Version: 3.0.0

A revolutionary blockchain protocol combining AI, quantum-resistant security,
and cosmic consciousness for the next generation of decentralized applications.
"""

__version__ = '3.0.0'
__author__ = 'LaniakeA Team'
__license__ = 'MIT'

from laniakea.core.blockchain import LaniakeABlockchain, Block, Transaction # Now Hypercube implementations
from laniakea.intelligence.brain import CosmicBrainAI, Thought, EvolutionResult
from laniakea.utils.logger import setup_logger, get_logger
from laniakea.utils.config import load_config, save_config, get_config

__all__ = [
    'LaniakeABlockchain',
    'Block',
    'Transaction',
    'CosmicBrainAI',
    'Thought',
    'EvolutionResult',
    'setup_logger',
    'get_logger',
    'load_config',
    'save_config',
    'get_config',
]
