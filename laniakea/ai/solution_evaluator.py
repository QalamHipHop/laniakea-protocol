"""AI Solution Evaluator
Evaluates solutions to Hard Problems and provides feedback and knowledge vector updates."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import numpy as np
from enum import Enum
from openai import OpenAI

from .problem_discovery_engine import ProblemDiscoveryEngine, HardProblem, ProblemAttempt

logger = logging.getLogger(__name__)

@dataclass
class SolutionEvaluation:
    """Represents the result of a solution evaluation."""
    evaluation_id: str
    scda_id: str
    problem_id: str
    overall_score: float  # 0.0 to 1.0
    feedback: str
    knowledge_gained: List[float]  # 8D vector update
    knowledge_insights: str
    evaluated_at: str

class SolutionEvaluator:
    """
    AI-powered engine for evaluating solutions to Hard Problems.
    Uses LLM APIs for nuanced assessment and knowledge vector calculation.
    """
    
    def __init__(self, llm_client: Optional[OpenAI] = None, problem_engine: Optional[ProblemDiscoveryEngine] = None):
        """Initialize the Solution Evaluator."""
        self.llm_client = llm_client
        self.problem_engine = problem_engine if problem_engine else ProblemDiscoveryEngine(llm_client=llm_client)
        self.evaluation_counter = 0
        logger.info("Solution Evaluator initialized")

    def evaluate_solution(self, problem_id: str, scda_id: str, solution_text: str) -> SolutionEvaluation:
        """
        Evaluate a solution provided by an SCDA for a specific problem.
        """
        problem = self.problem_engine.get_problem(problem_id)
        if not problem:
            raise ValueError(f"Problem with ID {problem_id} not found.")

        if not self.llm_client:
            logger.warning("LLM client not configured. Using heuristic evaluation.")
            return self._heuristic_evaluate(problem, scda_id, solution_text)

        try:
            prompt = self._prepare_evaluation_prompt(problem, solution_text)
            
            response = self.llm_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert scientific evaluator for the LaniakeA Protocol. Your task is to rigorously assess a user's solution to a complex problem. You must be objective, provide constructive feedback, and estimate the knowledge gained in an 8D vector format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            evaluation_data = json.loads(response.choices[0].message.content)
            
            # Create evaluation object
            self.evaluation_counter += 1
            evaluation_id = f"EVAL_{self.evaluation_counter:04d}"
            
            evaluation = SolutionEvaluation(
                evaluation_id=evaluation_id,
                scda_id=scda_id,
                problem_id=problem_id,
                overall_score=evaluation_data.get("overall_score", 0.0),
                feedback=evaluation_data.get("feedback", "No feedback provided."),
                knowledge_gained=evaluation_data.get("knowledge_gained", [0.0] * 8),
                knowledge_insights=evaluation_data.get("knowledge_insights", "No insights."),
                evaluated_at=datetime.now().isoformat()
            )
            
            # Record the attempt
            self.problem_engine.record_problem_attempt(
                scda_id=scda_id,
                problem_id=problem_id,
                solution_text=solution_text,
                success=evaluation.overall_score >= 0.7,  # Define success threshold
                time_spent=problem.time_estimate * 60, # Placeholder
                knowledge_gained=evaluation.knowledge_gained
            )
            
            logger.info(f"Evaluation {evaluation_id} completed for problem {problem_id}")
            return evaluation
        
        except Exception as e:
            logger.error(f"Error evaluating solution with LLM: {e}")
            # Fallback to heuristic evaluation on error
            return self._heuristic_evaluate(problem, scda_id, solution_text)

    def _prepare_evaluation_prompt(self, problem: HardProblem, solution_text: str) -> str:
        """
        Prepare a detailed prompt for LLM solution evaluation.
        """
        required_knowledge_str = ", ".join([f"{val:.2f}" for val in problem.required_knowledge])
        
        prompt = f"""
You are evaluating a solution for a Hard Problem in the LaniakeA Protocol.

**Problem Details:**
- Title: {problem.title}
- Description: {problem.description}
- Category: {problem.category}
- Difficulty: {problem.difficulty}
- Required Knowledge (8D Vector): [{required_knowledge_str}]
- Solution Outline (Reference): {problem.solution_outline}

**SCDA's Solution:**
---
{solution_text}
---

**Your Task:**
1. **Score (0.0 to 1.0):** Assign an `overall_score` based on the solution's correctness, completeness, depth, and creativity. A score of 0.7 or higher is considered a successful solution.
2. **Feedback:** Provide detailed, constructive `feedback` on the strengths and weaknesses of the solution.
3. **Knowledge Gained (8D Vector):** Estimate the `knowledge_gained` as an 8D vector (list of 8 floats, each between 0.0 and 1.0) representing the *increase* in the SCDA's knowledge across the 8 dimensions (Physics, Biology, Mathematics, Chemistry, Engineering, Computer Science, Philosophy, Cosmology). The magnitude of the vector should correlate with the score and the problem's difficulty.
4. **Insights:** Provide `knowledge_insights`—a brief summary of the key concepts learned or reinforced by the solution.

**Return the result as a JSON object with the following structure:**
{{
    "overall_score": 0.85,  # float between 0.0 and 1.0
    "feedback": "Your solution was excellent...",
    "knowledge_gained": [0.1, 0.05, 0.2, 0.0, 0.0, 0.15, 0.0, 0.0],  # 8D vector
    "knowledge_insights": "Deepened understanding of quantum field theory and its ethical implications."
}}
"""
        return prompt

    def _heuristic_evaluate(self, problem: HardProblem, scda_id: str, solution_text: str) -> SolutionEvaluation:
        """
        Fallback heuristic evaluation when LLM is unavailable or fails.
        """
        # Simple heuristic: score based on length and problem difficulty
        score = min(1.0, len(solution_text) / 500.0) * (problem.difficulty / 5.0)
        score = max(0.1, min(0.9, score)) # Clamp between 0.1 and 0.9

        # Knowledge gained is a fraction of required knowledge
        knowledge_gained = [x * score * 0.2 for x in problem.required_knowledge]

        evaluation_id = f"EVAL_HEURISTIC_{datetime.now().timestamp()}"
        
        evaluation = SolutionEvaluation(
            evaluation_id=evaluation_id,
            scda_id=scda_id,
            problem_id=problem.problem_id,
            overall_score=score,
            feedback="Heuristic evaluation used: The solution appears comprehensive based on its length and the problem's complexity. Please note that this is an automated, non-AI assessment.",
            knowledge_gained=knowledge_gained,
            knowledge_insights="Basic knowledge reinforcement across relevant domains.",
            evaluated_at=datetime.now().isoformat()
        )
        
        # Record the attempt
        self.problem_engine.record_problem_attempt(
            scda_id=scda_id,
            problem_id=problem.problem_id,
            solution_text=solution_text,
            success=evaluation.overall_score >= 0.7,
            time_spent=problem.time_estimate * 60, # Placeholder
            knowledge_gained=evaluation.knowledge_gained
        )
        
        return evaluation
