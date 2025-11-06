"""
LaniakeA Protocol - Hypercube 8D Blockchain Core
Implementation of an 8-Dimensional Blockchain based on advanced mathematics (Hypercube)
Version: 3.0.0
"""

import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import logging
import numpy as np
from scipy.spatial import distance

# Use the existing logger setup
from laniakea.utils.logger import get_logger
from laniakea.utils.config import get_config

logger = get_logger('laniakea.hypercube')
config = get_config()

# 8-Dimensional Space (Hypercube)
DIMENSIONS = 8

@dataclass
class HyperTransaction:
    """Represents a transaction in the 8D space"""
    sender: str
    recipient: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    position_8d: List[float] = field(default_factory=lambda: [0.0] * DIMENSIONS)
    transaction_id: str = field(default='')

    def __post_init__(self):
        if not self.transaction_id:
            self.transaction_id = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculates the hash of the transaction"""
        transaction_string = json.dumps(self.to_dict(include_hash=False), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def to_dict(self, include_hash: bool = True) -> Dict[str, Any]:
        """Converts the transaction to a dictionary"""
        data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'position_8d': self.position_8d,
        }
        if include_hash:
            data['transaction_id'] = self.transaction_id
        return data

@dataclass
class HyperBlock:
    """Represents a block in the 8D Hypercube Blockchain"""
    index: int
    timestamp: float
    transactions: List[HyperTransaction]
    previous_hash: str
    nonce: int = 0
    hash: str = field(default='')
    hypercube_coordinates: List[float] = field(default_factory=lambda: [0.0] * DIMENSIONS)

    def __post_init__(self):
        # The hash is calculated during mining (mine_pending_transactions)
        # We only calculate the hash here for the Genesis block (index=0)
        if self.index == 0 and not self.hash:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculates the hash of the block"""
        block_string = json.dumps(self.to_dict(include_hash=False), sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self, include_hash: bool = True) -> Dict[str, Any]:
        """Converts the block to a dictionary"""
        data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            # 'hypercube_coordinates': self.hypercube_coordinates, # Exclude from hash calculation
        }
        if include_hash:
            data['hash'] = self.hash
        return data

    def proof_of_hyperdistance(self, difficulty: int) -> bool:
        """
        Proof of HyperDistance (PoHD) - The 8D consensus mechanism.
        The hash must be "close" to the target coordinate in the 8D space.
        We use the hash to generate a point in the 8D space and check its Euclidean distance.
        """
        # Convert hash to 8D point (simplified: use first 8 chunks of 8 hex chars)
        hash_int = int(self.hash, 16)
        hash_str = self.hash
        
        # Generate 8 coordinates between 0 and 1
        coords = []
        for i in range(DIMENSIONS):
            # Take a slice of the hash and normalize it
            slice_start = i * 8
            slice_end = (i + 1) * 8
            hex_slice = hash_str[slice_start:slice_end]
            
            if not hex_slice:
                # Fallback for short hashes (should not happen with sha256)
                coord = (hash_int >> (i * 32)) & 0xFFFFFFFF
            else:
                coord = int(hex_slice, 16)
            
            # Normalize to [0, 1]
            normalized_coord = coord / 0xFFFFFFFF
            coords.append(normalized_coord)
        
        self.hypercube_coordinates = coords
        
        # Target is the center of the hypercube (0.5, 0.5, ..., 0.5)
        target_point = np.array([0.5] * DIMENSIONS)
        block_point = np.array(coords)
        
        # Calculate Euclidean distance
        dist = distance.euclidean(block_point, target_point)
        
        # The required distance (target_distance) decreases with difficulty
        # Max distance in 8D hypercube is sqrt(8 * 0.5^2) = sqrt(2) approx 1.414
        max_dist = np.sqrt(DIMENSIONS * 0.25) # Max distance from center to corner
        
        # Target distance is max_dist / (difficulty * constant)
        # We want a smaller distance for higher difficulty
        # Let's use a simple inverse exponential decay for target distance
        target_distance = max_dist * (0.5 ** (difficulty / 4.0))
        
        logger.debug(f"Block {self.index}: Distance={dist:.6f}, Target={target_distance:.6f}, Difficulty={difficulty}")
        
        return dist < target_distance

class HypercubeBlockchain:
    """The 8D Hypercube Blockchain implementation"""
    
    def __init__(self, node_id: str, logger: Optional[logging.Logger] = None):
        self.node_id = node_id
        self.logger = logger or get_logger('laniakea.hypercube')
        self.chain: List[HyperBlock] = []
        self.pending_transactions: List[HyperTransaction] = []
        self.difficulty = config.blockchain.difficulty
        self.block_reward = config.blockchain.block_reward
        
        # Create the genesis block
        if not self.chain:
            self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the first block in the chain"""
        genesis_block = HyperBlock(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0" * 64,
            hypercube_coordinates=[0.5] * DIMENSIONS # Center of the hypercube
        )
        self.chain.append(genesis_block)
        self.logger.info("🌟 Hypercube Genesis block created")

    def get_latest_block(self) -> HyperBlock:
        """Returns the last block in the chain"""
        return self.chain[-1]

    def add_transaction(self, transaction: HyperTransaction) -> bool:
        """Adds a new transaction to the list of pending transactions"""
        if not transaction.sender or not transaction.recipient or transaction.amount <= 0:
            self.logger.warning("Invalid transaction attempted")
            return False
        
        # Assign a random 8D position to the transaction
        transaction.position_8d = [np.random.uniform(0, 1) for _ in range(DIMENSIONS)]
        
        self.pending_transactions.append(transaction)
        self.logger.info(f"📝 Transaction added: {transaction.transaction_id[:8]}...")
        return True

    def mine_pending_transactions(self, miner_address: str) -> Optional[HyperBlock]:
        """Mines a new block with all pending transactions"""
        if not self.pending_transactions:
            self.logger.info("No pending transactions to mine")
            return None

        # Add the mining reward transaction
        reward_tx = HyperTransaction(
            sender="0-Hypercube-Reward",
            recipient=miner_address,
            amount=self.block_reward,
            metadata={"type": "mining_reward"}
        )
        
        # Include reward tx and all pending transactions
        transactions_to_include = [reward_tx] + self.pending_transactions
        
        new_block = HyperBlock(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=transactions_to_include,
            previous_hash=self.get_latest_block().hash
        )

        self.logger.info(f"⛏️  Mining block {new_block.index} with {len(transactions_to_include)} transactions...")
        
        # Proof of HyperDistance (PoHD) mining
        nonce = 0
        while True:
            new_block.nonce = nonce
            new_block.hash = new_block.calculate_hash()
            
            if new_block.proof_of_hyperdistance(self.difficulty):
                break
            
            nonce += 1
            if nonce % 10000 == 0:
                self.logger.debug(f"Mining attempt {nonce}...")

        self.chain.append(new_block)
        self.pending_transactions = [] # Clear pending transactions
        self.logger.info(f"✅ Block {new_block.index} mined! Hash: {new_block.hash[:16]}... Nonce: {nonce}")
        
        # Adjust difficulty (simplified)
        self.adjust_difficulty()
        
        return new_block

    def adjust_difficulty(self):
        """Adjusts the difficulty based on mining time (simplified)"""
        if len(self.chain) < 2:
            return
        
        latest_block = self.get_latest_block()
        previous_block = self.chain[-2]
        
        time_taken = latest_block.timestamp - previous_block.timestamp
        target_time = config.blockchain.block_time
        
        if time_taken < target_time / 2:
            self.difficulty += 1
            self.logger.info(f"⬆️  Difficulty increased to {self.difficulty}")
        elif time_taken > target_time * 2 and self.difficulty > 1:
            self.difficulty -= 1
            self.logger.info(f"⬇️  Difficulty decreased to {self.difficulty}")

    def is_chain_valid(self) -> bool:
        """Checks if the blockchain is valid"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Check if block hash is correct
            # Recalculate hash to ensure it matches the stored hash
            recalculated_hash = current_block.calculate_hash()
            if current_block.hash != recalculated_hash:
                self.logger.error(f"Block {i} hash is invalid. Stored: {current_block.hash[:8]}... Recalculated: {recalculated_hash[:8]}...")
                return False

            # Check if previous hash is correct
            if current_block.previous_hash != previous_block.hash:
                self.logger.error(f"Block {i} previous hash is invalid")
                return False
            
            # Check Proof of HyperDistance
            if not current_block.proof_of_hyperdistance(self.difficulty):
                self.logger.error(f"Block {i} failed Proof of HyperDistance")
                return False

        return True

    def get_balance(self, address: str) -> float:
        """Calculates the balance of an address"""
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.recipient == address:
                    balance += tx.amount
        return balance

    def get_status(self) -> Dict[str, Any]:
        """Returns the status of the blockchain"""
        total_transactions = sum(len(block.transactions) for block in self.chain)
        
        # Calculate TPS (simplified: transactions per block time)
        tps = total_transactions / (len(self.chain) * config.blockchain.block_time) if len(self.chain) > 1 else 0.0
        
        return {
            "chain_length": len(self.chain),
            "difficulty": self.difficulty,
            "total_transactions": total_transactions,
            "pending_transactions": len(self.pending_transactions),
            "tps": tps,
            "consensus": "Proof of HyperDistance (PoHD)",
            "dimensions": DIMENSIONS
        }

    def to_dict(self) -> Dict[str, Any]:
        """Converts the entire blockchain to a dictionary"""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
            "difficulty": self.difficulty,
            "node_id": self.node_id
        }

# Update the main blockchain file to use the Hypercube implementation
# This will be done in the next step (Phase 3) to ensure all components use the new core
