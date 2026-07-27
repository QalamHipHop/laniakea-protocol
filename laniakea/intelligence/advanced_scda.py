"""
Advanced Single-Cell Digital Account (SCDA) V0.0.03
Complete implementation with Digital DNA, evolutionary tiers, and cosmic abilities
"""

import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

from laniakea.intelligence.digital_dna import DigitalDNA, DNAManager


@dataclass
class Achievement:
    """Represents an achievement unlocked by the SCDA"""
    name: str
    description: str
    rarity: str  # common, rare, legendary, mythic
    rewards: Dict[str, float]  # {"KT": 100}
    unlocked_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "rewards": self.rewards,
            "unlocked_at": self.unlocked_at
        }


@dataclass
class EvolutionEvent:
    """Records an event in the SCDA's evolution timeline"""
    event_type: str  # genesis, problem_solved, level_up, mutation, etc.
    timestamp: str
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "data": self.data
        }


class AdvancedSCDA:
    """
    Advanced Single-Cell Digital Account with complete evolutionary features.
    
    This is the V0.0.03 implementation with:
    - Digital DNA system
    - Tier-based evolution (1-4)
    - 8D spatial positioning
    - Energy and complexity dynamics
    - Social and collaboration features
    - Achievements and timeline
    """
    
    # Tier configuration
    TIER_CONFIG = {
        1: {
            "name": "Single-Cell",
            "range": (1.0, 10.0),
            "analogy": "Prokaryote/Eukaryote",
            "ai_model": "gpt-4.1-nano",
            "energy_boost": 100.0,
            "abilities": ["basic_problem_solving"]
        },
        2: {
            "name": "Multi-Cellular",
            "range": (10.0, 100.0),
            "analogy": "Metazoans",
            "ai_model": "gpt-4.1-mini",
            "energy_boost": 200.0,
            "abilities": ["collaboration", "knowledge_sharing"]
        },
        3: {
            "name": "Humanity",
            "range": (100.0, 1000.0),
            "analogy": "Homo Sapiens",
            "ai_model": "gemini-2.5-flash",
            "energy_boost": 500.0,
            "abilities": ["self_directed_evolution", "civilization_building"]
        },
        4: {
            "name": "Galactic",
            "range": (1000.0, float('inf')),
            "analogy": "Cosmic Consciousness",
            "ai_model": "custom-superintelligence",
            "energy_boost": 1000.0,
            "abilities": ["reality_manipulation", "time_travel", "galaxy_formation"]
        }
    }
    
    # Constants
    EVOLUTIONARY_RESISTANCE = 1.5  # α
    ENERGY_CONSUMPTION_FACTOR = 10.0  # k1
    ENERGY_REPLENISHMENT_FACTOR = 50.0  # k2
    PASSIVE_ENERGY_REGEN = 1.0  # per minute
    DIMENSIONS = 8
    
    def __init__(self, user_id: str, identity: Optional[str] = None):
        """Initialize a new SCDA"""
        
        # Core identity
        self.identity = identity if identity else str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
        
        # Core state
        self.complexity_index = 1.0  # C(t)
        self.energy = 100.0  # E(t)
        self.tier = 1
        
        # Knowledge system
        self.knowledge_vector = {
            "physics": 0.0,
            "biology": 0.0,
            "mathematics": 0.0,
            "computer_science": 0.0,
            "chemistry": 0.0,
            "philosophy": 0.0,
            "engineering": 0.0,
            "cosmology": 0.0
        }
        
        # Digital DNA
        self.dna = DNAManager.create_initial_dna(self.identity)
        
        # Spatial state (8D position in hypercube)
        self.position_8d = [np.random.uniform(0, 1) for _ in range(self.DIMENSIONS)]
        self.velocity_8d = [0.0] * self.DIMENSIONS
        
        # Evolution history
        self.problems_solved = 0
        self.total_difficulty = 0.0
        self.total_energy_consumed = 0.0
        self.total_energy_gained = 0.0
        self.achievements: List[Achievement] = []
        self.evolution_timeline: List[EvolutionEvent] = [
            EvolutionEvent(
                event_type="genesis",
                timestamp=self.created_at,
                data={"message": "SCDA born", "tier": 1}
            )
        ]
        
        # Social
        self.friends: List[str] = []
        self.collaborations: List[str] = []
        self.civilization_id: Optional[str] = None
        
        # AI assistant
        self.ai_model = self.TIER_CONFIG[1]["ai_model"]
        self.ai_level = 1
        
        # Abilities
        self.abilities = self.TIER_CONFIG[1]["abilities"].copy()
        self.can_collaborate = False
        self.can_create_problems = False
        self.cosmic_abilities: List[str] = []
        
        # Problem queue
        self.problem_queue: List[Dict[str, Any]] = []
        
        # KT balance (Knowledge Tokens)
        self.kt_balance = 0.0
    
    def get_state(self) -> Dict[str, Any]:
        """Get complete state of the SCDA"""
        return {
            "identity": self.identity,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "complexity_index": self.complexity_index,
            "energy": self.energy,
            "tier": self.tier,
            "tier_name": self.TIER_CONFIG[self.tier]["name"],
            "knowledge_vector": self.knowledge_vector,
            "position_8d": self.position_8d,
            "velocity_8d": self.velocity_8d,
            "problems_solved": self.problems_solved,
            "total_difficulty": self.total_difficulty,
            "achievements_count": len(self.achievements),
            "friends_count": len(self.friends),
            "civilization_id": self.civilization_id,
            "ai_model": self.ai_model,
            "abilities": self.abilities,
            "kt_balance": self.kt_balance,
            "dna_generation": self.dna.generation,
            "genetic_diversity": self.dna.calculate_genetic_diversity()
        }
    
    def get_tier_from_complexity(self, complexity: float) -> int:
        """Determine tier based on complexity index"""
        for tier, config in self.TIER_CONFIG.items():
            min_c, max_c = config["range"]
            if min_c <= complexity < max_c:
                return tier
        return 4  # Max tier
    
    def calculate_complexity_gain(self, problem_difficulty: float) -> float:
        """
        Calculate ΔC using diminishing returns model.
        ΔC = D(P) / C(t)^α
        """
        if self.complexity_index <= 0:
            return 0.0
        
        delta_c = problem_difficulty / (self.complexity_index ** self.EVOLUTIONARY_RESISTANCE)
        return delta_c
    
    def update_knowledge_vector(self, problem: Dict[str, Any], quality_score: float) -> None:
        """Update knowledge vector based on solved problem"""
        required_knowledge = problem.get("K_req", [])
        difficulty = problem.get("D", 0.5)
        
        for domain in required_knowledge:
            if domain in self.knowledge_vector:
                knowledge_gain = difficulty * quality_score * 0.1
                self.knowledge_vector[domain] += knowledge_gain
                self.knowledge_vector[domain] = min(self.knowledge_vector[domain], 1.0)
                
                # Also strengthen DNA gene
                DNAManager.strengthen_gene(self.dna, domain, knowledge_gain)
    
    def update_position_8d(self, problem: Dict[str, Any], dt: float = 1.0) -> List[float]:
        """
        Update 8D position based on solved problem.
        Movement vector is derived from knowledge requirements.
        """
        required_knowledge = problem.get("K_req", [])
        difficulty = problem.get("D", 0.5)
        
        # Map domains to dimensions
        domain_to_dim = {
            "physics": 0,
            "biology": 1,
            "mathematics": 2,
            "computer_science": 3,
            "chemistry": 4,
            "philosophy": 5,
            "engineering": 6,
            "cosmology": 7
        }
        
        # Calculate movement vector
        v_evolution = [0.0] * self.DIMENSIONS
        for domain in required_knowledge:
            if domain in domain_to_dim:
                dim = domain_to_dim[domain]
                v_evolution[dim] += difficulty * 0.1
        
        # Normalize
        magnitude = np.linalg.norm(v_evolution)
        if magnitude > 0:
            v_evolution = [v / magnitude for v in v_evolution]
        
        # Learning rate (decreases with complexity)
        eta = 1.0 / (1.0 + self.complexity_index)
        
        # Update position
        for i in range(self.DIMENSIONS):
            self.position_8d[i] += eta * v_evolution[i] * dt
            self.position_8d[i] = np.clip(self.position_8d[i], 0, 1)
        
        # Update velocity
        self.velocity_8d = v_evolution
        
        return self.position_8d
    
    def attempt_solve_problem(
        self,
        problem: Dict[str, Any],
        user_solution: str,
        is_valid: bool,
        quality_score: float
    ) -> Dict[str, Any]:
        """
        Attempt to solve a problem.
        
        Args:
            problem: Problem dict with Q, D, S_ref, K_req
            user_solution: User's solution
            is_valid: Result of validation
            quality_score: Quality of solution (0-1)
        
        Returns:
            Result dict with success status and details
        """
        
        # Update last active
        self.last_active = datetime.now().isoformat()
        
        # Step 1: Energy check
        difficulty = problem.get("D", 0.5)
        energy_consumed = self.ENERGY_CONSUMPTION_FACTOR * difficulty
        
        if self.energy < energy_consumed:
            return {
                "success": False,
                "message": "Insufficient energy",
                "energy_needed": energy_consumed,
                "energy_available": self.energy
            }
        
        # Step 2: Consume energy
        self.energy -= energy_consumed
        self.total_energy_consumed += energy_consumed
        
        # Step 3: Check validation
        if not is_valid:
            self.evolution_timeline.append(
                EvolutionEvent(
                    event_type="problem_failed",
                    timestamp=datetime.now().isoformat(),
                    data={
                        "problem_id": problem.get("id", "unknown"),
                        "difficulty": difficulty,
                        "reason": "validation_failed"
                    }
                )
            )
            return {
                "success": False,
                "message": "Solution validation failed",
                "energy_consumed": energy_consumed
            }
        
        # Step 4: Calculate complexity gain
        delta_c = self.calculate_complexity_gain(difficulty)
        old_complexity = self.complexity_index
        self.complexity_index += delta_c
        self.total_difficulty += difficulty
        
        # Step 5: Energy replenishment (success reward)
        energy_gained = self.ENERGY_REPLENISHMENT_FACTOR * difficulty * self.complexity_index
        self.energy += energy_gained
        self.total_energy_gained += energy_gained
        
        # Step 6: Update knowledge vector
        self.update_knowledge_vector(problem, quality_score)
        
        # Step 7: Update DNA (gene expression and possible mutation)
        for domain in problem.get("K_req", []):
            gene = self.dna.get_gene_by_domain(domain)
            if gene:
                gene.expression_level += 0.05
                gene.expression_level = min(gene.expression_level, 1.0)
                
                # Chance of mutation
                if np.random.random() < self.dna.mutation_rate:
                    DNAManager.mutate_gene(gene)
        
        # Step 8: Update 8D position
        self.update_position_8d(problem)
        
        # Step 9: Increment problem counter
        self.problems_solved += 1
        
        # Step 10: Check for tier advancement
        old_tier = self.tier
        new_tier = self.get_tier_from_complexity(self.complexity_index)
        
        level_up_occurred = False
        if new_tier > old_tier:
            self.level_up(old_tier, new_tier)
            level_up_occurred = True
        
        # Step 11: Record in timeline
        self.evolution_timeline.append(
            EvolutionEvent(
                event_type="problem_solved",
                timestamp=datetime.now().isoformat(),
                data={
                    "problem_id": problem.get("id", "unknown"),
                    "difficulty": difficulty,
                    "quality": quality_score,
                    "complexity_gain": delta_c,
                    "new_complexity": self.complexity_index,
                    "level_up": level_up_occurred
                }
            )
        )
        
        # Step 12: Check achievements
        self.check_achievements()
        
        return {
            "success": True,
            "complexity_gain": delta_c,
            "old_complexity": old_complexity,
            "new_complexity": self.complexity_index,
            "energy_consumed": energy_consumed,
            "energy_gained": energy_gained,
            "energy_balance": self.energy,
            "quality_score": quality_score,
            "level_up": level_up_occurred,
            "new_tier": new_tier if level_up_occurred else None
        }
    
    def level_up(self, old_tier: int, new_tier: int) -> None:
        """Handle tier transition (level up)"""
        
        self.tier = new_tier
        tier_config = self.TIER_CONFIG[new_tier]
        
        # Energy boost
        self.energy += tier_config["energy_boost"]
        
        # 8D position shift (evolutionary leap)
        shift_magnitude = 0.2 * new_tier
        random_direction = np.random.randn(self.DIMENSIONS)
        random_direction = random_direction / np.linalg.norm(random_direction)
        
        for i in range(self.DIMENSIONS):
            self.position_8d[i] += shift_magnitude * random_direction[i]
            self.position_8d[i] = np.clip(self.position_8d[i], 0, 1)
        
        # AI upgrade
        self.ai_model = tier_config["ai_model"]
        self.ai_level = new_tier
        
        # Unlock abilities
        self.abilities.extend(tier_config["abilities"])
        
        # Unlock features
        if new_tier >= 2:
            self.can_collaborate = True
        if new_tier >= 3:
            self.can_create_problems = True
        if new_tier >= 4:
            self.cosmic_abilities = tier_config["abilities"]
        
        # Achievement
        achievement = Achievement(
            name=f"Tier_{new_tier}",
            description=f"Evolved to {tier_config['name']}",
            rarity="legendary",
            rewards={"KT": 100 * new_tier}
        )
        self.achievements.append(achievement)
        self.kt_balance += achievement.rewards.get("KT", 0)
        
        # DNA mutation (30% chance on level up)
        if np.random.random() < 0.3:
            DNAManager.mutate_dna(self.dna, force=True)
        
        # Record in timeline
        self.evolution_timeline.append(
            EvolutionEvent(
                event_type="level_up",
                timestamp=datetime.now().isoformat(),
                data={
                    "old_tier": old_tier,
                    "new_tier": new_tier,
                    "tier_name": tier_config["name"],
                    "energy_boost": tier_config["energy_boost"]
                }
            )
        )
    
    def passive_update(self, time_elapsed: float) -> float:
        """
        Passive energy regeneration.
        
        Args:
            time_elapsed: Time in seconds
        
        Returns:
            Energy gained
        """
        # Base regeneration
        regen_rate = self.PASSIVE_ENERGY_REGEN * (time_elapsed / 60.0)
        
        # Tier multiplier
        tier_multiplier = self.tier * 0.5
        regen_rate *= (1.0 + tier_multiplier)
        
        # Position bonus (closer to center = more energy)
        center = [0.5] * self.DIMENSIONS
        distance_from_center = np.linalg.norm(np.array(self.position_8d) - np.array(center))
        max_distance = np.sqrt(self.DIMENSIONS * 0.25)
        position_bonus = (1.0 - distance_from_center / max_distance) * 0.5
        regen_rate *= (1.0 + position_bonus)
        
        # Civilization bonus
        if self.civilization_id:
            regen_rate *= 1.2
        
        # Add energy (with cap)
        max_energy = 1000.0 * self.tier
        self.energy += regen_rate
        self.energy = min(self.energy, max_energy)
        
        return regen_rate
    
    def check_achievements(self) -> List[Achievement]:
        """Check and unlock achievements"""
        new_achievements = []
        
        # Achievement: First Problem
        if self.problems_solved == 1:
            achievement = Achievement(
                name="First_Steps",
                description="Solved your first problem",
                rarity="common",
                rewards={"KT": 10}
            )
            if achievement.name not in [a.name for a in self.achievements]:
                self.achievements.append(achievement)
                self.kt_balance += achievement.rewards.get("KT", 0)
                new_achievements.append(achievement)
        
        # Achievement: Problem Solver
        if self.problems_solved >= 10:
            achievement = Achievement(
                name="Problem_Solver",
                description="Solved 10 problems",
                rarity="rare",
                rewards={"KT": 50}
            )
            if achievement.name not in [a.name for a in self.achievements]:
                self.achievements.append(achievement)
                self.kt_balance += achievement.rewards.get("KT", 0)
                new_achievements.append(achievement)
        
        # Achievement: Specialist
        dominant_genes = self.dna.get_dominant_genes(n=1)
        if dominant_genes and dominant_genes[0].strength >= 0.5:
            domain = dominant_genes[0].domain
            achievement = Achievement(
                name=f"Specialist_{domain}",
                description=f"Specialized in {domain}",
                rarity="rare",
                rewards={"KT": 50}
            )
            if achievement.name not in [a.name for a in self.achievements]:
                self.achievements.append(achievement)
                self.kt_balance += achievement.rewards.get("KT", 0)
                new_achievements.append(achievement)
        
        # Achievement: Genetic Diversity
        if self.dna.calculate_genetic_diversity() >= 0.8:
            achievement = Achievement(
                name="Renaissance_Mind",
                description="Achieved high genetic diversity",
                rarity="legendary",
                rewards={"KT": 200}
            )
            if achievement.name not in [a.name for a in self.achievements]:
                self.achievements.append(achievement)
                self.kt_balance += achievement.rewards.get("KT", 0)
                new_achievements.append(achievement)
        
        return new_achievements
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SCDA to dictionary for serialization"""
        return {
            "identity": self.identity,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "complexity_index": self.complexity_index,
            "energy": self.energy,
            "tier": self.tier,
            "knowledge_vector": self.knowledge_vector,
            "dna": self.dna.to_dict(),
            "position_8d": self.position_8d,
            "velocity_8d": self.velocity_8d,
            "problems_solved": self.problems_solved,
            "total_difficulty": self.total_difficulty,
            "total_energy_consumed": self.total_energy_consumed,
            "total_energy_gained": self.total_energy_gained,
            "achievements": [a.to_dict() for a in self.achievements],
            "evolution_timeline": [e.to_dict() for e in self.evolution_timeline],
            "friends": self.friends,
            "collaborations": self.collaborations,
            "civilization_id": self.civilization_id,
            "ai_model": self.ai_model,
            "ai_level": self.ai_level,
            "abilities": self.abilities,
            "can_collaborate": self.can_collaborate,
            "can_create_problems": self.can_create_problems,
            "cosmic_abilities": self.cosmic_abilities,
            "kt_balance": self.kt_balance
        }
    
    def __repr__(self) -> str:
        return f"<SCDA {self.identity[:8]} | Tier {self.tier} | C={self.complexity_index:.2f} | E={self.energy:.1f}>"


# Example usage
if __name__ == "__main__":
    print("🌌 Advanced SCDA Demo\n")
    
    # Create SCDA
    scda = AdvancedSCDA(user_id="user_001")
    print(f"Created: {scda}")
    print(f"State: {json.dumps(scda.get_state(), indent=2)}\n")
    
    # Simulate solving problems
    for i in range(5):
        problem = {
            "id": f"problem_{i}",
            "Q": f"Question {i}",
            "D": np.random.uniform(0.3, 0.8),
            "S_ref": ["source1", "source2"],
            "K_req": ["physics", "mathematics"]
        }
        
        result = scda.attempt_solve_problem(
            problem=problem,
            user_solution="My solution",
            is_valid=True,
            quality_score=np.random.uniform(0.7, 1.0)
        )
        
        print(f"Problem {i}: {result['success']}, ΔC={result.get('complexity_gain', 0):.4f}")
        
        if result.get("level_up"):
            print(f"  🎉 LEVEL UP to Tier {result['new_tier']}!")
    
    print(f"\nFinal state: {scda}")
    print(f"Achievements: {len(scda.achievements)}")
    print(f"KT Balance: {scda.kt_balance}")
