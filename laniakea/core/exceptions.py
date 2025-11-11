"""
Custom exceptions for Laniakea Protocol

This module defines all custom exceptions used throughout the protocol
to provide better error handling and debugging capabilities.
"""

class LaniakeaException(Exception):
    """
    Base exception for all Laniakea Protocol errors
    
    All custom exceptions should inherit from this class to allow
    for centralized error handling and logging.
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
    - Invalid block
    - Chain validation failure
    - Mining errors
    """
    pass


class InvalidBlockError(BlockchainError):
    """Raised when a block is invalid"""
    pass


class ChainValidationError(BlockchainError):
    """Raised when blockchain validation fails"""
    pass


class MiningError(BlockchainError):
    """Raised when mining operation fails"""
    pass


class QuantumError(LaniakeaException):
    """
    Quantum computing simulation errors
    
    Raised when quantum operations fail, such as:
    - Invalid quantum circuit
    - Qubit limit exceeded
    - Quantum job execution failure
    """
    pass


class InvalidQuantumCircuitError(QuantumError):
    """Raised when quantum circuit is invalid"""
    pass


class QubitLimitExceededError(QuantumError):
    """Raised when qubit limit is exceeded"""
    pass


class CrossChainError(LaniakeaException):
    """
    Cross-chain bridge errors
    
    Raised when cross-chain operations fail, such as:
    - Unsupported chain
    - Transfer failure
    - Bridge validation error
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
    - LLM API failure
    - Problem generation error
    - Validation error
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
    - Invalid parameters
    - Missing required fields
    - Type mismatch
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
    - Insufficient energy
    - Invalid state transition
    - Tier progression error
    """
    pass


class InsufficientEnergyError(SCDAError):
    """Raised when SCDA has insufficient energy"""
    pass


class InvalidStateTransitionError(SCDAError):
    """Raised when SCDA state transition is invalid"""
    pass


class GovernanceError(LaniakeaException):
    """
    DAO Governance errors
    
    Raised when governance operations fail, such as:
    - Invalid proposal
    - Voting error
    - Quorum not met
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
    - Trading error
    - Listing error
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
    - Swap error
    - Liquidity error
    - Pool error
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
    
    Raised when configuration is invalid or missing
    """
    pass


class DatabaseError(LaniakeaException):
    """
    Database operation errors
    
    Raised when database operations fail
    """
    pass


class NetworkError(LaniakeaException):
    """
    Network communication errors
    
    Raised when network operations fail
    """
    pass


class AuthenticationError(LaniakeaException):
    """
    Authentication and authorization errors
    
    Raised when authentication or authorization fails
    """
    pass


class RateLimitError(LaniakeaException):
    """
    Rate limiting errors
    
    Raised when rate limit is exceeded
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
        Error code string
    """
    return ERROR_CODES.get(type(exception), "UNKNOWN_ERROR")
