"""
Metaverse Integration Module
Integrates SCDA with the 8D Hypercube Blockchain.
Manages SCDA positions, transactions, and state synchronization in the Metaverse.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# 8D Hypercube Constants
DIMENSIONS = 8
HYPERCUBE_CENTER = [0.5] * DIMENSIONS


@dataclass
class MetaverseTransaction:
    """Represents a transaction in the Metaverse."""
    scda_id: str
    transaction_type: str  # "problem_solved", "levelup", "collaboration", etc.
    timestamp: str
    position_8d: List[float]
    data: Dict[str, Any]
    transaction_id: str = ""


class MetaverseIntegration:
    """
    Manages the integration of SCDAs with the 8D Hypercube Blockchain.
    Tracks SCDA positions, movements, and interactions in the Metaverse.
    """
    
    def __init__(self):
        """Initialize the Metaverse Integration."""
        self.scda_positions: Dict[str, List[float]] = {}  # scda_id -> position_8d
        self.scda_metadata: Dict[str, Dict[str, Any]] = {}  # scda_id -> metadata
        self.metaverse_transactions: List[MetaverseTransaction] = []
        self.collaboration_groups: Dict[str, List[str]] = {}  # group_id -> [scda_ids]
        
        logger.info("Metaverse Integration initialized")
    
    def register_scda(self, scda_id: str, position_8d: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Register an SCDA in the Metaverse.
        Assigns a position in the 8D Hypercube if not provided.
        """
        if position_8d is None:
            # Random position in the hypercube
            position_8d = np.random.uniform(0, 1, DIMENSIONS).tolist()
        
        self.scda_positions[scda_id] = position_8d
        self.scda_metadata[scda_id] = {
            "registered_at": datetime.now().isoformat(),
            "tier": 1,
            "complexity_index": 1.0,
            "energy": 100.0,
            "problems_solved": 0,
            "position_8d": position_8d
        }
        
        logger.info(f"SCDA {scda_id} registered in Metaverse at position {position_8d}")
        
        return {
            "scda_id": scda_id,
            "position_8d": position_8d,
            "message": "SCDA successfully registered in the Metaverse"
        }
    
    def update_scda_position(self, scda_id: str, position_shift: List[float]) -> Dict[str, Any]:
        """
        Update an SCDA's position in the 8D Hypercube.
        Applies a position shift (movement vector).
        """
        if scda_id not in self.scda_positions:
            logger.error(f"SCDA {scda_id} not found in Metaverse")
            return {"error": "SCDA not found"}
        
        current_position = self.scda_positions[scda_id]
        
        # Apply shift with boundary constraints
        new_position = [
            min(1.0, max(0.0, current_position[i] + position_shift[i]))
            for i in range(DIMENSIONS)
        ]
        
        self.scda_positions[scda_id] = new_position
        self.scda_metadata[scda_id]["position_8d"] = new_position
        
        logger.debug(f"SCDA {scda_id} position updated: {current_position} -> {new_position}")
        
        return {
            "scda_id": scda_id,
            "old_position": current_position,
            "new_position": new_position,
            "shift": position_shift
        }
    
    def update_scda_metadata(self, scda_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update SCDA metadata (tier, complexity, energy, etc.)."""
        if scda_id not in self.scda_metadata:
            logger.error(f"SCDA {scda_id} not found in Metaverse")
            return {"error": "SCDA not found"}
        
        self.scda_metadata[scda_id].update(metadata)
        
        logger.debug(f"SCDA {scda_id} metadata updated")
        
        return {
            "scda_id": scda_id,
            "metadata": self.scda_metadata[scda_id]
        }
    
    def record_transaction(self, scda_id: str, transaction_type: str, data: Dict[str, Any]) -> MetaverseTransaction:
        """
        Record a transaction in the Metaverse.
        Transactions represent significant events in the SCDA's evolution.
        """
        if scda_id not in self.scda_positions:
            logger.error(f"SCDA {scda_id} not found in Metaverse")
            return None
        
        position_8d = self.scda_positions[scda_id]
        
        transaction = MetaverseTransaction(
            scda_id=scda_id,
            transaction_type=transaction_type,
            timestamp=datetime.now().isoformat(),
            position_8d=position_8d,
            data=data,
            transaction_id=self._generate_transaction_id(scda_id)
        )
        
        self.metaverse_transactions.append(transaction)
        
        logger.info(f"Transaction recorded: {transaction_type} for SCDA {scda_id}")
        
        return transaction
    
    def _generate_transaction_id(self, scda_id: str) -> str:
        """Generate a unique transaction ID."""
        import hashlib
        timestamp = datetime.now().isoformat()
        data = f"{scda_id}_{timestamp}_{len(self.metaverse_transactions)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def calculate_distance_between_scda(self, scda_id_1: str, scda_id_2: str) -> Optional[float]:
        """
        Calculate the Euclidean distance between two SCDAs in the 8D Hypercube.
        """
        if scda_id_1 not in self.scda_positions or scda_id_2 not in self.scda_positions:
            logger.error("One or both SCDAs not found")
            return None
        
        pos1 = np.array(self.scda_positions[scda_id_1])
        pos2 = np.array(self.scda_positions[scda_id_2])
        
        distance = np.linalg.norm(pos1 - pos2)
        
        return distance
    
    def find_nearby_scda(self, scda_id: str, radius: float = 0.3) -> List[str]:
        """
        Find all SCDAs within a certain radius in the 8D Hypercube.
        Used for discovering collaboration opportunities.
        """
        if scda_id not in self.scda_positions:
            logger.error(f"SCDA {scda_id} not found")
            return []
        
        nearby_scda = []
        target_position = np.array(self.scda_positions[scda_id])
        
        for other_scda_id, position in self.scda_positions.items():
            if other_scda_id == scda_id:
                continue
            
            distance = np.linalg.norm(target_position - np.array(position))
            if distance <= radius:
                nearby_scda.append(other_scda_id)
        
        logger.info(f"Found {len(nearby_scda)} nearby SCDAs for {scda_id}")
        
        return nearby_scda
    
    def create_collaboration_group(self, group_id: str, scda_ids: List[str]) -> Dict[str, Any]:
        """
        Create a collaboration group (Meta-Structure) of SCDAs.
        Multiple SCDAs can collaborate to solve complex problems.
        """
        # Verify all SCDAs exist
        for scda_id in scda_ids:
            if scda_id not in self.scda_positions:
                logger.error(f"SCDA {scda_id} not found")
                return {"error": f"SCDA {scda_id} not found"}
        
        self.collaboration_groups[group_id] = scda_ids
        
        logger.info(f"Collaboration group {group_id} created with {len(scda_ids)} SCDAs")
        
        return {
            "group_id": group_id,
            "scda_ids": scda_ids,
            "group_size": len(scda_ids),
            "message": "Collaboration group created successfully"
        }
    
    def get_collective_knowledge_vector(self, group_id: str) -> Optional[List[float]]:
        """
        Calculate the collective knowledge vector for a collaboration group.
        Aggregates the knowledge vectors of all SCDAs in the group.
        """
        if group_id not in self.collaboration_groups:
            logger.error(f"Collaboration group {group_id} not found")
            return None
        
        scda_ids = self.collaboration_groups[group_id]
        collective_vector = np.zeros(8)
        
        for scda_id in scda_ids:
            if scda_id in self.scda_metadata:
                # Assuming knowledge_vector_8d is stored in metadata
                # This is a placeholder; actual implementation depends on SCDA structure
                pass
        
        return collective_vector.tolist()
    
    def get_metaverse_status(self) -> Dict[str, Any]:
        """Get the overall status of the Metaverse."""
        return {
            "total_scda": len(self.scda_positions),
            "total_transactions": len(self.metaverse_transactions),
            "collaboration_groups": len(self.collaboration_groups),
            "dimensions": DIMENSIONS,
            "hypercube_center": HYPERCUBE_CENTER,
            "scda_distribution": self._calculate_scda_distribution()
        }
    
    def _calculate_scda_distribution(self) -> Dict[str, Any]:
        """Calculate the distribution of SCDAs in the 8D Hypercube."""
        if not self.scda_positions:
            return {"message": "No SCDAs in Metaverse"}
        
        positions = np.array(list(self.scda_positions.values()))
        
        return {
            "mean_position": positions.mean(axis=0).tolist(),
            "std_deviation": positions.std(axis=0).tolist(),
            "min_position": positions.min(axis=0).tolist(),
            "max_position": positions.max(axis=0).tolist()
        }
    
    def export_metaverse_state(self) -> str:
        """Export the complete Metaverse state to JSON."""
        data = {
            "status": self.get_metaverse_status(),
            "scda_positions": self.scda_positions,
            "scda_metadata": self.scda_metadata,
            "transactions": [
                {
                    "scda_id": t.scda_id,
                    "transaction_type": t.transaction_type,
                    "timestamp": t.timestamp,
                    "position_8d": t.position_8d,
                    "transaction_id": t.transaction_id,
                    "data": t.data
                }
                for t in self.metaverse_transactions
            ],
            "collaboration_groups": self.collaboration_groups
        }
        return json.dumps(data, indent=2)


# Example usage
if __name__ == "__main__":
    metaverse = MetaverseIntegration()
    
    # Register multiple SCDAs
    for i in range(5):
        scda_id = f"scda_{i:03d}"
        metaverse.register_scda(scda_id)
    
    # Update positions
    scda_0_shift = [0.1, -0.05, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0]
    metaverse.update_scda_position("scda_000", scda_0_shift)
    
    # Record transactions
    metaverse.record_transaction("scda_000", "problem_solved", {"difficulty": 0.8, "quality": 0.9})
    
    # Find nearby SCDAs
    nearby = metaverse.find_nearby_scda("scda_000", radius=0.5)
    print(f"Nearby SCDAs: {nearby}")
    
    # Create collaboration group
    metaverse.create_collaboration_group("group_001", ["scda_000", "scda_001", "scda_002"])
    
    # Print Metaverse status
    print("\n" + "="*50)
    print("Metaverse Status:")
    print(json.dumps(metaverse.get_metaverse_status(), indent=2))
