"""
LaniakeA Protocol - Configuration Management
Centralized configuration for the entire system
Version: 3.0.0
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class BlockchainConfig:
    """Blockchain-specific configuration"""
    difficulty: int = 4
    block_reward: float = 50.0
    block_time: int = 10  # seconds
    max_transactions_per_block: int = 100
    consensus: str = "PoHD"  # Proof of HyperDistance


@dataclass
class NetworkConfig:
    """Network configuration"""
    host: str = "0.0.0.0"
    port: int = 5000
    max_peers: int = 50
    peer_discovery_interval: int = 60
    heartbeat_interval: int = 30


@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", "default-secret-change-me"))
    encryption_key: str = field(default_factory=lambda: os.getenv("ENCRYPTION_KEY", "default-key-change-me"))
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds


@dataclass
class AIConfig:
    """AI and Intelligence configuration"""
    enabled: bool = True
    auto_optimize: bool = True
    learning_rate: float = 0.001
    model_update_interval: int = 300  # seconds


@dataclass
class StorageConfig:
    """Storage configuration"""
    data_dir: str = field(default_factory=lambda: os.getenv("DATA_DIR", "./data"))
    max_storage_size: int = 1024 * 1024 * 1024  # 1GB
    backup_enabled: bool = True
    backup_interval: int = 3600  # seconds


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE"))
    dev_mode: bool = field(default_factory=lambda: os.getenv("DEV_MODE", "false").lower() == "true")
    json_format: bool = False


@dataclass
class Config:
    """Main configuration class"""
    node_id: str = field(default_factory=lambda: os.getenv("NODE_ID", "laniakea-node"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    
    blockchain: BlockchainConfig = field(default_factory=BlockchainConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            return cls()
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return cls()
        
        # Create config instance
        config = cls()
        
        # Load blockchain config
        if 'blockchain' in data:
            bc_data = data['blockchain']
            config.blockchain = BlockchainConfig(
                difficulty=bc_data.get('difficulty', 4),
                block_reward=bc_data.get('block_reward', 50.0),
                block_time=bc_data.get('block_time', 10),
                max_transactions_per_block=bc_data.get('max_transactions_per_block', 100),
                consensus=bc_data.get('consensus', 'PoHD')
            )
        
        # Load network config
        if 'network' in data:
            net_data = data['network']
            config.network = NetworkConfig(
                host=net_data.get('host', '0.0.0.0'),
                port=net_data.get('port', 5000),
                max_peers=net_data.get('max_peers', 50),
                peer_discovery_interval=net_data.get('peer_discovery_interval', 60),
                heartbeat_interval=net_data.get('heartbeat_interval', 30)
            )
        
        # Load other configs...
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'node_id': self.node_id,
            'environment': self.environment,
            'blockchain': {
                'difficulty': self.blockchain.difficulty,
                'block_reward': self.blockchain.block_reward,
                'block_time': self.blockchain.block_time,
                'max_transactions_per_block': self.blockchain.max_transactions_per_block,
                'consensus': self.blockchain.consensus
            },
            'network': {
                'host': self.network.host,
                'port': self.network.port,
                'max_peers': self.network.max_peers
            },
            'ai': {
                'enabled': self.ai.enabled,
                'auto_optimize': self.ai.auto_optimize
            }
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    
    if _config is None:
        # Try to load from config.yaml
        config_path = Path("config.yaml")
        if config_path.exists():
            _config = Config.from_yaml(str(config_path))
        else:
            _config = Config()
    
    return _config


def set_config(config: Config):
    """Set global configuration instance"""
    global _config
    _config = config


# Example usage
if __name__ == '__main__':
    config = get_config()
    print("Configuration loaded:")
    print(f"  Node ID: {config.node_id}")
    print(f"  Environment: {config.environment}")
    print(f"  Blockchain Difficulty: {config.blockchain.difficulty}")
    print(f"  Network Port: {config.network.port}")
    print(f"  AI Enabled: {config.ai.enabled}")
