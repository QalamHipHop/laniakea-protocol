"""
Block Equation Solver and Hard Problem Generation System
Version: 0.0.01
Author: Manus AI

This module implements the block equation solving mechanism and hard problem generation
for the 8D metaverse. Users solve equations to create blocks and earn rewards.

Block Equation Formula: K_req · A = D(P) · E
Where:
- K_req: Knowledge vector required (8D)
- A: Action/Solution vector (8D) - what user must find
- D(P): Difficulty of the problem
- E: Energy vector (8D) - energy consumed
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import hashlib
import json
import logging
import random

logger = logging.getLogger(__name__)

# ============================================================================
# BLOCK EQUATION CONSTANTS
# ============================================================================

# Knowledge domains for the 8D space
KNOWLEDGE_DOMAINS = [
    "Physics",
    "Mathematics",
    "Biology",
    "Computer Science",
    "Consciousness",
    "Economics",
    "Art & Creativity",
    "Metaphysics"
]

# Difficulty levels and their characteristics
DIFFICULTY_LEVELS = {
    "easy": {"range": (0.1, 0.3), "min_quality": 0.5, "reward_multiplier": 1.0},
    "medium": {"range": (0.3, 0.6), "min_quality": 0.65, "reward_multiplier": 1.5},
    "hard": {"range": (0.6, 0.85), "min_quality": 0.8, "reward_multiplier": 2.0},
    "expert": {"range": (0.85, 1.0), "min_quality": 0.9, "reward_multiplier": 3.0}
}

# ============================================================================
# BLOCK EQUATION DATA STRUCTURES
# ============================================================================

@dataclass
class BlockEquation:
    """Represents a block equation to solve"""
    equation_id: str
    knowledge_required: np.ndarray  # K_req (8D)
    difficulty: float  # D(P)
    energy_required: np.ndarray  # E (8D)
    difficulty_level: str  # "easy", "medium", "hard", "expert"
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "equation_id": self.equation_id,
            "knowledge_required": self.knowledge_required.tolist(),
            "difficulty": self.difficulty,
            "energy_required": self.energy_required.tolist(),
            "difficulty_level": self.difficulty_level,
            "timestamp": self.timestamp
        }
    
    def verify_solution(self, action_vector: np.ndarray, tolerance: float = 0.1) -> Tuple[bool, float]:
        """
        Verifies if a proposed action vector solves the equation.
        
        Block Equation: K_req · A = D(P) · E
        
        Args:
            action_vector: Proposed solution (8D)
            tolerance: Tolerance for verification (0.0 to 1.0)
            
        Returns:
            (is_valid: bool, solution_quality: float)
        """
        # Calculate left side: K_req · A (dot product)
        left_side = np.dot(self.knowledge_required, action_vector)
        
        # Calculate right side: D(P) · E (element-wise, then sum)
        right_side = np.sum(self.difficulty * self.energy_required)
        
        # Check if equation is satisfied within tolerance
        if right_side == 0:
            return False, 0.0
        
        error = abs(left_side - right_side) / right_side
        is_valid = error <= tolerance
        
        # Calculate solution quality based on how close the solution is
        solution_quality = max(0.0, 1.0 - error)
        
        return is_valid, solution_quality

# ============================================================================
# HARD PROBLEM GENERATOR (KEA - Knowledge Extractor Agent)
# ============================================================================

class HardProblemGenerator:
    """
    Generates Hard Problems for SCDAs to solve.
    Acts as the Knowledge Extractor Agent (KEA).
    """
    
    def __init__(self):
        self.generated_problems: List[BlockEquation] = []
        self.problem_counter = 0
    
    def generate_problem_for_tier(self, tier: int, current_complexity: float) -> BlockEquation:
        """
        Generates a hard problem appropriate for the given tier.
        
        Args:
            tier: SCDA's current tier (1-4)
            current_complexity: SCDA's current complexity index
            
        Returns:
            BlockEquation object
        """
        # Determine difficulty level based on tier
        difficulty_level = self._get_difficulty_for_tier(tier)
        difficulty_range = DIFFICULTY_LEVELS[difficulty_level]["range"]
        
        # Generate difficulty within the range
        difficulty = np.random.uniform(difficulty_range[0], difficulty_range[1])
        
        # Generate knowledge requirements (emphasize domains relevant to tier)
        knowledge_req = self._generate_knowledge_requirements(tier, difficulty)
        
        # Generate energy requirements (correlated with difficulty)
        energy_req = self._generate_energy_requirements(difficulty)
        
        # Create the equation
        equation_id = f"eq_{self.problem_counter}_{int(__import__('time').time() * 1000)}"
        self.problem_counter += 1
        
        equation = BlockEquation(
            equation_id=equation_id,
            knowledge_required=knowledge_req,
            difficulty=difficulty,
            energy_required=energy_req,
            difficulty_level=difficulty_level
        )
        
        self.generated_problems.append(equation)
        logger.info(f"Generated {difficulty_level} problem: {equation_id}")
        
        return equation
    
    def _get_difficulty_for_tier(self, tier: int) -> str:
        """Maps tier to difficulty level"""
        tier_difficulty_map = {
            1: "easy",
            2: "medium",
            3: "hard",
            4: "expert"
        }
        return tier_difficulty_map.get(tier, "medium")
    
    def _generate_knowledge_requirements(self, tier: int, difficulty: float) -> np.ndarray:
        """
        Generates knowledge requirements vector for a problem.
        Higher tiers and difficulties emphasize more domains.
        """
        knowledge_req = np.zeros(8)
        
        # Tier 1: Focus on foundational sciences (Physics, Math)
        if tier == 1:
            knowledge_req[0] = np.random.uniform(0.3, 0.7)  # Physics
            knowledge_req[1] = np.random.uniform(0.2, 0.6)  # Math
        
        # Tier 2: Add structured sciences (Biology, CS)
        elif tier == 2:
            knowledge_req[0] = np.random.uniform(0.2, 0.5)  # Physics
            knowledge_req[1] = np.random.uniform(0.2, 0.5)  # Math
            knowledge_req[2] = np.random.uniform(0.2, 0.5)  # Biology
            knowledge_req[3] = np.random.uniform(0.2, 0.5)  # CS
        
        # Tier 3: Add interdisciplinary (Consciousness, Economics)
        elif tier == 3:
            for i in range(6):
                knowledge_req[i] = np.random.uniform(0.1, 0.4)
        
        # Tier 4: All domains equally important
        else:
            knowledge_req = np.random.uniform(0.1, 0.5, 8)
        
        # Scale by difficulty
        knowledge_req *= (0.5 + difficulty)
        
        # Normalize to unit vector
        norm = np.linalg.norm(knowledge_req)
        if norm > 0:
            knowledge_req /= norm
        
        return knowledge_req
    
    def _generate_energy_requirements(self, difficulty: float) -> np.ndarray:
        """
        Generates energy requirements vector.
        Higher difficulty requires more energy.
        """
        energy_req = np.random.uniform(0.1, 0.5, 8)
        energy_req *= difficulty
        return energy_req
    
    def generate_problem_description(self, equation: BlockEquation) -> Dict[str, Any]:
        """
        Generates a human-readable description of a block equation problem.
        
        Args:
            equation: BlockEquation object
            
        Returns:
            Problem description with question and context
        """
        # Identify dominant knowledge domains
        dominant_domains = np.argsort(equation.knowledge_required)[-3:][::-1]
        domain_names = [KNOWLEDGE_DOMAINS[i] for i in dominant_domains]
        
        # Generate problem description
        difficulty_level = equation.difficulty_level
        difficulty_pct = int(equation.difficulty * 100)
        
        description = {
            "equation_id": equation.equation_id,
            "difficulty_level": difficulty_level,
            "difficulty_percentage": difficulty_pct,
            "primary_domains": domain_names,
            "question": self._generate_question(domain_names, difficulty_level),
            "hint": self._generate_hint(domain_names),
            "knowledge_vector": equation.knowledge_required.tolist(),
            "energy_required": equation.energy_required.tolist()
        }
        
        return description
    
    def _generate_question(self, domains: List[str], difficulty: str) -> str:
        """Generates a question based on domains and difficulty"""
        questions = {
            ("Physics", "Mathematics"): {
                "easy": "How does the relationship between energy and momentum manifest in classical mechanics?",
                "medium": "Derive the connection between wave-particle duality and Fourier transforms.",
                "hard": "Explain the mathematical foundations of quantum field theory and its implications for spacetime.",
                "expert": "Formulate a unified framework connecting general relativity and quantum mechanics through information theory."
            },
            ("Biology", "Computer Science"): {
                "easy": "What are the key similarities between biological evolution and algorithmic optimization?",
                "medium": "How can neural networks be designed to mimic biological learning processes?",
                "hard": "Develop a computational model that explains emergent complexity in biological systems.",
                "expert": "Create a theoretical framework for artificial consciousness based on biological principles."
            }
        }
        
        # Default question if specific combination not found
        default_questions = {
            "easy": "How do the concepts of complexity and emergence relate to your field?",
            "medium": "Propose a novel solution to a fundamental problem in your domain.",
            "hard": "Synthesize knowledge across multiple disciplines to solve a complex challenge.",
            "expert": "Develop a paradigm-shifting framework that revolutionizes understanding in your field."
        }
        
        key = tuple(domains[:2]) if len(domains) >= 2 else None
        if key in questions:
            return questions[key].get(difficulty, default_questions[difficulty])
        
        return default_questions.get(difficulty, "Solve a complex problem.")
    
    def _generate_hint(self, domains: List[str]) -> str:
        """Generates a hint based on domains"""
        hints = {
            "Physics": "Consider the conservation laws and symmetries.",
            "Mathematics": "Look for patterns and mathematical structures.",
            "Biology": "Think about adaptation and evolution.",
            "Computer Science": "Consider algorithms and computational complexity.",
            "Consciousness": "Reflect on awareness and subjective experience.",
            "Economics": "Think about incentives and resource allocation.",
            "Art & Creativity": "Explore novel combinations and expressions.",
            "Metaphysics": "Question the nature of reality and existence."
        }
        
        hint_texts = [hints.get(domain, "Think deeply.") for domain in domains]
        return " ".join(hint_texts)

# ============================================================================
# BLOCK EQUATION SOLVER
# ============================================================================

class BlockEquationSolver:
    """
    Helps users solve block equations and verify solutions.
    """
    
    def __init__(self):
        self.solved_equations: List[Dict[str, Any]] = []
    
    def solve_equation(
        self,
        equation: BlockEquation,
        action_vector: np.ndarray,
        user_explanation: str
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Attempts to solve a block equation.
        
        Args:
            equation: BlockEquation to solve
            action_vector: Proposed solution (8D)
            user_explanation: User's explanation of the solution
            
        Returns:
            (is_valid, solution_quality, result_dict)
        """
        # Verify the solution
        is_valid, solution_quality = equation.verify_solution(action_vector)
        
        # Calculate reward
        reward = self._calculate_reward(equation, solution_quality)
        
        # Record the solution
        result = {
            "equation_id": equation.equation_id,
            "is_valid": is_valid,
            "solution_quality": solution_quality,
            "reward": reward,
            "explanation": user_explanation,
            "timestamp": __import__('time').time()
        }
        
        self.solved_equations.append(result)
        
        if is_valid:
            logger.info(f"✅ Equation {equation.equation_id} solved with quality {solution_quality:.2f}")
        else:
            logger.info(f"❌ Equation {equation.equation_id} not solved (quality: {solution_quality:.2f})")
        
        return is_valid, solution_quality, result
    
    def _calculate_reward(self, equation: BlockEquation, solution_quality: float) -> float:
        """
        Calculates reward for solving an equation.
        
        Reward = Base * Difficulty * Quality * Multiplier
        """
        base_reward = 10.0
        difficulty_factor = 1.0 + equation.difficulty
        quality_factor = solution_quality
        multiplier = DIFFICULTY_LEVELS[equation.difficulty_level]["reward_multiplier"]
        
        reward = base_reward * difficulty_factor * quality_factor * multiplier
        return reward

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize generator and solver
    generator = HardProblemGenerator()
    solver = BlockEquationSolver()
    
    print("=" * 60)
    print("Block Equation Solver - Example Usage")
    print("=" * 60)
    print()
    
    # Generate a problem for Tier 2
    equation = generator.generate_problem_for_tier(tier=2, current_complexity=15.0)
    
    print("Generated Block Equation:")
    print(f"  ID: {equation.equation_id}")
    print(f"  Difficulty: {equation.difficulty:.2f}")
    print(f"  Level: {equation.difficulty_level}")
    print(f"  Knowledge Required: {equation.knowledge_required}")
    print(f"  Energy Required: {equation.energy_required}")
    print()
    
    # Generate problem description
    description = generator.generate_problem_description(equation)
    print("Problem Description:")
    print(f"  Question: {description['question']}")
    print(f"  Hint: {description['hint']}")
    print(f"  Primary Domains: {', '.join(description['primary_domains'])}")
    print()
    
    # Attempt to solve
    print("Attempting to solve...")
    
    # Create a solution vector (in real system, user would provide this)
    action_vector = equation.knowledge_required + np.random.uniform(-0.1, 0.1, 8)
    
    is_valid, quality, result = solver.solve_equation(
        equation=equation,
        action_vector=action_vector,
        user_explanation="I applied the principles of the dominant knowledge domains."
    )
    
    print(f"  Valid: {is_valid}")
    print(f"  Quality: {quality:.2f}")
    print(f"  Reward: {result['reward']:.2f} tokens")
    print()
    
    # Generate another problem for Tier 3
    equation2 = generator.generate_problem_for_tier(tier=3, current_complexity=150.0)
    description2 = generator.generate_problem_description(equation2)
    
    print("Another Problem (Tier 3):")
    print(f"  Difficulty Level: {description2['difficulty_level']}")
    print(f"  Question: {description2['question']}")
    print(f"  Primary Domains: {', '.join(description2['primary_domains'])}")
