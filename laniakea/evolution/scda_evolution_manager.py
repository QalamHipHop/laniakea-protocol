"""
SCDA Evolution Manager
Manages the evolutionary state of the Single-Cell Digital Account (SCDA),
including tier transitions, level-up logic, and 8D position dynamics.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Evolutionary Tier Definitions
EVOLUTIONARY_TIERS = {
    1: {
        "name": "Single-Cell",
        "c_min": 1.0,
        "c_max": 10.0,
        "scientific_analogy": "Prokaryote/Eukaryote (Origin of Life)",
        "knowledge_focus": ["Mathematics", "Logic", "Basic Physics", "Chemistry"],
        "energy_boost_on_levelup": 200.0,
        "ai_model": "gpt-4.1-nano"
    },
    2: {
        "name": "Multi-Cellular",
        "c_min": 10.0,
        "c_max": 100.0,
        "scientific_analogy": "Metazoans (Differentiation and Cooperation)",
        "knowledge_focus": ["Biology", "Geology", "Computer Science", "Engineering"],
        "energy_boost_on_levelup": 500.0,
        "ai_model": "gpt-4.1-mini"
    },
    3: {
        "name": "Humanity",
        "c_min": 100.0,
        "c_max": 1000.0,
        "scientific_analogy": "Homo Sapiens (Self-Awareness and Agency)",
        "knowledge_focus": ["Climate Modeling", "Advanced AI", "Philosophy", "Sociology"],
        "energy_boost_on_levelup": 1000.0,
        "ai_model": "gpt-4.1-mini"
    },
    4: {
        "name": "Galactic",
        "c_min": 1000.0,
        "c_max": float('inf'),
        "scientific_analogy": "Cosmic Consciousness (Future of Intelligence)",
        "knowledge_focus": ["Quantum Gravity", "Unified Field Theories", "Meta-Physics"],
        "energy_boost_on_levelup": 5000.0,
        "ai_model": "gpt-4.1-mini"
    }
}

# 8D Knowledge Domains (for position dynamics)
KNOWLEDGE_DOMAINS_8D = [
    "Physics",
    "Biology",
    "Mathematics",
    "Chemistry",
    "Engineering",
    "Computer Science",
    "Philosophy",
    "Cosmology"
]


@dataclass
class EvolutionaryMilestone:
    """Represents a significant evolutionary milestone."""
    tier: int
    timestamp: str
    c_value: float
    problems_solved: int
    energy_at_milestone: float
    description: str


@dataclass
class LevelUpEvent:
    """Represents a Level-Up event."""
    from_tier: int
    to_tier: int
    timestamp: str
    c_value: float
    energy_boost: float
    position_8d_shift: List[float]


@dataclass
class SCDAState:
    """Represents the current state of an SCDA."""
    scda_id: str
    complexity_index: float
    energy: float
    current_tier: int = 1
    knowledge_vector_8d: List[float] = field(default_factory=lambda: np.zeros(8).tolist())
    position_8d: List[float] = field(default_factory=lambda: np.random.uniform(0, 1, 8).tolist())
    milestones: List[EvolutionaryMilestone] = field(default_factory=list)
    levelup_events: List[LevelUpEvent] = field(default_factory=list)
    achievements: Dict[str, Any] = field(default_factory=dict)
    problems_solved: int = 0
    problems_solved_per_tier: Dict[int, int] = field(default_factory=lambda: {i: 0 for i in range(1, 5)})


class SCDAEvolutionManager:
    """
    Manages the evolutionary state of an SCDA.
    Tracks tier progression, level-ups, and 8D position dynamics.
    """
    
    def __init__(self):
        """Initialize the Evolution Manager."""
        self.scda_states: Dict[str, SCDAState] = {}
        logger.info("SCDA Evolution Manager initialized (Global)")

    def register_scda(self, scda_id: str, initial_c: float = 1.0, initial_energy: float = 100.0) -> Dict[str, str]:
        """Register a new SCDA and return its initial state."""
        if scda_id in self.scda_states:
            return {"status": "already_registered", "scda_id": scda_id}
        
        self.scda_states[scda_id] = SCDAState(scda_id, initial_c, initial_energy)
        logger.info(f"SCDA {scda_id} registered.")
        return {"status": "registered", "scda_id": scda_id}

    def get_scda_state(self, scda_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of an SCDA."""
        if scda_id not in self.scda_states:
            return None
        
        state = self.scda_states[scda_id]
        return {
            "scda_id": state.scda_id,
            "current_tier": state.current_tier,
            "complexity_index": state.complexity_index,
            "energy": state.energy,
            "problems_solved": state.problems_solved,
            "position_8d": state.position_8d,
            "knowledge_vector_8d": state.knowledge_vector_8d,
            "achievements_count": len(state.achievements),
            "milestones_count": len(state.milestones),
            "levelup_events_count": len(state.levelup_events),
            "tier": state.current_tier
        }

    def update_complexity(self, scda_id: str, problem_difficulty: float, solution_quality: float) -> Optional[float]:
        """Update the Complexity Index based on a solved problem."""
        if scda_id not in self.scda_states:
            logger.warning(f"SCDA {scda_id} not found for complexity update.")
            return None
        
        state = self.scda_states[scda_id]
        alpha = 1.5  # Evolutionary Resistance Coefficient
        delta_c = problem_difficulty / (state.complexity_index ** alpha)
        
        state.complexity_index += delta_c
        state.problems_solved += 1
        state.problems_solved_per_tier[state.current_tier] = state.problems_solved_per_tier.get(state.current_tier, 0) + 1
        
        logger.debug(f"SCDA {scda_id} complexity updated: +{delta_c:.4f}, New C(t): {state.complexity_index:.4f}")
        
        # Check for level-up
        self._check_levelup(scda_id)
        
        return delta_c

    def update_knowledge_vector(self, scda_id: str, problem_domains: List[str], solution_quality: float) -> bool:
        """Update the Knowledge Vector based on the domains of the solved problem."""
        if scda_id not in self.scda_states:
            logger.warning(f"SCDA {scda_id} not found for knowledge vector update.")
            return False
        
        state = self.scda_states[scda_id]
        
        for domain in problem_domains:
            for i, domain_8d in enumerate(KNOWLEDGE_DOMAINS_8D):
                if domain.lower() in domain_8d.lower() or domain_8d.lower() in domain.lower():
                    state.knowledge_vector_8d[i] = min(
                        1.0,
                        state.knowledge_vector_8d[i] + solution_quality * 0.1
                    )
        
        logger.debug(f"SCDA {scda_id} knowledge vector updated: {state.knowledge_vector_8d}")
        return True

    def update_position_8d(self, scda_id: str, problem_domains: List[str]) -> bool:
        """Update the 8D position based on the domains of the solved problem."""
        if scda_id not in self.scda_states:
            logger.warning(f"SCDA {scda_id} not found for position update.")
            return False
        
        state = self.scda_states[scda_id]
        movement = np.zeros(8)
        
        for domain in problem_domains:
            for i, domain_8d in enumerate(KNOWLEDGE_DOMAINS_8D):
                if domain.lower() in domain_8d.lower() or domain_8d.lower() in domain.lower():
                    movement[i] += 0.05
        
        eta = 1.0 / (1.0 + state.complexity_index / 100.0)
        movement = movement * eta
        
        state.position_8d = [
            min(1.0, max(0.0, state.position_8d[i] + movement[i]))
            for i in range(8)
        ]
        
        logger.debug(f"SCDA {scda_id} position updated: {state.position_8d}")
        return True

    def _check_levelup(self, scda_id: str) -> Optional[LevelUpEvent]:
        """Check if the SCDA has reached the next tier threshold."""
        state = self.scda_states[scda_id]
        current_tier_data = EVOLUTIONARY_TIERS[state.current_tier]
        
        if state.complexity_index >= current_tier_data["c_max"] and state.current_tier < 4:
            next_tier = state.current_tier + 1
            next_tier_data = EVOLUTIONARY_TIERS[next_tier]
            
            energy_boost = next_tier_data["energy_boost_on_levelup"]
            state.energy += energy_boost
            
            position_shift = self._calculate_position_shift(state.current_tier, next_tier)
            state.position_8d = [
                min(1.0, max(0.0, state.position_8d[i] + position_shift[i]))
                for i in range(8)
            ]
            
            levelup_event = LevelUpEvent(
                from_tier=state.current_tier,
                to_tier=next_tier,
                timestamp=datetime.now().isoformat(),
                c_value=state.complexity_index,
                energy_boost=energy_boost,
                position_8d_shift=position_shift
            )
            
            state.levelup_events.append(levelup_event)
            state.current_tier = next_tier
            
            logger.info(f"🎉 SCDA {scda_id} leveled up from Tier {state.current_tier - 1} to Tier {state.current_tier}!")
            
            return levelup_event
        
        return None

    def _calculate_position_shift(self, from_tier: int, to_tier: int) -> List[float]:
        """Calculate the 8D position shift for a tier transition."""
        shift = np.zeros(8)
        
        new_tier_data = EVOLUTIONARY_TIERS[to_tier]
        knowledge_focus = new_tier_data["knowledge_focus"]
        
        for knowledge in knowledge_focus:
            for i, domain in enumerate(KNOWLEDGE_DOMAINS_8D):
                if knowledge.lower() in domain.lower() or domain.lower() in knowledge.lower():
                    shift[i] += 0.1
        
        shift = shift / (np.linalg.norm(shift) + 1e-8)
        shift = shift + np.random.normal(0, 0.05, 8)
        
        return shift.tolist()

    def record_milestone(self, scda_id: str, description: str) -> bool:
        """Record a significant evolutionary milestone."""
        if scda_id not in self.scda_states:
            logger.warning(f"SCDA {scda_id} not found for milestone recording.")
            return False
        
        state = self.scda_states[scda_id]
        milestone = EvolutionaryMilestone(
            tier=state.current_tier,
            timestamp=datetime.now().isoformat(),
            c_value=state.complexity_index,
            problems_solved=state.problems_solved,
            energy_at_milestone=state.energy,
            description=description
        )
        
        state.milestones.append(milestone)
        logger.info(f"SCDA {scda_id} milestone recorded: {description}")
        return True

    def unlock_achievement(self, scda_id: str, achievement_id: str, achievement_data: Dict[str, Any]) -> bool:
        """Unlock an achievement for this SCDA."""
        if scda_id not in self.scda_states:
            logger.warning(f"SCDA {scda_id} not found for achievement unlock.")
            return False
        
        state = self.scda_states[scda_id]
        if achievement_id not in state.achievements:
            state.achievements[achievement_id] = achievement_data
            logger.info(f"SCDA {scda_id} unlocked achievement: {achievement_id}")
            return True
        return False

    def export_scda_state(self, scda_id: str) -> Optional[Dict[str, Any]]:
        """Export the full state of an SCDA for persistence."""
        if scda_id not in self.scda_states:
            return None
        
        state = self.scda_states[scda_id]
        
        # Convert dataclasses to dicts for JSON serialization
        milestones_data = [milestone.__dict__ for milestone in state.milestones]
        levelup_events_data = [event.__dict__ for event in state.levelup_events]
        
        return {
            "scda_id": state.scda_id,
            "complexity_index": state.complexity_index,
            "energy": state.energy,
            "current_tier": state.current_tier,
            "knowledge_vector_8d": state.knowledge_vector_8d,
            "position_8d": state.position_8d,
            "problems_solved": state.problems_solved,
            "problems_solved_per_tier": state.problems_solved_per_tier,
            "achievements": state.achievements,
            "milestones": milestones_data,
            "levelup_events": levelup_events_data
        }

    def import_scda_state(self, state_data: Dict[str, Any]) -> bool:
        """Import the full state of an SCDA from persistence data."""
        scda_id = state_data["scda_id"]
        
        if scda_id in self.scda_states:
            logger.warning(f"SCDA {scda_id} already exists. Import aborted.")
            return False
        
        # Convert dicts back to dataclasses
        milestones = [EvolutionaryMilestone(**m) for m in state_data.get("milestones", [])]
        levelup_events = [LevelUpEvent(**e) for e in state_data.get("levelup_events", [])]
        
        state = SCDAState(
            scda_id=scda_id,
            complexity_index=state_data["complexity_index"],
            energy=state_data["energy"],
            current_tier=state_data["current_tier"],
            knowledge_vector_8d=state_data["knowledge_vector_8d"],
            position_8d=state_data["position_8d"],
            problems_solved=state_data["problems_solved"],
            problems_solved_per_tier=state_data["problems_solved_per_tier"],
            achievements=state_data["achievements"],
            milestones=milestones,
            levelup_events=levelup_events
        )
        
        self.scda_states[scda_id] = state
        logger.info(f"SCDA {scda_id} state imported.")
        return True

    def get_tier_info(self, tier: int) -> Optional[Dict[str, Any]]:
        """Get information about a specific evolutionary tier."""
        return EVOLUTIONARY_TIERS.get(tier)

    def get_all_scda_ids(self) -> List[str]:
        """Return a list of all registered SCDA IDs."""
        return list(self.scda_states.keys())

    def get_scda_position(self, scda_id: str) -> Optional[List[float]]:
        """Get the 8D position of an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.position_8d if state else None

    def get_scda_knowledge_vector(self, scda_id: str) -> Optional[List[float]]:
        """Get the 8D knowledge vector of an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.knowledge_vector_8d if state else None

    def get_scda_complexity(self, scda_id: str) -> Optional[float]:
        """Get the complexity index of an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.complexity_index if state else None

    def get_scda_tier(self, scda_id: str) -> Optional[int]:
        """Get the current evolutionary tier of an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.current_tier if state else None

    def get_scda_problems_solved(self, scda_id: str) -> Optional[int]:
        """Get the total number of problems solved by an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.problems_solved if state else None

    def get_scda_problems_solved_per_tier(self, scda_id: str) -> Optional[Dict[int, int]]:
        """Get the number of problems solved per tier by an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.problems_solved_per_tier if state else None

    def get_scda_achievements(self, scda_id: str) -> Optional[Dict[str, Any]]:
        """Get the achievements of an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.achievements if state else None

    def get_scda_milestones(self, scda_id: str) -> Optional[List[EvolutionaryMilestone]]:
        """Get the milestones of an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.milestones if state else None

    def get_scda_levelup_events(self, scda_id: str) -> Optional[List[LevelUpEvent]]:
        """Get the level-up events of an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.levelup_events if state else None

    def get_scda_energy(self, scda_id: str) -> Optional[float]:
        """Get the energy of an SCDA."""
        state = self.scda_states.get(scda_id)
        return state.energy if state else None

    def consume_energy(self, scda_id: str, amount: float) -> bool:
        """Consume energy from an SCDA."""
        if scda_id not in self.scda_states:
            logger.warning(f"SCDA {scda_id} not found for energy consumption.")
            return False
        
        state = self.scda_states[scda_id]
        if state.energy < amount:
            logger.warning(f"SCDA {scda_id} has insufficient energy ({state.energy:.2f} < {amount:.2f}).")
            return False
        
        state.energy -= amount
        logger.debug(f"SCDA {scda_id} consumed {amount:.2f} energy. Remaining: {state.energy:.2f}")
        return True

    def add_energy(self, scda_id: str, amount: float) -> bool:
        """Add energy to an SCDA."""
        if scda_id not in self.scda_states:
            logger.warning(f"SCDA {scda_id} not found for energy addition.")
            return False
        
        state = self.scda_states[scda_id]
        state.energy += amount
        logger.debug(f"SCDA {scda_id} added {amount:.2f} energy. Total: {state.energy:.2f}")
        return True

    def get_scda_state_for_social(self, scda_id: str) -> Optional[Dict[str, Any]]:
        """Get a simplified state for social features."""
        state = self.get_scda_state(scda_id)
        if not state:
            return None
        
        return {
            "scda_id": state["scda_id"],
            "current_tier": state["current_tier"],
            "complexity_index": state["complexity_index"],
            "problems_solved": state["problems_solved"],
            "position_8d": state["position_8d"],
            "knowledge_vector_8d": state["knowledge_vector_8d"]
        }

    def get_scda_state_for_mining(self, scda_id: str) -> Optional[Dict[str, Any]]:
        """Get a simplified state for mining dashboard."""
        state = self.get_scda_state(scda_id)
        if not state:
            return None
        
        return {
            "scda_id": state["scda_id"],
            "current_tier": state["current_tier"],
            "complexity_index": state["complexity_index"],
            "energy": state["energy"],
            "position_8d": state["position_8d"]
        }
