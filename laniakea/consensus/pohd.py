"""
Proof of Human Development (PoHD) - Consensus Mechanism for Laniakea Protocol
Version: 0.0.01
Author: Manus AI

PoHD is a consensus mechanism based on SCDA evolution and human intellectual development.
When an SCDA solves a Hard Problem, it provides proof of computational and intellectual work.
"""

import hashlib
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# PROOF OF HUMAN DEVELOPMENT CONSTANTS
# ============================================================================

# Difficulty adjustment parameters
POHD_MIN_DIFFICULTY = 1
POHD_MAX_DIFFICULTY = 10
POHD_TARGET_BLOCK_TIME = 60  # seconds
POHD_DIFFICULTY_ADJUSTMENT_INTERVAL = 10  # blocks

# Reward parameters
BASE_BLOCK_REWARD = 10.0  # Base reward in tokens
REWARD_SCALING_FACTOR = 1.5  # Scales with problem difficulty

# ============================================================================
# PROOF OF HUMAN DEVELOPMENT DATA STRUCTURES
# ============================================================================

@dataclass
class HardProblem:
    """Represents a Hard Problem that SCDA must solve for PoHD"""
    problem_id: str
    question: str
    difficulty: float  # 0.0 to 1.0
    knowledge_domains: Dict[int, float]  # 8D knowledge requirements
    sources: List[str]  # Scientific sources
    entropy_of_consensus: float  # Measure of disagreement in sources
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "problem_id": self.problem_id,
            "question": self.question,
            "difficulty": self.difficulty,
            "knowledge_domains": self.knowledge_domains,
            "sources": self.sources,
            "entropy_of_consensus": self.entropy_of_consensus,
            "timestamp": self.timestamp
        }
    
    def calculate_hash(self) -> str:
        """Calculate hash of the problem"""
        problem_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(problem_str.encode()).hexdigest()

@dataclass
class ProblemSolution:
    """Represents a solution to a Hard Problem"""
    problem_id: str
    scda_identity: str
    solution_text: str
    solution_quality: float  # 0.0 to 1.0
    reasoning: str
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "problem_id": self.problem_id,
            "scda_identity": self.scda_identity,
            "solution_text": self.solution_text,
            "solution_quality": self.solution_quality,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp
        }
    
    def calculate_hash(self) -> str:
        """Calculate hash of the solution"""
        solution_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(solution_str.encode()).hexdigest()

@dataclass
class PoHDProof:
    """Represents a Proof of Human Development"""
    proof_id: str
    scda_identity: str
    problem: HardProblem
    solution: ProblemSolution
    complexity_gain: float  # ΔC from solving the problem
    tier_transition: Optional[Dict[str, Any]] = None
    position_shift_8d: List[float] = field(default_factory=lambda: [0.0] * 8)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "proof_id": self.proof_id,
            "scda_identity": self.scda_identity,
            "problem": self.problem.to_dict(),
            "solution": self.solution.to_dict(),
            "complexity_gain": self.complexity_gain,
            "tier_transition": self.tier_transition,
            "position_shift_8d": self.position_shift_8d,
            "timestamp": self.timestamp
        }
    
    def calculate_hash(self) -> str:
        """Calculate hash of the proof"""
        proof_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(proof_str.encode()).hexdigest()

# ============================================================================
# PROOF OF HUMAN DEVELOPMENT VALIDATOR
# ============================================================================

class PoHDValidator:
    """
    Validates Proof of Human Development.
    Ensures that the solution is valid and meets the required standards.
    """
    
    def __init__(self):
        self.validation_history: List[Dict[str, Any]] = []
    
    def validate_solution(self, problem: HardProblem, solution: ProblemSolution) -> Tuple[bool, str]:
        """
        Validates a solution to a Hard Problem.
        
        Args:
            problem: HardProblem object
            solution: ProblemSolution object
            
        Returns:
            (is_valid: bool, validation_message: str)
        """
        # Check 1: Solution quality threshold
        if solution.solution_quality < 0.5:
            return False, "Solution quality below threshold (< 0.5)"
        
        # Check 2: Solution length (basic sanity check)
        if len(solution.solution_text) < 10:
            return False, "Solution text too short"
        
        # Check 3: Reasoning provided
        if not solution.reasoning or len(solution.reasoning) < 5:
            return False, "Insufficient reasoning provided"
        
        # Check 4: Problem-solution alignment (placeholder for LLM validation)
        # In a real system, this would use an LLM to check if the solution addresses the problem
        alignment_score = self._check_alignment(problem, solution)
        if alignment_score < 0.6:
            return False, f"Solution does not adequately address the problem (alignment: {alignment_score:.2f})"
        
        # Check 5: Difficulty-quality relationship
        # Higher difficulty problems should have higher quality solutions
        min_quality = 0.5 + (problem.difficulty * 0.3)
        if solution.solution_quality < min_quality:
            return False, f"Solution quality insufficient for difficulty level (required: {min_quality:.2f})"
        
        return True, "Solution is valid"
    
    def _check_alignment(self, problem: HardProblem, solution: ProblemSolution) -> float:
        """
        Checks if the solution aligns with the problem.
        This is a placeholder for more sophisticated LLM-based validation.
        
        Args:
            problem: HardProblem object
            solution: ProblemSolution object
            
        Returns:
            Alignment score (0.0 to 1.0)
        """
        # Simple heuristic: check if key words from the problem appear in the solution
        problem_words = set(problem.question.lower().split())
        solution_words = set(solution.solution_text.lower().split())
        
        common_words = problem_words.intersection(solution_words)
        alignment = len(common_words) / max(len(problem_words), 1)
        
        return min(alignment + 0.3, 1.0)  # Add 0.3 to account for paraphrasing
    
    def record_validation(self, problem_id: str, is_valid: bool, message: str):
        """Records a validation result"""
        self.validation_history.append({
            "problem_id": problem_id,
            "is_valid": is_valid,
            "message": message,
            "timestamp": time.time()
        })

# ============================================================================
# PROOF OF HUMAN DEVELOPMENT MINER
# ============================================================================

class PoHDMiner:
    """
    Manages the creation and validation of PoHD proofs.
    Coordinates between SCDA, Hard Problems, and blockchain.
    """
    
    def __init__(self, validator: Optional[PoHDValidator] = None):
        self.validator = validator or PoHDValidator()
        self.difficulty = POHD_MIN_DIFFICULTY
        self.block_reward = BASE_BLOCK_REWARD
        self.mining_history: List[Dict[str, Any]] = []
    
    def create_pohd_proof(
        self,
        scda_identity: str,
        problem: HardProblem,
        solution: ProblemSolution,
        complexity_gain: float,
        position_shift_8d: List[float],
        tier_transition: Optional[Dict[str, Any]] = None
    ) -> Optional[PoHDProof]:
        """
        Creates a PoHD proof if the solution is valid.
        
        Args:
            scda_identity: Identity of the SCDA
            problem: HardProblem object
            solution: ProblemSolution object
            complexity_gain: ΔC from solving the problem
            position_shift_8d: 8D position shift
            tier_transition: Optional tier transition event
            
        Returns:
            PoHDProof object if valid, None otherwise
        """
        # Validate the solution
        is_valid, validation_message = self.validator.validate_solution(problem, solution)
        
        if not is_valid:
            logger.warning(f"Solution validation failed: {validation_message}")
            return None
        
        # Create the proof
        proof_id = f"pohd_{int(time.time() * 1000)}"
        
        proof = PoHDProof(
            proof_id=proof_id,
            scda_identity=scda_identity,
            problem=problem,
            solution=solution,
            complexity_gain=complexity_gain,
            tier_transition=tier_transition,
            position_shift_8d=position_shift_8d,
            timestamp=time.time()
        )
        
        # Record in mining history
        self.mining_history.append({
            "proof_id": proof_id,
            "scda_identity": scda_identity,
            "problem_id": problem.problem_id,
            "timestamp": proof.timestamp,
            "complexity_gain": complexity_gain
        })
        
        logger.info(f"✅ PoHD Proof created: {proof_id}")
        return proof
    
    def calculate_block_reward(self, problem_difficulty: float, complexity_gain: float) -> float:
        """
        Calculates the block reward based on problem difficulty and complexity gain.
        
        Formula: Reward = BASE_REWARD * (1 + difficulty * SCALING_FACTOR) * (1 + complexity_gain / 10)
        
        Args:
            problem_difficulty: Difficulty of the solved problem
            complexity_gain: ΔC from solving the problem
            
        Returns:
            Block reward in tokens
        """
        difficulty_multiplier = 1.0 + (problem_difficulty * REWARD_SCALING_FACTOR)
        complexity_multiplier = 1.0 + (complexity_gain / 10.0)
        
        reward = self.block_reward * difficulty_multiplier * complexity_multiplier
        return reward
    
    def adjust_difficulty(self, average_block_time: float):
        """
        Adjusts the difficulty based on average block mining time.
        
        Args:
            average_block_time: Average time to mine a block (in seconds)
        """
        if average_block_time < POHD_TARGET_BLOCK_TIME / 2:
            self.difficulty = min(self.difficulty + 1, POHD_MAX_DIFFICULTY)
            logger.info(f"Difficulty increased to {self.difficulty}")
        elif average_block_time > POHD_TARGET_BLOCK_TIME * 2:
            self.difficulty = max(self.difficulty - 1, POHD_MIN_DIFFICULTY)
            logger.info(f"Difficulty decreased to {self.difficulty}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_hard_problem(
    problem_id: str,
    question: str,
    difficulty: float,
    knowledge_domains: Dict[int, float],
    sources: List[str],
    entropy_of_consensus: float
) -> HardProblem:
    """Factory function to create a HardProblem"""
    return HardProblem(
        problem_id=problem_id,
        question=question,
        difficulty=difficulty,
        knowledge_domains=knowledge_domains,
        sources=sources,
        entropy_of_consensus=entropy_of_consensus
    )

def create_problem_solution(
    problem_id: str,
    scda_identity: str,
    solution_text: str,
    solution_quality: float,
    reasoning: str
) -> ProblemSolution:
    """Factory function to create a ProblemSolution"""
    return ProblemSolution(
        problem_id=problem_id,
        scda_identity=scda_identity,
        solution_text=solution_text,
        solution_quality=solution_quality,
        reasoning=reasoning
    )

# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    # Create a validator and miner
    validator = PoHDValidator()
    miner = PoHDMiner(validator)
    
    # Create a sample Hard Problem
    problem = create_hard_problem(
        problem_id="prob_001",
        question="What is the relationship between entropy and evolution in complex systems?",
        difficulty=0.7,
        knowledge_domains={0: 0.4, 1: 0.3, 2: 0.2, 4: 0.1},  # Physics, Math, Biology, Consciousness
        sources=["arXiv:2301.12345", "Nature:2023", "Science:2023"],
        entropy_of_consensus=0.6
    )
    
    print("Hard Problem:")
    print(json.dumps(problem.to_dict(), indent=2))
    print()
    
    # Create a sample solution
    solution = create_problem_solution(
        problem_id="prob_001",
        scda_identity="scda_user_001",
        solution_text="Entropy and evolution are deeply connected. Systems with high entropy tend to evolve towards more complex states.",
        solution_quality=0.85,
        reasoning="Based on the second law of thermodynamics and principles of self-organization in complex systems."
    )
    
    print("Solution:")
    print(json.dumps(solution.to_dict(), indent=2))
    print()
    
    # Validate the solution
    is_valid, message = validator.validate_solution(problem, solution)
    print(f"Validation Result: {is_valid} - {message}")
    print()
    
    # Create a PoHD proof
    if is_valid:
        proof = miner.create_pohd_proof(
            scda_identity="scda_user_001",
            problem=problem,
            solution=solution,
            complexity_gain=2.5,
            position_shift_8d=[0.1, 0.05, 0.02, 0.0, 0.08, 0.0, 0.0, 0.0],
            tier_transition=None
        )
        
        if proof:
            print("PoHD Proof:")
            print(json.dumps(proof.to_dict(), indent=2))
            print()
            
            # Calculate block reward
            reward = miner.calculate_block_reward(problem.difficulty, proof.complexity_gain)
            print(f"Block Reward: {reward:.2f} tokens")
