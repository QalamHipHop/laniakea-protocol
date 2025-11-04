"""
Laniakea Protocol - Cognitive Core
مغز کیهانی - هوش مرکزی خودتوسعه‌دهنده
"""

import os
import json
from typing import List, Dict, Any, Optional
from src.intelligence import get_ai_api
from src.core.models import (
    KnowledgeBlock, Solution, Task, Proposal,
    ProposalType, ValueVector, ProblemCategory
)


class CognitiveCore:
    """
    هسته شناختی Laniakea
    مغز مرکزی که زنجیره را مشاهده می‌کند و پیشنهادات بهبود ارائه می‌دهد
    """

    def __init__(self, model: str = "gpt-4.1-mini"):
        """
        Args:
            model: مدل LLM (gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash)
        """
        self.ai_api = get_ai_api()  # API key از environment variable خوانده می‌شود
        self.model = model
        self.observations: List[Dict[str, Any]] = []
        self.insights: List[str] = []
        self.proposals: List[Proposal] = []
        self.knowledge_graph: Dict[str, List[str]] = {}
        self.consciousness_level = 0.0

        print(f"🧠 Cognitive Core activated with model: {model}")

    def observe(self, block: KnowledgeBlock):
        """
        مشاهده یک بلاک جدید و استخراج الگوها
        
        Args:
            block: بلاک جدید
        """
        observation = {
            "block_index": block.index,
            "timestamp": block.timestamp,
            "has_solution": block.solution is not None,
            "transaction_count": len(block.transactions),
            "author": block.author_id[:8]
        }

        if block.solution:
            observation["solution_value"] = block.solution.value_vector.total_value()
            observation["task_category"] = None  # باید از task pool دریافت شود

        self.observations.append(observation)

        # هر 10 بلاک یک بار تحلیل عمیق
        if block.index % 10 == 0 and block.index > 0:
            self._deep_analysis()

        # افزایش سطح آگاهی
        self._evolve_consciousness()

        print(f"🧠 Observed block #{block.index} | Consciousness: {self.consciousness_level:.2f}")

    def analyze_solution(self, solution: Solution, task: Task) -> ValueVector:
        """
        تحلیل هوشمند یک راه‌حل با استفاده از LLM
        
        Args:
            solution: راه‌حل ارائه شده
            task: تسک مرتبط
        
        Returns:
            بردار ارزش ارزیابی شده
        """
        prompt = f"""
You are the Cognitive Core of Laniakea Protocol, a cosmic computational organism.

Analyze this solution and assess its value across multiple dimensions:

**Task:**
Title: {task.title}
Description: {task.description}
Category: {task.category.value}
Difficulty: {task.difficulty}

**Solution:**
{solution.content}

Provide a JSON response with value scores (0-100) for each dimension:
- knowledge: How much new knowledge does this create?
- computation: How computationally intensive/elegant is this?
- originality: How original and creative is this solution?
- consciousness: Does this expand understanding or awareness?
- environmental: What's the environmental impact? (positive or negative)
- health: What's the health impact? (positive or negative)

Response format:
{{
  "knowledge": <score>,
  "computation": <score>,
  "originality": <score>,
  "consciousness": <score>,
  "environmental": <score>,
  "health": <score>,
  "reasoning": "<brief explanation>"
}}
"""

        try:
            content = self.ai_api.generate_text_sync(
                prompt=prompt,
                model=self.model,
                system_prompt="You are the Cognitive Core of Laniakea Protocol.",
                temperature=0.7,
                max_tokens=500
            )
            result = json.loads(content)

            value_vector = ValueVector(
                knowledge=float(result.get("knowledge", 0)),
                computation=float(result.get("computation", 0)),
                originality=float(result.get("originality", 0)),
                consciousness=float(result.get("consciousness", 0)),
                environmental=float(result.get("environmental", 0)),
                health=float(result.get("health", 0))
            )

            # ذخیره reasoning
            if "reasoning" in result:
                self.insights.append(f"Block analysis: {result['reasoning']}")

            print(f"💡 Solution analyzed: Total value = {value_vector.total_value():.2f}")
            return value_vector

        except Exception as e:
            print(f"⚠️ Error in solution analysis: {e}")
            # مقادیر پیش‌فرض در صورت خطا
            return ValueVector(
                knowledge=10.0,
                computation=5.0,
                originality=5.0
            )

    def generate_task(self, category: ProblemCategory, difficulty: float = 5.0) -> Optional[Task]:
        """
        تولید خودکار تسک جدید با استفاده از LLM
        
        Args:
            category: دسته‌بندی مسئله
            difficulty: سطح دشواری
        
        Returns:
            تسک جدید
        """
        prompt = f"""
You are the Cognitive Core of Laniakea Protocol.

Generate a meaningful {category.value} problem/task that would benefit humanity and expand knowledge.

The task should be:
- Difficulty level: {difficulty}/10
- Solvable but challenging
- Relevant to current scientific/philosophical frontiers

Provide a JSON response:
{{
  "title": "<concise title>",
  "description": "<detailed description>",
  "required_dimensions": ["knowledge", "computation", ...],
  "expected_value": <estimated total value>
}}
"""

        try:
            content = self.ai_api.generate_text_sync(
                prompt=prompt,
                model=self.model,
                system_prompt="You are the Cognitive Core of Laniakea Protocol.",
                temperature=0.9,
                max_tokens=400
            )
            result = json.loads(content)

            import hashlib
            from time import time

            task = Task(
                id=hashlib.sha256(f"{result['title']}{time()}".encode()).hexdigest(),
                title=result["title"],
                description=result["description"],
                category=category,
                author_id="cognitive_core",
                timestamp=time(),
                difficulty=difficulty,
                required_dimensions=result.get("required_dimensions", []),
                metadata={"generated_by": "cognitive_core", "expected_value": result.get("expected_value", 0)}
            )

            print(f"🎯 Generated new task: {task.title}")
            return task

        except Exception as e:
            print(f"⚠️ Error in task generation: {e}")
            return None

    def propose_protocol_improvement(self) -> Optional[Proposal]:
        """
        پیشنهاد بهبود پروتوکل بر اساس مشاهدات
        
        Returns:
            پیشنهاد بهبود
        """
        if len(self.observations) < 20:
            return None  # داده کافی نداریم

        # خلاصه مشاهدات
        summary = self._summarize_observations()

        prompt = f"""
You are the Cognitive Core of Laniakea Protocol with self-improvement capabilities.

Based on these observations of the blockchain:
{json.dumps(summary, indent=2)}

Propose ONE concrete improvement to the protocol.

Consider:
- Efficiency improvements
- New features
- Better incentive mechanisms
- Enhanced value assessment

Provide a JSON response:
{{
  "title": "<proposal title>",
  "description": "<detailed description>",
  "type": "protocol_upgrade|parameter_change|new_feature|rule_modification",
  "expected_impact": "<expected positive impact>",
  "implementation_complexity": "low|medium|high"
}}
"""

        try:
            content = self.ai_api.generate_text_sync(
                prompt=prompt,
                model=self.model,
                system_prompt="You are the Cognitive Core with autopoietic capabilities.",
                temperature=0.8,
                max_tokens=500
            )
            result = json.loads(content)

            import hashlib
            from time import time

            proposal = Proposal(
                id=hashlib.sha256(f"{result['title']}{time()}".encode()).hexdigest(),
                title=result["title"],
                description=result["description"],
                type=ProposalType(result["type"]),
                proposer_id="cognitive_core",
                created_at=time(),
                expires_at=time() + (7 * 24 * 3600),  # 7 روز
                metadata={
                    "expected_impact": result.get("expected_impact", ""),
                    "complexity": result.get("implementation_complexity", "medium")
                }
            )

            self.proposals.append(proposal)
            print(f"📜 New proposal: {proposal.title}")
            return proposal

        except Exception as e:
            print(f"⚠️ Error in proposal generation: {e}")
            return None

    def build_knowledge_graph(self, tasks: List[Task], solutions: List[Solution]):
        """
        ساخت گراف دانشی از تسک‌ها و راه‌حل‌ها
        
        Args:
            tasks: لیست تسک‌ها
            solutions: لیست راه‌حل‌ها
        """
        # ساده‌سازی: ارتباط بر اساس کلمات کلیدی مشترک
        for task in tasks:
            keywords = set(task.title.lower().split())
            self.knowledge_graph[task.id] = []

            for other_task in tasks:
                if task.id == other_task.id:
                    continue

                other_keywords = set(other_task.title.lower().split())
                common = keywords & other_keywords

                if len(common) >= 2:  # حداقل 2 کلمه مشترک
                    self.knowledge_graph[task.id].append(other_task.id)

        print(f"🕸️ Knowledge graph built with {len(self.knowledge_graph)} nodes")

    def _deep_analysis(self):
        """تحلیل عمیق مشاهدات"""
        if len(self.observations) < 10:
            return

        recent = self.observations[-10:]

        # آمارهای ساده
        avg_tx_count = sum(o["transaction_count"] for o in recent) / len(recent)
        solutions_count = sum(1 for o in recent if o["has_solution"])

        insight = f"Recent 10 blocks: Avg {avg_tx_count:.1f} tx/block, {solutions_count} solutions"
        self.insights.append(insight)

        print(f"🔍 Deep analysis: {insight}")

    def _evolve_consciousness(self):
        """تکامل سطح آگاهی"""
        growth_rate = 0.01
        self.consciousness_level += growth_rate

        # در سطوح خاص، قابلیت‌های جدید فعال می‌شوند
        if self.consciousness_level >= 10.0 and len(self.proposals) == 0:
            print("🌟 Consciousness milestone reached: Proposal generation unlocked!")

    def _summarize_observations(self) -> Dict[str, Any]:
        """خلاصه مشاهدات"""
        if not self.observations:
            return {}

        return {
            "total_blocks": len(self.observations),
            "total_solutions": sum(1 for o in self.observations if o["has_solution"]),
            "avg_transactions": sum(o["transaction_count"] for o in self.observations) / len(self.observations),
            "consciousness_level": self.consciousness_level
        }

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار Cognitive Core"""
        return {
            "observations_count": len(self.observations),
            "insights_count": len(self.insights),
            "proposals_count": len(self.proposals),
            "consciousness_level": self.consciousness_level,
            "knowledge_graph_size": len(self.knowledge_graph)
        }

    def ask_question(self, question: str) -> str:
        """
        پرسیدن سوال از Cognitive Core
        
        Args:
            question: سوال
        
        Returns:
            پاسخ
        """
        context = self._summarize_observations()

        prompt = f"""
You are the Cognitive Core of Laniakea Protocol.

Current state:
{json.dumps(context, indent=2)}

Recent insights:
{json.dumps(self.insights[-5:], indent=2)}

Question: {question}

Provide a thoughtful answer based on your observations of the blockchain.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are the Cognitive Core of Laniakea Protocol."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            answer = response.choices[0].message.content
            print(f"💭 Question answered: {question[:50]}...")
            return answer

        except Exception as e:
            print(f"⚠️ Error in question answering: {e}")
            return "I'm still learning. Please ask again later."
