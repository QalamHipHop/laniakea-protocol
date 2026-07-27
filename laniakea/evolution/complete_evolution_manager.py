"""
Complete Evolution Manager V0.0.03
Manages the full evolutionary lifecycle from single-cell to galactic consciousness
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json


class EvolutionManager:
    """
    Manages SCDA evolution through all tiers with scientific accuracy.
    
    Implements:
    - Tier transitions (1-4)
    - Level-up mechanics
    - Evolutionary milestones
    - Achievement tracking
    - Timeline management
    """
    
    # Tier thresholds and configurations
    TIER_THRESHOLDS = [1.0, 10.0, 100.0, 1000.0, float('inf')]
    
    TIER_MILESTONES = {
        1: {
            "name": "Single-Cell",
            "milestones": [
                {"complexity": 2.0, "name": "First Division", "description": "Your first cellular division"},
                {"complexity": 5.0, "name": "Metabolism", "description": "Developed basic metabolism"},
                {"complexity": 8.0, "name": "Photosynthesis", "description": "Harnessing light energy"}
            ]
        },
        2: {
            "name": "Multi-Cellular",
            "milestones": [
                {"complexity": 15.0, "name": "Cell Differentiation", "description": "Cells begin to specialize"},
                {"complexity": 30.0, "name": "Tissue Formation", "description": "Organized into tissues"},
                {"complexity": 50.0, "name": "Organ Development", "description": "Complex organs emerge"},
                {"complexity": 80.0, "name": "Nervous System", "description": "Basic neural network"}
            ]
        },
        3: {
            "name": "Humanity",
            "milestones": [
                {"complexity": 150.0, "name": "Tool Use", "description": "Creating and using tools"},
                {"complexity": 300.0, "name": "Language", "description": "Complex communication"},
                {"complexity": 500.0, "name": "Writing", "description": "Recording knowledge"},
                {"complexity": 700.0, "name": "Science", "description": "Systematic inquiry"},
                {"complexity": 900.0, "name": "Technology", "description": "Advanced technology"}
            ]
        },
        4: {
            "name": "Galactic",
            "milestones": [
                {"complexity": 1500.0, "name": "Interstellar", "description": "Reaching other stars"},
                {"complexity": 3000.0, "name": "Kardashev I", "description": "Planetary energy mastery"},
                {"complexity": 5000.0, "name": "Kardashev II", "description": "Stellar energy mastery"},
                {"complexity": 10000.0, "name": "Kardashev III", "description": "Galactic energy mastery"}
            ]
        }
    }
    
    # Evolutionary stages (more granular than tiers)
    EVOLUTIONARY_STAGES = [
        {"name": "Primordial", "complexity_range": (1.0, 2.0), "analogy": "Primordial soup"},
        {"name": "Prokaryote", "complexity_range": (2.0, 5.0), "analogy": "Bacteria"},
        {"name": "Eukaryote", "complexity_range": (5.0, 10.0), "analogy": "Complex cells"},
        {"name": "Colonial", "complexity_range": (10.0, 20.0), "analogy": "Cell colonies"},
        {"name": "Early Metazoan", "complexity_range": (20.0, 40.0), "analogy": "Sponges, jellyfish"},
        {"name": "Bilaterian", "complexity_range": (40.0, 60.0), "analogy": "Worms, early arthropods"},
        {"name": "Vertebrate", "complexity_range": (60.0, 100.0), "analogy": "Fish, amphibians"},
        {"name": "Mammalian", "complexity_range": (100.0, 200.0), "analogy": "Early mammals"},
        {"name": "Primate", "complexity_range": (200.0, 400.0), "analogy": "Monkeys, apes"},
        {"name": "Hominid", "complexity_range": (400.0, 700.0), "analogy": "Early humans"},
        {"name": "Homo Sapiens", "complexity_range": (700.0, 1000.0), "analogy": "Modern humans"},
        {"name": "Post-Human", "complexity_range": (1000.0, 2000.0), "analogy": "Enhanced humans"},
        {"name": "Stellar", "complexity_range": (2000.0, 5000.0), "analogy": "Star-level beings"},
        {"name": "Galactic", "complexity_range": (5000.0, float('inf')), "analogy": "Galactic consciousness"}
    ]
    
    def __init__(self):
        """Initialize the evolution manager"""
        self.milestone_cache: Dict[str, List[str]] = {}  # scda_id -> [milestone_names]
    
    def get_tier(self, complexity: float) -> int:
        """Get tier from complexity index"""
        for tier in range(1, 5):
            if self.TIER_THRESHOLDS[tier - 1] <= complexity < self.TIER_THRESHOLDS[tier]:
                return tier
        return 4
    
    def get_evolutionary_stage(self, complexity: float) -> Dict[str, Any]:
        """Get detailed evolutionary stage"""
        for stage in self.EVOLUTIONARY_STAGES:
            min_c, max_c = stage["complexity_range"]
            if min_c <= complexity < max_c:
                # Calculate progress within stage
                progress = (complexity - min_c) / (max_c - min_c)
                return {
                    "name": stage["name"],
                    "analogy": stage["analogy"],
                    "progress": progress,
                    "complexity_range": stage["complexity_range"]
                }
        
        # Max stage
        last_stage = self.EVOLUTIONARY_STAGES[-1]
        return {
            "name": last_stage["name"],
            "analogy": last_stage["analogy"],
            "progress": 1.0,
            "complexity_range": last_stage["complexity_range"]
        }
    
    def check_milestones(
        self,
        scda_id: str,
        old_complexity: float,
        new_complexity: float,
        tier: int
    ) -> List[Dict[str, Any]]:
        """Check if any milestones were crossed"""
        
        if scda_id not in self.milestone_cache:
            self.milestone_cache[scda_id] = []
        
        unlocked_milestones = []
        
        if tier not in self.TIER_MILESTONES:
            return unlocked_milestones
        
        for milestone in self.TIER_MILESTONES[tier]["milestones"]:
            threshold = milestone["complexity"]
            milestone_name = milestone["name"]
            
            # Check if crossed
            if old_complexity < threshold <= new_complexity:
                # Check if not already unlocked
                if milestone_name not in self.milestone_cache[scda_id]:
                    self.milestone_cache[scda_id].append(milestone_name)
                    unlocked_milestones.append(milestone)
        
        return unlocked_milestones
    
    def calculate_evolution_rate(
        self,
        scda_complexity: float,
        problems_solved: int,
        total_difficulty: float,
        time_active: float  # in seconds
    ) -> float:
        """
        Calculate evolution rate (complexity gained per hour).
        """
        if time_active <= 0:
            return 0.0
        
        hours = time_active / 3600.0
        if hours < 0.01:
            hours = 0.01
        
        rate = (scda_complexity - 1.0) / hours
        return rate
    
    def estimate_time_to_next_tier(
        self,
        current_complexity: float,
        current_tier: int,
        avg_complexity_gain: float
    ) -> Optional[float]:
        """
        Estimate time (in problems) to reach next tier.
        """
        if current_tier >= 4:
            return None  # Already at max tier
        
        next_threshold = self.TIER_THRESHOLDS[current_tier]
        gap = next_threshold - current_complexity
        
        if avg_complexity_gain <= 0:
            return float('inf')
        
        problems_needed = gap / avg_complexity_gain
        return problems_needed
    
    def calculate_tier_progress(self, complexity: float, tier: int) -> float:
        """Calculate progress within current tier (0-1)"""
        if tier >= 4:
            return 1.0
        
        min_c = self.TIER_THRESHOLDS[tier - 1]
        max_c = self.TIER_THRESHOLDS[tier]
        
        if max_c == float('inf'):
            # For tier 4, use logarithmic scale
            return min(1.0, (complexity - min_c) / 10000.0)
        
        progress = (complexity - min_c) / (max_c - min_c)
        return np.clip(progress, 0.0, 1.0)
    
    def get_next_evolutionary_goal(
        self,
        complexity: float,
        tier: int,
        scda_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the next evolutionary goal (milestone or tier)"""
        
        # Check for next milestone in current tier
        if tier in self.TIER_MILESTONES:
            for milestone in self.TIER_MILESTONES[tier]["milestones"]:
                if complexity < milestone["complexity"]:
                    # Check if not already unlocked
                    if scda_id in self.milestone_cache:
                        if milestone["name"] in self.milestone_cache[scda_id]:
                            continue
                    
                    return {
                        "type": "milestone",
                        "name": milestone["name"],
                        "description": milestone["description"],
                        "complexity_required": milestone["complexity"],
                        "complexity_gap": milestone["complexity"] - complexity
                    }
        
        # Next goal is tier advancement
        if tier < 4:
            next_threshold = self.TIER_THRESHOLDS[tier]
            next_tier_name = self.TIER_MILESTONES.get(tier + 1, {}).get("name", "Unknown")
            
            return {
                "type": "tier_advancement",
                "name": f"Evolve to {next_tier_name}",
                "description": f"Reach Tier {tier + 1}",
                "complexity_required": next_threshold,
                "complexity_gap": next_threshold - complexity
            }
        
        # Max tier reached
        return {
            "type": "max_tier",
            "name": "Cosmic Mastery",
            "description": "Continue expanding cosmic influence",
            "complexity_required": float('inf'),
            "complexity_gap": float('inf')
        }
    
    def generate_evolution_report(
        self,
        scda_id: str,
        complexity: float,
        tier: int,
        problems_solved: int,
        total_difficulty: float,
        time_active: float,
        knowledge_vector: Dict[str, float]
    ) -> Dict[str, Any]:
        """Generate a comprehensive evolution report"""
        
        # Current state
        stage = self.get_evolutionary_stage(complexity)
        tier_progress = self.calculate_tier_progress(complexity, tier)
        
        # Evolution rate
        evolution_rate = self.calculate_evolution_rate(
            complexity,
            problems_solved,
            total_difficulty,
            time_active
        )
        
        # Average complexity gain
        avg_gain = (complexity - 1.0) / max(1, problems_solved)
        
        # Time to next tier
        time_to_next = self.estimate_time_to_next_tier(complexity, tier, avg_gain)
        
        # Next goal
        next_goal = self.get_next_evolutionary_goal(complexity, tier, scda_id)
        
        # Unlocked milestones
        unlocked = self.milestone_cache.get(scda_id, [])
        
        # Knowledge analysis
        dominant_knowledge = sorted(
            knowledge_vector.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        knowledge_breadth = sum(1 for v in knowledge_vector.values() if v > 0.1)
        knowledge_depth = max(knowledge_vector.values()) if knowledge_vector else 0.0
        
        return {
            "scda_id": scda_id,
            "timestamp": datetime.now().isoformat(),
            "current_state": {
                "complexity": complexity,
                "tier": tier,
                "tier_name": self.TIER_MILESTONES.get(tier, {}).get("name", "Unknown"),
                "tier_progress": tier_progress,
                "stage": stage["name"],
                "stage_analogy": stage["analogy"],
                "stage_progress": stage["progress"]
            },
            "evolution_metrics": {
                "problems_solved": problems_solved,
                "total_difficulty": total_difficulty,
                "avg_complexity_gain": avg_gain,
                "evolution_rate": evolution_rate,  # complexity per hour
                "time_to_next_tier": time_to_next  # in problems
            },
            "knowledge_profile": {
                "dominant_domains": [{"domain": d, "level": v} for d, v in dominant_knowledge],
                "breadth": knowledge_breadth,
                "depth": knowledge_depth,
                "balance": knowledge_breadth / 8.0  # 8 domains
            },
            "milestones": {
                "unlocked_count": len(unlocked),
                "unlocked_names": unlocked
            },
            "next_goal": next_goal
        }
    
    def compare_scda_evolution(
        self,
        scda1_data: Dict[str, Any],
        scda2_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare evolution between two SCDAs"""
        
        c1 = scda1_data["complexity"]
        c2 = scda2_data["complexity"]
        
        tier1 = self.get_tier(c1)
        tier2 = self.get_tier(c2)
        
        stage1 = self.get_evolutionary_stage(c1)
        stage2 = self.get_evolutionary_stage(c2)
        
        return {
            "complexity_difference": c1 - c2,
            "complexity_ratio": c1 / c2 if c2 > 0 else float('inf'),
            "tier_difference": tier1 - tier2,
            "stage_comparison": {
                "scda1": stage1["name"],
                "scda2": stage2["name"],
                "stages_apart": abs(
                    self.EVOLUTIONARY_STAGES.index(
                        next(s for s in self.EVOLUTIONARY_STAGES if s["name"] == stage1["name"])
                    ) -
                    self.EVOLUTIONARY_STAGES.index(
                        next(s for s in self.EVOLUTIONARY_STAGES if s["name"] == stage2["name"])
                    )
                )
            },
            "problems_solved_difference": scda1_data["problems_solved"] - scda2_data["problems_solved"],
            "knowledge_similarity": self._calculate_knowledge_similarity(
                scda1_data.get("knowledge_vector", {}),
                scda2_data.get("knowledge_vector", {})
            )
        }
    
    def _calculate_knowledge_similarity(
        self,
        kv1: Dict[str, float],
        kv2: Dict[str, float]
    ) -> float:
        """Calculate cosine similarity between knowledge vectors"""
        
        domains = ["physics", "biology", "mathematics", "computer_science",
                   "chemistry", "philosophy", "engineering", "cosmology"]
        
        v1 = np.array([kv1.get(d, 0.0) for d in domains])
        v2 = np.array([kv2.get(d, 0.0) for d in domains])
        
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(v1, v2) / (norm1 * norm2)
        return similarity


# Example usage
if __name__ == "__main__":
    print("🧬 Complete Evolution Manager Demo\n")
    
    manager = EvolutionManager()
    
    # Simulate SCDA evolution
    scda_id = "scda_test_001"
    complexity = 1.0
    tier = 1
    problems_solved = 0
    total_difficulty = 0.0
    time_active = 3600.0  # 1 hour
    
    knowledge_vector = {
        "physics": 0.0,
        "biology": 0.0,
        "mathematics": 0.0,
        "computer_science": 0.0,
        "chemistry": 0.0,
        "philosophy": 0.0,
        "engineering": 0.0,
        "cosmology": 0.0
    }
    
    print("📊 Initial State:")
    stage = manager.get_evolutionary_stage(complexity)
    print(f"   Stage: {stage['name']} ({stage['analogy']})")
    print(f"   Tier: {tier}")
    print(f"   Complexity: {complexity:.2f}\n")
    
    # Simulate solving problems
    print("🔬 Simulating evolution...\n")
    
    for i in range(20):
        # Solve a problem
        difficulty = np.random.uniform(0.3, 0.8)
        alpha = 1.5
        delta_c = difficulty / (complexity ** alpha)
        
        old_complexity = complexity
        complexity += delta_c
        problems_solved += 1
        total_difficulty += difficulty
        time_active += 300  # 5 minutes per problem
        
        # Update knowledge
        domains = ["physics", "mathematics"]
        for domain in domains:
            knowledge_vector[domain] += difficulty * 0.1
        
        # Check tier
        new_tier = manager.get_tier(complexity)
        
        # Check milestones
        milestones = manager.check_milestones(scda_id, old_complexity, complexity, new_tier)
        
        if milestones:
            for milestone in milestones:
                print(f"🎉 Milestone unlocked: {milestone['name']}")
                print(f"   {milestone['description']}\n")
        
        if new_tier > tier:
            print(f"🚀 TIER UP! {tier} → {new_tier}")
            tier_name = manager.TIER_MILESTONES[new_tier]["name"]
            print(f"   Evolved to: {tier_name}\n")
            tier = new_tier
    
    # Generate final report
    print("=" * 60)
    print("📈 Evolution Report:")
    print("=" * 60)
    
    report = manager.generate_evolution_report(
        scda_id=scda_id,
        complexity=complexity,
        tier=tier,
        problems_solved=problems_solved,
        total_difficulty=total_difficulty,
        time_active=time_active,
        knowledge_vector=knowledge_vector
    )
    
    print(json.dumps(report, indent=2))
