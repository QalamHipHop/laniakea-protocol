"""
LaniakeA Protocol - Achievement System
Mathematical challenges that unlock badges and complexity boosts
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger("AchievementSystem")


class Achievement:
    """Single achievement definition"""
    
    def __init__(
        self,
        achievement_id: str,
        name: str,
        description: str,
        category: str,
        requirement: str,
        complexity_boost: float,
        badge_icon: str,
        validator_func: callable
    ):
        self.id = achievement_id
        self.name = name
        self.description = description
        self.category = category
        self.requirement = requirement
        self.complexity_boost = complexity_boost
        self.badge_icon = badge_icon
        self.validator = validator_func
    
    def check(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if user meets achievement requirements
        
        Returns:
            (is_unlocked, reasoning)
        """
        try:
            return self.validator(user_data)
        except Exception as e:
            logger.error(f"Achievement validation error: {e}")
            return False, f"Validation error: {str(e)}"


class AchievementSystem:
    """
    Achievement System with Mathematical Challenges
    
    Achievements are unlocked by:
    1. Solving meta-problems (mathematical proofs)
    2. Reaching milestones (complexity thresholds)
    3. Demonstrating mastery (problem categories)
    """
    
    def __init__(self):
        """Initialize achievement system"""
        self.achievements: Dict[str, Achievement] = {}
        self._register_achievements()
        logger.info(f"✅ Achievement System initialized with {len(self.achievements)} achievements")
    
    def _register_achievements(self):
        """Register all achievements"""
        
        # === MATHEMATICAL FOUNDATIONS ===
        
        self.register_achievement(Achievement(
            achievement_id="euler_identity",
            name="Euler's Identity Master",
            description="Prove Euler's Identity: e^(iπ) + 1 = 0",
            category="Mathematical Foundations",
            requirement="Provide mathematical proof of Euler's identity",
            complexity_boost=0.5,
            badge_icon="🔢",
            validator_func=self._validate_euler_identity
        ))
        
        self.register_achievement(Achievement(
            achievement_id="pythagorean_theorem",
            name="Pythagorean Scholar",
            description="Prove Pythagorean Theorem: a² + b² = c²",
            category="Mathematical Foundations",
            requirement="Provide geometric or algebraic proof",
            complexity_boost=0.3,
            badge_icon="📐",
            validator_func=self._validate_pythagorean
        ))
        
        self.register_achievement(Achievement(
            achievement_id="golden_ratio",
            name="Golden Ratio Explorer",
            description="Derive Golden Ratio: φ = (1 + √5) / 2",
            category="Mathematical Foundations",
            requirement="Show φ² = φ + 1",
            complexity_boost=0.4,
            badge_icon="✨",
            validator_func=self._validate_golden_ratio
        ))
        
        # === PHYSICS MASTERY ===
        
        self.register_achievement(Achievement(
            achievement_id="quantum_entanglement",
            name="Quantum Entanglement Solver",
            description="Analyze Bell State: |ψ⟩ = (|00⟩ + |11⟩)/√2",
            category="Physics Mastery",
            requirement="Demonstrate understanding of quantum entanglement",
            complexity_boost=0.8,
            badge_icon="⚛️",
            validator_func=self._validate_quantum_entanglement
        ))
        
        self.register_achievement(Achievement(
            achievement_id="schrodinger_equation",
            name="Schrödinger's Apprentice",
            description="Solve time-independent Schrödinger equation",
            category="Physics Mastery",
            requirement="Solve Hψ = Eψ for simple potential",
            complexity_boost=1.0,
            badge_icon="🌊",
            validator_func=self._validate_schrodinger
        ))
        
        self.register_achievement(Achievement(
            achievement_id="maxwell_equations",
            name="Maxwell's Disciple",
            description="Derive electromagnetic wave equation from Maxwell's equations",
            category="Physics Mastery",
            requirement="Show ∇²E = μ₀ε₀ ∂²E/∂t²",
            complexity_boost=1.2,
            badge_icon="⚡",
            validator_func=self._validate_maxwell
        ))
        
        # === COMPUTATIONAL EXCELLENCE ===
        
        self.register_achievement(Achievement(
            achievement_id="p_vs_np",
            name="P vs NP Explorer",
            description="Analyze P vs NP problem complexity",
            category="Computational Excellence",
            requirement="Demonstrate understanding of computational complexity classes",
            complexity_boost=1.5,
            badge_icon="🧮",
            validator_func=self._validate_p_vs_np
        ))
        
        self.register_achievement(Achievement(
            achievement_id="turing_machine",
            name="Turing's Legacy",
            description="Design a Turing machine for a specific computation",
            category="Computational Excellence",
            requirement="Provide formal Turing machine definition",
            complexity_boost=0.9,
            badge_icon="🤖",
            validator_func=self._validate_turing_machine
        ))
        
        # === MILESTONE ACHIEVEMENTS ===
        
        self.register_achievement(Achievement(
            achievement_id="complexity_2",
            name="Organism Level",
            description="Reach complexity index 2.0",
            category="Evolution Milestones",
            requirement="Evolve from cell to organism",
            complexity_boost=0.2,
            badge_icon="🦠",
            validator_func=lambda u: (u.get('complexity', 0) >= 2.0, "Complexity >= 2.0")
        ))
        
        self.register_achievement(Achievement(
            achievement_id="complexity_3",
            name="Intelligence Awakened",
            description="Reach complexity index 3.0",
            category="Evolution Milestones",
            requirement="Achieve conscious intelligence",
            complexity_boost=0.5,
            badge_icon="🧠",
            validator_func=lambda u: (u.get('complexity', 0) >= 3.0, "Complexity >= 3.0")
        ))
        
        self.register_achievement(Achievement(
            achievement_id="complexity_5",
            name="Humanity Ascended",
            description="Reach complexity index 5.0",
            category="Evolution Milestones",
            requirement="Transcend individual to collective",
            complexity_boost=1.0,
            badge_icon="👥",
            validator_func=lambda u: (u.get('complexity', 0) >= 5.0, "Complexity >= 5.0")
        ))
        
        self.register_achievement(Achievement(
            achievement_id="first_solve",
            name="First Steps",
            description="Solve your first problem",
            category="Evolution Milestones",
            requirement="Submit one validated solution",
            complexity_boost=0.1,
            badge_icon="🌱",
            validator_func=lambda u: (u.get('solved_count', 0) >= 1, "Solved >= 1")
        ))
        
        self.register_achievement(Achievement(
            achievement_id="solve_10",
            name="Problem Solver",
            description="Solve 10 problems",
            category="Evolution Milestones",
            requirement="Submit 10 validated solutions",
            complexity_boost=0.3,
            badge_icon="🎯",
            validator_func=lambda u: (u.get('solved_count', 0) >= 10, "Solved >= 10")
        ))
        
        self.register_achievement(Achievement(
            achievement_id="solve_100",
            name="Knowledge Seeker",
            description="Solve 100 problems",
            category="Evolution Milestones",
            requirement="Submit 100 validated solutions",
            complexity_boost=1.0,
            badge_icon="📚",
            validator_func=lambda u: (u.get('solved_count', 0) >= 100, "Solved >= 100")
        ))
    
    def register_achievement(self, achievement: Achievement):
        """Register an achievement"""
        self.achievements[achievement.id] = achievement
    
    def check_achievement(self, achievement_id: str, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if user has unlocked an achievement
        
        Args:
            achievement_id: Achievement identifier
            user_data: User statistics and data
        
        Returns:
            (is_unlocked, reasoning)
        """
        if achievement_id not in self.achievements:
            return False, "Achievement not found"
        
        achievement = self.achievements[achievement_id]
        return achievement.check(user_data)
    
    def check_all_achievements(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check all achievements for a user
        
        Args:
            user_data: User statistics and data
        
        Returns:
            List of newly unlocked achievements
        """
        unlocked = []
        
        for achievement_id, achievement in self.achievements.items():
            is_unlocked, reasoning = achievement.check(user_data)
            
            if is_unlocked:
                unlocked.append({
                    'id': achievement.id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'category': achievement.category,
                    'complexity_boost': achievement.complexity_boost,
                    'badge_icon': achievement.badge_icon,
                    'reasoning': reasoning,
                    'unlocked_at': datetime.now().isoformat()
                })
        
        return unlocked
    
    def get_achievement_info(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """Get achievement information"""
        if achievement_id not in self.achievements:
            return None
        
        achievement = self.achievements[achievement_id]
        return {
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'category': achievement.category,
            'requirement': achievement.requirement,
            'complexity_boost': achievement.complexity_boost,
            'badge_icon': achievement.badge_icon
        }
    
    def get_all_achievements(self) -> List[Dict[str, Any]]:
        """Get all achievements"""
        return [self.get_achievement_info(aid) for aid in self.achievements.keys()]
    
    # === VALIDATORS ===
    
    def _validate_euler_identity(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate Euler's Identity proof"""
        proof = user_data.get('proof', '').lower()
        
        # Check for key concepts
        required_concepts = ['euler', 'complex', 'exponential', 'trigonometric']
        concepts_found = sum(1 for concept in required_concepts if concept in proof)
        
        # Check for mathematical notation
        has_notation = 'e^' in proof or 'exp' in proof
        has_pi = 'π' in proof or 'pi' in proof
        has_i = 'i' in proof or 'imaginary' in proof
        
        if concepts_found >= 2 and has_notation and has_pi and has_i:
            return True, "Valid proof with key concepts and notation"
        
        return False, f"Incomplete proof (concepts: {concepts_found}/4)"
    
    def _validate_pythagorean(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate Pythagorean theorem proof"""
        proof = user_data.get('proof', '').lower()
        
        # Check for proof type
        is_geometric = 'square' in proof or 'area' in proof or 'triangle' in proof
        is_algebraic = 'a²' in proof or 'b²' in proof or 'c²' in proof
        
        if is_geometric or is_algebraic:
            return True, "Valid geometric or algebraic proof"
        
        return False, "No valid proof structure detected"
    
    def _validate_golden_ratio(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate golden ratio derivation"""
        proof = user_data.get('proof', '').lower()
        
        # Check for golden ratio concepts
        has_phi = 'φ' in proof or 'phi' in proof or 'golden' in proof
        has_equation = 'φ²' in proof or 'phi^2' in proof
        has_sqrt5 = '√5' in proof or 'sqrt(5)' in proof or 'sqrt 5' in proof
        
        if has_phi and (has_equation or has_sqrt5):
            return True, "Valid golden ratio derivation"
        
        return False, "Incomplete derivation"
    
    def _validate_quantum_entanglement(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate quantum entanglement understanding"""
        solution = user_data.get('solution', '').lower()
        
        # Check for quantum concepts
        concepts = ['entangle', 'bell', 'superposition', 'measurement', 'correlation']
        concepts_found = sum(1 for concept in concepts if concept in solution)
        
        # Check for notation
        has_ket = '|' in solution or 'ket' in solution
        has_sqrt2 = '√2' in solution or 'sqrt(2)' in solution
        
        if concepts_found >= 2 and (has_ket or has_sqrt2):
            return True, f"Strong understanding ({concepts_found} concepts)"
        
        return False, f"Insufficient understanding ({concepts_found}/5 concepts)"
    
    def _validate_schrodinger(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate Schrödinger equation solution"""
        solution = user_data.get('solution', '').lower()
        
        # Check for key elements
        has_hamiltonian = 'hamiltonian' in solution or 'h' in solution
        has_wavefunction = 'ψ' in solution or 'psi' in solution or 'wavefunction' in solution
        has_energy = 'energy' in solution or 'eigenvalue' in solution
        
        if has_hamiltonian and has_wavefunction and has_energy:
            return True, "Valid solution structure"
        
        return False, "Missing key elements"
    
    def _validate_maxwell(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate Maxwell equations derivation"""
        solution = user_data.get('solution', '').lower()
        
        # Check for Maxwell equations
        has_gauss = 'gauss' in solution or '∇·e' in solution
        has_faraday = 'faraday' in solution or '∇×e' in solution
        has_ampere = 'ampere' in solution or '∇×b' in solution
        has_wave = 'wave equation' in solution or '∇²' in solution
        
        equations_found = sum([has_gauss, has_faraday, has_ampere, has_wave])
        
        if equations_found >= 2:
            return True, f"Valid derivation ({equations_found}/4 equations)"
        
        return False, f"Incomplete derivation ({equations_found}/4 equations)"
    
    def _validate_p_vs_np(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate P vs NP understanding"""
        solution = user_data.get('solution', '').lower()
        
        # Check for complexity concepts
        concepts = ['polynomial', 'nondeterministic', 'np-complete', 'reduction', 'verification']
        concepts_found = sum(1 for concept in concepts if concept in solution)
        
        if concepts_found >= 3:
            return True, f"Strong understanding ({concepts_found} concepts)"
        
        return False, f"Insufficient understanding ({concepts_found}/5 concepts)"
    
    def _validate_turing_machine(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate Turing machine design"""
        solution = user_data.get('solution', '').lower()
        
        # Check for Turing machine components
        has_states = 'state' in solution or 'q' in solution
        has_tape = 'tape' in solution
        has_transitions = 'transition' in solution or 'δ' in solution
        has_alphabet = 'alphabet' in solution or 'symbol' in solution
        
        components_found = sum([has_states, has_tape, has_transitions, has_alphabet])
        
        if components_found >= 3:
            return True, f"Valid Turing machine ({components_found}/4 components)"
        
        return False, f"Incomplete design ({components_found}/4 components)"


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    system = AchievementSystem()
    
    print("\n" + "="*60)
    print("Achievement System Test")
    print("="*60)
    
    # Test user data
    user_data = {
        'complexity': 2.5,
        'solved_count': 15,
        'proof': """
        Euler's Identity proof:
        Using Euler's formula: e^(ix) = cos(x) + i·sin(x)
        When x = π:
        e^(iπ) = cos(π) + i·sin(π)
        e^(iπ) = -1 + i·0
        e^(iπ) = -1
        Therefore: e^(iπ) + 1 = 0
        """,
        'solution': """
        Quantum entanglement in Bell states:
        The state |ψ⟩ = (|00⟩ + |11⟩)/√2 represents maximum entanglement.
        Measuring one qubit instantly determines the other's state,
        demonstrating non-local correlation.
        """
    }
    
    # Check all achievements
    print("\nChecking achievements...")
    unlocked = system.check_all_achievements(user_data)
    
    print(f"\n✅ Unlocked {len(unlocked)} achievements:")
    for ach in unlocked:
        print(f"\n{ach['badge_icon']} {ach['name']}")
        print(f"   Category: {ach['category']}")
        print(f"   Boost: +{ach['complexity_boost']} complexity")
        print(f"   Reason: {ach['reasoning']}")
    
    # Show all available achievements
    print("\n" + "="*60)
    print("All Available Achievements")
    print("="*60)
    
    all_achievements = system.get_all_achievements()
    by_category = {}
    for ach in all_achievements:
        category = ach['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(ach)
    
    for category, achievements in by_category.items():
        print(f"\n📁 {category}:")
        for ach in achievements:
            print(f"   {ach['badge_icon']} {ach['name']} (+{ach['complexity_boost']} C)")
            print(f"      {ach['description']}")
