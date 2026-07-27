"""
SCDA Tier System and Position Dynamics in 8D Metaverse
Version: 0.0.01
Author: Manus AI

This module implements the Tier system for SCDA evolution and the 8D position dynamics
based on the scientific and mathematical models defined in SCIENTIFIC_MATHEMATICAL_MODEL_V0.0.01.md
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
import logging

# Configure logger
logger = logging.getLogger(__name__)

# ============================================================================
# TIER SYSTEM CONSTANTS (Based on Scientific Model)
# ============================================================================

TIER_THRESHOLDS = {
    1: {"min": 1.0, "max": 10.0, "name": "Single-Cell", "description": "Origin of Life"},
    2: {"min": 10.0, "max": 100.0, "name": "Multi-Cellular", "description": "Differentiation and Cooperation"},
    3: {"min": 100.0, "max": 1000.0, "name": "Humanity", "description": "Self-Awareness and Agency"},
    4: {"min": 1000.0, "max": float('inf'), "name": "Galactic", "description": "Cosmic Consciousness"}
}

# 8D Knowledge Domains (Dimensions of the Metaverse)
KNOWLEDGE_DOMAINS = {
    0: "Physics",
    1: "Mathematics",
    2: "Biology",
    3: "Computer Science",
    4: "Consciousness",
    5: "Economics",
    6: "Art & Creativity",
    7: "Metaphysics"
}

# Tier-specific rewards and properties
TIER_PROPERTIES = {
    1: {
        "energy_boost": 100.0,
        "position_shift_magnitude": 0.1,
        "ai_upgrade_factor": 1.0,
        "problem_complexity_range": (0.1, 0.3)
    },
    2: {
        "energy_boost": 500.0,
        "position_shift_magnitude": 0.3,
        "ai_upgrade_factor": 1.5,
        "problem_complexity_range": (0.3, 0.6)
    },
    3: {
        "energy_boost": 2000.0,
        "position_shift_magnitude": 0.5,
        "ai_upgrade_factor": 2.0,
        "problem_complexity_range": (0.6, 0.9)
    },
    4: {
        "energy_boost": 10000.0,
        "position_shift_magnitude": 1.0,
        "ai_upgrade_factor": 3.0,
        "problem_complexity_range": (0.8, 1.0)
    }
}

# ============================================================================
# TIER TRANSITION EVENT
# ============================================================================

@dataclass
class TierTransitionEvent:
    """Represents a Tier Level-Up event"""
    scda_identity: str
    old_tier: int
    new_tier: int
    complexity_index: float
    timestamp: float
    energy_boost: float
    position_shift: List[float]
    ai_upgrade_factor: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        return {
            "scda_identity": self.scda_identity,
            "old_tier": self.old_tier,
            "new_tier": self.new_tier,
            "complexity_index": self.complexity_index,
            "timestamp": self.timestamp,
            "energy_boost": self.energy_boost,
            "position_shift": self.position_shift,
            "ai_upgrade_factor": self.ai_upgrade_factor
        }

# ============================================================================
# SCDA TIER SYSTEM CLASS
# ============================================================================

class SCDATierSystem:
    """
    Manages the Tier system for SCDA evolution.
    Handles tier transitions, position dynamics, and reward distribution.
    """
    
    def __init__(self, scda_identity: str):
        self.scda_identity = scda_identity
        self.current_tier = 1
        self.complexity_index = 1.0
        self.position_8d = np.array([0.5] * 8)  # Start at center of 8D hypercube
        self.knowledge_vector = np.zeros(8)  # Knowledge in each domain
        self.tier_history: List[TierTransitionEvent] = []
        
    def get_current_tier(self) -> int:
        """Returns the current tier based on complexity index"""
        for tier_id in sorted(TIER_THRESHOLDS.keys()):
            threshold = TIER_THRESHOLDS[tier_id]
            if threshold["min"] <= self.complexity_index < threshold["max"]:
                return tier_id
        return 4  # Maximum tier
    
    def check_tier_transition(self, new_complexity: float) -> Tuple[bool, int, int]:
        """
        Checks if a tier transition has occurred.
        
        Returns:
            (has_transitioned, old_tier, new_tier)
        """
        old_tier = self.current_tier
        new_tier = self.get_current_tier_for_complexity(new_complexity)
        
        if new_tier > old_tier:
            return True, old_tier, new_tier
        return False, old_tier, old_tier
    
    def get_current_tier_for_complexity(self, complexity: float) -> int:
        """Returns the tier for a given complexity index"""
        for tier_id in sorted(TIER_THRESHOLDS.keys()):
            threshold = TIER_THRESHOLDS[tier_id]
            if threshold["min"] <= complexity < threshold["max"]:
                return tier_id
        return 4
    
    def calculate_position_shift(self, problem_knowledge_requirements: np.ndarray, delta_c: float) -> np.ndarray:
        """
        Calculates the 8D position shift based on the solved problem's knowledge requirements.
        
        Formula: V_evolution = (ΔC / C(t)) * K_req
        
        Args:
            problem_knowledge_requirements: 8D vector of knowledge required for the problem
            delta_c: Change in complexity index
            
        Returns:
            8D position shift vector
        """
        if self.complexity_index <= 0:
            return np.zeros(8)
        
        # Normalize the shift by current complexity
        shift_magnitude = delta_c / self.complexity_index
        
        # Calculate movement vector
        movement_vector = shift_magnitude * problem_knowledge_requirements
        
        return movement_vector
    
    def apply_tier_transition(self, new_complexity: float, problem_knowledge_requirements: np.ndarray) -> TierTransitionEvent:
        """
        Applies a tier transition with all associated rewards and state changes.
        
        Args:
            new_complexity: New complexity index
            problem_knowledge_requirements: 8D vector of knowledge required
            
        Returns:
            TierTransitionEvent object
        """
        import time
        
        has_transitioned, old_tier, new_tier = self.check_tier_transition(new_complexity)
        
        if not has_transitioned:
            raise ValueError(f"No tier transition occurred. Old tier: {old_tier}, New tier: {new_tier}")
        
        # Calculate delta C for position shift
        delta_c = new_complexity - self.complexity_index
        
        # Update complexity index
        self.complexity_index = new_complexity
        self.current_tier = new_tier
        
        # Calculate position shift
        position_shift = self.calculate_position_shift(problem_knowledge_requirements, delta_c)
        
        # Apply position shift (with normalization to keep within [0, 1])
        self.position_8d = np.clip(self.position_8d + position_shift, 0, 1)
        
        # Update knowledge vector
        self.knowledge_vector += problem_knowledge_requirements
        
        # Get tier properties
        tier_props = TIER_PROPERTIES[new_tier]
        
        # Create transition event
        event = TierTransitionEvent(
            scda_identity=self.scda_identity,
            old_tier=old_tier,
            new_tier=new_tier,
            complexity_index=new_complexity,
            timestamp=time.time(),
            energy_boost=tier_props["energy_boost"],
            position_shift=position_shift.tolist(),
            ai_upgrade_factor=tier_props["ai_upgrade_factor"]
        )
        
        # Record in history
        self.tier_history.append(event)
        
        logger.info(f"🚀 SCDA {self.scda_identity} transitioned from Tier {old_tier} to Tier {new_tier}!")
        logger.info(f"   Energy Boost: {event.energy_boost}")
        logger.info(f"   Position Shift: {position_shift}")
        logger.info(f"   AI Upgrade Factor: {event.ai_upgrade_factor}")
        
        return event
    
    def update_position_8d(self, problem_knowledge_requirements: np.ndarray, delta_c: float):
        """
        Updates the 8D position based on a solved problem (without tier transition).
        
        Args:
            problem_knowledge_requirements: 8D vector of knowledge required
            delta_c: Change in complexity index
        """
        position_shift = self.calculate_position_shift(problem_knowledge_requirements, delta_c)
        self.position_8d = np.clip(self.position_8d + position_shift, 0, 1)
        self.knowledge_vector += problem_knowledge_requirements
        
        logger.debug(f"Position updated for {self.scda_identity}: {self.position_8d}")
    
    def get_tier_info(self) -> Dict[str, Any]:
        """Returns information about the current tier"""
        tier_data = TIER_THRESHOLDS[self.current_tier]
        return {
            "tier_id": self.current_tier,
            "tier_name": tier_data["name"],
            "tier_description": tier_data["description"],
            "complexity_index": self.complexity_index,
            "position_8d": self.position_8d.tolist(),
            "knowledge_vector": self.knowledge_vector.tolist(),
            "knowledge_domains": KNOWLEDGE_DOMAINS,
            "tier_history_count": len(self.tier_history)
        }
    
    def get_problem_complexity_range(self) -> Tuple[float, float]:
        """Returns the recommended problem complexity range for the current tier"""
        tier_props = TIER_PROPERTIES[self.current_tier]
        return tier_props["problem_complexity_range"]
    
    def get_position_in_metaverse(self) -> Dict[str, Any]:
        """Returns the SCDA's position and state in the 8D metaverse"""
        return {
            "scda_identity": self.scda_identity,
            "tier": self.current_tier,
            "complexity_index": self.complexity_index,
            "position_8d": self.position_8d.tolist(),
            "knowledge_vector": self.knowledge_vector.tolist(),
            "knowledge_domains": {
                idx: {"domain": KNOWLEDGE_DOMAINS[idx], "knowledge_level": float(self.knowledge_vector[idx])}
                for idx in range(8)
            }
        }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_knowledge_vector_from_problem(problem_domains: Dict[int, float]) -> np.ndarray:
    """
    Creates an 8D knowledge vector from problem domain requirements.
    
    Args:
        problem_domains: Dict mapping domain index to knowledge requirement (0-1)
        
    Returns:
        8D numpy array
    """
    vector = np.zeros(8)
    for domain_idx, requirement in problem_domains.items():
        if 0 <= domain_idx < 8:
            vector[domain_idx] = requirement
    return vector / (np.linalg.norm(vector) + 1e-10)  # Normalize

def calculate_8d_distance(pos1: np.ndarray, pos2: np.ndarray) -> float:
    """Calculates Euclidean distance between two 8D positions"""
    return np.linalg.norm(pos1 - pos2)

def get_tier_name_from_complexity(complexity: float) -> str:
    """Returns the tier name for a given complexity index"""
    for tier_id in sorted(TIER_THRESHOLDS.keys()):
        threshold = TIER_THRESHOLDS[tier_id]
        if threshold["min"] <= complexity < threshold["max"]:
            return threshold["name"]
    return "Galactic"

# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    # Initialize a tier system for a test SCDA
    tier_system = SCDATierSystem("test_scda_001")
    
    print("Initial Tier Info:")
    print(tier_system.get_tier_info())
    print()
    
    # Simulate solving a problem that increases complexity
    problem_domains = {0: 0.5, 1: 0.3, 2: 0.2}  # Physics, Math, Biology
    knowledge_req = create_knowledge_vector_from_problem(problem_domains)
    
    # Update position without tier transition
    tier_system.update_position_8d(knowledge_req, delta_c=2.0)
    tier_system.complexity_index = 5.0
    
    print("After solving problem (no tier transition):")
    print(f"Complexity: {tier_system.complexity_index}")
    print(f"Position: {tier_system.position_8d}")
    print()
    
    # Simulate a tier transition
    tier_system.complexity_index = 9.5
    has_transitioned, old_tier, new_tier = tier_system.check_tier_transition(10.5)
    
    if has_transitioned:
        event = tier_system.apply_tier_transition(10.5, knowledge_req)
        print("Tier Transition Event:")
        print(event.to_dict())
        print()
    
    print("Final Tier Info:")
    print(tier_system.get_tier_info())
    print()
    
    print("Position in Metaverse:")
    print(tier_system.get_position_in_metaverse())
