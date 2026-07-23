# laniakea/core/config.py

import os
from typing import List

class Config:
    """Centralized configuration for the Laniakea Protocol with validation."""
    
    # --- General Settings ---
    PROJECT_NAME: str = "Laniakea Protocol"
    PROJECT_VERSION: str = "1.0.0-Unified"
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # --- Blockchain Settings ---
    MINING_DIFFICULTY: int = int(os.getenv("MINING_DIFFICULTY", "4"))
    AUTHORITIES: List[str] = os.getenv("AUTHORITIES", "Validator_A,Validator_B,Validator_C,Manus_Core").split(",")
    
    # Validate authorities list is not empty
    if not AUTHORITIES or AUTHORITIES == ['']:
        AUTHORITIES = ["Validator_A", "Validator_B", "Validator_C", "Manus_Core"]
    
    # --- Cross-Chain Settings ---
    SUPPORTED_CHAINS: List[str] = os.getenv(
        "SUPPORTED_CHAINS", 
        "Laniakea_Main,Laniakea_Sidechain_1,Ethereum_Sim,Cosmos_Sim"
    ).split(",")
    
    # --- Quantum Settings ---
    MAX_QUBITS: int = int(os.getenv("MAX_QUBITS", "5"))
    MIN_QUBITS: int = 1
    
    # Validate qubit range
    if MAX_QUBITS < MIN_QUBITS:
        MAX_QUBITS = MIN_QUBITS
    
    # --- Governance Settings ---
    TOTAL_TOKEN_SUPPLY: int = int(os.getenv("TOTAL_TOKEN_SUPPLY", "1000000000"))
    REQUIRED_QUORUM: float = float(os.getenv("REQUIRED_QUORUM", "0.51"))
    
    # Validate quorum percentage [0, 1]
    if not (0 <= REQUIRED_QUORUM <= 1):
        REQUIRED_QUORUM = 0.51
    
    # --- Simulation Settings ---
    SIMULATION_TIME_STEP: float = float(os.getenv("SIMULATION_TIME_STEP", "1000.0"))
    
    # Validate time step is positive and reasonable
    if SIMULATION_TIME_STEP <= 0:
        SIMULATION_TIME_STEP = 1000.0
    
    # --- Database Settings ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./laniakea.db"
    )
    
    # --- Deployment Settings ---
    DEPLOYMENT_ENV: str = os.getenv("DEPLOYMENT_ENV", "development")
    
    # --- Security Settings ---
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    ENABLE_HTTPS: bool = os.getenv("ENABLE_HTTPS", "False").lower() == "true"
    
    # --- Logging Settings ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/laniakea.log")
    
    # --- Rate Limiting ---
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate all configuration values.
        
        Returns:
            bool: True if all configurations are valid
            
        Raises:
            ValueError: If any critical configuration is invalid
        """
        # Validate authorities
        if not cls.AUTHORITIES or len(cls.AUTHORITIES) == 0:
            raise ValueError("AUTHORITIES list cannot be empty")
        
        # Validate port
        if not (1 <= cls.API_PORT <= 65535):
            raise ValueError(f"API_PORT must be between 1 and 65535, got {cls.API_PORT}")
        
        # Validate quantum settings
        if cls.MAX_QUBITS < 1:
            raise ValueError(f"MAX_QUBITS must be at least 1, got {cls.MAX_QUBITS}")
        
        # Validate simulation time step
        if cls.SIMULATION_TIME_STEP <= 0:
            raise ValueError(f"SIMULATION_TIME_STEP must be positive, got {cls.SIMULATION_TIME_STEP}")
        
        # Validate token supply
        if cls.TOTAL_TOKEN_SUPPLY <= 0:
            raise ValueError(f"TOTAL_TOKEN_SUPPLY must be positive, got {cls.TOTAL_TOKEN_SUPPLY}")
        
        # Validate quorum
        if not (0 <= cls.REQUIRED_QUORUM <= 1):
            raise ValueError(f"REQUIRED_QUORUM must be between 0 and 1, got {cls.REQUIRED_QUORUM}")
        
        # Validate mining difficulty
        if cls.MINING_DIFFICULTY < 0:
            raise ValueError(f"MINING_DIFFICULTY cannot be negative, got {cls.MINING_DIFFICULTY}")
        
        return True
    
    @classmethod
    def to_dict(cls) -> dict:
        """
        Export configuration as dictionary.
        
        Returns:
            dict: Configuration as dictionary (excludes SECRET_KEY)
        """
        return {
            "PROJECT_NAME": cls.PROJECT_NAME,
            "PROJECT_VERSION": cls.PROJECT_VERSION,
            "API_HOST": cls.API_HOST,
            "API_PORT": cls.API_PORT,
            "AUTHORITIES": cls.AUTHORITIES,
            "SUPPORTED_CHAINS": cls.SUPPORTED_CHAINS,
            "MAX_QUBITS": cls.MAX_QUBITS,
            "TOTAL_TOKEN_SUPPLY": cls.TOTAL_TOKEN_SUPPLY,
            "REQUIRED_QUORUM": cls.REQUIRED_QUORUM,
            "SIMULATION_TIME_STEP": cls.SIMULATION_TIME_STEP,
            "DEPLOYMENT_ENV": cls.DEPLOYMENT_ENV,
            "DATABASE_URL": cls.DATABASE_URL,
            "LOG_LEVEL": cls.LOG_LEVEL,
        }

# Validate configuration on import
try:
    Config.validate()
    settings = Config()
except ValueError as e:
    print(f"Configuration Error: {e}")
    raise
