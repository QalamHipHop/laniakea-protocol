"""LaniakeA Protocol - Unified Settings (pydantic-settings).

This module is the **single source of truth** for all configuration values
in the LaniakeA Protocol. It is built on top of :mod:`pydantic_settings`,
which means every field is:

* type-checked at import time,
* overridable via environment variables or a ``.env`` file,
* self-documenting via the JSON schema that Pydantic generates.

The legacy dataclass-based configuration in
:mod:`laniakea.utils.config` is preserved as a thin shim that delegates
to this module so older call-sites keep working.

Typical usage:

    >>> from laniakea.core.config import settings
    >>> settings.API_PORT
    8000
    >>> settings.TOTAL_TOKEN_SUPPLY
    1000000000

Author: LaniakeA Dev
"""

from __future__ import annotations

import os
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str, default: List[str]) -> List[str]:
    """Split a comma-separated env value into a clean list (skip blanks)."""
    if not value:
        return default
    out = [v.strip() for v in value.split(",") if v.strip()]
    return out or default


class LaniakeaSettings(BaseSettings):
    """Centralised settings for the entire LaniakeA Protocol.

    Every field can be overridden by an environment variable of the same
    name (case-insensitive). A ``.env`` file at the project root is also
    loaded automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- General ---
    PROJECT_NAME: str = "Laniakea Protocol"
    PROJECT_VERSION: str = "1.0.0-Unified"
    NODE_ID: str = "laniakea-node"
    DEPLOYMENT_ENV: str = "development"
    DEBUG: bool = False

    # --- API / Network ---
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # --- Blockchain ---
    MINING_DIFFICULTY: int = 4
    AUTHORITIES: List[str] = Field(
        default_factory=lambda: ["Validator_A", "Validator_B", "Validator_C", "Manus_Core"]
    )

    # --- Cross-chain ---
    SUPPORTED_CHAINS: List[str] = Field(
        default_factory=lambda: [
            "Laniakea_Main",
            "Laniakea_Sidechain_1",
            "Ethereum_Sim",
            "Cosmos_Sim",
        ]
    )

    # --- Quantum ---
    MAX_QUBITS: int = 5
    MIN_QUBITS: int = 1

    # --- Governance ---
    TOTAL_TOKEN_SUPPLY: int = 1_000_000_000
    REQUIRED_QUORUM: float = 0.51

    # --- Simulation ---
    SIMULATION_TIME_STEP: float = 1000.0

    # --- Token Economy ---
    TOKEN_SYMBOL: str = "LAN"
    TOKEN_NAME: str = "Laniakea"
    TOKEN_DECIMALS: int = 18
    TOKEN_INFLATION_RATE: float = 0.02
    TOKEN_BURN_RATE: float = 0.01
    STAKING_APY: float = 0.05

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./laniakea.db"

    # --- Security ---
    SECRET_KEY: str = "dev-key-change-in-production"
    ENABLE_HTTPS: bool = False

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/laniakea.log"

    # --- Rate limiting ---
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # --- AI / Cognitive (added for parity with utils/config.py) ---
    AI_ENABLED: bool = True
    AUTO_OPTIMIZE: bool = True
    COGNITIVE_MODEL: str = "gpt-4.1-mini"
    SIMULATION_ENABLED: bool = True
    SIMULATION_SPEED: float = 1.0
    OPENAI_API_KEY: Optional[str] = None

    # --- JWT (added for parity with security/auth.py) ---
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: Optional[str] = None
    HASH_ROUNDS: int = 12
    API_KEY_HEADER: str = "X-API-Key"
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"]
    )

    # --- Postgres convenience (parity with .env / docker-compose) ---
    POSTGRES_USER: str = "laniakea_user"
    POSTGRES_PASSWORD: str = "laniakea_password"
    POSTGRES_DB: str = "laniakea_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "laniakea"
    DB_USER: str = "laniakea"
    DB_PASSWORD: str = "laniakea123"
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "redis123"

    # --- Auth toggle (added for Step 5 of the roadmap) ---
    LANIAKEA_AUTH_ENABLED: bool = False

    # --- Observability ---
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None
    LANIAKEA_RUN_MIGRATIONS: bool = False

    # --- Validators ---------------------------------------------------------
    @field_validator("AUTHORITIES", mode="before")
    @classmethod
    def _split_authorities(cls, v):
        if isinstance(v, str):
            return _split_csv(v, ["Validator_A", "Validator_B", "Validator_C", "Manus_Core"])
        return v

    @field_validator("SUPPORTED_CHAINS", mode="before")
    @classmethod
    def _split_chains(cls, v):
        if isinstance(v, str):
            return _split_csv(
                v,
                ["Laniakea_Main", "Laniakea_Sidechain_1", "Ethereum_Sim", "Cosmos_Sim"],
            )
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            return _split_csv(v, ["*"])
        return v

    @field_validator("REQUIRED_QUORUM")
    @classmethod
    def _validate_quorum(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("REQUIRED_QUORUM must be in [0, 1]")
        return v

    @field_validator("SIMULATION_TIME_STEP")
    @classmethod
    def _validate_timestep(cls, v: float) -> float:
        if v <= 0:
            return 1000.0
        return v

    @field_validator("API_PORT")
    @classmethod
    def _validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            return 8000
        return v

    # --- Helpers ------------------------------------------------------------
    def to_public_dict(self) -> dict:
        """Return a dict safe to expose via /version or /core/status.

        Excludes any secret-bearing field (SECRET_KEY, OPENAI_API_KEY,
        ENCRYPTION_KEY, JWT_SECRET, POSTGRES_PASSWORD, DB_PASSWORD, etc.).
        """
        blacklist = {
            "SECRET_KEY",
            "OPENAI_API_KEY",
            "ENCRYPTION_KEY",
            "JWT_SECRET",
            "POSTGRES_PASSWORD",
            "DB_PASSWORD",
            "REDIS_PASSWORD",
        }
        return {
            k: (v if k not in blacklist else "***")
            for k, v in self.model_dump().items()
        }


# Singleton accessor --------------------------------------------------------
settings = LaniakeaSettings()


# Backwards compatibility alias --------------------------------------------
# Older code paths (and a couple of tests) import `Config` as a class.
# Expose the same name pointing to the new singleton so attribute access
# patterns like `Config.PROJECT_NAME` keep working.
class _ConfigCompat:
    """Proxy that delegates attribute access to :data:`settings`."""

    def __getattr__(self, name):
        return getattr(settings, name)

    def __setattr__(self, name, value):
        setattr(settings, name, value)


Config = _ConfigCompat()
