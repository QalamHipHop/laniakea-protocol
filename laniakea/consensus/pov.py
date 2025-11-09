"""
Laniakea Protocol - Proof of Value (PoV) Enhanced
اثبات ارزش - نسخه بهبودیافته v0.0.01

بهبودها:
- الگوریتم انتخاب هوشمند با وزن‌دهی
- جلوگیری از تمرکز قدرت
- سیستم امتیازدهی پویا
- یکپارچگی با سیستم reputation
"""

import random
import hashlib
from typing import List, Optional, Dict, Any
from functools import lru_cache
from src.core.models import Solution, ValueVector


class ProofOfValue:
    """
    الگوریتم اجماع اثبات ارزش
    
    این الگوریتم به جای قدرت محاسباتی، به راه‌حل‌ها بر اساس 
    ارزش چندبعدی آن‌ها پاداش می‌دهد.
    
    ویژگی‌های کلیدی:
    - انتخاب وزن‌دار برای جلوگیری از تمرکز
    - امتیازدهی پویا بر اساس شرایط شبکه
    - یکپارچگی با سیستم reputation
    - بهینه‌سازی با caching
    """

    def __init__(
        self,
        solution_pool: List[Solution],
        min_value_threshold: float = 10.0,
        diversity_factor: float = 0.3,
        reputation_weight: float = 0.2,
    ):
        """
        راه‌اندازی الگوریتم PoV
        
        Args:
            solution_pool: استخر راه‌حل‌های موجود برای انتخاب
            min_value_threshold: حداقل ارزش کل برای در نظر گرفتن یک راه‌حل
            diversity_factor: ضریب تنوع (0-1) - هرچه بالاتر، تنوع بیشتر
            reputation_weight: وزن reputation در امتیاز نهایی (0-1)
        """
        self.solution_pool = solution_pool
        self.min_value_threshold = min_value_threshold
        self.diversity_factor = diversity_factor
        self.reputation_weight = reputation_weight
        
        # آمار
        self.stats = {
            "total_selections": 0,
            "unique_winners": set(),
            "avg_value": 0.0,
            "diversity_score": 0.0,
        }

    @lru_cache(maxsize=128)
    def _calculate_value_score(self, solution_id: str, total_value: float) -> float:
        """
        محاسبه امتیاز ارزش با caching برای بهینه‌سازی
        
        Args:
            solution_id: شناسه راه‌حل
            total_value: ارزش کل
            
        Returns:
            امتیاز محاسبه شده
        """
        # استفاده از تابع لگاریتمی برای کاهش تأثیر ارزش‌های بسیار بالا
        import math
        return math.log1p(total_value)

    def calculate_solution_score(
        self,
        solution: Solution,
        network_state: Optional[Dict[str, Any]] = None,
        reputation_scores: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        محاسبه امتیاز نهایی یک راه‌حل
        
        این امتیاز ترکیبی از:
        - ارزش کل Value Vector
        - Reputation حل‌کننده
        - تنوع (فاصله از راه‌حل‌های قبلی)
        - شرایط شبکه
        
        Args:
            solution: راه‌حل مورد نظر
            network_state: وضعیت فعلی شبکه (اختیاری)
            reputation_scores: امتیازات reputation (اختیاری)
            
        Returns:
            امتیاز نهایی (float)
        """
        # محاسبه ارزش پایه
        base_value = solution.value_vector.total_value()
        value_score = self._calculate_value_score(solution.id, base_value)
        
        # امتیاز reputation
        reputation_score = 1.0
        if reputation_scores and solution.solver_id in reputation_scores:
            reputation_score = 1.0 + (reputation_scores[solution.solver_id] * self.reputation_weight)
        
        # امتیاز تنوع (بر اساس Originality)
        diversity_score = 1.0 + (solution.value_vector.originality * self.diversity_factor)
        
        # امتیاز شرایط شبکه
        network_multiplier = 1.0
        if network_state:
            # اگر شبکه به دنبال راه‌حل‌های خاصی است، وزن بیشتری بده
            if "priority_categories" in network_state:
                # این بخش می‌تواند بر اساس نیاز شبکه توسعه یابد
                pass
        
        # محاسبه امتیاز نهایی
        final_score = value_score * reputation_score * diversity_score * network_multiplier
        
        return final_score

    def select_winning_solution(
        self,
        network_state: Optional[Dict[str, Any]] = None,
        reputation_scores: Optional[Dict[str, float]] = None,
        use_weighted_random: bool = True,
    ) -> Optional[Solution]:
        """
        انتخاب بهترین راه‌حل از استخر
        
        Args:
            network_state: وضعیت فعلی شبکه
            reputation_scores: امتیازات reputation
            use_weighted_random: استفاده از انتخاب تصادفی وزن‌دار
            
        Returns:
            راه‌حل برنده یا None اگر هیچ راه‌حلی واجد شرایط نباشد
        """
        # فیلتر راه‌حل‌های واجد شرایط
        eligible_solutions = [
            s
            for s in self.solution_pool
            if s.value_vector.total_value() >= self.min_value_threshold
        ]

        if not eligible_solutions:
            return None

        # محاسبه امتیاز برای هر راه‌حل
        scored_solutions = [
            (
                solution,
                self.calculate_solution_score(solution, network_state, reputation_scores),
            )
            for solution in eligible_solutions
        ]

        # مرتب‌سازی بر اساس امتیاز
        scored_solutions.sort(key=lambda x: x[1], reverse=True)

        # انتخاب برنده
        if use_weighted_random and len(scored_solutions) > 1:
            # انتخاب تصادفی وزن‌دار برای جلوگیری از تمرکز
            winner = self._weighted_random_selection(scored_solutions)
        else:
            # انتخاب بهترین
            winner = scored_solutions[0][0]

        # به‌روزرسانی آمار
        self._update_stats(winner, scored_solutions)

        return winner

    def _weighted_random_selection(
        self, scored_solutions: List[tuple[Solution, float]]
    ) -> Solution:
        """
        انتخاب تصادفی وزن‌دار
        
        راه‌حل‌های با امتیاز بالاتر شانس بیشتری برای انتخاب دارند،
        اما راه‌حل‌های دیگر هم شانس دارند (برای تنوع)
        
        Args:
            scored_solutions: لیست راه‌حل‌ها و امتیازات
            
        Returns:
            راه‌حل انتخاب شده
        """
        # محدود کردن به top 10 برای کارایی
        top_solutions = scored_solutions[:10]
        
        # محاسبه وزن‌ها
        total_score = sum(score for _, score in top_solutions)
        
        if total_score == 0:
            return top_solutions[0][0]
        
        # نرمال‌سازی وزن‌ها
        weights = [score / total_score for _, score in top_solutions]
        
        # انتخاب تصادفی وزن‌دار
        selected = random.choices(
            [solution for solution, _ in top_solutions], weights=weights, k=1
        )[0]
        
        return selected

    def _update_stats(self, winner: Solution, all_scored: List[tuple[Solution, float]]):
        """به‌روزرسانی آمار"""
        self.stats["total_selections"] += 1
        self.stats["unique_winners"].add(winner.solver_id)
        
        # محاسبه میانگین ارزش
        total_value = sum(s.value_vector.total_value() for s, _ in all_scored)
        self.stats["avg_value"] = total_value / len(all_scored)
        
        # محاسبه امتیاز تنوع
        unique_solvers = len(set(s.solver_id for s, _ in all_scored))
        self.stats["diversity_score"] = unique_solvers / len(all_scored)

    def get_stats(self) -> Dict[str, Any]:
        """
        دریافت آمار الگوریتم
        
        Returns:
            دیکشنری حاوی آمار
        """
        return {
            "total_selections": self.stats["total_selections"],
            "unique_winners_count": len(self.stats["unique_winners"]),
            "avg_value": self.stats["avg_value"],
            "diversity_score": self.stats["diversity_score"],
            "min_value_threshold": self.min_value_threshold,
            "diversity_factor": self.diversity_factor,
            "reputation_weight": self.reputation_weight,
        }

    def adjust_difficulty(self, network_load: float):
        """
        تنظیم دشواری بر اساس بار شبکه
        
        Args:
            network_load: بار شبکه (0-1)
        """
        # افزایش threshold در صورت بار بالا
        if network_load > 0.8:
            self.min_value_threshold *= 1.1
        elif network_load < 0.3:
            self.min_value_threshold *= 0.9
        
        # محدود کردن threshold
        self.min_value_threshold = max(5.0, min(50.0, self.min_value_threshold))

    def simulate_selection(
        self, num_rounds: int = 100
    ) -> Dict[str, Any]:
        """
        شبیه‌سازی انتخاب برای تست الگوریتم
        
        Args:
            num_rounds: تعداد دور شبیه‌سازی
            
        Returns:
            نتایج شبیه‌سازی
        """
        winners = []
        
        for _ in range(num_rounds):
            winner = self.select_winning_solution(use_weighted_random=True)
            if winner:
                winners.append(winner.solver_id)
        
        # تحلیل نتایج
        from collections import Counter
        winner_counts = Counter(winners)
        
        return {
            "total_rounds": num_rounds,
            "unique_winners": len(winner_counts),
            "winner_distribution": dict(winner_counts.most_common(10)),
            "concentration_index": max(winner_counts.values()) / num_rounds if winners else 0,
        }
