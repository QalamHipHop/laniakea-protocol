"""AI Module - Problem Discovery and Solution Evaluation"""

from .problem_discovery_engine import ProblemDiscoveryEngine, HardProblem, ProblemDifficulty
from .solution_evaluator import SolutionEvaluator, SolutionEvaluation
from .model import AIModel

__all__ = [
    "ProblemDiscoveryEngine",
    "HardProblem",
    "ProblemDifficulty",
    "SolutionEvaluator",
    "SolutionEvaluation",
    "AIModel",
    "generate_hard_problem",
    "validate_hard_problem",
]

try:
    from .llm_integration import generate_hard_problem, validate_hard_problem  # type: ignore
except ImportError:  # pragma: no cover - optional helper module
    def generate_hard_problem(*_args, **_kwargs):  # type: ignore
        raise RuntimeError(
            "laniakea.ai.llm_integration is not installed. Install openai and "
            "create the module to enable LLM-driven problem generation."
        )

    def validate_hard_problem(*_args, **_kwargs):  # type: ignore
        raise RuntimeError(
            "laniakea.ai.llm_integration is not installed. Install openai and "
            "create the module to enable LLM-driven problem validation."
        )
