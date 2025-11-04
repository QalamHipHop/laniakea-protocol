"""
Laniakea Protocol - Hash Modernity System
سیستم تبدیل کشفیات علمی/فلسفی به نرخ‌های هش مدرنیته
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.core.models import Task, Solution, ValueVector, ProblemCategory


class HashModernityEngine:
    """
    موتور Hash Modernity
    تبدیل کشفیات و دانش به هش‌های قابل اعتبارسنجی
    """

    def __init__(self):
        self.discovery_cache: Dict[str, str] = {}
        self.modernity_index = 0.0

    def compute_discovery_hash(
        self,
        discovery_content: str,
        context: Dict[str, Any],
        timestamp: Optional[float] = None
    ) -> str:
        """
        محاسبه هش یک کشف
        
        Args:
            discovery_content: محتوای کشف
            context: زمینه و متادیتا
            timestamp: زمان کشف
        
        Returns:
            هش کشف
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()

        discovery_data = {
            "content": discovery_content,
            "context": context,
            "timestamp": timestamp,
            "modernity_index": self.modernity_index
        }

        discovery_json = json.dumps(discovery_data, sort_keys=True)
        discovery_hash = hashlib.sha256(discovery_json.encode()).hexdigest()

        # ذخیره در کش
        self.discovery_cache[discovery_hash] = discovery_content

        return discovery_hash

    def compute_proof_of_discovery(
        self,
        task: Task,
        solution: Solution,
        difficulty: int = 4
    ) -> str:
        """
        محاسبه Proof of Discovery
        اثبات اینکه یک کشف واقعی انجام شده است
        
        Args:
            task: تسک اصلی
            solution: راه‌حل ارائه شده
            difficulty: سطح دشواری (تعداد صفرهای ابتدایی)
        
        Returns:
            proof string
        """
        nonce = 0
        prefix = '0' * difficulty

        while True:
            proof_data = {
                "task_id": task.id,
                "solution_id": solution.id,
                "content": solution.content,
                "nonce": nonce
            }
            proof_json = json.dumps(proof_data, sort_keys=True)
            proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()

            if proof_hash.startswith(prefix):
                return proof_hash

            nonce += 1

            # محدودیت برای جلوگیری از حلقه بی‌نهایت
            if nonce > 1000000:
                break

        return ""

    def assess_modernity_rate(
        self,
        solution: Solution,
        task: Task,
        existing_solutions: List[Solution]
    ) -> float:
        """
        ارزیابی نرخ مدرنیته یک راه‌حل
        
        نرخ مدرنیته نشان می‌دهد که راه‌حل چقدر نو و پیشرفته است
        
        Args:
            solution: راه‌حل جدید
            task: تسک مرتبط
            existing_solutions: راه‌حل‌های موجود
        
        Returns:
            نرخ مدرنیته (0.0 تا 1.0)
        """
        # فاکتور 1: تشابه با راه‌حل‌های موجود (کمتر بهتر)
        similarity_penalty = self._calculate_similarity_penalty(solution, existing_solutions)

        # فاکتور 2: پیچیدگی راه‌حل
        complexity_score = self._calculate_complexity_score(solution)

        # فاکتور 3: ارزش چند بُعدی
        value_score = solution.value_vector.total_value() / 100.0  # نرمال‌سازی

        # فاکتور 4: دشواری تسک
        difficulty_multiplier = task.difficulty / 10.0

        # محاسبه نهایی
        modernity_rate = (
            (1.0 - similarity_penalty) * 0.3 +
            complexity_score * 0.3 +
            value_score * 0.3 +
            difficulty_multiplier * 0.1
        )

        return min(1.0, max(0.0, modernity_rate))

    def _calculate_similarity_penalty(
        self,
        solution: Solution,
        existing_solutions: List[Solution]
    ) -> float:
        """محاسبه جریمه تشابه با راه‌حل‌های موجود"""
        if not existing_solutions:
            return 0.0

        solution_hash = hashlib.sha256(solution.content.encode()).hexdigest()
        max_similarity = 0.0

        for existing in existing_solutions:
            existing_hash = hashlib.sha256(existing.content.encode()).hexdigest()

            # محاسبه تشابه ساده بر اساس هش
            # در واقعیت باید از الگوریتم‌های پیچیده‌تر استفاده شود
            common_chars = sum(
                1 for a, b in zip(solution_hash, existing_hash) if a == b
            )
            similarity = common_chars / len(solution_hash)
            max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _calculate_complexity_score(self, solution: Solution) -> float:
        """محاسبه امتیاز پیچیدگی راه‌حل"""
        content = solution.content

        # فاکتورهای پیچیدگی
        length_score = min(1.0, len(content) / 1000.0)
        unique_words = len(set(content.split()))
        vocabulary_score = min(1.0, unique_words / 100.0)

        # امتیاز نهایی
        complexity = (length_score * 0.5 + vocabulary_score * 0.5)

        return complexity

    def create_modernity_token(
        self,
        solution: Solution,
        task: Task,
        modernity_rate: float
    ) -> Dict[str, Any]:
        """
        ایجاد توکن مدرنیته
        
        توکن مدرنیته نشان‌دهنده ارزش نوآوری و پیشرفت است
        
        Args:
            solution: راه‌حل
            task: تسک
            modernity_rate: نرخ مدرنیته
        
        Returns:
            توکن مدرنیته
        """
        token = {
            "id": self._generate_token_id(solution, task),
            "solution_id": solution.id,
            "task_id": task.id,
            "modernity_rate": modernity_rate,
            "value_vector": solution.value_vector.to_dict(),
            "category": task.category.value,
            "timestamp": solution.timestamp,
            "hash": self.compute_discovery_hash(
                solution.content,
                {"task": task.title, "category": task.category.value},
                solution.timestamp
            )
        }

        return token

    def _generate_token_id(self, solution: Solution, task: Task) -> str:
        """تولید شناسه یکتا برای توکن"""
        data = f"{solution.id}{task.id}{solution.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_proof_of_discovery(
        self,
        proof_hash: str,
        difficulty: int = 4
    ) -> bool:
        """
        اعتبارسنجی Proof of Discovery
        
        Args:
            proof_hash: هش اثبات
            difficulty: سطح دشواری
        
        Returns:
            True اگر معتبر باشد
        """
        prefix = '0' * difficulty
        return proof_hash.startswith(prefix)

    def compute_hash_rate(
        self,
        solutions_count: int,
        time_period: float
    ) -> float:
        """
        محاسبه نرخ هش (تعداد کشفیات در واحد زمان)
        
        Args:
            solutions_count: تعداد راه‌حل‌ها
            time_period: بازه زمانی (ثانیه)
        
        Returns:
            نرخ هش (کشف در ثانیه)
        """
        if time_period <= 0:
            return 0.0

        return solutions_count / time_period

    def update_modernity_index(self, new_discoveries: int):
        """
        به‌روزرسانی شاخص مدرنیته کلی سیستم
        
        Args:
            new_discoveries: تعداد کشفیات جدید
        """
        growth_rate = 0.01
        self.modernity_index += new_discoveries * growth_rate

    def get_modernity_stats(self) -> Dict[str, Any]:
        """دریافت آمار مدرنیته"""
        return {
            "modernity_index": self.modernity_index,
            "total_discoveries": len(self.discovery_cache),
            "cache_size": len(self.discovery_cache)
        }


class ProofOfValue:
    """
    Proof of Value - اثبات ارزش
    جایگزین Proof of Work که بر اساس ارزش واقعی است
    """

    @staticmethod
    def calculate_value_proof(
        solution: Solution,
        task: Task,
        validators: List[str]
    ) -> float:
        """
        محاسبه اثبات ارزش
        
        Args:
            solution: راه‌حل
            task: تسک
            validators: لیست اعتبارسنج‌ها
        
        Returns:
            امتیاز اثبات ارزش
        """
        # ارزش پایه از ValueVector
        base_value = solution.value_vector.total_value()

        # ضریب دشواری تسک
        difficulty_multiplier = task.difficulty / 10.0

        # ضریب اعتبارسنج‌ها (هر چه بیشتر، معتبرتر)
        validator_multiplier = min(2.0, len(validators) / 5.0)

        # محاسبه نهایی
        value_proof = base_value * difficulty_multiplier * validator_multiplier

        return value_proof

    @staticmethod
    def verify_value_proof(
        solution: Solution,
        minimum_value: float
    ) -> bool:
        """
        اعتبارسنجی اثبات ارزش
        
        Args:
            solution: راه‌حل
            minimum_value: حداقل ارزش مورد نیاز
        
        Returns:
            True اگر ارزش کافی باشد
        """
        total_value = solution.value_vector.total_value()
        return total_value >= minimum_value
