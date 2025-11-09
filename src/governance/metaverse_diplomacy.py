"""
Laniakea Protocol - Metaverse Diplomacy System
سیستم دیپلماسی متاورس برای تعامل بین تمدن‌ها و Meta-Structures
Version: 0.0.01
Copyright: LaniakeA Protocol
"""

import uuid
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field


class TreatyType(str, Enum):
    """انواع پیمان‌های بین‌المللی"""
    
    ALLIANCE = "alliance"  # اتحاد
    TRADE = "trade"  # تجارت
    NON_AGGRESSION = "non_aggression"  # عدم تجاوز
    KNOWLEDGE_SHARING = "knowledge_sharing"  # اشتراک دانش
    MUTUAL_DEFENSE = "mutual_defense"  # دفاع متقابل
    CULTURAL_EXCHANGE = "cultural_exchange"  # تبادل فرهنگی


class TreatyStatus(str, Enum):
    """وضعیت پیمان"""
    
    PROPOSED = "proposed"  # پیشنهادی
    NEGOTIATING = "negotiating"  # در حال مذاکره
    ACTIVE = "active"  # فعال
    SUSPENDED = "suspended"  # معلق
    TERMINATED = "terminated"  # خاتمه‌یافته


@dataclass
class TreatyClause:
    """یک بند در پیمان"""
    
    clause_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    obligations: List[str] = field(default_factory=list)  # تعهدات
    benefits: List[str] = field(default_factory=list)  # مزایا
    penalties: List[str] = field(default_factory=list)  # جریمه‌ها
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Treaty:
    """یک پیمان بین دو Meta-Structure"""
    
    treaty_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    treaty_type: TreatyType = TreatyType.ALLIANCE
    party_a_id: str = ""
    party_b_id: str = ""
    status: TreatyStatus = TreatyStatus.PROPOSED
    
    # شرایط
    clauses: List[TreatyClause] = field(default_factory=list)
    
    # تاریخ و مدت
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_days: int = 365  # مدت پیمان به روز
    
    # امضاکنندگان
    signed_by_a: bool = False
    signed_by_b: bool = False
    
    # تاریخچه
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_clause(self, clause: TreatyClause):
        """افزودن یک بند به پیمان"""
        self.clauses.append(clause)
        self._record_history(f"Clause added: {clause.title}")
    
    def sign_by_party(self, party_id: str) -> bool:
        """امضای پیمان توسط یک طرف"""
        if party_id == self.party_a_id:
            self.signed_by_a = True
            self._record_history(f"Party A ({party_id}) signed the treaty")
        elif party_id == self.party_b_id:
            self.signed_by_b = True
            self._record_history(f"Party B ({party_id}) signed the treaty")
        else:
            return False
        
        # اگر هر دو طرف امضا کردند، پیمان فعال می‌شود
        if self.signed_by_a and self.signed_by_b:
            self.activate()
        
        return True
    
    def activate(self):
        """فعال‌سازی پیمان"""
        if self.signed_by_a and self.signed_by_b:
            self.status = TreatyStatus.ACTIVE
            self.start_date = datetime.now().isoformat()
            self.end_date = (datetime.now() + timedelta(days=self.duration_days)).isoformat()
            self._record_history("Treaty activated")
    
    def suspend(self):
        """معلق کردن پیمان"""
        self.status = TreatyStatus.SUSPENDED
        self._record_history("Treaty suspended")
    
    def terminate(self):
        """خاتمه دادن به پیمان"""
        self.status = TreatyStatus.TERMINATED
        self._record_history("Treaty terminated")
    
    def _record_history(self, event: str):
        """ثبت رویداد در تاریخچه پیمان"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "event": event
        })
    
    def is_expired(self) -> bool:
        """بررسی انقضای پیمان"""
        if self.end_date:
            return datetime.fromisoformat(self.end_date) < datetime.now()
        return False


class DiplomaticRepresentative:
    """نماینده دیپلماتیک (سفیر) یک Meta-Structure"""
    
    def __init__(self, scda_id: str, civilization_id: str, complexity_index: float):
        self.representative_id = str(uuid.uuid4())[:8]
        self.scda_id = scda_id
        self.civilization_id = civilization_id
        self.complexity_index = complexity_index
        self.voting_weight = min(2.0, 1.0 + (complexity_index / 10.0))  # وزن رأی بر اساس پیچیدگی
        self.created_at = datetime.now().isoformat()
        self.active = True
    
    def get_influence_score(self) -> float:
        """محاسبه نمره نفوذ سفیر"""
        return self.complexity_index * self.voting_weight


class MetaverseDiplomacySystem:
    """سیستم دیپلماسی متاورس برای مدیریت روابط بین تمدن‌ها"""
    
    def __init__(self):
        self.treaties: Dict[str, Treaty] = {}
        self.representatives: Dict[str, DiplomaticRepresentative] = {}
        self.diplomatic_relations: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self.created_at = datetime.now().isoformat()
    
    def register_representative(self, scda_id: str, civilization_id: str, complexity_index: float) -> DiplomaticRepresentative:
        """ثبت نماینده دیپلماتیک برای یک تمدن"""
        representative = DiplomaticRepresentative(scda_id, civilization_id, complexity_index)
        self.representatives[representative.representative_id] = representative
        return representative
    
    def propose_treaty(self, party_a_id: str, party_b_id: str, treaty_type: TreatyType) -> Treaty:
        """پیشنهاد یک پیمان جدید"""
        treaty = Treaty(
            treaty_type=treaty_type,
            party_a_id=party_a_id,
            party_b_id=party_b_id
        )
        self.treaties[treaty.treaty_id] = treaty
        
        # ثبت رابطه دیپلماتیک
        relation_key = tuple(sorted([party_a_id, party_b_id]))
        if relation_key not in self.diplomatic_relations:
            self.diplomatic_relations[relation_key] = {
                "party_a": party_a_id,
                "party_b": party_b_id,
                "treaties": [],
                "interaction_history": []
            }
        
        self.diplomatic_relations[relation_key]["treaties"].append(treaty.treaty_id)
        
        return treaty
    
    def negotiate_treaty(self, treaty_id: str, party_id: str, proposed_changes: List[str]) -> bool:
        """مذاکره برای تغییر شرایط پیمان"""
        if treaty_id not in self.treaties:
            return False
        
        treaty = self.treaties[treaty_id]
        
        if treaty.status != TreatyStatus.PROPOSED and treaty.status != TreatyStatus.NEGOTIATING:
            return False
        
        treaty.status = TreatyStatus.NEGOTIATING
        
        # ثبت پیشنهادات تغییر
        for change in proposed_changes:
            treaty._record_history(f"Party {party_id} proposed: {change}")
        
        return True
    
    def sign_treaty(self, treaty_id: str, party_id: str) -> bool:
        """امضای پیمان توسط یک طرف"""
        if treaty_id not in self.treaties:
            return False
        
        treaty = self.treaties[treaty_id]
        return treaty.sign_by_party(party_id)
    
    def calculate_diplomatic_score(self, civilization_a_id: str, civilization_b_id: str) -> float:
        """محاسبه نمره روابط دیپلماتیک بین دو تمدن"""
        relation_key = tuple(sorted([civilization_a_id, civilization_b_id]))
        
        if relation_key not in self.diplomatic_relations:
            return 0.5  # نمره بی‌طرفی
        
        relation = self.diplomatic_relations[relation_key]
        
        # بر اساس تعداد پیمان‌های فعال
        active_treaties = sum(
            1 for treaty_id in relation["treaties"]
            if self.treaties[treaty_id].status == TreatyStatus.ACTIVE
        )
        
        # بر اساس تاریخچه تعامل
        positive_interactions = sum(
            1 for event in relation["interaction_history"]
            if event.get("type") == "positive"
        )
        
        negative_interactions = sum(
            1 for event in relation["interaction_history"]
            if event.get("type") == "negative"
        )
        
        # محاسبه نمره
        base_score = 0.5
        treaty_bonus = active_treaties * 0.1
        positive_bonus = positive_interactions * 0.05
        negative_penalty = negative_interactions * 0.05
        
        score = base_score + treaty_bonus + positive_bonus - negative_penalty
        
        return np.clip(score, 0.0, 1.0)
    
    def record_interaction(self, civilization_a_id: str, civilization_b_id: str, 
                          interaction_type: str, description: str):
        """ثبت تعامل بین دو تمدن"""
        relation_key = tuple(sorted([civilization_a_id, civilization_b_id]))
        
        if relation_key not in self.diplomatic_relations:
            self.diplomatic_relations[relation_key] = {
                "party_a": civilization_a_id,
                "party_b": civilization_b_id,
                "treaties": [],
                "interaction_history": []
            }
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "description": description
        }
        
        self.diplomatic_relations[relation_key]["interaction_history"].append(interaction)
    
    def get_diplomatic_network_summary(self) -> Dict[str, Any]:
        """دریافت خلاصه‌ای از شبکه دیپلماتیک"""
        return {
            "total_treaties": len(self.treaties),
            "active_treaties": sum(1 for t in self.treaties.values() if t.status == TreatyStatus.ACTIVE),
            "total_representatives": len(self.representatives),
            "diplomatic_relations": len(self.diplomatic_relations),
            "created_at": self.created_at
        }


# Import numpy for clip function
import numpy as np


# Global diplomacy system instance
_diplomacy_system = MetaverseDiplomacySystem()


def get_diplomacy_system() -> MetaverseDiplomacySystem:
    """دریافت instance جهانی سیستم دیپلماسی"""
    return _diplomacy_system
