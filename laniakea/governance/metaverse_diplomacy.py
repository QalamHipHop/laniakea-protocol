"""
Metaverse Diplomacy System
Version: 0.0.01
Author: Manus AI

This module implements the core logic for the Metaverse Diplomacy System,
allowing SCDAs to form alliances, negotiate treaties, and engage in
collaborative governance.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import numpy as np

logger = logging.getLogger(__name__)

# --- Constants ---
DIPLOMACY_DOMAINS = [
    "Trust", "Collaboration_Index", "Shared_Knowledge_Overlap",
    "Mutual_Complexity_Gain", "Resource_Contribution", "Conflict_Resolution_Rate"
]

# --- Data Structures ---

@dataclass
class Alliance:
    """Represents a formal alliance between multiple SCDAs."""
    alliance_id: str
    name: str
    founder_scda_id: str
    members: List[str]
    creation_date: str
    shared_knowledge_vector: List[float]
    reputation_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alliance_id": self.alliance_id,
            "name": self.name,
            "founder_scda_id": self.founder_scda_id,
            "members": self.members,
            "creation_date": self.creation_date,
            "shared_knowledge_vector": self.shared_knowledge_vector,
            "reputation_score": self.reputation_score
        }

@dataclass
class Treaty:
    """Represents a formal agreement between two or more SCDAs/Alliances."""
    treaty_id: str
    parties: List[str] # List of SCDA IDs or Alliance IDs
    type: str # e.g., "Knowledge_Sharing", "Defense_Pact", "Resource_Allocation"
    terms: str
    creation_date: str
    expiration_date: Optional[str] = None
    status: str = "active" # "active", "violated", "expired"

# --- Core Logic ---

class DiplomacySystem:
    """Manages alliances, treaties, and diplomatic interactions in the Metaverse."""
    
    def __init__(self):
        self.alliances: Dict[str, Alliance] = {}
        self.treaties: Dict[str, Treaty] = {}
        logger.info("DiplomacySystem initialized.")
    
    def _generate_id(self, prefix: str) -> str:
        """Generates a unique ID."""
        return f"{prefix}-{uuid.uuid4().hex[:8]}"
    
    def create_alliance(
        self,
        name: str,
        founder_scda_id: str,
        initial_members: List[str],
        initial_knowledge_vectors: Dict[str, List[float]]
    ) -> Alliance:
        """
        Creates a new alliance.
        
        Args:
            name: Name of the alliance.
            founder_scda_id: ID of the founding SCDA.
            initial_members: List of initial SCDA members.
            initial_knowledge_vectors: Dictionary of member IDs to their 8D knowledge vectors.
            
        Returns:
            The newly created Alliance object.
        """
        alliance_id = self._generate_id("ALLIANCE")
        
        # Calculate initial shared knowledge vector (average of members)
        vectors = [np.array(v) for v in initial_knowledge_vectors.values()]
        if not vectors:
            shared_knowledge = np.zeros(8).tolist()
        else:
            # Ensure all vectors are 8D
            vectors = [v for v in vectors if len(v) == 8]
            if not vectors:
                shared_knowledge = np.zeros(8).tolist()
            else:
                shared_knowledge = np.mean(vectors, axis=0).tolist()
            
        alliance = Alliance(
            alliance_id=alliance_id,
            name=name,
            founder_scda_id=founder_scda_id,
            members=initial_members,
            creation_date=datetime.now().isoformat(),
            shared_knowledge_vector=shared_knowledge,
            reputation_score=1.0 # Start with a neutral/good reputation
        )
        
        self.alliances[alliance_id] = alliance
        logger.info(f"Alliance '{name}' ({alliance_id}) created by {founder_scda_id}.")
        return alliance

    def add_member_to_alliance(self, alliance_id: str, scda_id: str, scda_knowledge_vector: List[float]) -> Alliance:
        """Adds an SCDA to an existing alliance and updates the shared knowledge."""
        if alliance_id not in self.alliances:
            raise ValueError(f"Alliance {alliance_id} not found.")
        
        alliance = self.alliances[alliance_id]
        if scda_id in alliance.members:
            raise ValueError(f"SCDA {scda_id} is already a member of {alliance.name}.")
            
        alliance.members.append(scda_id)
        
        # Update shared knowledge vector (simple average update)
        current_members_count = len(alliance.members) - 1
        current_vector = np.array(alliance.shared_knowledge_vector)
        new_member_vector = np.array(scda_knowledge_vector)
        
        # Ensure new member vector is 8D
        if len(new_member_vector) != 8:
            raise ValueError("SCDA knowledge vector must be 8-dimensional.")
        
        # New average = (Old Sum + New Vector) / New Count
        # Note: This assumes the current_vector is the average of the *previous* members.
        # To correctly update the average:
        # Sum_new = Sum_old + Vector_new
        # Avg_new = Sum_new / Count_new
        
        # Calculate the sum of previous members' vectors
        sum_old = current_vector * current_members_count
        
        # Calculate the new sum
        sum_new = sum_old + new_member_vector
        
        # Calculate the new average
        alliance.shared_knowledge_vector = (sum_new / len(alliance.members)).tolist()
        
        logger.info(f"SCDA {scda_id} joined Alliance {alliance.name}. Shared knowledge updated.")
        return alliance

    def create_treaty(
        self,
        parties: List[str],
        type: str,
        terms: str,
        expiration_date: Optional[str] = None
    ) -> Treaty:
        """Creates a new treaty between parties."""
        treaty_id = self._generate_id("TREATY")
        
        # Basic validation: ensure parties exist (SCDA or Alliance)
        # In a real system, we'd check a global SCDA/Alliance registry
        
        treaty = Treaty(
            treaty_id=treaty_id,
            parties=parties,
            type=type,
            terms=terms,
            creation_date=datetime.now().isoformat(),
            expiration_date=expiration_date
        )
        
        self.treaties[treaty_id] = treaty
        logger.info(f"Treaty '{type}' ({treaty_id}) created between {', '.join(parties)}.")
        return treaty

    def violate_treaty(self, treaty_id: str, violating_party: str, penalty: float) -> Treaty:
        """Marks a treaty as violated and applies a penalty (e.g., reputation loss)."""
        if treaty_id not in self.treaties:
            raise ValueError(f"Treaty {treaty_id} not found.")
        
        treaty = self.treaties[treaty_id]
        treaty.status = "violated"
        
        # Apply penalty to the violating party's reputation (if Alliance)
        if violating_party.startswith("ALLIANCE-") and violating_party in self.alliances:
            alliance = self.alliances[violating_party]
            alliance.reputation_score = max(0.0, alliance.reputation_score - penalty)
            logger.warning(f"Alliance {alliance.name} violated Treaty {treaty_id}. Reputation reduced by {penalty}.")
        
        logger.warning(f"Treaty {treaty_id} violated by {violating_party}.")
        return treaty

    def get_alliance_reputation(self, alliance_id: str) -> float:
        """Gets the current reputation score of an alliance."""
        if alliance_id not in self.alliances:
            raise ValueError(f"Alliance {alliance_id} not found.")
        return self.alliances[alliance_id].reputation_score

    def get_alliance_by_member(self, scda_id: str) -> Optional[Alliance]:
        """Finds the alliance an SCDA belongs to."""
        for alliance in self.alliances.values():
            if scda_id in alliance.members:
                return alliance
        return None

# --- Example Usage ---
if __name__ == "__main__":
    diplomacy = DiplomacySystem()
    
    # Mock SCDA knowledge vectors
    scda_knowledge = {
        "scda_alice": [0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], # Physics focus
        "scda_bob": [0.1, 0.1, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1],   # Biology focus
        "scda_charlie": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5] # Balanced
    }
    
    # 1. Create an Alliance
    alliance_members = ["scda_alice", "scda_bob"]
    alliance_vectors = {k: scda_knowledge[k] for k in alliance_members}
    alliance = diplomacy.create_alliance(
        name="The Cosmic Thinkers",
        founder_scda_id="scda_alice",
        initial_members=alliance_members,
        initial_knowledge_vectors=alliance_vectors
    )
    print(f"Alliance Created: {alliance.name} (ID: {alliance.alliance_id})")
    print(f"Shared Knowledge Vector: {alliance.shared_knowledge_vector}")
    
    # 2. Add a new member
    diplomacy.add_member_to_alliance(alliance.alliance_id, "scda_charlie", scda_knowledge["scda_charlie"])
    print(f"Charlie Joined. New Shared Knowledge Vector: {diplomacy.alliances[alliance.alliance_id].shared_knowledge_vector}")
    
    # 3. Create a Treaty
    treaty = diplomacy.create_treaty(
        parties=[alliance.alliance_id, "scda_diana"],
        type="Knowledge_Sharing",
        terms="All members must share 10% of new knowledge assets.",
        expiration_date="2026-01-01T00:00:00Z"
    )
    print(f"Treaty Created: {treaty.type} (ID: {treaty.treaty_id})")
    
    # 4. Violate the Treaty
    try:
        diplomacy.violate_treaty(treaty.treaty_id, alliance.alliance_id, 0.2)
        print(f"Treaty Violated. New Alliance Reputation: {diplomacy.get_alliance_reputation(alliance.alliance_id)}")
    except ValueError as e:
        print(f"Error: {e}")
