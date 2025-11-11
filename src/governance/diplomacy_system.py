"""
Laniakea Protocol - SCDA Diplomacy and Treaty Management System
مدیریت روابط دیپلماتیک (Alliance/Hostile) و قراردادهای بین SCDAها.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from time import time
import uuid

class RelationType(str, Enum):
    """انواع روابط دیپلماتیک بین SCDAها"""
    NEUTRAL = "Neutral"
    ALLIANCE = "Alliance"
    HOSTILE = "Hostile"
    PROTECTORATE = "Protectorate"
    VASSAL = "Vassal"

class TreatyType(str, Enum):
    """انواع قراردادهای دیپلماتیک"""
    NON_AGGRESSION = "Non-Aggression Pact"
    TRADE_AGREEMENT = "Trade Agreement"
    RESEARCH_PACT = "Joint Research Pact"
    DEFENSIVE_PACT = "Defensive Pact"
    FULL_ALLIANCE = "Full Alliance"

class Treaty:
    """مدل قرارداد دیپلماتیک"""
    def __init__(self, parties: List[str], treaty_type: TreatyType, duration: float, terms: Dict[str, Any]):
        self.treaty_id = str(uuid.uuid4())
        self.parties = sorted(parties) # Ensure consistent order
        self.treaty_type = treaty_type
        self.start_time = time()
        self.duration = duration # in seconds
        self.terms = terms
        self.is_active = True

    def is_expired(self) -> bool:
        """بررسی انقضای قرارداد"""
        return time() > self.start_time + self.duration

    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "treaty_id": self.treaty_id,
            "parties": self.parties,
            "treaty_type": self.treaty_type.value,
            "start_time": self.start_time,
            "duration": self.duration,
            "is_active": self.is_active and not self.is_expired(),
            "terms": self.terms
        }

class DiplomacySystem:
    """
    سیستم مدیریت دیپلماسی SCDA
    """
    def __init__(self):
        # روابط SCDAها: {scda_id: {other_scda_id: RelationType}}
        self.relations: Dict[str, Dict[str, RelationType]] = {}
        # قراردادهای فعال: {treaty_id: Treaty}
        self.active_treaties: Dict[str, Treaty] = {}
        print("🤝 Diplomacy System initialized")

    def _get_relation_key(self, scda1: str, scda2: str) -> str:
        """تولید کلید ثابت برای جفت SCDA"""
        return tuple(sorted([scda1, scda2]))

    def get_relation(self, scda1: str, scda2: str) -> RelationType:
        """دریافت نوع رابطه بین دو SCDA"""
        if scda1 == scda2:
            return RelationType.NEUTRAL # رابطه با خود
        
        # Check if relation is explicitly set
        if scda1 in self.relations and scda2 in self.relations[scda1]:
            return self.relations[scda1][scda2]
        
        # Default to Neutral
        return RelationType.NEUTRAL

    def set_relation(self, scda1: str, scda2: str, relation: RelationType) -> None:
        """تنظیم نوع رابطه بین دو SCDA (دو طرفه)"""
        if scda1 == scda2:
            return

        # Ensure the relation is set symmetrically
        if scda1 not in self.relations:
            self.relations[scda1] = {}
        if scda2 not in self.relations:
            self.relations[scda2] = {}

        self.relations[scda1][scda2] = relation
        self.relations[scda2][scda1] = relation
        print(f"Diplomacy: {scda1[:8]} and {scda2[:8]} set to {relation.value}")

    def propose_treaty(self, parties: List[str], treaty_type: TreatyType, duration: float, terms: Dict[str, Any]) -> Treaty:
        """پیشنهاد یک قرارداد جدید"""
        if len(parties) < 2:
            raise ValueError("A treaty must have at least two parties.")
        
        # Check for existing conflicting treaties (simplified)
        # In a real system, this would be a complex check
        
        new_treaty = Treaty(parties, treaty_type, duration, terms)
        self.active_treaties[new_treaty.treaty_id] = new_treaty
        
        # Update relations based on treaty type (simplified)
        if treaty_type in [TreatyType.DEFENSIVE_PACT, TreatyType.FULL_ALLIANCE]:
            for i in range(len(parties)):
                for j in range(i + 1, len(parties)):
                    self.set_relation(parties[i], parties[j], RelationType.ALLIANCE)
        
        print(f"Treaty proposed and signed: {treaty_type.value} between {', '.join(p[:8] for p in parties)}")
        return new_treaty

    def dissolve_treaty(self, treaty_id: str, reason: str) -> bool:
        """فسخ یک قرارداد"""
        treaty = self.active_treaties.pop(treaty_id, None)
        if not treaty:
            return False
        
        treaty.is_active = False
        print(f"Treaty {treaty_id[:8]} dissolved: {reason}")
        
        # Logic to potentially revert relations (complex, simplified here)
        # e.g., revert to NEUTRAL unless other treaties/relations exist
        
        return True

    def get_treaty_info(self, treaty_id: str) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات قرارداد"""
        treaty = self.active_treaties.get(treaty_id)
        if treaty:
            return treaty.to_dict()
        return None

    def get_scda_diplomacy_summary(self, scda_id: str) -> Dict[str, Any]:
        """دریافت خلاصه دیپلماتیک SCDA"""
        summary = {
            "relations": {},
            "active_treaties": []
        }
        
        # Relations
        if scda_id in self.relations:
            for other_scda, relation in self.relations[scda_id].items():
                summary["relations"][other_scda] = relation.value
        
        # Treaties
        for treaty in self.active_treaties.values():
            if scda_id in treaty.parties and not treaty.is_expired():
                summary["active_treaties"].append(treaty.to_dict())
                
        return summary

# Singleton instance
_diplomacy_system: Optional[DiplomacySystem] = None

def get_diplomacy_system() -> DiplomacySystem:
    """دریافت نمونه Singleton از DiplomacySystem"""
    global _diplomacy_system
    if _diplomacy_system is None:
        _diplomacy_system = DiplomacySystem()
    return _diplomacy_system
