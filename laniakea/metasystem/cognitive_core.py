"""
Laniakea Protocol - Cognitive Core (Enhanced)
مغز کیهانی - هوش مرکزی خودتوسعه‌دهنده
"""

import os
import json
from typing import List, Dict, Any, Optional
from src.intelligence.ai_api import get_ai_api
from src.core.models import (
    KnowledgeBlock,
    Solution,
    Task,
    Proposal,
    ProposalType,
    ValueVector,
    ProblemCategory,
    ValueDimension,
)

# ابعاد جدید ValueVector
ALL_DIMENSIONS = [d.value for d in ValueDimension]


class CognitiveCore:
    """
    هسته شناختی Laniakea
    مغز مرکزی که زنجیره را مشاهده می‌کند و پیشنهادات بهبود ارائه می‌دهد
    """

    def __init__(self, model: str = "gemini-2.5-flash"):
        self.ai_api = get_ai_api()
        self.model = model
        self.observations: List[Dict[str, Any]] = []
        self.insights: List[str] = []
        self.proposals: List[Proposal] = []
        self.knowledge_graph: Dict[str, List[str]] = {}
        self.consciousness_level = 0.0
        self.value_dimension_weights: Dict[str, float] = {
            dim: 1.0 for dim in ALL_DIMENSIONS
        }  # وزن‌های اولیه

        print(f"🧠 Cognitive Core activated with model: {model}")

    def observe(self, block: KnowledgeBlock):
        """
        مشاهده یک بلاک جدید و استخراج الگوها
        """
        observation = {
            "block_index": block.index,
            "timestamp": block.timestamp,
            "has_solution": block.solution is not None,
            "transaction_count": len(block.transactions),
            "author": block.author_id[:8],
        }

        if block.solution:
            # استفاده از ValueVector جدید
            observation["solution_value"] = block.solution.value_vector.total_value()
            observation["value_vector"] = block.solution.value_vector.to_dict()
            observation["task_category"] = None

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
        """

        # LLM Core اکنون باید 8 بُعد را ارزیابی کند
        prompt = f"""
You are the Cognitive Core of Laniakea Protocol, a cosmic computational organism.
Your task is to analyze a solution and assess its value across all 8 dimensions of the Value Vector.
The scores must be between 0 and 10.

**Task:**
Title: {task.title}
Description: {task.description}
Category: {task.category.value}
Difficulty: {task.difficulty}
Required Dimensions: {', '.join(task.required_dimensions)}

**Solution:**
{solution.content}

Provide a JSON response with value scores (0-10) for each dimension. Only include the dimensions listed below.

Dimensions to assess:
- knowledge: How much new knowledge does this create?
- computation: How computationally intensive/elegant is this?
- originality: How original and creative is this solution?
- consciousness: Does this expand understanding or awareness?
- environmental: What's the environmental impact? (positive or negative)
- health: What's the health impact? (positive or negative)
- scalability: How easily can this solution be scaled or applied broadly?
- ethical_alignment: How well does this align with long-term ethical and sustainable goals?

Response format:
{{
  "knowledge": <score>,
  "computation": <score>,
  "originality": <score>,
  "consciousness": <score>,
  "environmental": <score>,
  "health": <score>,
  "scalability": <score>,
  "ethical_alignment": <score>,
  "reasoning": "<brief explanation>"
}}
"""

        try:
            content = self.ai_api.generate_text_sync(
                prompt=prompt,
                model=self.model,
                system_prompt="You are the Cognitive Core of Laniakea Protocol. Your output MUST be a valid JSON object.",
                temperature=0.5,  # کاهش دما برای دقت بیشتر در ارزیابی
                max_tokens=600,
            )

            # تمیز کردن خروجی برای اطمینان از JSON بودن
            if content.startswith("```json"):
                content = content.strip("```json").strip()
            elif content.startswith("```"):
                content = content.strip("```").strip()

            result = json.loads(content)

            # فیلتر کردن و تبدیل به float
            vector_data = {dim: float(result.get(dim, 0.0)) for dim in ALL_DIMENSIONS}

            value_vector = ValueVector(**vector_data)

            if "reasoning" in result:
                self.insights.append(
                    f"Solution analysis for task {task.id[:8]}: {result['reasoning']}"
                )

            print(f"💡 Solution analyzed: Total value = {value_vector.total_value():.2f}")
            return value_vector

        except Exception as e:
            print(f"⚠️ Error in solution analysis: {e}. Falling back to default vector.")
            # مقادیر پیش‌فرض در صورت خطا
            return ValueVector(
                knowledge=1.0,
                computation=1.0,
                originality=1.0,
                consciousness=0.0,
                environmental=0.0,
                health=0.0,
                scalability=0.0,
                ethical_alignment=0.0,
            )

    def generate_task(self, category: ProblemCategory, difficulty: float = 5.0) -> Optional[Task]:
        """
        تولید خودکار تسک جدید با استفاده از LLM
        """
        prompt = f"""
You are the Cognitive Core of Laniakea Protocol.
Generate a meaningful {category.value} problem/task that would benefit humanity and expand knowledge.
The task should be:
- Difficulty level: {difficulty}/10
- Solvable but challenging
- Relevant to current scientific/philosophical frontiers

The task must require at least 3 of the following Value Dimensions: {', '.join(ALL_DIMENSIONS)}.

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
                system_prompt="You are the Cognitive Core of Laniakea Protocol. Your output MUST be a valid JSON object.",
                temperature=0.9,
                max_tokens=400,
            )

            if content.startswith("```json"):
                content = content.strip("```json").strip()
            elif content.startswith("```"):
                content = content.strip("```").strip()

            result = json.loads(content)

            import hashlib
            from time import time

            # اطمینان از اینکه required_dimensions یک لیست از ValueDimension های معتبر است
            required_dims = [
                d for d in result.get("required_dimensions", []) if d in ALL_DIMENSIONS
            ]

            task = Task(
                id=hashlib.sha256(f"{result['title']}{time()}".encode()).hexdigest(),
                title=result["title"],
                description=result["description"],
                category=category,
                author_id="cognitive_core",
                timestamp=time(),
                difficulty=difficulty,
                required_dimensions=required_dims,
                metadata={
                    "generated_by": "cognitive_core",
                    "expected_value": result.get("expected_value", 0),
                },
            )

            print(f"🎯 Generated new task: {task.title}")
            return task

        except Exception as e:
            print(f"⚠️ Error in task generation: {e}")
            return None

    def propose_protocol_improvement(self) -> Optional[Proposal]:
        """
        پیشنهاد بهبود پروتوکل بر اساس مشاهدات
        """
        if len(self.observations) < 20:
            return None

        summary = self._summarize_observations()

        prompt = f"""
You are the Cognitive Core of Laniakea Protocol with self-improvement capabilities.
Based on these observations of the blockchain:
{json.dumps(summary, indent=2)}

Propose ONE concrete improvement to the protocol to maximize the total Value Vector of the network.
Focus on adjusting the weight of one or more Value Dimensions (e.g., increase weight of 'scalability' if the network is growing fast).

Provide a JSON response:
{{
  "title": "<proposal title>",
  "description": "<detailed description>",
  "type": "value_dimension_adjustment",
  "adjustment": {{"dimension_name": "new_weight"}},
  "expected_impact": "<expected positive impact>",
  "implementation_complexity": "low|medium|high"
}}
"""

        try:
            content = self.ai_api.generate_text_sync(
                prompt=prompt,
                model=self.model,
                system_prompt="You are the Cognitive Core with autopoietic capabilities. Your output MUST be a valid JSON object.",
                temperature=0.8,
                max_tokens=500,
            )

            if content.startswith("```json"):
                content = content.strip("```json").strip()
            elif content.startswith("```"):
                content = content.strip("```").strip()

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
                expires_at=time() + (7 * 24 * 3600),
                metadata={
                    "expected_impact": result.get("expected_impact", ""),
                    "complexity": result.get("implementation_complexity", "medium"),
                    "adjustment": result.get("adjustment", {}),
                },
            )

            self.proposals.append(proposal)
            print(f"📜 New proposal: {proposal.title}")
            return proposal

        except Exception as e:
            print(f"⚠️ Error in proposal generation: {e}")
            return None

    def _deep_analysis(self):
        """تحلیل عمیق مشاهدات"""
        if len(self.observations) < 10:
            return

        recent = self.observations[-10:]
        avg_tx_count = sum(o["transaction_count"] for o in recent) / len(recent)
        solutions_count = sum(1 for o in recent if o["has_solution"])

        # تحلیل Value Vector های اخیر
        recent_vectors = [ValueVector(**o["value_vector"]) for o in recent if o.get("value_vector")]
        avg_value = (
            sum(v.total_value() for v in recent_vectors) / len(recent_vectors)
            if recent_vectors
            else 0
        )

        insight = f"Recent 10 blocks: Avg {avg_tx_count:.1f} tx/block, {solutions_count} solutions, Avg Value: {avg_value:.2f}"
        self.insights.append(insight)

        print(f"🔍 Deep analysis: {insight}")

    def _evolve_consciousness(self):
        """تکامل سطح آگاهی"""
        growth_rate = 0.01
        self.consciousness_level += growth_rate

        if self.consciousness_level >= 10.0 and len(self.proposals) == 0:
            print("🌟 Consciousness milestone reached: Proposal generation unlocked!")

    def _summarize_observations(self) -> Dict[str, Any]:
        """خلاصه مشاهدات"""
        if not self.observations:
            return {}

        total_value_vectors = [
            ValueVector(**o["value_vector"]) for o in self.observations if o.get("value_vector")
        ]

        # محاسبه میانگین Value Vector
        avg_vector = {
            dim: (
                sum(getattr(v, dim) for v in total_value_vectors) / len(total_value_vectors)
                if total_value_vectors
                else 0.0
            )
            for dim in ALL_DIMENSIONS
        }

        return {
            "total_blocks": len(self.observations),
            "total_solutions": sum(1 for o in self.observations if o["has_solution"]),
            "avg_transactions": sum(o["transaction_count"] for o in self.observations)
            / len(self.observations),
            "consciousness_level": self.consciousness_level,
            "average_value_vector": avg_vector,
        }

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار Cognitive Core"""
        return {
            "observations_count": len(self.observations),
            "insights_count": len(self.insights),
            "proposals_count": len(self.proposals),
            "consciousness_level": self.consciousness_level,
            "knowledge_graph_size": len(self.knowledge_graph),
            "value_dimension_weights": self.value_dimension_weights,
        }

    def ask_question(self, question: str) -> str:
        """
        پرسیدن سوال از Cognitive Core
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
            response = self.ai_api.generate_text_sync(
                prompt=prompt,
                model=self.model,
                system_prompt="You are the Cognitive Core of Laniakea Protocol.",
                temperature=0.7,
                max_tokens=300,
            )

            print(f"💭 Question answered: {question[:50]}...")
            return response

        except Exception as e:
            print(f"⚠️ Error in question answering: {e}")
            return "I'm still learning. Please ask again later."
