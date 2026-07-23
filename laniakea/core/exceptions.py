"""
Custom exceptions for Laniakea Protocol

This module defines all custom exceptions used throughout the protocol
to provide better error handling and debugging capabilities.

All exceptions inherit from LaniakeaException for centralized handling.
"""

class LaniakeaException(Exception):
    """
    Base exception for all Laniakea Protocol errors
    
    All custom exceptions should inherit from this class to allow
    for centralized error handling and logging.
    
    Attributes:
        message (str): Human-readable error message
        details (dict): Additional error context and details
    """
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class BlockchainError(LaniakeaException):
    """
    Blockchain-related errors
    
    Raised when blockchain operations fail, such as:
    - Invalid block structure or proof
    - Chain validation failure
    - Mining errors
    - Transaction validation errors
    
    Example:
        raise BlockchainError("Invalid block nonce", {"block_id": 42, "nonce": "abc"})
    """
    pass


class InvalidBlockError(BlockchainError):
    """Raised when a block is invalid or malformed"""
    pass


class ChainValidationError(BlockchainError):
    """Raised when blockchain validation fails (chain integrity check)"""
    pass


class MiningError(BlockchainError):
    """Raised when mining operation fails"""
    pass


class QuantumError(LaniakeaException):
    """
    Quantum computing simulation errors
    
    Raised when quantum operations fail, such as:
    - Invalid quantum circuit structure
    - Qubit limit exceeded
    - Quantum job execution failure
    - Gate application errors
    
    Example:
        raise QuantumError("Qubit limit exceeded", {"max": 5, "requested": 10})
    """
    pass


class InvalidQuantumCircuitError(QuantumError):
    """Raised when quantum circuit is invalid or malformed"""
    pass


class QubitLimitExceededError(QuantumError):
    """Raised when qubit limit is exceeded"""
    pass


class CrossChainError(LaniakeaException):
    """
    Cross-chain bridge errors
    
    Raised when cross-chain operations fail, such as:
    - Unsupported chain specification
    - Transfer failure or timeout
    - Bridge validation error
    - Asset mismatch
    
    Example:
        raise CrossChainError("Unsupported target chain", {"chain": "Polygon"})
    """
    pass


class UnsupportedChainError(CrossChainError):
    """Raised when attempting to bridge to unsupported chain"""
    pass


class TransferFailedError(CrossChainError):
    """Raised when cross-chain transfer fails"""
    pass


class AIError(LaniakeaException):
    """
    AI/LLM related errors
    
    Raised when AI operations fail, such as:
    - LLM API connection failure
    - Problem generation error
    - Solution validation error
    - Model inference failure
    
    Example:
        raise AIError("LLM API timeout", {"endpoint": "openai", "timeout": 30})
    """
    pass


class LLMAPIError(AIError):
    """Raised when LLM API call fails"""
    pass


class ProblemGenerationError(AIError):
    """Raised when hard problem generation fails"""
    pass


class ValidationError(LaniakeaException):
    """
    Data validation errors
    
    Raised when input validation fails, such as:
    - Invalid parameters or types
    - Missing required fields
    - Type mismatch
    - Value out of acceptable range
    
    Example:
        raise ValidationError("Amount must be positive", {"amount": -100})
    """
    pass


class InvalidParameterError(ValidationError):
    """Raised when parameter validation fails"""
    pass


class MissingFieldError(ValidationError):
    """Raised when required field is missing"""
    pass


class SCDAError(LaniakeaException):
    """
    SCDA (Single-Cell Digital Account) errors
    
    Raised when SCDA operations fail, such as:
    - Insufficient energy for operation
    - Invalid state transition
    - Tier progression error
    - Problem-solving failure
    
    Example:
        raise SCDAError("Insufficient energy", {"required": 100, "available": 50})
    """
    pass


class InsufficientEnergyError(SCDAError):
    """Raised when SCDA has insufficient energy for operation"""
    pass


class InvalidStateTransitionError(SCDAError):
    """Raised when SCDA state transition is invalid"""
    pass


class GovernanceError(LaniakeaException):
    """
    DAO Governance errors
    
    Raised when governance operations fail, such as:
    - Invalid proposal structure
    - Voting error or validation failure
    - Quorum not met
    - Voting period expired
    
    Example:
        raise GovernanceError("Quorum not met", {"required": 0.51, "current": 0.3})
    """
    pass


class InvalidProposalError(GovernanceError):
    """Raised when proposal is invalid"""
    pass


class VotingError(GovernanceError):
    """Raised when voting operation fails"""
    pass


class QuorumNotMetError(GovernanceError):
    """Raised when quorum is not met"""
    pass


class MarketplaceError(LaniakeaException):
    """
    Marketplace errors
    
    Raised when marketplace operations fail, such as:
    - NFT minting error
    - Trading/transaction error
    - Listing error
    - Price validation failure
    
    Example:
        raise MarketplaceError("NFT not found", {"token_id": "xyz"})
    """
    pass


class NFTMintingError(MarketplaceError):
    """Raised when NFT minting fails"""
    pass


class TradingError(MarketplaceError):
    """Raised when trading operation fails"""
    pass


class DeFiError(LaniakeaException):
    """
    DeFi operations errors
    
    Raised when DeFi operations fail, such as:
    - Swap execution error
    - Liquidity operation failure
    - Pool imbalance
    - Slippage exceeds tolerance
    
    Example:
        raise DeFiError("Insufficient liquidity", {"pool": "LANA/ETH", "amount": 1000})
    """
    pass


class SwapError(DeFiError):
    """Raised when token swap fails"""
    pass


class LiquidityError(DeFiError):
    """Raised when liquidity operation fails"""
    pass


class ConfigurationError(LaniakeaException):
    """
    Configuration errors
    
    Raised when configuration is invalid or missing:
    - Invalid environment variables
    - Missing required config
    - Config validation failure
    
    Example:
        raise ConfigurationError("DATABASE_URL not set")
    """
    pass


class DatabaseError(LaniakeaException):
    """
    Database operation errors
    
    Raised when database operations fail:
    - Connection failure
    - Query execution error
    - Data integrity violation
    
    Example:
        raise DatabaseError("Connection timeout", {"timeout": 30})
    """
    pass


class NetworkError(LaniakeaException):
    """
    Network communication errors
    
    Raised when network operations fail:
    - Connection refused/timeout
    - DNS resolution failure
    - Protocol error
    
    Example:
        raise NetworkError("Connection timeout", {"host": "example.com", "port": 8000})
    """
    pass


class AuthenticationError(LaniakeaException):
    """
    Authentication and authorization errors
    
    Raised when authentication or authorization fails:
    - Invalid credentials
    - Token expired
    - Insufficient permissions
    
    Example:
        raise AuthenticationError("Invalid API key", {"key": "***"})
    """
    pass


class RateLimitError(LaniakeaException):
    """
    Rate limiting errors
    
    Raised when rate limit is exceeded:
    - Too many requests
    - Request quota exceeded
    
    Example:
        raise RateLimitError("Rate limit exceeded", {"limit": 100, "window": 60})
    """
    pass


# Error code mapping for API responses
ERROR_CODES = {
    LaniakeaException: "LANIAKEA_ERROR",
    BlockchainError: "BLOCKCHAIN_ERROR",
    InvalidBlockError: "INVALID_BLOCK",
    ChainValidationError: "CHAIN_VALIDATION_FAILED",
    MiningError: "MINING_ERROR",
    QuantumError: "QUANTUM_ERROR",
    InvalidQuantumCircuitError: "INVALID_QUANTUM_CIRCUIT",
    QubitLimitExceededError: "QUBIT_LIMIT_EXCEEDED",
    CrossChainError: "CROSSCHAIN_ERROR",
    UnsupportedChainError: "UNSUPPORTED_CHAIN",
    TransferFailedError: "TRANSFER_FAILED",
    AIError: "AI_ERROR",
    LLMAPIError: "LLM_API_ERROR",
    ProblemGenerationError: "PROBLEM_GENERATION_ERROR",
    ValidationError: "VALIDATION_ERROR",
    InvalidParameterError: "INVALID_PARAMETER",
    MissingFieldError: "MISSING_FIELD",
    SCDAError: "SCDA_ERROR",
    InsufficientEnergyError: "INSUFFICIENT_ENERGY",
    InvalidStateTransitionError: "INVALID_STATE_TRANSITION",
    GovernanceError: "GOVERNANCE_ERROR",
    InvalidProposalError: "INVALID_PROPOSAL",
    VotingError: "VOTING_ERROR",
    QuorumNotMetError: "QUORUM_NOT_MET",
    MarketplaceError: "MARKETPLACE_ERROR",
    NFTMintingError: "NFT_MINTING_ERROR",
    TradingError: "TRADING_ERROR",
    DeFiError: "DEFI_ERROR",
    SwapError: "SWAP_ERROR",
    LiquidityError: "LIQUIDITY_ERROR",
    ConfigurationError: "CONFIGURATION_ERROR",
    DatabaseError: "DATABASE_ERROR",
    NetworkError: "NETWORK_ERROR",
    AuthenticationError: "AUTHENTICATION_ERROR",
    RateLimitError: "RATE_LIMIT_EXCEEDED",
}


def get_error_code(exception: Exception) -> str:
    """
    Get error code for an exception
    
    Args:
        exception: The exception instance
        
    Returns:
        Error code string for API response
        
    Example:
        >>> exc = InvalidBlockError("Bad nonce")
        >>> get_error_code(exc)
        'INVALID_BLOCK'
    """
    return ERROR_CODES.get(type(exception), "UNKNOWN_ERROR")
