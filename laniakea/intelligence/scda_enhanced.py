"""
Enhanced SCDA with Tier System Integration
Version: 0.0.01
Author: Manus AI

This module extends the existing SingleCellDigitalAccount class with Tier system
and 8D position dynamics based on the scientific model.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import uuid
from .scda_model import SingleCellDigitalAccount
from .scda_tier_system import SCDATierSystem, TierTransitionEvent, create_knowledge_vector_from_problem
from .digital_dna import DigitalDNA, DNAManager
import logging

logger = logging.getLogger(__name__)

class EnhancedSCDA(SingleCellDigitalAccount):
    """
    Extended SCDA class that integrates Tier system and 8D position dynamics.
    Maintains backward compatibility with existing SCDA while adding new features.
    """
    
    def __init__(self, identity: str = None, dna: Optional[DigitalDNA] = None):
        """
        Initializes the Enhanced SCDA with Tier system.
        
        Args:
            identity: Unique identifier for the SCDA
            dna: Optional DigitalDNA object
        """
        super().__init__(identity=identity, dna=dna)
        
        # Initialize Tier System
        self.tier_system = SCDATierSystem(self.identity)
        
        # Track tier transitions for blockchain recording
        self.tier_transition_events: List[TierTransitionEvent] = []
        
        logger.info(f"Enhanced SCDA initialized with Tier system: {self.identity}")
    
    def attempt_solve_problem_with_tier(
        self, 
        problem_difficulty: float, 
        solution_quality: float, 
        is_valid: bool,
        problem_domains: Optional[Dict[int, float]] = None
    ) -> Tuple[bool, Optional[TierTransitionEvent]]:
        """
        Enhanced problem solving with Tier system integration.
        
        Args:
            problem_difficulty: D(P) in [0, 1]
            solution_quality: Solution quality in [0, 1]
            is_valid: Whether the solution is valid
            problem_domains: Dict mapping knowledge domain index to requirement
            
        Returns:
            (success: bool, tier_transition_event: Optional[TierTransitionEvent])
        """
        # Default problem domains if not provided
        if problem_domains is None:
            problem_domains = {0: 0.5, 1: 0.3, 2: 0.2}  # Physics, Math, Biology
        
        # Create knowledge vector from problem domains
        knowledge_req = create_knowledge_vector_from_problem(problem_domains)
        
        # Call parent class method for basic problem solving
        success = self.attempt_solve_problem(problem_difficulty, solution_quality, is_valid)
        
        tier_transition_event = None
        
        if success:
            # Calculate the complexity gain
            delta_c = self._calculate_complexity_gain(problem_difficulty)
            new_complexity = self.complexity_index
            
            # Update 8D position (regardless of tier transition)
            self.tier_system.update_position_8d(knowledge_req, delta_c)
            
            # Check for tier transition
            has_transitioned, old_tier, new_tier = self.tier_system.check_tier_transition(new_complexity)
            
            if has_transitioned:
                # Apply tier transition
                tier_transition_event = self.tier_system.apply_tier_transition(new_complexity, knowledge_req)
                
                # Apply rewards from tier transition
                self._apply_tier_rewards(tier_transition_event)
                
                # Record the event
                self.tier_transition_events.append(tier_transition_event)
                
                logger.info(f"✨ Tier Transition for {self.identity}: {old_tier} → {new_tier}")
        
        return success, tier_transition_event
    
    def _apply_tier_rewards(self, event: TierTransitionEvent):
        """
        Applies rewards from a tier transition event.
        
        Args:
            event: TierTransitionEvent object
        """
        # Energy boost
        self.energy += event.energy_boost
        logger.info(f"Energy boost applied: +{event.energy_boost}")
        
        # AI upgrade factor could be used to scale future problem complexity
        # This is a placeholder for future implementation
        self.ai_upgrade_factor = event.ai_upgrade_factor
        
        # Genetic strengthening based on tier
        for domain in DNAManager.KNOWLEDGE_DOMAINS:
            DNAManager.strengthen_gene(self.dna, domain, event.ai_upgrade_factor * 0.1)
    
    def get_metaverse_state(self) -> Dict[str, Any]:
        """
        Returns the complete state of the SCDA in the 8D metaverse.
        
        Returns:
            Dict containing all relevant state information
        """
        return {
            "identity": self.identity,
            "complexity_index": self.complexity_index,
            "energy": self.energy,
            "tier_info": self.tier_system.get_tier_info(),
            "position_8d": self.tier_system.position_8d.tolist(),
            "knowledge_vector": self.tier_system.knowledge_vector.tolist(),
            "knowledge_domains": self.tier_system.get_position_in_metaverse()["knowledge_domains"],
            "tier_transition_count": len(self.tier_transition_events),
            "genetic_diversity": self.dna.calculate_genetic_diversity(),
            "problem_queue_size": len(self.problem_queue)
        }
    
    def get_position_in_metaverse(self) -> Dict[str, Any]:
        """Returns the SCDA's position and state in the 8D metaverse"""
        return self.tier_system.get_position_in_metaverse()
    
    def get_tier_info(self) -> Dict[str, Any]:
        """Returns information about the current tier"""
        return self.tier_system.get_tier_info()
    
    def get_tier_history(self) -> List[Dict[str, Any]]:
        """Returns the history of tier transitions"""
        return [event.to_dict() for event in self.tier_transition_events]
    
    def get_problem_complexity_range(self) -> Tuple[float, float]:
        """Returns the recommended problem complexity range for the current tier"""
        return self.tier_system.get_problem_complexity_range()
    
    def passive_update_with_tier(self):
        """
        Enhanced passive update that includes tier system considerations.
        """
        # Call parent class passive update
        self.passive_update()
        
        # Additional tier-based passive updates could go here
        # For example: passive position drift, energy recovery based on tier, etc.
        pass

# ============================================================================
# FACTORY FUNCTION FOR CREATING ENHANCED SCDA
# ============================================================================

def create_enhanced_scda(identity: Optional[str] = None) -> EnhancedSCDA:
    """
    Factory function to create an Enhanced SCDA instance.
    
    Args:
        identity: Optional unique identifier
        
    Returns:
        EnhancedSCDA instance
    """
    return EnhancedSCDA(identity=identity)

# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    # Create an enhanced SCDA
    scda = create_enhanced_scda("test_user_001")
    
    print("=" * 60)
    print("Initial State:")
    print("=" * 60)
    print(scda.get_metaverse_state())
    print()
    
    # Simulate solving multiple problems to reach tier 2
    print("=" * 60)
    print("Solving Problems to Reach Tier 2...")
    print("=" * 60)
    
    for i in range(15):
        problem_domains = {
            0: np.random.uniform(0.1, 0.5),  # Physics
            1: np.random.uniform(0.1, 0.5),  # Math
            2: np.random.uniform(0.0, 0.3),  # Biology
        }
        
        success, tier_event = scda.attempt_solve_problem_with_tier(
            problem_difficulty=0.5,
            solution_quality=0.9,
            is_valid=True,
            problem_domains=problem_domains
        )
        
        print(f"Problem {i+1}: Complexity = {scda.complexity_index:.2f}, Tier = {scda.tier_system.current_tier}")
        
        if tier_event:
            print(f"  ✨ TIER TRANSITION: {tier_event.old_tier} → {tier_event.new_tier}")
            print(f"     Energy Boost: {tier_event.energy_boost}")
    
    print()
    print("=" * 60)
    print("Final State:")
    print("=" * 60)
    print(scda.get_metaverse_state())
    print()
    
    print("=" * 60)
    print("Tier Transition History:")
    print("=" * 60)
    for event in scda.get_tier_history():
        print(f"  {event['old_tier']} → {event['new_tier']} at C(t) = {event['complexity_index']:.2f}")
    print()
    
    print("=" * 60)
    print("Position in Metaverse:")
    print("=" * 60)
    print(scda.get_position_in_metaverse())
