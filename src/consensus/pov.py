"""
Laniakea Protocol - Proof of Value (PoV)
اثبات ارزش
"""

from typing import List
from src.core.models import Solution, ValueVector

class ProofOfValue:
    """
    الگوریتم اجماع اثبات ارزش
    به جای قدرت محاسباتی، به راه‌حل‌ها بر اساس ارزش چندبعدی آن‌ها پاداش می‌دهد.
    """

    def __init__(self, solution_pool: List[Solution], min_value_threshold: float = 10.0):
        """
        Args:
            solution_pool: استخر راه‌حل‌های موجود برای انتخاب
            min_value_threshold: حداقل ارزش کل برای در نظر گرفتن یک راه‌حل
        """
        self.solution_pool = solution_pool
        self.min_value_threshold = min_value_threshold

    def select_winning_solution(self) -> Solution:
        """
        انتخاب بهترین راه‌حل از استخر بر اساس ارزش کل.

        Returns:
            راه‌حل برنده یا None اگر هیچ راه‌حلی واجد شرایط نباشد.
        """
        eligible_solutions = [s for s in self.solution_pool if s.value_vector.total_value() >= self.min_value_threshold]

        if not eligible_solutions:
            return None

        # مرتب‌سازی بر اساس ارزش کل به صورت نزولی
        sorted_solutions = sorted(eligible_solutions, key=lambda s: s.value_vector.total_value(), reverse=True)

        # در یک سیستم واقعی، ممکن است مکانیزم‌های پیچیده‌تری برای جلوگیری از تمرکز وجود داشته باشد
        # مانند انتخاب تصادفی وزن‌دار.
        
        return sorted_solutions[0]
