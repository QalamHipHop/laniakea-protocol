"""
Unified System V0.0.03
Integrates all components: SCDA, Blockchain, Metaverse, Evolution
"""

import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Import all components
import sys
sys.path.insert(0, '/home/ubuntu/laniakea-protocol')

from laniakea.intelligence.advanced_scda import AdvancedSCDA
from laniakea.intelligence.digital_dna import DNAManager
from laniakea.metaverse.advanced_metaverse import AdvancedMetaverse
from laniakea.evolution.complete_evolution_manager import EvolutionManager


class UnifiedLaniakeaSystem:
    """
    The complete unified system that brings together all components.
    
    This is the main interface for interacting with the LaniakeA Protocol.
    """
    
    def __init__(self):
        """Initialize the unified system"""
        print("🌌 Initializing LaniakeA Protocol V0.0.03...")
        
        # Core components
        self.metaverse = AdvancedMetaverse()
        self.evolution_manager = EvolutionManager()
        
        # SCDA registry
        self.scdas: Dict[str, AdvancedSCDA] = {}
        
        # User mapping
        self.user_to_scda: Dict[str, str] = {}  # user_id -> scda_id
        
        # System statistics
        self.total_problems_solved = 0
        self.total_complexity_gained = 0.0
        self.total_level_ups = 0
        
        print("✅ LaniakeA Protocol initialized successfully")
    
    def create_scda(self, user_id: str) -> AdvancedSCDA:
        """Create a new SCDA for a user"""
        
        # Check if user already has an SCDA
        if user_id in self.user_to_scda:
            existing_id = self.user_to_scda[user_id]
            return self.scdas[existing_id]
        
        # Create new SCDA
        scda = AdvancedSCDA(user_id=user_id)
        
        # Register in system
        self.scdas[scda.identity] = scda
        self.user_to_scda[user_id] = scda.identity
        
        # Register in metaverse
        self.metaverse.register_scda(
            scda_id=scda.identity,
            position_8d=scda.position_8d,
            metadata={
                "tier": scda.tier,
                "complexity_index": scda.complexity_index,
                "energy": scda.energy,
                "created_at": scda.created_at
            }
        )
        
        print(f"✨ Created SCDA for user {user_id}: {scda.identity[:8]}...")
        
        return scda
    
    def get_scda(self, scda_id: str) -> Optional[AdvancedSCDA]:
        """Get SCDA by ID"""
        return self.scdas.get(scda_id)
    
    def get_scda_by_user(self, user_id: str) -> Optional[AdvancedSCDA]:
        """Get SCDA by user ID"""
        scda_id = self.user_to_scda.get(user_id)
        if scda_id:
            return self.scdas.get(scda_id)
        return None
    
    def solve_problem(
        self,
        scda_id: str,
        problem: Dict[str, Any],
        user_solution: str,
        is_valid: bool,
        quality_score: float
    ) -> Dict[str, Any]:
        """
        Complete problem-solving workflow with full integration.
        """
        
        scda = self.get_scda(scda_id)
        if not scda:
            return {"error": "SCDA not found"}
        
        # Store old state for comparison
        old_complexity = scda.complexity_index
        old_tier = scda.tier
        old_position = scda.position_8d.copy()
        
        # SCDA attempts to solve
        result = scda.attempt_solve_problem(
            problem=problem,
            user_solution=user_solution,
            is_valid=is_valid,
            quality_score=quality_score
        )
        
        if not result["success"]:
            return result
        
        # Update system statistics
        self.total_problems_solved += 1
        self.total_complexity_gained += result["complexity_gain"]
        
        if result.get("level_up"):
            self.total_level_ups += 1
        
        # Update metaverse position
        self.metaverse.update_scda_position(
            scda_id=scda_id,
            new_position=scda.position_8d
        )
        
        # Update metaverse metadata
        self.metaverse.scda_metadata[scda_id].update({
            "tier": scda.tier,
            "complexity_index": scda.complexity_index,
            "energy": scda.energy,
            "problems_solved": scda.problems_solved
        })
        
        # Check for milestones
        milestones = self.evolution_manager.check_milestones(
            scda_id=scda_id,
            old_complexity=old_complexity,
            new_complexity=scda.complexity_index,
            tier=scda.tier
        )
        
        # Add milestones to result
        result["milestones_unlocked"] = milestones
        
        # Check for cosmic events (if tier 4)
        if scda.tier >= 4 and result.get("level_up"):
            # Trigger cosmic event
            event = self.metaverse.trigger_cosmic_event(
                event_type="supernova",
                epicenter=scda.position_8d,
                triggered_by=scda_id
            )
            result["cosmic_event"] = event.to_dict()
        
        return result
    
    def collaborate(
        self,
        scda_ids: List[str],
        problem: Dict[str, Any],
        combined_solution: str
    ) -> Dict[str, Any]:
        """
        Collaborative problem solving.
        """
        
        # Validate all SCDAs
        scdas = []
        for scda_id in scda_ids:
            scda = self.get_scda(scda_id)
            if not scda:
                return {"error": f"SCDA {scda_id} not found"}
            if not scda.can_collaborate:
                return {"error": f"SCDA {scda_id} cannot collaborate (Tier 2+ required)"}
            scdas.append(scda)
        
        # Calculate collective knowledge
        collective_knowledge = {}
        for domain in scdas[0].knowledge_vector.keys():
            collective_knowledge[domain] = np.mean([
                scda.knowledge_vector[domain] for scda in scdas
            ])
        
        # Validate solution (simplified)
        is_valid = True
        quality_score = 0.85
        
        # Distribute rewards
        difficulty = problem.get("D", 0.5)
        avg_complexity = np.mean([scda.complexity_index for scda in scdas])
        
        delta_c_total = difficulty / (avg_complexity ** 1.5)
        
        results = []
        for scda in scdas:
            share = 1.0 / len(scdas)  # Equal share for simplicity
            
            scda.complexity_index += delta_c_total * share
            scda.energy += 50.0 * difficulty * share
            scda.problems_solved += 1
            
            # Update knowledge
            scda.update_knowledge_vector(problem, quality_score)
            
            # DNA exchange (20% chance)
            if len(scdas) >= 2 and np.random.random() < 0.2:
                other_scda = np.random.choice([s for s in scdas if s != scda])
                domain = np.random.choice(list(scda.knowledge_vector.keys()))
                DNAManager.exchange_genes(scda.dna, other_scda.dna, domain)
            
            results.append({
                "scda_id": scda.identity,
                "complexity_gain": delta_c_total * share,
                "new_complexity": scda.complexity_index
            })
        
        return {
            "success": True,
            "collaboration_id": str(uuid.uuid4()),
            "participants": len(scdas),
            "results": results
        }
    
    def create_civilization(
        self,
        founder_scda_id: str,
        name: str,
        government_type: str = "democracy"
    ) -> Dict[str, Any]:
        """Create a civilization"""
        
        scda = self.get_scda(founder_scda_id)
        if not scda:
            return {"error": "SCDA not found"}
        
        if scda.tier < 3:
            return {"error": "Tier 3 required to create civilization"}
        
        if scda.energy < 500.0:
            return {"error": "Insufficient energy (need 500)"}
        
        # Create in metaverse
        civilization = self.metaverse.create_civilization(
            founder_id=founder_scda_id,
            name=name,
            government_type=government_type
        )
        
        # Deduct energy
        scda.energy -= 500.0
        
        # Update SCDA
        scda.civilization_id = civilization.id
        
        return {
            "success": True,
            "civilization_id": civilization.id,
            "name": name
        }
    
    def create_galaxy(
        self,
        core_scda_ids: List[str],
        name: str
    ) -> Dict[str, Any]:
        """Create a galaxy"""
        
        # Validate all SCDAs are Tier 4
        for scda_id in core_scda_ids:
            scda = self.get_scda(scda_id)
            if not scda:
                return {"error": f"SCDA {scda_id} not found"}
            if scda.tier < 4:
                return {"error": f"All SCDAs must be Tier 4"}
        
        # Create in metaverse
        galaxy = self.metaverse.create_galaxy(
            core_members=core_scda_ids,
            name=name
        )
        
        # Update SCDAs
        for scda_id in core_scda_ids:
            scda = self.get_scda(scda_id)
            if scda:
                scda.cosmic_abilities = ["reality_manipulation", "time_travel", "galaxy_formation"]
        
        return {
            "success": True,
            "galaxy_id": galaxy.id,
            "name": name,
            "collective_complexity": galaxy.collective_complexity
        }
    
    def get_evolution_report(self, scda_id: str) -> Dict[str, Any]:
        """Get comprehensive evolution report"""
        
        scda = self.get_scda(scda_id)
        if not scda:
            return {"error": "SCDA not found"}
        
        # Calculate time active
        created = datetime.fromisoformat(scda.created_at)
        now = datetime.now()
        time_active = (now - created).total_seconds()
        
        report = self.evolution_manager.generate_evolution_report(
            scda_id=scda_id,
            complexity=scda.complexity_index,
            tier=scda.tier,
            problems_solved=scda.problems_solved,
            total_difficulty=scda.total_difficulty,
            time_active=time_active,
            knowledge_vector=scda.knowledge_vector
        )
        
        # Add DNA info
        report["dna"] = {
            "generation": scda.dna.generation,
            "genetic_diversity": scda.dna.calculate_genetic_diversity(),
            "dominant_genes": [
                {"domain": g.domain, "strength": g.strength}
                for g in scda.dna.get_dominant_genes(3)
            ]
        }
        
        # Add metaverse info
        report["metaverse"] = {
            "position_8d": scda.position_8d,
            "civilization_id": scda.civilization_id,
            "nearby_scdas": len(self.metaverse.find_nearby_scda(scda.position_8d, radius=0.3))
        }
        
        return report
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "version": "0.0.03",
            "statistics": {
                "total_scdas": len(self.scdas),
                "total_problems_solved": self.total_problems_solved,
                "total_complexity_gained": self.total_complexity_gained,
                "total_level_ups": self.total_level_ups
            },
            "metaverse": self.metaverse.get_metaverse_status(),
            "tier_distribution": self._get_tier_distribution(),
            "top_scdas": self._get_top_scdas(n=5)
        }
    
    def _get_tier_distribution(self) -> Dict[int, int]:
        """Get distribution of SCDAs by tier"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0}
        for scda in self.scdas.values():
            distribution[scda.tier] += 1
        return distribution
    
    def _get_top_scdas(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get top N SCDAs by complexity"""
        sorted_scdas = sorted(
            self.scdas.values(),
            key=lambda s: s.complexity_index,
            reverse=True
        )
        
        return [
            {
                "scda_id": scda.identity,
                "user_id": scda.user_id,
                "complexity": scda.complexity_index,
                "tier": scda.tier,
                "problems_solved": scda.problems_solved
            }
            for scda in sorted_scdas[:n]
        ]


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("🌌 LaniakeA Protocol V0.0.03 - Unified System Demo")
    print("=" * 70)
    print()
    
    # Initialize system
    system = UnifiedLaniakeaSystem()
    print()
    
    # Create SCDAs
    print("👥 Creating SCDAs...")
    users = ["alice", "bob", "charlie"]
    for user in users:
        scda = system.create_scda(user)
        print(f"   {user}: {scda.identity[:12]}... (Tier {scda.tier}, C={scda.complexity_index:.2f})")
    print()
    
    # Simulate problem solving
    print("🔬 Simulating problem solving...")
    alice_scda = system.get_scda_by_user("alice")
    
    for i in range(5):
        problem = {
            "id": f"problem_{i}",
            "Q": f"Scientific question {i}",
            "D": np.random.uniform(0.4, 0.8),
            "S_ref": ["source1", "source2"],
            "K_req": ["physics", "mathematics"]
        }
        
        result = system.solve_problem(
            scda_id=alice_scda.identity,
            problem=problem,
            user_solution="My solution",
            is_valid=True,
            quality_score=0.85
        )
        
        if result["success"]:
            print(f"   Problem {i}: ΔC={result['complexity_gain']:.4f}, C={result['new_complexity']:.2f}")
            if result.get("level_up"):
                print(f"      🎉 LEVEL UP to Tier {result['new_tier']}!")
    print()
    
    # Evolution report
    print("📊 Evolution Report for Alice:")
    print("-" * 70)
    report = system.get_evolution_report(alice_scda.identity)
    print(json.dumps(report, indent=2))
    print()
    
    # System status
    print("=" * 70)
    print("🌐 System Status:")
    print("=" * 70)
    status = system.get_system_status()
    print(json.dumps(status, indent=2))
