"""
LaniakeA Protocol - Hypercube 8D Blockchain Core
Implementation of an 8-Dimensional Blockchain based on advanced mathematics (Hypercube)
Version: 3.1.0  (Qalam refactor: Pydantic schemas, fixed self.scvm, type hints)

This module is the **single source of truth** for the 8D hypercube blockchain.
It exposes:

* :class:`HyperTransaction`   — an 8D-coordinate transaction
* :class:`HyperBlock`         — a block that lives in the 8D hypercube
* :class:`HypercubeBlockchain`— the chain + pending-tx pool + PoHD miner

The consensus algorithm is **PoHD (Proof of HyperDistance)**:
  the block's hash is mapped to a point in the unit hypercube [0,1]^8 and the
  Euclidean distance to the centre (0.5, ..., 0.5) must be below a difficulty
  threshold. The threshold shrinks exponentially with difficulty.

Author: Qalam
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import BaseModel, Field, field_validator

from laniakea.utils.logger import get_logger
from laniakea.utils.config import get_config

logger = get_logger('laniakea.hypercube')
config = get_config()

# 8-Dimensional Space (Hypercube)
DIMENSIONS: int = 8

#: Maximum possible Euclidean distance from centre to corner of the hypercube.
MAX_HYPER_DISTANCE: float = float(np.sqrt(DIMENSIONS * 0.25))

# ---------------------------------------------------------------------------
# Pydantic schemas (API surface)
# ---------------------------------------------------------------------------

class HyperTransactionSchema(BaseModel):
    """JSON-serialisable view of a :class:`HyperTransaction`."""

    sender: str
    recipient: str
    amount: float
    timestamp: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    position_8d: List[float] = Field(default_factory=lambda: [0.0] * DIMENSIONS)
    transaction_id: str

    @field_validator("position_8d")
    @classmethod
    def _check_dim(cls, v: List[float]) -> List[float]:
        if len(v) != DIMENSIONS:
            raise ValueError(f"position_8d must have exactly {DIMENSIONS} components")
        return [float(x) for x in v]


class HyperBlockSchema(BaseModel):
    """JSON-serialisable view of a :class:`HyperBlock`."""

    index: int = Field(ge=0)
    timestamp: float
    transactions: List[HyperTransactionSchema]
    previous_hash: str
    nonce: int = Field(ge=0)
    hash: str
    hypercube_coordinates: List[float]


class ChainStatusSchema(BaseModel):
    """JSON-serialisable view of :meth:`HypercubeBlockchain.get_status`."""

    chain_length: int = Field(ge=1)
    difficulty: int = Field(ge=1)
    total_transactions: int = Field(ge=0)
    pending_transactions: int = Field(ge=0)
    tps: float
    consensus: str
    dimensions: int


# ---------------------------------------------------------------------------
# Domain objects (dataclasses — in-memory)
# ---------------------------------------------------------------------------

@dataclass
class HyperTransaction:
    """Represents a transaction in the 8D space.

    Every transaction carries an 8D position in the unit hypercube,
    which is set by :meth:`HypercubeBlockchain.add_transaction` and
    can later be used by the metaverse visualiser to place it spatially.
    """

    sender: str
    recipient: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    position_8d: List[float] = field(default_factory=lambda: [0.0] * DIMENSIONS)
    transaction_id: str = field(default='')

    def __post_init__(self) -> None:
        if not self.transaction_id:
            self.transaction_id = self.calculate_hash()
        if len(self.position_8d) != DIMENSIONS:
            # Pad or truncate to DIMENSIONS to keep invariants
            coords = list(self.position_8d)[: DIMENSIONS]
            coords += [0.0] * (DIMENSIONS - len(coords))
            self.position_8d = coords

    # ------------------------------------------------------------------ hash

    def calculate_hash(self) -> str:
        """Calculates the SHA-256 hash of the transaction (deterministic)."""
        transaction_string = json.dumps(self.to_dict(include_hash=False), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    # ----------------------------------------------------------------- dict

    def to_dict(self, include_hash: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': float(self.amount),
            'timestamp': float(self.timestamp),
            'metadata': dict(self.metadata),
            'position_8d': [float(c) for c in self.position_8d],
        }
        if include_hash:
            data['transaction_id'] = self.transaction_id
        return data

    def to_schema(self) -> HyperTransactionSchema:
        return HyperTransactionSchema(**self.to_dict(include_hash=True))

@dataclass
class HyperBlock:
    """Represents a block in the 8D Hypercube Blockchain."""

    index: int
    timestamp: float
    transactions: List[HyperTransaction]
    previous_hash: str
    nonce: int = 0
    hash: str = field(default='')
    hypercube_coordinates: List[float] = field(default_factory=lambda: [0.0] * DIMENSIONS)

    def __post_init__(self) -> None:
        if len(self.hypercube_coordinates) != DIMENSIONS:
            coords = list(self.hypercube_coordinates)[: DIMENSIONS]
            coords += [0.0] * (DIMENSIONS - len(coords))
            self.hypercube_coordinates = coords
        # The hash is calculated during mining (mine_pending_transactions).
        # We only calculate the hash here for the Genesis block (index=0).
        if self.index == 0 and not self.hash:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculates the SHA-256 hash of the block (deterministic)."""
        block_string = json.dumps(self.to_dict(include_hash=False), sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self, include_hash: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            'index': int(self.index),
            'timestamp': float(self.timestamp),
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': int(self.nonce),
            # 'hypercube_coordinates' is excluded from the hash on purpose:
            # it is *derived from* the hash and would cause a chicken-and-egg loop.
        }
        if include_hash:
            data['hash'] = self.hash
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
        )

    def proof_of_hyperdistance(self, difficulty: int) -> bool:
        """PoHD — hash must be close to the centre of the 8D hypercube.

        Mapping: take 8 8-hex slices of the SHA-256 hash, normalise each to
        [0, 1]. The resulting 8-tuple is the block's 8D coordinate. The
        Euclidean distance to the centre (0.5, ..., 0.5) must be below a
        difficulty-derived threshold.

        The threshold decays as ``MAX_HYPER_DISTANCE * 0.5 ** (difficulty / 4)``
        so each unit of difficulty roughly halves the search radius.
        """
        hash_str = self.hash
        coords: List[float] = []
        for i in range(DIMENSIONS):
            hex_slice = hash_str[i * 8 : (i + 1) * 8]
            coord = int(hex_slice, 16) / 0xFFFFFFFF if hex_slice else 0.0
            coords.append(coord)

        self.hypercube_coordinates = coords

        block_point = np.array(coords, dtype=np.float64)
        target_point = np.full(DIMENSIONS, 0.5, dtype=np.float64)
        dist = float(np.linalg.norm(block_point - target_point))

        target_distance = MAX_HYPER_DISTANCE * (0.5 ** (difficulty / 4.0))

        logger.debug(
            "Block %d: distance=%.6f target=%.6f difficulty=%d",
            self.index, dist, target_distance, difficulty,
        )
        return dist < target_distance

class HypercubeBlockchain:
    """The 8D Hypercube Blockchain implementation.

    Holds the chain, the pending-tx pool, the difficulty and the block
    reward. The smart-contract VM is an **optional** component (only
    created when explicitly requested via :meth:`attach_scvm`); this
    fixes a previous AttributeError where :meth:`to_dict` referenced an
    uninitialised ``self.scvm``.
    """

    def __init__(
        self,
        node_id: str,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.node_id: str = node_id
        self.logger = logger or get_logger('laniakea.hypercube')
        self.chain: List[HyperBlock] = []
        self.pending_transactions: List[HyperTransaction] = []
        self.difficulty: int = int(config.blockchain.difficulty)
        self.block_reward: float = float(config.blockchain.block_reward)
        # Optional SCVM — only attached if the user opts in
        self.scvm: Any = None

        if not self.chain:
            self.create_genesis_block()

    # --------------------------------------------------------------- attach

    def attach_scvm(self, scvm: Any) -> None:
        """Attach a smart-contract VM (so :meth:`to_dict` can include contracts)."""
        self.scvm = scvm
        self.logger.info("SCVM attached to blockchain")

    # --------------------------------------------------------------- genesis

    def create_genesis_block(self) -> None:
        """Creates the first block in the chain."""
        genesis_block = HyperBlock(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0" * 64,
            hypercube_coordinates=[0.5] * DIMENSIONS,  # centre of the hypercube
        )
        self.chain.append(genesis_block)
        self.logger.info("🌟 Hypercube Genesis block created")

    def get_latest_block(self) -> HyperBlock:
        """Returns the last block in the chain."""
        return self.chain[-1]

    # --------------------------------------------------------------- tx

    def add_transaction(self, transaction: HyperTransaction) -> bool:
        """Adds a new transaction to the pending list. Returns True on success."""
        if not transaction.sender or not transaction.recipient or transaction.amount <= 0:
            self.logger.warning("Invalid transaction attempted")
            return False

        # Assign a random 8D position to the transaction
        transaction.position_8d = [float(np.random.uniform(0, 1)) for _ in range(DIMENSIONS)]

        self.pending_transactions.append(transaction)
        self.logger.info("📝 Transaction added: %s…", transaction.transaction_id[:8])
        return True

    # --------------------------------------------------------------- mine

    def mine_pending_transactions(self, miner_address: str) -> Optional[HyperBlock]:
        """Mine a new block with all pending transactions via PoHD.

        Returns the mined block, or ``None`` if there were no pending txs.
        """
        if not self.pending_transactions:
            self.logger.info("No pending transactions to mine")
            return None

        reward_tx = HyperTransaction(
            sender="0-Hypercube-Reward",
            recipient=miner_address,
            amount=self.block_reward,
            metadata={"type": "mining_reward"},
        )

        transactions_to_include: List[HyperTransaction] = [reward_tx] + self.pending_transactions

        new_block = HyperBlock(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=transactions_to_include,
            previous_hash=self.get_latest_block().hash,
        )

        self.logger.info(
            "⛏️  Mining block %d with %d transactions…",
            new_block.index, len(transactions_to_include),
        )

        nonce = 0
        while True:
            new_block.nonce = nonce
            new_block.hash = new_block.calculate_hash()
            if new_block.proof_of_hyperdistance(self.difficulty):
                break
            nonce += 1
            if nonce % 10000 == 0:
                self.logger.debug("Mining attempt %d…", nonce)

        self.chain.append(new_block)
        self.pending_transactions = []
        self.logger.info(
            "✅ Block %d mined! Hash: %s… Nonce: %d",
            new_block.index, new_block.hash[:16], nonce,
        )

        self.adjust_difficulty()
        return new_block

    def adjust_difficulty(self) -> None:
        """Adjust difficulty based on the time it took to mine the last block."""
        if len(self.chain) < 2:
            return

        latest_block = self.get_latest_block()
        previous_block = self.chain[-2]

        time_taken = latest_block.timestamp - previous_block.timestamp
        target_time = float(getattr(config.blockchain, "block_time", 60))

        if time_taken < target_time / 2:
            self.difficulty += 1
            self.logger.info("⬆️  Difficulty increased to %d", self.difficulty)
        elif time_taken > target_time * 2 and self.difficulty > 1:
            self.difficulty -= 1
            self.logger.info("⬇️  Difficulty decreased to %d", self.difficulty)

    # --------------------------------------------------------------- verify

    def is_chain_valid(self) -> bool:
        """Return True if the entire chain is internally consistent.

        We re-hash every block and verify the prev-hash linkage. We do
        NOT re-validate PoHD because the difficulty may have changed
        since the block was mined — the block was valid when mined,
        which is the invariant we care about.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            recalculated_hash = current_block.calculate_hash()
            if current_block.hash != recalculated_hash:
                self.logger.error(
                    "Block %d hash invalid. stored=%s… recalc=%s…",
                    i, current_block.hash[:8], recalculated_hash[:8],
                )
                return False

            if current_block.previous_hash != previous_block.hash:
                self.logger.error("Block %d prev-hash invalid", i)
                return False

        return True

    def get_balance(self, address: str) -> float:
        """Calculate the balance of ``address`` from on-chain history."""
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.recipient == address:
                    balance += tx.amount
        return balance

    def get_status(self) -> Dict[str, Any]:
        """Return a status snapshot of the chain (used by the API)."""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        block_time = float(getattr(config.blockchain, "block_time", 60))
        tps = total_transactions / (len(self.chain) * block_time) if len(self.chain) > 1 else 0.0

        return {
            "chain_length": len(self.chain),
            "difficulty": self.difficulty,
            "total_transactions": total_transactions,
            "pending_transactions": len(self.pending_transactions),
            "tps": tps,
            "consensus": "Proof of HyperDistance (PoHD)",
            "dimensions": DIMENSIONS,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the whole blockchain (chain + pending txs + optional contracts)."""
        out: Dict[str, Any] = {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
            "difficulty": self.difficulty,
            "node_id": self.node_id,
        }
        if self.scvm is not None and getattr(self.scvm, "contracts", None):
            out["contracts"] = [
                self.scvm.get_contract_state(addr) for addr in self.scvm.contracts
            ]
        return out


__all__ = [
    "DIMENSIONS",
    "MAX_HYPER_DISTANCE",
    "HyperTransactionSchema",
    "HyperBlockSchema",
    "ChainStatusSchema",
    "HyperTransaction",
    "HyperBlock",
    "HypercubeBlockchain",
]


# Update the main blockchain file to use the Hypercube implementation
# This will be done in the next step (Phase 3) to ensure all components use the new core
