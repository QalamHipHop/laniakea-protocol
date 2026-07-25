"""Chain registry - multi-chain RPC endpoint catalog.

Maintains a list of supported EVM-compatible chains with metadata used
by the SCDA cross-chain bridge and WalletLinkService. Inspired by
viem's `chain` definitions and WalletConnect's `caip` namespace
(``eip155:<chainId>``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ChainInfo:
    """Static metadata about a supported chain.

    Attributes:
        caip2: CAIP-2 chain identifier (e.g. ``"eip155:1"``).
        chain_id: EIP-155 numeric chain id.
        name: Human-readable chain name.
        short_name: Compact label.
        native_symbol: Native gas token symbol.
        rpc_env_var: Env var that overrides the default public RPC URL.
        default_rpc: Public RPC used when no env override is present.
        explorer: Block explorer base URL.
        is_testnet: True for non-mainnet networks.
    """

    caip2: str
    chain_id: int
    name: str
    short_name: str
    native_symbol: str
    default_rpc: str
    explorer: str
    is_testnet: bool = False
    rpc_env_var: str = ""

    def rpc_url(self) -> str:
        """Resolve the effective RPC URL using env override if set."""
        if self.rpc_env_var:
            override = os.getenv(self.rpc_env_var)
            if override:
                return override
        return self.default_rpc


SUPPORTED_CHAINS: List[ChainInfo] = [
    ChainInfo(
        caip2="eip155:1",
        chain_id=1,
        name="Ethereum Mainnet",
        short_name="eth",
        native_symbol="ETH",
        default_rpc="https://eth.llamarpc.com",
        explorer="https://etherscan.io",
        rpc_env_var="ETH_RPC_URL",
    ),
    ChainInfo(
        caip2="eip155:137",
        chain_id=137,
        name="Polygon PoS",
        short_name="polygon",
        native_symbol="MATIC",
        default_rpc="https://polygon-rpc.com",
        explorer="https://polygonscan.com",
        rpc_env_var="POLYGON_RPC_URL",
    ),
    ChainInfo(
        caip2="eip155:42161",
        chain_id=42161,
        name="Arbitrum One",
        short_name="arb",
        native_symbol="ETH",
        default_rpc="https://arb1.arbitrum.io/rpc",
        explorer="https://arbiscan.io",
        rpc_env_var="ARB_RPC_URL",
    ),
    ChainInfo(
        caip2="eip155:10",
        chain_id=10,
        name="Optimism",
        short_name="op",
        native_symbol="ETH",
        default_rpc="https://mainnet.optimism.io",
        explorer="https://optimistic.etherscan.io",
        rpc_env_var="OP_RPC_URL",
    ),
    ChainInfo(
        caip2="eip155:8453",
        chain_id=8453,
        name="Base",
        short_name="base",
        native_symbol="ETH",
        default_rpc="https://mainnet.base.org",
        explorer="https://basescan.org",
        rpc_env_var="BASE_RPC_URL",
    ),
    ChainInfo(
        caip2="eip155:11155111",
        chain_id=11155111,
        name="Sepolia Testnet",
        short_name="sepolia",
        native_symbol="ETH",
        default_rpc="https://rpc.sepolia.org",
        explorer="https://sepolia.etherscan.io",
        is_testnet=True,
        rpc_env_var="SEPOLIA_RPC_URL",
    ),
]


class ChainRegistry:
    """Thread-safe lookup of chain metadata + RPC resolution.

    Designed to be a singleton accessed via :py:meth:`get_registry`.
    The registry is intentionally read-only after construction - chain
    metadata is not mutated at runtime.
    """

    _instance: Optional["ChainRegistry"] = None

    def __init__(self, chains: Optional[List[ChainInfo]] = None) -> None:
        self._by_id: Dict[int, ChainInfo] = {}
        self._by_caip: Dict[str, ChainInfo] = {}
        for chain in chains or SUPPORTED_CHAINS:
            self._register(chain)

    def _register(self, chain: ChainInfo) -> None:
        if chain.chain_id in self._by_id:
            raise ValueError(f"duplicate chain_id: {chain.chain_id}")
        if chain.caip2 in self._by_caip:
            raise ValueError(f"duplicate caip2: {chain.caip2}")
        self._by_id[chain.chain_id] = chain
        self._by_caip[chain.caip2] = chain

    # -- lookups ----------------------------------------------------------
    def by_id(self, chain_id: int) -> ChainInfo:
        try:
            return self._by_id[chain_id]
        except KeyError as exc:
            raise KeyError(f"unsupported chain_id: {chain_id}") from exc

    def by_caip(self, caip2: str) -> ChainInfo:
        try:
            return self._by_caip[caip2]
        except KeyError as exc:
            raise KeyError(f"unsupported caip2 namespace: {caip2}") from exc

    def all(self) -> List[ChainInfo]:
        return list(self._by_id.values())

    def mainnets(self) -> List[ChainInfo]:
        return [c for c in self._by_id.values() if not c.is_testnet]

    def testnets(self) -> List[ChainInfo]:
        return [c for c in self._by_id.values() if c.is_testnet]

    # -- rpc resolution ---------------------------------------------------
    def rpc_for(self, chain_id: int) -> str:
        return self.by_id(chain_id).rpc_url()

    # -- singleton helper -------------------------------------------------
    @classmethod
    def instance(cls) -> "ChainRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Drop the cached singleton (test helper)."""
        cls._instance = None
