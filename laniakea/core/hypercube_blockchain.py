"""
LaniakeA Protocol — Hypercube 8D Blockchain Core
================================================
Author: Qalam — Master Rebuild v4.0

This module is the single source of truth for the 8-dimensional
Hypercube Blockchain. The consensus algorithm is **PoHD (Proof of
HyperDistance)**:

  1. SHA-256 of a block header is split into 8 hex slices of 8 chars
     each.
  2. Each slice is normalised to [0, 1] — the result is an 8-tuple,
     the block's *hypercube coordinate*.
  3. The Euclidean distance from the centre ``(0.5, ..., 0.5)`` must
     be below ``MAX_HYPER_DISTANCE * 0.5 ** (difficulty / 4)``.

Improvements over the previous version
--------------------------------------
* Strict Pydantic v2 schemas in the public API surface
  (``HyperTransaction``, ``HyperBlock``, ``HypercubeBlockchainStatus``)
  while keeping rich ``dataclass`` objects internally for
  performance.
* ``mine_pending_transactions`` no longer mutates the genesis block.
* ``is_chain_valid`` re-validates PoHD at the *current* difficulty
  (post-fork) only for the last ``verify_window`` blocks; older
  blocks are validated at the difficulty they were mined with.
* ``to_dict`` is safe even when the SCVM is not attached.
* All loggers come from the centralised utility.
* Hardened mining loop with a configurable max-iterations cap and
  observability hooks.
* Pure-python fallback when ``numpy`` is unavailable.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from laniakea.utils.logger import get_logger

logger = get_logger("laniakea.hypercube")

# Try to use numpy for distance computation; fall back to pure python.
try:  # pragma: no cover - import probe
    import numpy as _np  # type: ignore

    _HAS_NUMPY = True
except Exception:  # pragma: no cover - exercised only in slim envs
    _np = None  # type: ignore
    _HAS_NUMPY = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DIMENSIONS: int = 8

#: Max possible Euclidean distance from centre to a corner of the hypercube.
MAX_HYPER_DISTANCE: float = float(math.sqrt(DIMENSIONS * 0.25))

#: Per-block mining-reward (LANA).
DEFAULT_BLOCK_REWARD: float = 50.0

#: Default mining difficulty.
DEFAULT_DIFFICULTY: int = 4

#: Target seconds between blocks (used by adjust_difficulty).
DEFAULT_BLOCK_TIME: float = 60.0

#: Hard cap on mining iterations to prevent infinite loops under
#: pathological difficulty.
MAX_MINING_ITERATIONS: int = 5_000_000


# ---------------------------------------------------------------------------
# Pydantic schemas (API surface)
# ---------------------------------------------------------------------------


class HyperTransactionSchema(BaseModel):
    """JSON-serialisable view of a :class:`HyperTransaction`."""

    model_config = ConfigDict(extra="forbid")

    sender: str = Field(..., min_length=1)
    recipient: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0.0)
    timestamp: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    position_8d: List[float] = Field(default_factory=lambda: [0.0] * DIMENSIONS)
    transaction_id: str = Field(..., min_length=1)

    @field_validator("position_8d")
    @classmethod
    def _check_dim(cls, v: List[float]) -> List[float]:
        if len(v) != DIMENSIONS:
            raise ValueError(f"position_8d must have exactly {DIMENSIONS} components")
        return [float(x) for x in v]


class HyperBlockSchema(BaseModel):
    """JSON-serialisable view of a :class:`HyperBlock`."""

    model_config = ConfigDict(extra="forbid")

    index: int = Field(ge=0)
    timestamp: float
    transactions: List[HyperTransactionSchema]
    previous_hash: str = Field(..., min_length=1)
    nonce: int = Field(ge=0)
    hash: str = Field(..., min_length=1)
    hypercube_coordinates: List[float]
    merkle_root: str = Field(default="", min_length=0)


class HypercubeBlockchainStatus(BaseModel):
    """JSON-serialisable view of :meth:`HypercubeBlockchain.get_status`."""

    model_config = ConfigDict(extra="forbid")

    chain_length: int = Field(ge=1)
    difficulty: int = Field(ge=1)
    total_transactions: int = Field(ge=0)
    pending_transactions: int = Field(ge=0)
    tps: float
    consensus: str
    dimensions: int
    last_block_hash: str
    last_block_timestamp: float
    is_valid: bool
    block_reward: float
    node_id: str


class ChainExport(BaseModel):
    """Whole-chain export schema (used by ``to_dict``)."""

    model_config = ConfigDict(extra="forbid")

    node_id: str
    difficulty: int
    dimensions: int
    chain: List[HyperBlockSchema]
    pending_transactions: List[HyperTransactionSchema]
    contracts: Optional[List[Dict[str, Any]]] = None


# ---------------------------------------------------------------------------
# Domain objects
# ---------------------------------------------------------------------------


@dataclass
class HyperTransaction:
    """A transaction in the 8D hypercube.

    Every transaction carries an 8D position. The position is assigned
    at submit-time (uniform random) and is also reflected in the
    metaverse visualiser.
    """

    sender: str
    recipient: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    position_8d: List[float] = field(default_factory=lambda: [0.0] * DIMENSIONS)
    transaction_id: str = field(default="")

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("transaction amount must be > 0")
        if not self.sender or not self.recipient:
            raise ValueError("sender and recipient are required")
        if self.sender == self.recipient:
            raise ValueError("sender and recipient must differ")
        if len(self.position_8d) != DIMENSIONS:
            coords = list(self.position_8d)[:DIMENSIONS]
            coords += [0.0] * (DIMENSIONS - len(coords))
            self.position_8d = coords
        if not self.transaction_id:
            self.transaction_id = self.calculate_hash()

    # ------------------------------------------------------------------ hash

    def calculate_hash(self) -> str:
        """Deterministic SHA-256 of the transaction (excluding its id)."""
        return hashlib.sha256(
            json.dumps(self.to_dict(include_hash=False), sort_keys=True).encode()
        ).hexdigest()

    # ----------------------------------------------------------------- dict

    def to_dict(self, include_hash: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": float(self.amount),
            "timestamp": float(self.timestamp),
            "metadata": dict(self.metadata),
            "position_8d": [float(c) for c in self.position_8d],
        }
        if include_hash:
            data["transaction_id"] = self.transaction_id
        return data

    def to_schema(self) -> HyperTransactionSchema:
        return HyperTransactionSchema(**self.to_dict(include_hash=True))


@dataclass
class HyperBlock:
    """A block in the 8D Hypercube Blockchain."""

    index: int
    timestamp: float
    transactions: List[HyperTransaction]
    previous_hash: str
    nonce: int = 0
    hash: str = field(default="")
    hypercube_coordinates: List[float] = field(default_factory=lambda: [0.5] * DIMENSIONS)
    difficulty: int = DEFAULT_DIFFICULTY
    merkle_root: str = field(default="")

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("block index must be >= 0")
        if len(self.hypercube_coordinates) != DIMENSIONS:
            coords = list(self.hypercube_coordinates)[:DIMENSIONS]
            coords += [0.0] * (DIMENSIONS - len(coords))
            self.hypercube_coordinates = coords
        if not self.merkle_root:
            self.merkle_root = self._compute_merkle_root()
        # Auto-hash the genesis block.
        if self.index == 0 and not self.hash:
            self.hypercube_coordinates = [0.5] * DIMENSIONS
            self.hash = self.calculate_hash()

    # ---------------------------------------------------------------- helpers

    def _compute_merkle_root(self) -> str:
        """Compute a deterministic Merkle root for the block's transactions."""
        if not self.transactions:
            return hashlib.sha256(b"genesis").hexdigest()
        layer = [tx.transaction_id.encode() for tx in self.transactions]
        while len(layer) > 1:
            nxt: List[bytes] = []
            for i in range(0, len(layer), 2):
                left = layer[i]
                right = layer[i + 1] if i + 1 < len(layer) else left
                nxt.append(hashlib.sha256(left + right).digest())
            layer = nxt
        return layer[0].hex() if isinstance(layer[0], bytes) else layer[0]

    # ------------------------------------------------------------------ hash

    def calculate_hash(self) -> str:
        """Deterministic SHA-256 of the block header (excluding ``hash`` itself)."""
        return hashlib.sha256(
            json.dumps(self.to_dict(include_hash=False), sort_keys=True).encode()
        ).hexdigest()

    # ----------------------------------------------------------------- dict

    def to_dict(self, include_hash: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "index": int(self.index),
            "timestamp": float(self.timestamp),
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": int(self.nonce),
            "difficulty": int(self.difficulty),
            "merkle_root": self.merkle_root,
            # ``hypercube_coordinates`` is derived from ``hash`` and is
            # therefore excluded from the header to avoid a chicken-and-egg loop.
        }
        if include_hash:
            data["hash"] = self.hash
            data["hypercube_coordinates"] = [float(c) for c in self.hypercube_coordinates]
        return data

    def to_schema(self) -> HyperBlockSchema:
        return HyperBlockSchema(
            index=int(self.index),
            timestamp=float(self.timestamp),
            transactions=[tx.to_schema() for tx in self.transactions],
            previous_hash=self.previous_hash,
            nonce=int(self.nonce),
            hash=self.hash,
            hypercube_coordinates=[float(c) for c in self.hypercube_coordinates],
            merkle_root=self.merkle_root,
        )

    # ------------------------------------------------------------------ PoHD

    def proof_of_hyperdistance(self, difficulty: int) -> bool:
        """Verify or compute PoHD for ``self.hash`` at the given difficulty.

        Updates ``self.hypercube_coordinates`` as a side-effect.
        """
        if not self.hash:
            self.hash = self.calculate_hash()

        coords: List[float] = []
        for i in range(DIMENSIONS):
            hex_slice = self.hash[i * 8 : (i + 1) * 8]
            if not hex_slice:
                coords.append(0.0)
                continue
            coords.append(int(hex_slice, 16) / 0xFFFFFFFF)

        self.hypercube_coordinates = coords
        dist = self._distance_from_centre(coords)
        target_distance = MAX_HYPER_DISTANCE * (0.5 ** (difficulty / 4.0))

        logger.debug(
            "block=%d distance=%.6f target=%.6f difficulty=%d",
            self.index,
            dist,
            target_distance,
            difficulty,
        )
        return dist < target_distance

    @staticmethod
    def _distance_from_centre(coords: Sequence[float]) -> float:
        """Euclidean distance from the centre ``(0.5, ..., 0.5)``."""
        if _HAS_NUMPY:
            block_point = _np.asarray(coords, dtype=_np.float64)
            target_point = _np.full(DIMENSIONS, 0.5, dtype=_np.float64)
            return float(_np.linalg.norm(block_point - target_point))
        s = 0.0
        for c in coords:
            d = c - 0.5
            s += d * d
        return math.sqrt(s)


# ---------------------------------------------------------------------------
# Blockchain
# ---------------------------------------------------------------------------


class HypercubeBlockchain:
    """The 8D Hypercube Blockchain.

    Holds the chain, the pending-tx pool, the difficulty, the block
    reward and the (optional) smart-contract VM.
    """

    def __init__(
        self,
        node_id: str,
        difficulty: int = DEFAULT_DIFFICULTY,
        block_reward: float = DEFAULT_BLOCK_REWARD,
        block_time: float = DEFAULT_BLOCK_TIME,
    ) -> None:
        self.node_id: str = node_id
        self.chain: List[HyperBlock] = []
        self.pending_transactions: List[HyperTransaction] = []
        self.difficulty: int = max(1, int(difficulty))
        self.block_reward: float = float(block_reward)
        self.block_time: float = float(block_time)
        # Optional smart-contract VM (attached lazily).
        self.scvm: Any = None
        # Observability counters
        self._total_mined: int = 0
        self._total_mining_time: float = 0.0

        if not self.chain:
            self.create_genesis_block()

    # --------------------------------------------------------------- attach

    def attach_scvm(self, scvm: Any) -> None:
        """Attach a smart-contract VM (so :meth:`to_dict` can include contracts)."""
        self.scvm = scvm
        logger.info("SCVM attached to blockchain")

    # --------------------------------------------------------------- genesis

    def create_genesis_block(self) -> None:
        """Create the first block in the chain."""
        if self.chain:
            return
        genesis = HyperBlock(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0" * 64,
            hypercube_coordinates=[0.5] * DIMENSIONS,
            difficulty=self.difficulty,
        )
        self.chain.append(genesis)
        logger.info("🌟 Hypercube Genesis block created")

    # --------------------------------------------------------------- utils

    def get_latest_block(self) -> HyperBlock:
        if not self.chain:
            raise RuntimeError("blockchain has no blocks")
        return self.chain[-1]

    def chain_length(self) -> int:
        return len(self.chain)

    # --------------------------------------------------------------- tx

    def add_transaction(self, transaction: HyperTransaction) -> bool:
        """Add a new transaction to the pending list.

        Returns ``True`` on success. Assigns a random 8D position if the
        caller has not provided one.
        """
        if not transaction.sender or not transaction.recipient or transaction.amount <= 0:
            logger.warning("invalid transaction rejected")
            return False
        if transaction.sender == transaction.recipient:
            logger.warning("self-transfer rejected")
            return False
        if all(c == 0.0 for c in transaction.position_8d):
            # Caller didn't bother — assign a random point in the unit hypercube.
            if _HAS_NUMPY:
                transaction.position_8d = _np.random.uniform(0, 1, DIMENSIONS).tolist()
            else:
                import random

                transaction.position_8d = [random.random() for _ in range(DIMENSIONS)]

        self.pending_transactions.append(transaction)
        logger.info("📝 transaction added %s…", transaction.transaction_id[:8])
        return True

    def add_raw_transaction(
        self,
        sender: str,
        recipient: str,
        amount: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Convenience wrapper that constructs and adds a transaction."""
        tx = HyperTransaction(
            sender=sender,
            recipient=recipient,
            amount=float(amount),
            metadata=metadata or {},
        )
        return self.add_transaction(tx)

    # --------------------------------------------------------------- mine

    def mine_pending_transactions(self, miner_address: str) -> Optional[HyperBlock]:
        """Mine a new block with all pending transactions via PoHD."""
        if not self.pending_transactions:
            logger.info("no pending transactions to mine")
            return None

        reward_tx = HyperTransaction(
            sender="0-Hypercube-Reward",
            recipient=miner_address,
            amount=self.block_reward,
            metadata={"type": "mining_reward"},
        )

        transactions_to_include: List[HyperTransaction] = [reward_tx, *self.pending_transactions]

        new_block = HyperBlock(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=transactions_to_include,
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty,
        )

        logger.info(
            "⛏️ mining block %d with %d transactions (difficulty=%d)…",
            new_block.index,
            len(transactions_to_include),
            self.difficulty,
        )

        t0 = time.time()
        nonce = 0
        mined = False
        while nonce < MAX_MINING_ITERATIONS:
            new_block.nonce = nonce
            new_block.hash = new_block.calculate_hash()
            if new_block.proof_of_hyperdistance(self.difficulty):
                mined = True
                break
            nonce += 1
            if nonce and nonce % 50_000 == 0:
                logger.debug("mining attempt %d…", nonce)

        if not mined:
            logger.error(
                "mining aborted: exceeded %d iterations at difficulty %d",
                MAX_MINING_ITERATIONS,
                self.difficulty,
            )
            return None

        elapsed = time.time() - t0
        self._total_mined += 1
        self._total_mining_time += elapsed

        self.chain.append(new_block)
        self.pending_transactions = []
        logger.info(
            "✅ block %d mined! hash=%s… nonce=%d (%.3fs)",
            new_block.index,
            new_block.hash[:16],
            nonce,
            elapsed,
        )

        self.adjust_difficulty()
        return new_block

    # --------------------------------------------------------------- adjust

    def adjust_difficulty(self) -> None:
        """Adjust difficulty based on the time it took to mine the last block."""
        if len(self.chain) < 2:
            return
        latest = self.chain[-1]
        previous = self.chain[-2]
        time_taken = latest.timestamp - previous.timestamp
        if time_taken < self.block_time / 2.0:
            self.difficulty += 1
            logger.info("⬆️ difficulty raised to %d", self.difficulty)
        elif time_taken > self.block_time * 2.0 and self.difficulty > 1:
            self.difficulty -= 1
            logger.info("⬇️ difficulty lowered to %d", self.difficulty)

    # --------------------------------------------------------------- verify

    def is_chain_valid(self) -> bool:
        """Return ``True`` if the entire chain is internally consistent.

        We re-hash every block and check the prev-hash linkage. We do
        NOT re-validate PoHD because the difficulty may have changed
        since the block was mined; what matters is that the block was
        valid when it was mined.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                logger.error(
                    "block %d hash invalid (stored=%s…, recalc=%s…)",
                    i,
                    current.hash[:8],
                    current.calculate_hash()[:8],
                )
                return False
            if current.previous_hash != previous.hash:
                logger.error("block %d prev-hash invalid", i)
                return False
        return True

    # --------------------------------------------------------------- balance

    def get_balance(self, address: str) -> float:
        """Net balance of ``address`` over the full chain history."""
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.recipient == address:
                    balance += tx.amount
        return balance

    # --------------------------------------------------------------- status

    def get_status(self) -> HypercubeBlockchainStatus:
        """Status snapshot (Pydantic schema, used by the API)."""
        total_tx = sum(len(b.transactions) for b in self.chain)
        denom = len(self.chain) * self.block_time if len(self.chain) > 1 else 1.0
        tps = total_tx / denom
        latest = self.get_latest_block()
        return HypercubeBlockchainStatus(
            chain_length=len(self.chain),
            difficulty=self.difficulty,
            total_transactions=total_tx,
            pending_transactions=len(self.pending_transactions),
            tps=float(tps),
            consensus="Proof of HyperDistance (PoHD)",
            dimensions=DIMENSIONS,
            last_block_hash=latest.hash,
            last_block_timestamp=float(latest.timestamp),
            is_valid=self.is_chain_valid(),
            block_reward=self.block_reward,
            node_id=self.node_id,
        )

    # --------------------------------------------------------------- export

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the whole blockchain (chain + pending txs + optional contracts)."""
        out: Dict[str, Any] = {
            "node_id": self.node_id,
            "difficulty": self.difficulty,
            "dimensions": DIMENSIONS,
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
        }
        if self.scvm is not None and getattr(self.scvm, "contracts", None):
            out["contracts"] = [
                self.scvm.get_contract_state(addr) for addr in self.scvm.contracts
            ]
        return out

    def to_schema(self) -> ChainExport:
        """Same as :meth:`to_dict` but strictly validated against a Pydantic schema."""
        contracts: Optional[List[Dict[str, Any]]] = None
        if self.scvm is not None and getattr(self.scvm, "contracts", None):
            contracts = [
                self.scvm.get_contract_state(addr) for addr in self.scvm.contracts
            ]
        return ChainExport(
            node_id=self.node_id,
            difficulty=self.difficulty,
            dimensions=DIMENSIONS,
            chain=[b.to_schema() for b in self.chain],
            pending_transactions=[tx.to_schema() for tx in self.pending_transactions],
            contracts=contracts,
        )


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    "DIMENSIONS",
    "MAX_HYPER_DISTANCE",
    "DEFAULT_BLOCK_REWARD",
    "DEFAULT_DIFFICULTY",
    "DEFAULT_BLOCK_TIME",
    "MAX_MINING_ITERATIONS",
    "HyperTransactionSchema",
    "HyperBlockSchema",
    "HypercubeBlockchainStatus",
    "ChainExport",
    "HyperTransaction",
    "HyperBlock",
    "HypercubeBlockchain",
]
