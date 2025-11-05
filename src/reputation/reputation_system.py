"""
Laniakea Protocol - Advanced Reputation System
سیستم اعتبار پیشرفته با الگوریتم‌های ریاضی

این سیستم امتیازدهی به نودها را بر اساس:
- کیفیت مشارکت‌ها
- تعداد و تنوع مشارکت‌ها
- قدمت و تاریخچه
- نرخ موفقیت
- رفتار در شبکه
"""

import math
import hashlib
from time import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict
from pydantic import BaseModel, Field


class ReputationEvent(str, Enum):
    """انواع رویدادهای تأثیرگذار بر اعتبار"""

    TASK_CREATED = "task_created"
    SOLUTION_SUBMITTED = "solution_submitted"
    SOLUTION_ACCEPTED = "solution_accepted"
    SOLUTION_REJECTED = "solution_rejected"
    BLOCK_VALIDATED = "block_validated"
    INVALID_BLOCK = "invalid_block"
    VOTE_CAST = "vote_cast"
    PROPOSAL_CREATED = "proposal_created"
    STAKE_INCREASED = "stake_increased"
    SLASH_EVENT = "slash_event"
    PEER_REPORT_POSITIVE = "peer_report_positive"
    PEER_REPORT_NEGATIVE = "peer_report_negative"


class ReputationScore(BaseModel):
    """امتیاز اعتبار"""

    total_score: float = Field(default=0.0, description="امتیاز کل (0-100)")
    quality_score: float = Field(default=0.0, description="امتیاز کیفیت")
    quantity_score: float = Field(default=0.0, description="امتیاز کمیت")
    diversity_score: float = Field(default=0.0, description="امتیاز تنوع")
    age_score: float = Field(default=0.0, description="امتیاز قدمت")
    reliability_score: float = Field(default=1.0, description="امتیاز قابلیت اطمینان")
    trust_level: str = Field(default="new", description="سطح اعتماد")

    def to_dict(self) -> Dict:
        return {
            "total": round(self.total_score, 2),
            "quality": round(self.quality_score, 2),
            "quantity": round(self.quantity_score, 2),
            "diversity": round(self.diversity_score, 2),
            "age": round(self.age_score, 2),
            "reliability": round(self.reliability_score, 3),
            "trust_level": self.trust_level,
        }


class NodeHistory(BaseModel):
    """تاریخچه نود"""

    node_id: str
    created_at: float
    total_contributions: int = 0
    accepted_contributions: int = 0
    rejected_contributions: int = 0
    dimensions_contributed: set = Field(default_factory=set)
    total_value_created: float = 0.0
    events: List[Tuple[float, ReputationEvent, Dict]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


class ReputationSystem:
    """
    سیستم اعتبار پیشرفته

    فرمول کلی:
    R = w₁×Q + w₂×log(1+C) + w₃×D + w₄×A + w₅×S

    که در آن:
    - R: امتیاز اعتبار (0-100)
    - Q: کیفیت میانگین (0-100)
    - C: تعداد مشارکت‌ها
    - D: تنوع (0-1)
    - A: قدمت (روز)
    - S: نرخ موفقیت (0-1)
    - w₁, w₂, w₃, w₄, w₅: وزن‌ها
    """

    def __init__(self):
        # ذخیره‌سازی
        self.node_histories: Dict[str, NodeHistory] = {}
        self.reputation_scores: Dict[str, ReputationScore] = {}

        # وزن‌ها (مجموع = 1)
        self.weights = {
            "quality": 0.35,  # کیفیت مهم‌ترین فاکتور
            "quantity": 0.20,  # کمیت مشارکت
            "diversity": 0.15,  # تنوع مشارکت
            "age": 0.15,  # قدمت حساب
            "reliability": 0.15,  # قابلیت اطمینان
        }

        # پارامترها
        self.max_quality_score = 100.0
        self.max_age_days = 365.0  # یک سال
        self.decay_factor = 0.95  # ضریب زوال برای رویدادهای قدیمی

        # آستانه‌های trust level
        self.trust_thresholds = {
            "new": (0, 20),
            "bronze": (20, 40),
            "silver": (40, 60),
            "gold": (60, 80),
            "platinum": (80, 100),
        }

        print("🏆 Reputation System initialized")

    def register_node(self, node_id: str) -> bool:
        """ثبت نود جدید"""
        if node_id in self.node_histories:
            return False

        self.node_histories[node_id] = NodeHistory(node_id=node_id, created_at=time())

        self.reputation_scores[node_id] = ReputationScore()

        print(f"📝 Node registered: {node_id[:12]}")
        return True

    def record_event(self, node_id: str, event: ReputationEvent, metadata: Dict = None):
        """ثبت رویداد"""
        if node_id not in self.node_histories:
            self.register_node(node_id)

        history = self.node_histories[node_id]
        history.events.append((time(), event, metadata or {}))

        # به‌روزرسانی آمار
        if event == ReputationEvent.SOLUTION_SUBMITTED:
            history.total_contributions += 1
            if metadata and "dimension" in metadata:
                history.dimensions_contributed.add(metadata["dimension"])

        elif event == ReputationEvent.SOLUTION_ACCEPTED:
            history.accepted_contributions += 1
            if metadata and "value" in metadata:
                history.total_value_created += metadata["value"]

        elif event == ReputationEvent.SOLUTION_REJECTED:
            history.rejected_contributions += 1

        # محاسبه مجدد امتیاز
        self._recalculate_reputation(node_id)

    def _recalculate_reputation(self, node_id: str):
        """محاسبه مجدد امتیاز اعتبار"""
        if node_id not in self.node_histories:
            return

        history = self.node_histories[node_id]
        score = self.reputation_scores[node_id]

        # 1. امتیاز کیفیت (Q)
        score.quality_score = self._calculate_quality_score(history)

        # 2. امتیاز کمیت (C)
        score.quantity_score = self._calculate_quantity_score(history)

        # 3. امتیاز تنوع (D)
        score.diversity_score = self._calculate_diversity_score(history)

        # 4. امتیاز قدمت (A)
        score.age_score = self._calculate_age_score(history)

        # 5. امتیاز قابلیت اطمینان (S)
        score.reliability_score = self._calculate_reliability_score(history)

        # محاسبه امتیاز کل
        score.total_score = (
            self.weights["quality"] * score.quality_score
            + self.weights["quantity"] * score.quantity_score
            + self.weights["diversity"] * score.diversity_score * 100
            + self.weights["age"] * score.age_score
            + self.weights["reliability"] * score.reliability_score * 100
        )

        # تعیین سطح اعتماد
        score.trust_level = self._determine_trust_level(score.total_score)

    def _calculate_quality_score(self, history: NodeHistory) -> float:
        """
        محاسبه امتیاز کیفیت

        Q = (total_value / total_contributions) × normalization_factor
        """
        if history.total_contributions == 0:
            return 0.0

        avg_value = history.total_value_created / history.total_contributions

        # نرمال‌سازی به 0-100
        normalized = min(100.0, (avg_value / 10.0) * 100)

        return normalized

    def _calculate_quantity_score(self, history: NodeHistory) -> float:
        """
        محاسبه امتیاز کمیت

        C = log₂(1 + contributions) × scale_factor
        """
        if history.total_contributions == 0:
            return 0.0

        # استفاده از لگاریتم برای کاهش تأثیر تعداد بسیار زیاد
        log_contributions = math.log2(1 + history.total_contributions)

        # نرمال‌سازی (فرض: 1000 مشارکت = امتیاز 100)
        normalized = min(100.0, (log_contributions / math.log2(1001)) * 100)

        return normalized

    def _calculate_diversity_score(self, history: NodeHistory) -> float:
        """
        محاسبه امتیاز تنوع

        D = dimensions_contributed / total_dimensions
        """
        total_dimensions = (
            6  # knowledge, computation, originality, consciousness, environmental, health
        )

        if not history.dimensions_contributed:
            return 0.0

        diversity = len(history.dimensions_contributed) / total_dimensions

        return diversity

    def _calculate_age_score(self, history: NodeHistory) -> float:
        """
        محاسبه امتیاز قدمت

        A = min(age_days / max_age_days, 1.0) × 100
        """
        age_seconds = time() - history.created_at
        age_days = age_seconds / 86400

        # نرمال‌سازی
        normalized = min(1.0, age_days / self.max_age_days) * 100

        return normalized

    def _calculate_reliability_score(self, history: NodeHistory) -> float:
        """
        محاسبه امتیاز قابلیت اطمینان

        S = accepted / (accepted + rejected)
        """
        total = history.accepted_contributions + history.rejected_contributions

        if total == 0:
            return 1.0  # نود جدید: فرض خوش‌بینانه

        reliability = history.accepted_contributions / total

        return reliability

    def _determine_trust_level(self, total_score: float) -> str:
        """تعیین سطح اعتماد"""
        for level, (min_score, max_score) in self.trust_thresholds.items():
            if min_score <= total_score < max_score:
                return level

        return "platinum"  # بالاترین سطح

    def get_reputation(self, node_id: str) -> Optional[ReputationScore]:
        """دریافت امتیاز اعتبار"""
        return self.reputation_scores.get(node_id)

    def get_trust_score(self, node_id: str) -> float:
        """
        دریافت امتیاز اعتماد (0-1)
        برای استفاده در اجماع
        """
        score = self.reputation_scores.get(node_id)
        if not score:
            return 0.1  # حداقل اعتماد برای نود جدید

        return score.total_score / 100.0

    def get_top_nodes(self, limit: int = 10) -> List[Tuple[str, float]]:
        """دریافت برترین نودها"""
        sorted_nodes = sorted(
            self.reputation_scores.items(), key=lambda x: x[1].total_score, reverse=True
        )

        return [(node_id, score.total_score) for node_id, score in sorted_nodes[:limit]]

    def get_stats(self) -> Dict:
        """دریافت آمار سیستم"""
        if not self.reputation_scores:
            return {"total_nodes": 0, "avg_reputation": 0.0, "trust_distribution": {}}

        total_nodes = len(self.reputation_scores)
        avg_reputation = sum(s.total_score for s in self.reputation_scores.values()) / total_nodes

        # توزیع سطوح اعتماد
        trust_distribution = defaultdict(int)
        for score in self.reputation_scores.values():
            trust_distribution[score.trust_level] += 1

        return {
            "total_nodes": total_nodes,
            "avg_reputation": round(avg_reputation, 2),
            "trust_distribution": dict(trust_distribution),
            "top_nodes": self.get_top_nodes(5),
        }

    def apply_decay(self):
        """
        اعمال زوال زمانی به رویدادهای قدیمی

        رویدادهای قدیمی‌تر تأثیر کمتری دارند
        """
        current_time = time()
        decay_threshold = 30 * 86400  # 30 روز

        for node_id, history in self.node_histories.items():
            # فیلتر رویدادهای خیلی قدیمی
            history.events = [
                (t, event, meta)
                for t, event, meta in history.events
                if current_time - t < decay_threshold
            ]

            # محاسبه مجدد
            self._recalculate_reputation(node_id)

    def detect_suspicious_behavior(self, node_id: str) -> List[str]:
        """
        شناسایی رفتار مشکوک

        Returns:
            لیست هشدارها
        """
        warnings = []

        if node_id not in self.node_histories:
            return warnings

        history = self.node_histories[node_id]
        score = self.reputation_scores[node_id]

        # 1. نرخ رد بالا
        if history.total_contributions > 10:
            rejection_rate = history.rejected_contributions / history.total_contributions
            if rejection_rate > 0.5:
                warnings.append(f"High rejection rate: {rejection_rate:.1%}")

        # 2. مشارکت‌های ناگهانی زیاد
        recent_events = [e for t, e, m in history.events if time() - t < 3600]  # آخرین ساعت
        if len(recent_events) > 100:
            warnings.append(f"Suspicious activity: {len(recent_events)} events in 1 hour")

        # 3. کیفیت پایین مداوم
        if score.quality_score < 20 and history.total_contributions > 5:
            warnings.append(f"Consistently low quality: {score.quality_score:.1f}")

        return warnings


# Singleton instance
_reputation_system = None


def get_reputation_system() -> ReputationSystem:
    """دریافت instance سیستم اعتبار"""
    global _reputation_system
    if _reputation_system is None:
        _reputation_system = ReputationSystem()
    return _reputation_system
