"""
🌌 Laniakea Protocol - Unified Configuration v0.0.02
فایل پیکربندی یکپارچه و مدیریت تنظیمات

این فایل شامل تمام تنظیمات مورد نیاز برای سیستم‌های مختلف است:
- شبکه و ارتباطات
- بلاکچین و اجماع
- امنیت و رمزنگاری
- هوش مصنوعی و یادگیری
- بهینه‌سازی عملکرد
- مانیتورینگ و لاگینگ
"""

import os
import json
import yaml
from typing import Dict, List, Tuple, Set, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
from enum import Enum

# بارگذاری متغیرهای محیطی
load_dotenv()


class Environment(Enum):
    """محیط‌های اجرایی"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """سطوح لاگینگ"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class NetworkConfig:
    """تنظیمات شبکه"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    
    # CORS settings
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # WebSocket
    websocket_enabled: bool = True
    websocket_max_connections: int = 1000
    websocket_heartbeat_interval: int = 30


@dataclass
class BlockchainConfig:
    """تنظیمات بلاکچین"""
    # Network settings
    bootstrap_nodes: List[Tuple[str, int]] = field(default_factory=list)
    max_peers: int = 50
    min_peers: int = 5
    
    # Consensus
    block_time: int = 20  # seconds
    block_reward: float = 10.0
    difficulty_adjustment_period: int = 100  # blocks
    max_block_size: int = 1024 * 1024  # 1MB
    
    # Authority nodes
    authority_nodes: Set[str] = field(default_factory=set)
    is_authority: bool = False
    
    # Storage
    data_dir: str = "./data"
    max_chain_length: int = 10000000
    prune_old_blocks: bool = True
    block_pruning_limit: int = 100000
    
    # Value system
    value_dimensions: List[str] = field(default_factory=lambda: [
        "knowledge", "computation", "originality", 
        "consciousness", "environmental", "health"
    ])
    max_value_per_dimension: float = 10.0
    value_decay_rate: float = 0.01


@dataclass
class SecurityConfig:
    """تنظیمات امنیتی"""
    # Authentication
    jwt_secret_key: str = "your-secret-key-change-this"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # seconds
    mfa_enabled: bool = False
    
    # Encryption
    encryption_key: Optional[str] = None
    encryption_algorithm: str = "AES-256-GCM"
    quantum_resistant: bool = True
    
    # Neural security
    neural_security_enabled: bool = True
    neural_model_path: str = "./models/neural_security"
    threat_threshold: float = 0.7
    learning_rate: float = 0.001
    
    # Rate limiting
    ip_rate_limit: int = 1000  # requests per hour
    user_rate_limit: int = 100   # requests per hour
    
    # Firewall
    whitelist_ips: List[str] = field(default_factory=list)
    blacklist_ips: List[str] = field(default_factory=list)
    
    # Audit
    audit_enabled: bool = True
    audit_log_path: str = "./logs/audit.log"
    log_retention_days: int = 90


@dataclass
class AIConfig:
    """تنظیمات هوش مصنوعی"""
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7
    
    # Cosmic Brain
    cosmic_brain_enabled: bool = True
    brain_regions: List[str] = field(default_factory=lambda: [
        "neocortex", "limbic_system", "cerebellum",
        "hippocampus", "prefrontal_cortex", "amygdala"
    ])
    max_thoughts: int = 10000
    consciousness_level: float = 0.5
    
    # Neural networks
    neural_input_size: int = 64
    neural_hidden_size: int = 128
    neural_learning_rate: float = 0.001
    neural_batch_size: int = 32
    
    # Memory
    short_term_memory_limit: int = 100
    long_term_memory_limit: int = 10000
    memory_consolidation_threshold: int = 5
    
    # Creative mode
    creativity_enabled: bool = True
    dream_mode_enabled: bool = True
    inspiration_sources: List[str] = field(default_factory=lambda: [
        "quantum_patterns", "cosmic_background", "nebula_creativity"
    ])


@dataclass
class PerformanceConfig:
    """تنظیمات عملکرد"""
    # Optimization
    auto_optimize: bool = True
    optimization_interval: int = 60  # seconds
    target_efficiency: float = 0.85
    optimization_strategy: str = "balanced"  # energy, performance, quantum, evolutionary
    
    # Resources
    max_memory_usage: float = 0.8  # 80% of available memory
    max_cpu_usage: float = 0.8     # 80% of available CPU
    
    # Caching
    cache_enabled: bool = True
    cache_max_size: int = 10000
    cache_ttl: int = 3600  # seconds
    cache_learning_rate: float = 0.1
    
    # Threading
    thread_pool_size: int = 32
    process_pool_size: int = 4
    async_enabled: bool = True
    
    # Profiling
    profiling_enabled: bool = False
    profile_output_path: str = "./profiles"
    
    # Benchmarking
    benchmark_enabled: bool = True
    benchmark_interval: int = 3600  # seconds


@dataclass
class MonitoringConfig:
    """تنظیمات مانیتورینگ"""
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/laniakea.log"
    log_max_size: int = 100 * 1024 * 1024  # 100MB
    log_backup_count: int = 5
    structured_logging: bool = True
    
    # Metrics
    metrics_enabled: bool = True
    metrics_port: int = 9090
    metrics_path: str = "/metrics"
    
    # Health checks
    health_check_enabled: bool = True
    health_check_interval: int = 30  # seconds
    
    # Alerts
    alert_enabled: bool = True
    alert_webhook_url: Optional[str] = None
    alert_threshold_cpu: float = 0.9
    alert_threshold_memory: float = 0.9
    alert_threshold_disk: float = 0.9
    
    # Dashboard
    dashboard_enabled: bool = True
    dashboard_refresh_interval: int = 5  # seconds
    
    # External monitoring
    prometheus_enabled: bool = False
    grafana_enabled: bool = False
    datadog_enabled: bool = False


@dataclass
class QuantumConfig:
    """تنظیمات کوانتومی"""
    # Quantum system
    quantum_enabled: bool = True
    quantum_coherence: float = 0.8
    entanglement_strength: float = 0.9
    
    # Quantum algorithms
    grover_iterations: int = 100
    shor_qubits: int = 2048
    
    # Quantum cryptography
    post_quantum_enabled: bool = True
    kyber_key_size: int = 1024
    dilithium_signature_size: int = 2048
    
    # Quantum simulation
    simulation_enabled: bool = True
    simulator_type: str = "qiskit"  # qiskit, cirq, custom
    quantum_noise: float = 0.01
    
    # Quantum networking
    quantum_networking: bool = False
    quantum_key_distribution: bool = False


@dataclass
class CrossChainConfig:
    """تنظیمات跨链"""
    # Supported chains
    supported_chains: List[str] = field(default_factory=lambda: [
        "bitcoin", "ethereum", "polygon", "binance", "solana"
    ])
    
    # Bridge settings
    bridge_enabled: bool = True
    bridge_fee_rate: float = 0.001  # 0.1%
    min_bridge_amount: float = 0.01
    max_bridge_amount: float = 1000000.0
    
    # Liquidity
    liquidity_pools: Dict[str, float] = field(default_factory=dict)
    auto_rebalance: bool = True
    
    # Oracle
    oracle_enabled: bool = True
    oracle_update_interval: int = 60  # seconds
    price_sources: List[str] = field(default_factory=lambda: [
        "coingecko", "coinmarketcap", "binance"
    ])
    
    # Security
    bridge_security_level: str = "high"  # low, medium, high
    multi_sig_required: bool = True
    timelock_enabled: bool = True


@dataclass
class DatabaseConfig:
    """تنظیمات پایگاه داده"""
    # Primary database
    db_type: str = "sqlite"  # sqlite, postgresql, mysql
    db_path: str = "./data/laniakea.db"
    
    # PostgreSQL (if used)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "laniakea"
    postgres_user: str = "laniakea"
    postgres_password: str = ""
    
    # Connection settings
    max_connections: int = 20
    connection_timeout: int = 30
    connection_pool_size: int = 10
    
    # Caching
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Backup
    backup_enabled: bool = True
    backup_interval: int = 3600  # seconds
    backup_retention: int = 7  # days
    backup_path: str = "./backups"


class UnifiedConfig:
    """مدیریت یکپارچه تنظیمات"""
    
    def __init__(self, config_file: Optional[str] = None, environment: str = "production"):
        self.environment = Environment(environment)
        self.config_file = config_file or os.getenv("CONFIG_FILE", "./config.yaml")
        
        # Initialize configuration sections
        self.network = NetworkConfig()
        self.blockchain = BlockchainConfig()
        self.security = SecurityConfig()
        self.ai = AIConfig()
        self.performance = PerformanceConfig()
        self.monitoring = MonitoringConfig()
        self.quantum = QuantumConfig()
        self.crosschain = CrossChainConfig()
        self.database = DatabaseConfig()
        
        # Load configurations
        self._load_configurations()
        self._override_from_env()
        self._validate_configurations()
    
    def _load_configurations(self):
        """بارگذاری تنظیمات از فایل"""
        if not Path(self.config_file).exists():
            self._create_default_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # Update configuration sections
            if 'network' in config_data:
                self._update_dataclass(self.network, config_data['network'])
            
            if 'blockchain' in config_data:
                self._update_dataclass(self.blockchain, config_data['blockchain'])
            
            if 'security' in config_data:
                self._update_dataclass(self.security, config_data['security'])
            
            if 'ai' in config_data:
                self._update_dataclass(self.ai, config_data['ai'])
            
            if 'performance' in config_data:
                self._update_dataclass(self.performance, config_data['performance'])
            
            if 'monitoring' in config_data:
                self._update_dataclass(self.monitoring, config_data['monitoring'])
            
            if 'quantum' in config_data:
                self._update_dataclass(self.quantum, config_data['quantum'])
            
            if 'crosschain' in config_data:
                self._update_dataclass(self.crosschain, config_data['crosschain'])
            
            if 'database' in config_data:
                self._update_dataclass(self.database, config_data['database'])
                
        except Exception as e:
            print(f"Error loading config file: {e}")
            print("Using default configurations")
    
    def _update_dataclass(self, dataclass_instance, config_dict):
        """به‌روزرسانی dataclass با دیکشنری"""
        for key, value in config_dict.items():
            if hasattr(dataclass_instance, key):
                setattr(dataclass_instance, key, value)
    
    def _override_from_env(self):
        """بازنویسی تنظیمات با متغیرهای محیطی"""
        # Network
        if os.getenv("HOST"):
            self.network.host = os.getenv("HOST")
        if os.getenv("PORT"):
            self.network.port = int(os.getenv("PORT"))
        
        # Blockchain
        if os.getenv("BLOCK_TIME"):
            self.blockchain.block_time = int(os.getenv("BLOCK_TIME"))
        if os.getenv("BLOCK_REWARD"):
            self.blockchain.block_reward = float(os.getenv("BLOCK_REWARD"))
        
        # Security
        if os.getenv("JWT_SECRET_KEY"):
            self.security.jwt_secret_key = os.getenv("JWT_SECRET_KEY")
        if os.getenv("ENCRYPTION_KEY"):
            self.security.encryption_key = os.getenv("ENCRYPTION_KEY")
        
        # AI
        if os.getenv("OPENAI_API_KEY"):
            self.ai.openai_api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_MODEL"):
            self.ai.openai_model = os.getenv("OPENAI_MODEL")
        
        # Database
        if os.getenv("DATABASE_URL"):
            self.database.db_path = os.getenv("DATABASE_URL")
        if os.getenv("REDIS_URL"):
            redis_url = os.getenv("REDIS_URL")
            # Parse redis_url and update redis config
            if "redis://" in redis_url:
                self.database.redis_enabled = True
        
        # Environment-specific settings
        if self.environment == Environment.DEVELOPMENT:
            self.monitoring.log_level = "DEBUG"
            self.network.reload = True
            self.monitoring.profiling_enabled = True
        elif self.environment == Environment.PRODUCTION:
            self.monitoring.log_level = "INFO"
            self.network.reload = False
            self.security.neural_security_enabled = True
            self.performance.auto_optimize = True
    
    def _validate_configurations(self):
        """اعتبارسنجی تنظیمات"""
        errors = []
        
        # Network validation
        if not (1 <= self.network.port <= 65535):
            errors.append("Network port must be between 1 and 65535")
        
        # Security validation
        if not self.security.jwt_secret_key or self.security.jwt_secret_key == "your-secret-key-change-this":
            errors.append("JWT secret key must be set in production")
        
        # AI validation
        if self.ai.cosmic_brain_enabled and not self.ai.openai_api_key:
            errors.append("OpenAI API key required for cosmic brain AI")
        
        # Database validation
        if self.database.db_type == "postgresql" and not self.database.postgres_password:
            errors.append("PostgreSQL password required")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(errors)
            if self.environment == Environment.PRODUCTION:
                raise ValueError(error_msg)
            else:
                print(f"Warning: {error_msg}")
    
    def _create_default_config(self):
        """ایجاد فایل کانفیگ پیش‌فرض"""
        default_config = {
            "network": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 1,
                "cors_origins": ["*"],
                "rate_limit_enabled": True
            },
            "blockchain": {
                "block_time": 20,
                "block_reward": 10.0,
                "data_dir": "./data"
            },
            "security": {
                "neural_security_enabled": True,
                "quantum_resistant": True,
                "audit_enabled": True
            },
            "ai": {
                "cosmic_brain_enabled": True,
                "openai_model": "gpt-4",
                "creativity_enabled": True
            },
            "performance": {
                "auto_optimize": True,
                "target_efficiency": 0.85,
                "cache_enabled": True
            },
            "monitoring": {
                "log_level": "INFO",
                "metrics_enabled": True,
                "dashboard_enabled": True
            },
            "quantum": {
                "quantum_enabled": True,
                "post_quantum_enabled": True
            },
            "crosschain": {
                "bridge_enabled": True,
                "supported_chains": ["bitcoin", "ethereum", "polygon"]
            },
            "database": {
                "db_type": "sqlite",
                "db_path": "./data/laniakea.db",
                "backup_enabled": True
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            print(f"Default configuration created at {self.config_file}")
        except Exception as e:
            print(f"Error creating default config: {e}")
    
    def save_config(self):
        """ذخیره تنظیمات فعلی"""
        config_data = {
            "network": self.network.__dict__,
            "blockchain": self.blockchain.__dict__,
            "security": self.security.__dict__,
            "ai": self.ai.__dict__,
            "performance": self.performance.__dict__,
            "monitoring": self.monitoring.__dict__,
            "quantum": self.quantum.__dict__,
            "crosschain": self.crosschain.__dict__,
            "database": self.database.__dict__
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_config_dict(self) -> Dict[str, Any]:
        """دریافت تمام تنظیمات به صورت دیکشنری"""
        return {
            "environment": self.environment.value,
            "network": self.network.__dict__,
            "blockchain": self.blockchain.__dict__,
            "security": self.security.__dict__,
            "ai": self.ai.__dict__,
            "performance": self.performance.__dict__,
            "monitoring": self.monitoring.__dict__,
            "quantum": self.quantum.__dict__,
            "crosschain": self.crosschain.__dict__,
            "database": self.database.__dict__
        }
    
    def get_bootstrap_nodes(self) -> List[Tuple[str, int]]:
        """دریافت نودهای bootstrap"""
        nodes = []
        
        # From environment variable
        env_nodes = os.getenv("BOOTSTRAP_NODES", "")
        if env_nodes:
            for node_str in env_nodes.split(","):
                try:
                    host, port_str = node_str.strip().split(":")
                    nodes.append((host, int(port_str)))
                except (ValueError, IndexError):
                    pass
        
        # Add default nodes if none specified
        if not nodes:
            nodes = [
                ("laniakea-seed1.protocol.org", 8000),
                ("laniakea-seed2.protocol.org", 8000),
                ("laniakea-seed3.protocol.org", 8000)
            ]
        
        return nodes
    
    def is_authority(self, node_id: str) -> bool:
        """بررسی اینکه آیا نود authority است"""
        # From environment
        if os.getenv("IS_AUTHORITY", "false").lower() == "true":
            return True
        
        # From config
        if node_id in self.blockchain.authority_nodes:
            return True
        
        return False
    
    def update_from_dict(self, updates: Dict[str, Any]):
        """به‌روزرسانی تنظیمات از دیکشنری"""
        for section_name, section_updates in updates.items():
            if hasattr(self, section_name):
                section = getattr(self, section_name)
                if hasattr(section, '__dict__'):
                    for key, value in section_updates.items():
                        if hasattr(section, key):
                            setattr(section, key, value)


# Global configuration instance
CONFIG = UnifiedConfig()


def get_config() -> UnifiedConfig:
    """دریافت instance سراسری تنظیمات"""
    return CONFIG


def reload_config(config_file: Optional[str] = None):
    """بارگذاری مجدد تنظیمات"""
    global CONFIG
    CONFIG = UnifiedConfig(config_file or CONFIG.config_file)
    return CONFIG


# Legacy compatibility functions
def get_bootstrap_nodes() -> List[Tuple[str, int]]:
    """نودهای bootstrap برای سازگاری با کد قدیمی"""
    return CONFIG.get_bootstrap_nodes()


def is_authority(node_id: str) -> bool:
    """بررسی authority برای سازگاری با کد قدیمی"""
    return CONFIG.is_authority(node_id)


# Export configuration constants
HOST = CONFIG.network.host
PORT = CONFIG.network.port
BLOCK_TIME = CONFIG.blockchain.block_time
BLOCK_REWARD = CONFIG.blockchain.block_reward
AUTHORITY_NODES = CONFIG.blockchain.authority_nodes