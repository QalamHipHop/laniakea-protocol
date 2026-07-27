"""Laniakea Protocol - Web3 Integration Layer.

Provides wallet-based authentication (SIWE - Sign-In With Ethereum),
chain-agnostic signature verification, and on-chain proof-of-humanness
anchoring for SCDA identities.

Inspired by:
- EIP-4361 (Sign-In with Ethereum)
- EIP-1271 (isValidSignature for smart accounts)
- WalletConnect v2 sign-in flow
- Lens / Farcaster auth patterns
"""

from .siwe_auth import SiweAuthenticator, SiweMessage, NonceStore
from .signature import (
    SignatureVerifier,
    VerificationResult,
    SignatureType,
    verify_personal_sign,
    verify_eip1271,
)
from .chain_registry import ChainRegistry, ChainInfo, SUPPORTED_CHAINS, FALLBACK_RPCS
from .wallet_link import WalletLinkService, WalletBinding

__all__ = [
    "SiweAuthenticator",
    "SiweMessage",
    "NonceStore",
    "SignatureVerifier",
    "VerificationResult",
    "SignatureType",
    "verify_personal_sign",
    "verify_eip1271",
    "ChainRegistry",
    "ChainInfo",
    "SUPPORTED_CHAINS",
    "FALLBACK_RPCS",
    "WalletLinkService",
    "WalletBinding",
]
