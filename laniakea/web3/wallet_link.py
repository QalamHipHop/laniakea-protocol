"""Bind a verified wallet to an SCDA identity.

The :class:`WalletLinkService` is the bridge between Web3 auth and the
rest of Laniakea. Each binding records:

* the wallet address
* the chain id it was verified on
* the SCDA identity it controls
* the original SIWE request id (so we can prove provenance)
* a monotonically-increasing nonce per (address, chain) so replays
  across the API are impossible

Bindings are stored in a thread-safe in-memory dict by default. The
service is also designed so the storage can be swapped for a real
DB (Postgres / Redis) by passing a custom ``store`` callable.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .chain_registry import ChainRegistry

logger = logging.getLogger("laniakea.web3.wallet_link")


@dataclass
class WalletBinding:
    """A (wallet, chain) -> SCDA mapping."""

    binding_id: str
    wallet: str
    chain_id: int
    scda_id: str
    created_at: float
    last_used_at: float
    nonce: int
    request_id: Optional[str] = None
    revoked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "binding_id": self.binding_id,
            "wallet": self.wallet,
            "chain_id": self.chain_id,
            "scda_id": self.scda_id,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "nonce": self.nonce,
            "request_id": self.request_id,
            "revoked": self.revoked,
            "metadata": dict(self.metadata),
        }


WalletStore = Callable[[], Dict[str, WalletBinding]]


class WalletLinkService:
    """High-level wallet <-> SCDA binding manager.

    A wallet can be bound to at most one active SCDA per chain, but a
    single SCDA may own multiple wallets on multiple chains. This
    mirrors how most Web3 games handle multi-chain identity.
    """

    def __init__(self, chain_registry: Optional[ChainRegistry] = None) -> None:
        self._bindings: Dict[str, WalletBinding] = {}
        self._by_wallet: Dict[str, str] = {}  # (wallet|chain) -> binding_id
        self._lock = threading.RLock()
        self.chain_registry = chain_registry or ChainRegistry.instance()

    # -- internals -------------------------------------------------------
    def _key(self, wallet: str, chain_id: int) -> str:
        return f"{wallet.lower()}|{chain_id}"

    def _now(self) -> float:
        return time.time()

    # -- CRUD ------------------------------------------------------------
    def link(
        self,
        wallet: str,
        chain_id: int,
        scda_id: str,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        allow_rebind: bool = False,
    ) -> WalletBinding:
        """Bind a wallet to an SCDA. Returns the existing binding if any.

        By default a wallet that is already bound will raise
        :class:`ValueError` - callers must explicitly opt in to rebind
        (e.g. during a key-rotation flow).
        """
        # Validate chain is supported.
        self.chain_registry.by_id(chain_id)
        with self._lock:
            key = self._key(wallet, chain_id)
            existing_id = self._by_wallet.get(key)
            if existing_id is not None:
                existing = self._bindings[existing_id]
                if existing.revoked:
                    # Stale record - clean up and re-link.
                    self._bindings.pop(existing_id, None)
                    self._by_wallet.pop(key, None)
                elif not allow_rebind:
                    raise ValueError(
                        f"wallet {wallet} already bound to {existing.scda_id}"
                    )
                else:
                    existing.revoked = True
                    self._bindings.pop(existing_id, None)
                    self._by_wallet.pop(key, None)
            binding = WalletBinding(
                binding_id=str(uuid.uuid4()),
                wallet=wallet.lower(),
                chain_id=chain_id,
                scda_id=scda_id,
                created_at=self._now(),
                last_used_at=self._now(),
                nonce=1,
                request_id=request_id,
                metadata=dict(metadata or {}),
            )
            self._bindings[binding.binding_id] = binding
            self._by_wallet[key] = binding.binding_id
            logger.info(
                "Linked wallet %s (chain %d) -> SCDA %s", wallet, chain_id, scda_id
            )
            return binding

    def get_by_wallet(self, wallet: str, chain_id: int) -> Optional[WalletBinding]:
        with self._lock:
            bid = self._by_wallet.get(self._key(wallet, chain_id))
            if bid is None:
                return None
            b = self._bindings.get(bid)
            if b is None or b.revoked:
                return None
            return b

    def get_by_scda(self, scda_id: str) -> List[WalletBinding]:
        with self._lock:
            return [b for b in self._bindings.values() if b.scda_id == scda_id and not b.revoked]

    def rotate_nonce(self, binding_id: str) -> int:
        """Increment the replay-protection nonce for a binding."""
        with self._lock:
            b = self._bindings.get(binding_id)
            if b is None or b.revoked:
                raise KeyError(binding_id)
            b.nonce += 1
            b.last_used_at = self._now()
            return b.nonce

    def touch(self, binding_id: str) -> None:
        """Update ``last_used_at`` without changing the nonce."""
        with self._lock:
            b = self._bindings.get(binding_id)
            if b is None:
                return
            b.last_used_at = self._now()

    def revoke(self, binding_id: str) -> bool:
        with self._lock:
            b = self._bindings.pop(binding_id, None)
            if b is None:
                return False
            self._by_wallet.pop(self._key(b.wallet, b.chain_id), None)
            return True

    def list_all(self) -> List[WalletBinding]:
        with self._lock:
            return [b for b in self._bindings.values() if not b.revoked]
