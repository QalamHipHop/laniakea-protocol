"""
Laniakea Protocol - Autonomous Task Generation System
سیستم تولید خودکار تسک

این سیستم به صورت خودکار تسک‌های جدید تولید می‌کند بر اساس:
- نیازهای شبکه
- دانش جمع‌آوری شده
- الگوهای کشف شده
- اهداف بلندمدت پروتوکل

ویژگی‌ها:
- تولید خودکار تسک بر اساس اولویت
- دسته‌بندی هوشمند
- تخمین دشواری
- پیشنهاد پاداش
- یکپارچگی با Knowledge Graph
"""

import asyncio
import random
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import json


class TaskCategory(Enum):
    """دسته‌بندی تسک‌ها"""

    SCIENTIFIC_RESEARCH = "scientific_research"
    DATA_ANALYSIS = "data_analysis"
    OPTIMIZATION = "optimization"
    PREDICTION = "prediction"
    KNOWLEDGE_SYNTHESIS = "knowledge_synthesis"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE = "creative"
    VERIFICATION = "verification"
    SIMULATION = "simulation"
    EDUCATION = "education"


class TaskDifficulty(Enum):
    """سطح دشواری"""

    TRIVIAL = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXPERT = 5
    RESEARCH = 6


class TaskPriority(Enum):
    """اولویت تسک"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


@dataclass
class TaskRequirements:
    """نیازمندی‌های یک تسک"""

    min_reputation: float = 0.0
    required_skills: List[str] = field(default_factory=list)
    min_compute_power: float = 0.0
    estimated_time_hours: float = 1.0
    requires_verification: bool = False


@dataclass
class TaskReward:
    """پاداش یک تسک"""

    base_reward: float
    bonus_multiplier: float = 1.0
    time_bonus: bool = True
    quality_bonus: bool = True

    def calculate_total(self, time_factor: float = 1.0, quality_factor: float = 1.0) -> float:
        """محاسبه پاداش کل"""
        total = self.base_reward * self.bonus_multiplier

        if self.time_bonus:
            total *= time_factor

        if self.quality_bonus:
            total *= quality_factor

        return total


@dataclass
class GeneratedTask:
    """یک تسک تولید شده"""

    id: str
    title: str
    description: str
    category: TaskCategory
    difficulty: TaskDifficulty
    priority: TaskPriority
    requirements: TaskRequirements
    reward: TaskReward
    created_at: float
    expires_at: Optional[float]
    tags: List[str]
    related_knowledge: List[str]
    verification_method: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "difficulty": self.difficulty.value,
            "priority": self.priority.value,
            "requirements": asdict(self.requirements),
            "reward": asdict(self.reward),
            "created_at": self.created_at,
            "created_at_iso": datetime.fromtimestamp(self.created_at).isoformat(),
            "expires_at": self.expires_at,
            "expires_at_iso": (
                datetime.fromtimestamp(self.expires_at).isoformat() if self.expires_at else None
            ),
            "tags": self.tags,
            "related_knowledge": self.related_knowledge,
            "verification_method": self.verification_method,
        }


class TaskGenerator:
    """
    سیستم تولید خودکار تسک

    این سیستم با استفاده از هوش مصنوعی و دانش جمع‌آوری شده،
    تسک‌های جدید و مفید تولید می‌کند.
    """

    def __init__(self):
        """راه‌اندازی task generator"""
        # تسک‌های تولید شده
        self.generated_tasks: Dict[str, GeneratedTask] = {}

        # تمپلیت‌های تسک
        self.task_templates = self._load_task_templates()

        # آمار
        self.stats = {
            "total_generated": 0,
            "by_category": {cat.value: 0 for cat in TaskCategory},
            "by_difficulty": {diff.value: 0 for diff in TaskDifficulty},
            "active_tasks": 0,
            "completed_tasks": 0,
        }

    def _load_task_templates(self) -> Dict[TaskCategory, List[Dict]]:
        """بارگذاری تمپلیت‌های تسک"""
        return {
            TaskCategory.SCIENTIFIC_RESEARCH: [
                {
                    "title_template": "تحلیل داده‌های {topic} از {source}",
                    "description_template": "تحلیل و استخراج الگوهای معنادار از داده‌های {topic} که از {source} جمع‌آوری شده است.",
                    "tags": ["research", "analysis", "data"],
                },
                {
                    "title_template": "بررسی ارتباط بین {concept1} و {concept2}",
                    "description_template": "یافتن و تحلیل ارتباطات بین {concept1} و {concept2} در حوزه {domain}.",
                    "tags": ["research", "correlation", "analysis"],
                },
            ],
            TaskCategory.DATA_ANALYSIS: [
                {
                    "title_template": "تحلیل آماری {dataset}",
                    "description_template": "انجام تحلیل آماری جامع بر روی {dataset} و ارائه گزارش.",
                    "tags": ["statistics", "analysis", "data"],
                },
            ],
            TaskCategory.OPTIMIZATION: [
                {
                    "title_template": "بهینه‌سازی {system} برای {goal}",
                    "description_template": "بهینه‌سازی عملکرد {system} برای دستیابی به {goal}.",
                    "tags": ["optimization", "performance"],
                },
            ],
            TaskCategory.PREDICTION: [
                {
                    "title_template": "پیش‌بینی {variable} بر اساس {factors}",
                    "description_template": "ساخت مدل پیش‌بینی برای {variable} با استفاده از {factors}.",
                    "tags": ["prediction", "ml", "forecasting"],
                },
            ],
            TaskCategory.KNOWLEDGE_SYNTHESIS: [
                {
                    "title_template": "ترکیب دانش از {sources} درباره {topic}",
                    "description_template": "جمع‌آوری و ترکیب دانش از {sources} مختلف درباره {topic}.",
                    "tags": ["synthesis", "knowledge", "integration"],
                },
            ],
        }

    def _generate_task_id(self, title: str) -> str:
        """تولید شناسه یکتا برای تسک"""
        timestamp = str(datetime.now().timestamp())
        unique_string = f"{title}_{timestamp}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    def _estimate_difficulty(
        self, category: TaskCategory, complexity_factors: Dict[str, Any]
    ) -> TaskDifficulty:
        """تخمین دشواری تسک"""
        # الگوریتم ساده برای تخمین دشواری
        score = 0

        # بر اساس دسته
        category_difficulty = {
            TaskCategory.SCIENTIFIC_RESEARCH: 4,
            TaskCategory.DATA_ANALYSIS: 3,
            TaskCategory.OPTIMIZATION: 4,
            TaskCategory.PREDICTION: 4,
            TaskCategory.KNOWLEDGE_SYNTHESIS: 3,
            TaskCategory.PROBLEM_SOLVING: 3,
            TaskCategory.CREATIVE: 2,
            TaskCategory.VERIFICATION: 2,
            TaskCategory.SIMULATION: 4,
            TaskCategory.EDUCATION: 2,
        }

        score += category_difficulty.get(category, 3)

        # بر اساس پیچیدگی
        if complexity_factors.get("requires_ml", False):
            score += 1
        if complexity_factors.get("large_dataset", False):
            score += 1
        if complexity_factors.get("novel_approach", False):
            score += 2

        # نرمال‌سازی
        score = min(6, max(1, score))

        return TaskDifficulty(score)

    def _calculate_reward(
        self, difficulty: TaskDifficulty, priority: TaskPriority, estimated_time: float
    ) -> TaskReward:
        """محاسبه پاداش تسک"""
        # پاداش پایه بر اساس دشواری
        base_rewards = {
            TaskDifficulty.TRIVIAL: 10,
            TaskDifficulty.EASY: 50,
            TaskDifficulty.MEDIUM: 150,
            TaskDifficulty.HARD: 400,
            TaskDifficulty.EXPERT: 1000,
            TaskDifficulty.RESEARCH: 2500,
        }

        base = base_rewards[difficulty]

        # ضریب اولویت
        priority_multipliers = {
            TaskPriority.LOW: 0.8,
            TaskPriority.NORMAL: 1.0,
            TaskPriority.HIGH: 1.5,
            TaskPriority.CRITICAL: 2.0,
            TaskPriority.URGENT: 2.5,
        }

        multiplier = priority_multipliers[priority]

        # ضریب زمان
        multiplier *= 1 + estimated_time / 10

        return TaskReward(
            base_reward=base, bonus_multiplier=multiplier, time_bonus=True, quality_bonus=True
        )

    async def generate_task(
        self,
        category: Optional[TaskCategory] = None,
        priority: Optional[TaskPriority] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> GeneratedTask:
        """
        تولید یک تسک جدید

        Args:
            category: دسته تسک (اختیاری)
            priority: اولویت (اختیاری)
            context: اطلاعات زمینه‌ای (اختیاری)

        Returns:
            تسک تولید شده
        """
        # انتخاب دسته
        if category is None:
            category = random.choice(list(TaskCategory))

        # انتخاب اولویت
        if priority is None:
            priority = random.choice(list(TaskPriority))

        # انتخاب تمپلیت
        templates = self.task_templates.get(category, [])
        if not templates:
            templates = [
                {"title_template": "تسک {category}", "description_template": "توضیحات", "tags": []}
            ]

        template = random.choice(templates)

        # پر کردن تمپلیت
        context = context or {}
        title = template["title_template"].format(
            topic=context.get("topic", "موضوع"),
            source=context.get("source", "منبع"),
            concept1=context.get("concept1", "مفهوم اول"),
            concept2=context.get("concept2", "مفهوم دوم"),
            domain=context.get("domain", "حوزه"),
            dataset=context.get("dataset", "مجموعه داده"),
            system=context.get("system", "سیستم"),
            goal=context.get("goal", "هدف"),
            variable=context.get("variable", "متغیر"),
            factors=context.get("factors", "عوامل"),
            sources=context.get("sources", "منابع"),
            category=category.value,
        )

        description = template["description_template"].format(**context, category=category.value)

        # تخمین دشواری
        complexity_factors = context.get("complexity_factors", {})
        difficulty = self._estimate_difficulty(category, complexity_factors)

        # تخمین زمان
        estimated_time = context.get("estimated_time", difficulty.value * 2)

        # محاسبه پاداش
        reward = self._calculate_reward(difficulty, priority, estimated_time)

        # نیازمندی‌ها
        requirements = TaskRequirements(
            min_reputation=difficulty.value * 10,
            required_skills=context.get("required_skills", []),
            min_compute_power=difficulty.value * 100,
            estimated_time_hours=estimated_time,
            requires_verification=difficulty.value >= 4,
        )

        # زمان انقضا
        expires_at = None
        if priority.value >= TaskPriority.HIGH.value:
            expires_at = datetime.now().timestamp() + (24 * 3600)  # 24 ساعت

        # تولید تسک
        task = GeneratedTask(
            id=self._generate_task_id(title),
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            priority=priority,
            requirements=requirements,
            reward=reward,
            created_at=datetime.now().timestamp(),
            expires_at=expires_at,
            tags=template.get("tags", []) + context.get("extra_tags", []),
            related_knowledge=context.get("related_knowledge", []),
            verification_method=context.get("verification_method"),
        )

        # ذخیره
        self.generated_tasks[task.id] = task

        # به‌روزرسانی آمار
        self.stats["total_generated"] += 1
        self.stats["by_category"][category.value] += 1
        self.stats["by_difficulty"][difficulty.value] += 1
        self.stats["active_tasks"] += 1

        return task

    async def generate_batch(
        self, count: int = 10, categories: Optional[List[TaskCategory]] = None
    ) -> List[GeneratedTask]:
        """تولید دسته‌ای از تسک‌ها"""
        tasks = []

        for _ in range(count):
            category = random.choice(categories) if categories else None
            task = await self.generate_task(category=category)
            tasks.append(task)

            # کمی تأخیر برای جلوگیری از ID تکراری
            await asyncio.sleep(0.01)

        return tasks

    def get_task(self, task_id: str) -> Optional[GeneratedTask]:
        """دریافت یک تسک"""
        return self.generated_tasks.get(task_id)

    def get_tasks_by_category(self, category: TaskCategory) -> List[GeneratedTask]:
        """دریافت تسک‌ها بر اساس دسته"""
        return [task for task in self.generated_tasks.values() if task.category == category]

    def get_tasks_by_difficulty(self, difficulty: TaskDifficulty) -> List[GeneratedTask]:
        """دریافت تسک‌ها بر اساس دشواری"""
        return [task for task in self.generated_tasks.values() if task.difficulty == difficulty]

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار"""
        return self.stats

    def export_tasks(self, filepath: str):
        """صادرات تسک‌ها به فایل"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "stats": self.stats,
            "tasks": [task.to_dict() for task in self.generated_tasks.values()],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ {len(self.generated_tasks)} تسک به {filepath} صادر شد")


# Singleton
_task_generator_instance: Optional[TaskGenerator] = None


def get_task_generator() -> TaskGenerator:
    """دریافت instance"""
    global _task_generator_instance

    if _task_generator_instance is None:
        _task_generator_instance = TaskGenerator()

    return _task_generator_instance


# مثال
async def main():
    """تست"""
    print("🧪 تست Task Generator\n")

    generator = get_task_generator()

    # تولید تسک‌های مختلف
    print("📝 تولید تسک‌ها...")
    tasks = await generator.generate_batch(count=5)

    for task in tasks:
        print(f"\n{'='*60}")
        print(f"🆔 ID: {task.id}")
        print(f"📌 عنوان: {task.title}")
        print(f"📝 توضیحات: {task.description}")
        print(f"🏷️  دسته: {task.category.value}")
        print(f"⚡ دشواری: {task.difficulty.name}")
        print(f"🎯 اولویت: {task.priority.name}")
        print(f"💰 پاداش پایه: {task.reward.base_reward}")
        print(f"🏷️  تگ‌ها: {', '.join(task.tags)}")

    # آمار
    print(f"\n{'='*60}")
    print("📊 آمار:")
    stats = generator.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # صادرات
    generator.export_tasks("generated_tasks.json")


if __name__ == "__main__":
    asyncio.run(main())
