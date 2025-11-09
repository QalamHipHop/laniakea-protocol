"""
Advanced Metaverse Integration V0.0.03
Complete 8D metaverse with cosmic events, civilizations, and galaxies
"""

import uuid
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class CosmicEvent:
    """Represents a cosmic event in the metaverse"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""  # supernova, black_hole, big_bang, galaxy_birth, etc.
    epicenter: List[float] = field(default_factory=list)  # 8D position
    radius: float = 0.5
    duration: int = 100  # in blocks
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    effects: Dict[str, Any] = field(default_factory=dict)
    triggered_by: Optional[str] = None  # SCDA ID
    participants: List[str] = field(default_factory=list)  # Affected SCDA IDs
    status: str = "active"  # active, ended
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "epicenter": self.epicenter,
            "radius": self.radius,
            "duration": self.duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "effects": self.effects,
            "triggered_by": self.triggered_by,
            "participants": self.participants,
            "status": self.status
        }


@dataclass
class Civilization:
    """Represents a civilization in the metaverse"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    founder: str = ""  # SCDA ID
    members: List[str] = field(default_factory=list)  # SCDA IDs
    territory_center: List[float] = field(default_factory=list)  # 8D position
    territory_radius: float = 0.1
    government_type: str = "democracy"  # democracy, meritocracy, anarchy
    laws: List[Dict[str, Any]] = field(default_factory=list)
    kt_treasury: float = 0.0
    knowledge_library: Dict[str, float] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    wars: List[str] = field(default_factory=list)  # War IDs
    alliances: List[str] = field(default_factory=list)  # Civilization IDs
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "founder": self.founder,
            "members": self.members,
            "territory_center": self.territory_center,
            "territory_radius": self.territory_radius,
            "government_type": self.government_type,
            "laws": self.laws,
            "kt_treasury": self.kt_treasury,
            "knowledge_library": self.knowledge_library,
            "achievements": self.achievements,
            "wars": self.wars,
            "alliances": self.alliances,
            "created_at": self.created_at
        }


@dataclass
class Galaxy:
    """Represents a galaxy (highest level of organization)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    core_members: List[str] = field(default_factory=list)  # Tier 4 SCDA IDs
    all_members: List[str] = field(default_factory=list)  # All SCDA IDs
    center_8d: List[float] = field(default_factory=list)
    radius: float = 0.5
    collective_complexity: float = 0.0
    collective_knowledge: Dict[str, float] = field(default_factory=dict)
    leader: Optional[str] = None  # SCDA ID
    council: List[str] = field(default_factory=list)  # Top SCDAs
    gravitational_strength: float = 0.0
    cosmic_events: List[str] = field(default_factory=list)  # Event IDs
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "core_members": self.core_members,
            "all_members": self.all_members,
            "center_8d": self.center_8d,
            "radius": self.radius,
            "collective_complexity": self.collective_complexity,
            "collective_knowledge": self.collective_knowledge,
            "leader": self.leader,
            "council": self.council,
            "gravitational_strength": self.gravitational_strength,
            "cosmic_events": self.cosmic_events,
            "created_at": self.created_at
        }


class AdvancedMetaverse:
    """
    Advanced Metaverse Integration with complete cosmic simulation.
    
    Features:
    - 8D spatial management
    - Cosmic events
    - Civilizations
    - Galaxies
    - Gravitational fields
    - Time dilation regions
    """
    
    DIMENSIONS = 8
    HYPERCUBE_CENTER = [0.5] * DIMENSIONS
    
    # Cosmic event templates
    COSMIC_EVENT_TYPES = {
        "supernova": {
            "radius": 0.3,
            "duration": 50,
            "effects": {
                "complexity_multiplier": 2.0,
                "energy_boost": 500.0,
                "mutation_rate_increase": 0.1
            }
        },
        "black_hole": {
            "radius": 0.2,
            "duration": 100,
            "effects": {
                "energy_drain": 0.5,  # 50% energy drain
                "position_pull": 0.1,  # Pull towards center
                "time_dilation": 0.5  # Time slows down
            }
        },
        "big_bang": {
            "radius": 1.0,
            "duration": 200,
            "effects": {
                "complexity_multiplier": 5.0,
                "energy_boost": 2000.0,
                "knowledge_boost": 0.5,
                "tier_advancement": True
            }
        },
        "galaxy_birth": {
            "radius": 0.8,
            "duration": 150,
            "effects": {
                "complexity_multiplier": 1.5,
                "energy_boost": 1000.0,
                "collaboration_bonus": 2.0
            }
        },
        "heat_death": {
            "radius": 0.4,
            "duration": 80,
            "effects": {
                "energy_decay": 0.02,  # 2% per block
                "complexity_freeze": True,
                "mutation_stop": True
            }
        }
    }
    
    def __init__(self):
        """Initialize the advanced metaverse"""
        # SCDA tracking
        self.scda_positions: Dict[str, List[float]] = {}
        self.scda_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Cosmic structures
        self.cosmic_events: Dict[str, CosmicEvent] = {}
        self.civilizations: Dict[str, Civilization] = {}
        self.galaxies: Dict[str, Galaxy] = {}
        
        # Spatial structures
        self.gravitational_fields: List[Dict[str, Any]] = []
        self.time_dilation_zones: List[Dict[str, Any]] = []
        
        # History
        self.event_history: List[Dict[str, Any]] = []
        
        print("🌌 Advanced Metaverse initialized")
    
    def register_scda(
        self,
        scda_id: str,
        position_8d: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register an SCDA in the metaverse"""
        
        if position_8d is None:
            position_8d = [np.random.uniform(0, 1) for _ in range(self.DIMENSIONS)]
        
        self.scda_positions[scda_id] = position_8d
        
        self.scda_metadata[scda_id] = metadata or {
            "registered_at": datetime.now().isoformat(),
            "tier": 1,
            "complexity_index": 1.0,
            "energy": 100.0,
            "civilization_id": None,
            "galaxy_id": None
        }
        
        return {
            "scda_id": scda_id,
            "position_8d": position_8d,
            "message": "SCDA registered in metaverse"
        }
    
    def update_scda_position(
        self,
        scda_id: str,
        new_position: Optional[List[float]] = None,
        position_shift: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Update SCDA position"""
        
        if scda_id not in self.scda_positions:
            return {"error": "SCDA not found"}
        
        old_position = self.scda_positions[scda_id].copy()
        
        if new_position:
            self.scda_positions[scda_id] = [np.clip(p, 0, 1) for p in new_position]
        elif position_shift:
            for i in range(self.DIMENSIONS):
                self.scda_positions[scda_id][i] += position_shift[i]
                self.scda_positions[scda_id][i] = np.clip(self.scda_positions[scda_id][i], 0, 1)
        
        # Check for cosmic event effects
        self._apply_cosmic_effects(scda_id)
        
        # Check for gravitational pull
        self._apply_gravitational_pull(scda_id)
        
        return {
            "scda_id": scda_id,
            "old_position": old_position,
            "new_position": self.scda_positions[scda_id]
        }
    
    def calculate_distance(self, pos1: List[float], pos2: List[float]) -> float:
        """Calculate Euclidean distance in 8D space"""
        return np.linalg.norm(np.array(pos1) - np.array(pos2))
    
    def find_nearby_scda(
        self,
        position: List[float],
        radius: float = 0.3,
        exclude: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]:
        """Find SCDAs within radius of a position"""
        
        exclude = exclude or []
        nearby = []
        
        for scda_id, scda_pos in self.scda_positions.items():
            if scda_id in exclude:
                continue
            
            distance = self.calculate_distance(position, scda_pos)
            if distance <= radius:
                nearby.append((scda_id, distance))
        
        # Sort by distance
        nearby.sort(key=lambda x: x[1])
        
        return nearby
    
    def trigger_cosmic_event(
        self,
        event_type: str,
        epicenter: Optional[List[float]] = None,
        triggered_by: Optional[str] = None,
        custom_effects: Optional[Dict[str, Any]] = None
    ) -> CosmicEvent:
        """Trigger a cosmic event"""
        
        if event_type not in self.COSMIC_EVENT_TYPES:
            raise ValueError(f"Unknown event type: {event_type}")
        
        template = self.COSMIC_EVENT_TYPES[event_type]
        
        if epicenter is None:
            epicenter = [np.random.uniform(0, 1) for _ in range(self.DIMENSIONS)]
        
        effects = template["effects"].copy()
        if custom_effects:
            effects.update(custom_effects)
        
        event = CosmicEvent(
            event_type=event_type,
            epicenter=epicenter,
            radius=template["radius"],
            duration=template["duration"],
            effects=effects,
            triggered_by=triggered_by
        )
        
        # Find affected SCDAs
        affected = self.find_nearby_scda(epicenter, radius=event.radius)
        event.participants = [scda_id for scda_id, _ in affected]
        
        self.cosmic_events[event.id] = event
        
        # Record in history
        self.event_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "cosmic_event_triggered",
            "event_id": event.id,
            "event_type": event_type,
            "epicenter": epicenter,
            "affected_count": len(event.participants)
        })
        
        print(f"🌟 Cosmic event triggered: {event_type} at {epicenter[:3]}...")
        print(f"   Affected SCDAs: {len(event.participants)}")
        
        return event
    
    def _apply_cosmic_effects(self, scda_id: str) -> None:
        """Apply effects from active cosmic events"""
        
        position = self.scda_positions[scda_id]
        
        for event in self.cosmic_events.values():
            if event.status != "active":
                continue
            
            distance = self.calculate_distance(position, event.epicenter)
            
            if distance <= event.radius:
                # SCDA is within event radius
                if scda_id not in event.participants:
                    event.participants.append(scda_id)
                
                # Apply effects (would be done by SCDA manager in real system)
                # Here we just mark the SCDA as affected
                if "affected_by_events" not in self.scda_metadata[scda_id]:
                    self.scda_metadata[scda_id]["affected_by_events"] = []
                
                if event.id not in self.scda_metadata[scda_id]["affected_by_events"]:
                    self.scda_metadata[scda_id]["affected_by_events"].append(event.id)
    
    def _apply_gravitational_pull(self, scda_id: str) -> None:
        """Apply gravitational pull from galaxies and civilizations"""
        
        position = np.array(self.scda_positions[scda_id])
        
        # Pull from galaxies
        for galaxy in self.galaxies.values():
            distance = self.calculate_distance(position.tolist(), galaxy.center_8d)
            
            if distance <= galaxy.radius:
                # Apply gravitational pull
                direction = np.array(galaxy.center_8d) - position
                pull_strength = galaxy.gravitational_strength / (distance + 0.1)
                
                position += direction * pull_strength * 0.01
                position = np.clip(position, 0, 1)
                
                self.scda_positions[scda_id] = position.tolist()
    
    def create_civilization(
        self,
        founder_id: str,
        name: str,
        government_type: str = "democracy"
    ) -> Civilization:
        """Create a new civilization"""
        
        if founder_id not in self.scda_positions:
            raise ValueError("Founder SCDA not found")
        
        civilization = Civilization(
            name=name,
            founder=founder_id,
            members=[founder_id],
            territory_center=self.scda_positions[founder_id].copy(),
            territory_radius=0.1,
            government_type=government_type
        )
        
        self.civilizations[civilization.id] = civilization
        
        # Update SCDA metadata
        self.scda_metadata[founder_id]["civilization_id"] = civilization.id
        
        # Record in history
        self.event_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "civilization_created",
            "civilization_id": civilization.id,
            "name": name,
            "founder": founder_id
        })
        
        print(f"🏛️ Civilization created: {name}")
        
        return civilization
    
    def join_civilization(self, scda_id: str, civilization_id: str) -> Dict[str, Any]:
        """SCDA joins a civilization"""
        
        if scda_id not in self.scda_positions:
            return {"error": "SCDA not found"}
        
        if civilization_id not in self.civilizations:
            return {"error": "Civilization not found"}
        
        civilization = self.civilizations[civilization_id]
        
        # Check if within territory
        distance = self.calculate_distance(
            self.scda_positions[scda_id],
            civilization.territory_center
        )
        
        if distance > civilization.territory_radius:
            return {"error": "SCDA too far from civilization territory"}
        
        # Add to civilization
        if scda_id not in civilization.members:
            civilization.members.append(scda_id)
        
        # Update SCDA metadata
        self.scda_metadata[scda_id]["civilization_id"] = civilization_id
        
        return {
            "success": True,
            "civilization_id": civilization_id,
            "member_count": len(civilization.members)
        }
    
    def create_galaxy(
        self,
        core_members: List[str],
        name: str
    ) -> Galaxy:
        """Create a galaxy (requires Tier 4 SCDAs)"""
        
        if len(core_members) < 10:
            raise ValueError("Need at least 10 core members")
        
        # Calculate center of mass
        positions = [self.scda_positions[scda_id] for scda_id in core_members]
        center = np.mean(positions, axis=0).tolist()
        
        # Calculate collective complexity
        collective_complexity = sum(
            self.scda_metadata[scda_id].get("complexity_index", 0)
            for scda_id in core_members
        )
        
        galaxy = Galaxy(
            name=name,
            core_members=core_members,
            all_members=core_members.copy(),
            center_8d=center,
            radius=0.5,
            collective_complexity=collective_complexity,
            gravitational_strength=collective_complexity / 1000.0
        )
        
        # Find leader (highest complexity)
        leader_id = max(
            core_members,
            key=lambda sid: self.scda_metadata[sid].get("complexity_index", 0)
        )
        galaxy.leader = leader_id
        
        # Council (top 5)
        sorted_members = sorted(
            core_members,
            key=lambda sid: self.scda_metadata[sid].get("complexity_index", 0),
            reverse=True
        )
        galaxy.council = sorted_members[:5]
        
        self.galaxies[galaxy.id] = galaxy
        
        # Update SCDA metadata
        for scda_id in core_members:
            self.scda_metadata[scda_id]["galaxy_id"] = galaxy.id
        
        # Trigger galaxy birth event
        self.trigger_cosmic_event(
            "galaxy_birth",
            epicenter=center,
            triggered_by=leader_id
        )
        
        # Record in history
        self.event_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "galaxy_created",
            "galaxy_id": galaxy.id,
            "name": name,
            "core_members": len(core_members),
            "collective_complexity": collective_complexity
        })
        
        print(f"🌌 Galaxy created: {name}")
        print(f"   Core members: {len(core_members)}")
        print(f"   Collective complexity: {collective_complexity:.2f}")
        
        return galaxy
    
    def get_metaverse_status(self) -> Dict[str, Any]:
        """Get overall metaverse status"""
        
        active_events = sum(1 for e in self.cosmic_events.values() if e.status == "active")
        
        return {
            "total_scda": len(self.scda_positions),
            "civilizations": len(self.civilizations),
            "galaxies": len(self.galaxies),
            "active_cosmic_events": active_events,
            "total_events_triggered": len(self.cosmic_events),
            "dimensions": self.DIMENSIONS,
            "hypercube_center": self.HYPERCUBE_CENTER,
            "event_history_size": len(self.event_history)
        }
    
    def export_state(self) -> str:
        """Export complete metaverse state"""
        
        data = {
            "status": self.get_metaverse_status(),
            "scda_positions": self.scda_positions,
            "scda_metadata": self.scda_metadata,
            "cosmic_events": {eid: e.to_dict() for eid, e in self.cosmic_events.items()},
            "civilizations": {cid: c.to_dict() for cid, c in self.civilizations.items()},
            "galaxies": {gid: g.to_dict() for gid, g in self.galaxies.items()},
            "event_history": self.event_history
        }
        
        return json.dumps(data, indent=2)


# Example usage
if __name__ == "__main__":
    print("🌌 Advanced Metaverse Demo\n")
    
    metaverse = AdvancedMetaverse()
    
    # Register SCDAs
    print("📍 Registering SCDAs...")
    scda_ids = []
    for i in range(15):
        scda_id = f"scda_{i:03d}"
        metaverse.register_scda(
            scda_id,
            metadata={
                "tier": 4 if i < 10 else 2,
                "complexity_index": 1000.0 + i * 100 if i < 10 else 50.0
            }
        )
        scda_ids.append(scda_id)
    
    print(f"Registered {len(scda_ids)} SCDAs\n")
    
    # Trigger cosmic event
    print("🌟 Triggering supernova...")
    event = metaverse.trigger_cosmic_event("supernova", epicenter=[0.5] * 8)
    print()
    
    # Create civilization
    print("🏛️ Creating civilization...")
    civ = metaverse.create_civilization(
        founder_id="scda_010",
        name="The First Civilization",
        government_type="meritocracy"
    )
    print()
    
    # Create galaxy
    print("🌌 Creating galaxy...")
    galaxy = metaverse.create_galaxy(
        core_members=scda_ids[:10],
        name="Laniakea Prime"
    )
    print()
    
    # Status
    print("📊 Metaverse Status:")
    status = metaverse.get_metaverse_status()
    print(json.dumps(status, indent=2))
