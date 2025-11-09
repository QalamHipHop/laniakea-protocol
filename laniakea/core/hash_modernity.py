"""
Laniakea Protocol - Hash Modernity System (Enhanced)
سیستم تبدیل کشفیات علمی/فلسفی به نرخ‌های هش مدرنیته و اثبات ارزش (PoV)
"""

import hashlib
import json
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.core.models import Task, Solution, ValueVector, ProblemCategory

# --- ثابت‌های ریاضی ---
# برای نرمال‌سازی و وزن‌دهی در محاسبات مدرنیته
MAX_VALUE_DIMENSION = 10.0
MAX_DIFFICULTY = 10.0


class HashModernityEngine:
    """
    موتور Hash Modernity
    تبدیل کشفیات و دانش به هش‌های قابل اعتبارسنجی
    """

    def __init__(self):
        self.discovery_cache: Dict[str, str] = {}
        self.modernity_index = 0.0

    def compute_discovery_hash(
        self, discovery_content: str, context: Dict[str, Any], timestamp: Optional[float] = None
    ) -> str:
        """
        محاسبه هش یک کشف
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()

        discovery_data = {
            "content": discovery_content,
            "context": context,
            "timestamp": timestamp,
            "modernity_index": self.modernity_index,
        }

        # استفاده از JSON استاندارد برای اطمینان از ترتیب کلیدها
        discovery_json = json.dumps(discovery_data, sort_keys=True)
        discovery_hash = hashlib.sha256(discovery_json.encode()).hexdigest()

        self.discovery_cache[discovery_hash] = discovery_content

        return discovery_hash

    def compute_proof_of_discovery(
        self, task: Task, solution: Solution, difficulty: int = 4
    ) -> str:
        """
        محاسبه Proof of Discovery (PoD)
        اثبات اینکه یک کشف واقعی انجام شده است (شبیه به PoW ساده)
        """
        nonce = 0
        prefix = "0" * difficulty

        # ترکیب هش تسک و راه‌حل برای ایجاد یک فضای جستجوی منحصر به فرد
        base_hash = hashlib.sha256(f"{task.id}{solution.id}".encode()).hexdigest()

        while True:
            proof_data = f"{base_hash}{nonce}"
            proof_hash = hashlib.sha256(proof_data.encode()).hexdigest()

            if proof_hash.startswith(prefix):
                return proof_hash

            nonce += 1

            # محدودیت برای جلوگیری از حلقه بی‌نهایت در محیط شبیه‌سازی
            if nonce > 1000000:
                break

        return ""

    def assess_modernity_rate(
        self, solution: Solution, task: Task, existing_solutions: List[Solution]
    ) -> float:
        """
        ارزیابی نرخ مدرنیته یک راه‌حل (بر اساس الگوهای ریاضی پیشرفته)

        نرخ مدرنیته نشان می‌دهد که راه‌حل چقدر نو، پیچیده و ارزشمند است.
        """

        solution_vector_array = np.array(list(solution.value_vector.to_dict().values()))

        # 1. امتیاز نوآوری (Originality Score)
        if not existing_solutions:
            originality_score = 1.0
        else:
            existing_arrays = [
                np.array(list(s.value_vector.to_dict().values())) for s in existing_solutions
            ]
            mean_vector = np.mean(existing_arrays, axis=0)

            # فاصله اقلیدسی از میانگین (نشان‌دهنده نوآوری)
            distance = np.linalg.norm(solution_vector_array - mean_vector)

            # استفاده از تابع tanh برای نرمال‌سازی و محدود کردن فاصله (بهتر از سیگموئید برای مقادیر بزرگ)
            # tanh(x) = (e^x - e^-x) / (e^x + e^-x)
            # نرمال‌سازی فاصله: 0.5 * (np.tanh(distance / 5.0) + 1.0)
            originality_score = 0.5 * (np.tanh(distance / 5.0) + 1.0)  # 5.0 یک ضریب مقیاس است

        # 2. امتیاز پیچیدگی (Complexity Score)
        # تمرکز بر ابعاد دانش و محاسبات
        knowledge_score = solution.value_vector.knowledge / MAX_VALUE_DIMENSION
        computation_score = solution.value_vector.computation / MAX_VALUE_DIMENSION
        complexity_score = (knowledge_score + computation_score) / 2.0

        # 3. امتیاز ارزش (Value Score)
        # نرمال‌سازی ارزش کل
        total_value = solution.value_vector.total_value()
        value_score = total_value / (len(solution.value_vector.to_dict()) * MAX_VALUE_DIMENSION)

        # 4. ضریب دشواری تسک
        difficulty_multiplier = task.difficulty / MAX_DIFFICULTY

        # ترکیب نهایی با وزن‌دهی (می‌تواند توسط سیستم حکمرانی تغییر کند)
        modernity_rate = (
            originality_score * 0.40
            + complexity_score * 0.30
            + value_score * 0.20
            + difficulty_multiplier * 0.10
        )

        return min(1.0, max(0.0, modernity_rate))

    def create_modernity_token(
        self, solution: Solution, task: Task, modernity_rate: float
    ) -> Dict[str, Any]:
        """
        ایجاد توکن مدرنیته
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
                solution.timestamp,
            ),
        }

        return token

    def _generate_token_id(self, solution: Solution, task: Task) -> str:
        """تولید شناسه یکتا برای توکن"""
        data = f"{solution.id}{task.id}{solution.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_proof_of_discovery(self, proof_hash: str, difficulty: int = 4) -> bool:
        """
        اعتبارسنجی Proof of Discovery
        """
        prefix = "0" * difficulty
        return proof_hash.startswith(prefix)

    def update_modernity_index(self, new_discoveries: int, avg_modernity: float):
        """
        به‌روزرسانی شاخص مدرنیته کلی سیستم
        """
        # رشد شاخص بر اساس تعداد کشفیات و میانگین مدرنیته آنها
        growth_rate = 0.01 * avg_modernity
        self.modernity_index += new_discoveries * growth_rate

    def get_modernity_stats(self) -> Dict[str, Any]:
        """دریافت آمار مدرنیته"""
        return {
            "modernity_index": self.modernity_index,
            "total_discoveries": len(self.discovery_cache),
            "cache_size": len(self.discovery_cache),
        }


class ProofOfValue:
    """
    Proof of Value - اثبات ارزش (PoV)
    جایگزین Proof of Work که بر اساس ارزش واقعی است
    """

    @staticmethod
    def calculate_value_proof(
        solution: Solution, task: Task, modernity_rate: float, validators_count: int
    ) -> float:
        """
        محاسبه اثبات ارزش (PoV Score)

        PoV Score = (Total Value) * (Modernity Rate) * (Task Difficulty Multiplier) * (Validator Multiplier)
        """
        # 1. ارزش پایه از ValueVector
        base_value = solution.value_vector.total_value()

        # 2. ضریب دشواری تسک
        difficulty_multiplier = task.difficulty / MAX_DIFFICULTY
        # 2. ضریب اعتبارسنج‌ها (هر چه بیشتر، معتبرتر)
        # استفاده از لگاریتم برای کاهش تأثیر تعداد زیاد اعتبارسنج‌ها
        # ضریب اعتبارسنجی باید از 1.0 شروع شود و با افزایش تعداد اعتبارسنج‌ها به آرامی افزایش یابد.
        validator_multiplier = 1.0 + (
            np.log1p(validators_count) / np.log1p(10)
        )  # نرمال‌سازی بر اساس 10 اعتبارسنج
        # محاسبه نهایی
        value_proof = base_value * modernity_rate * difficulty_multiplier * validator_multiplier

        return float(value_proof)

    @staticmethod
    def verify_value_proof(
        solution: Solution, modernity_rate: float, minimum_value_proof: float
    ) -> bool:
        """
        اعتبارسنجی اثبات ارزش
        """
        # حداقل ارزش مورد نیاز بر اساس مدرنیته
        required_value = minimum_value_proof / modernity_rate

        total_value = solution.value_vector.total_value()

        # بررسی اینکه آیا ارزش کل راه‌حل با توجه به مدرنیته آن، حداقل مورد نیاز را برآورده می‌کند
        # در PoV، ما به دنبال حداکثرسازی ارزش هستیم، نه فقط برآورده کردن حداقل.
        # این تابع باید در نهایت با مقایسه PoV Score با PoV Score های دیگر جایگزین شود.
        # برای این نسخه، اعتبارسنجی ساده را حفظ می‌کنیم.
        return total_value >= minimum_value_proof / modernity_rate
