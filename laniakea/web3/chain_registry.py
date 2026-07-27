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


# Fallback RPC pool — used when the primary RPC fails (rate-limited,
# cloudflare-protected, geo-blocked, etc.). Ordered from most reliable
# to least. ``ChainRegistry.rpc_with_fallback`` walks this list.
FALLBACK_RPCS: Dict[str, List[str]] = {
    "eth": [
        "https://rpc.ankr.com/eth",
        "https://eth.llamarpc.com",
        "https://cloudflare-eth.com",
        "https://1rpc.io/eth",
    ],
    "polygon": [
        "https://rpc.ankr.com/polygon",
        "https://polygon.llamarpc.com",
        "https://polygon-bor-rpc.publicnode.com",
        "https://polygon-rpc.com",
    ],
    "arb": [
        "https://rpc.ankr.com/arbitrum",
        "https://arbitrum.llamarpc.com",
        "https://arbitrum-one-rpc.publicnode.com",
        "https://arb1.arbitrum.io/rpc",
    ],
    "op": [
        "https://mainnet.optimism.io",
        "https://rpc.ankr.com/optimism",
        "https://optimism.llamarpc.com",
        "https://optimism-rpc.publicnode.com",
    ],
    "base": [
        "https://mainnet.base.org",
        "https://rpc.ankr.com/base",
        "https://base.llamarpc.com",
        "https://base-rpc.publicnode.com",
    ],
    "bsc": [
        "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io",
        "https://bsc-dataseed1.ninicoin.io",
        "https://1rpc.io/bnb",
    ],
    "avax": [
        "https://api.avax.network/ext/bc/C/rpc",
        "https://avalanche.public-rpc.com",
        "https://rpc.ankr.com/avalanche",
    ],
    "ftm": [
        "https://rpc.ftm.tools",
        "https://fantom.publicnode.com",
        "https://rpc.ankr.com/fantom",
    ],
}


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

    def rpc_pool(self, chain_id: int) -> List[str]:
        """Return an ordered list of RPC endpoints to try, primary first.

        Combines the configured RPC (env override or default) with the
        global ``FALLBACK_RPCS`` pool for this chain's short name. Used
        by ``rpc_with_fallback`` and any caller that wants resilient
        on-chain reads.
        """
        info = self.by_id(chain_id)
        primary = info.rpc_url()
        pool = [primary]
        for url in FALLBACK_RPCS.get(info.short_name, []):
            if url and url != primary and url not in pool:
                pool.append(url)
        return pool

    def rpc_with_fallback(self, chain_id: int, body: bytes, timeout: float = 8.0) -> Dict[str, Any]:
        """POST ``body`` to the chain's RPC pool and return the first JSON
        response that does not carry an ``error`` field.

        Walks ``rpc_pool(chain_id)`` in order, falls back on any
        network/HTTP error, and returns ``{"error": "..."}`` if every
        endpoint is unreachable.
        """
        import json as _json
        import urllib.request as _ur
        import urllib.error as _ue

        last_err: Optional[str] = None
        for url in self.rpc_pool(chain_id):
            try:
                req = _ur.Request(
                    url,
                    data=body,
                    headers={"Content-Type": "application/json", "User-Agent": "laniakea-protocol/6.0"},
                )
                with _ur.urlopen(req, timeout=timeout) as resp:
                    data = _json.loads(resp.read().decode("utf-8"))
                if isinstance(data, dict) and "error" in data:
                    last_err = str(data["error"])
                    continue
                return data
            except Exception as exc:  # pragma: no cover - defensive
                last_err = f"{type(exc).__name__}: {exc}"
                continue
        return {"error": last_err or "all rpc endpoints failed", "chain_id": chain_id}

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
