"""AI Module - Problem Discovery and Solution Evaluation"""

from .problem_discovery_engine import ProblemDiscoveryEngine, HardProblem, ProblemDifficulty
from .solution_evaluator import SolutionEvaluator, SolutionEvaluation

__all__ = [
    "ProblemDiscoveryEngine",
    "HardProblem",
    "ProblemDifficulty",
    "SolutionEvaluator",
    "SolutionEvaluation"
]

from .llm_integration import generate_hard_problem, validate_hard_problem
