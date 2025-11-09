# laniakea/core/config.py

import os

class Config:
    """Centralized configuration for the Laniakea Protocol."""
    
    # --- General Settings ---
    PROJECT_NAME: str = "Laniakea Protocol"
    PROJECT_VERSION: str = "1.0.0-Unified"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # --- Blockchain Settings ---
    MINING_DIFFICULTY: int = 4 # Number of leading zeros for PoW (if used)
    AUTHORITIES: list = ["Validator_A", "Validator_B", "Validator_C", "Manus_Core"]
    
    # --- Cross-Chain Settings ---
    SUPPORTED_CHAINS: list = ["Laniakea_Main", "Laniakea_Sidechain_1", "Ethereum_Sim", "Cosmos_Sim"]
    
    # --- Quantum Settings ---
    MAX_QUBITS: int = 5
    
    # --- Governance Settings ---
    TOTAL_TOKEN_SUPPLY: int = 1000000000
    REQUIRED_QUORUM: float = 0.51
    
    # --- Simulation Settings ---
    SIMULATION_TIME_STEP: float = 1000.0 # Time step in simulated seconds
    
    # --- Database Settings (Placeholder) ---
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./laniakea.db")
    
    # --- Deployment Settings ---
    DEPLOYMENT_ENV: str = os.getenv("DEPLOYMENT_ENV", "development")

settings = Config()
