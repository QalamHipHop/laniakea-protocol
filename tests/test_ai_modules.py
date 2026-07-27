"""
Unit Tests for AI Modules (Problem Discovery and Solution Evaluation)
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from laniakea.ai.problem_discovery_engine import ProblemDiscoveryEngine
from laniakea.ai.solution_evaluator import SolutionEvaluator


class TestProblemDiscoveryEngine(unittest.TestCase):
    """Test cases for Problem Discovery Engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = ProblemDiscoveryEngine()
        self.knowledge_vector = [0.7, 0.5, 0.8, 0.4, 0.3, 0.6, 0.4, 0.5]

    def test_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertGreater(len(self.engine.problems), 0)

    def test_discover_problem(self):
        """Test problem discovery."""
        problem = self.engine.discover_problem_from_knowledge(self.knowledge_vector)
        self.assertIsNotNone(problem)
        self.assertIsNotNone(problem.problem_id)
        self.assertGreater(problem.difficulty, 0)

class TestSolutionEvaluator(unittest.TestCase):
    """Test cases for Solution Evaluator."""

    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = SolutionEvaluator()
        self.problem_id = "HARD_PROB_001"
        self.scda_id = "test_scda_001"

    def test_initialization(self):
        """Test evaluator initialization."""
        self.assertIsNotNone(self.evaluator)

    def test_evaluate_solution_heuristic(self):
        """Test solution evaluation using heuristics."""
        solution = "A comprehensive analysis of quantum mechanics principles."
        evaluation = self.evaluator.evaluate_solution(self.problem_id, self.scda_id, solution)
        self.assertIsNotNone(evaluation)
        self.assertGreaterEqual(evaluation.overall_score, 0.0)
        self.assertLessEqual(evaluation.overall_score, 1.0)

    def test_knowledge_extraction(self):
        """Test knowledge insight extraction."""
        solution = "This solution shows understanding of quantum mechanics and ethics."
        evaluation = self.evaluator.evaluate_solution(self.problem_id, self.scda_id, solution)
        self.assertGreater(len(evaluation.knowledge_insights), 0)


class TestAIIntegration(unittest.TestCase):
    """Integration tests for AI modules."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = ProblemDiscoveryEngine()
        self.evaluator = SolutionEvaluator()
        self.knowledge_vector = [0.7, 0.5, 0.8, 0.4, 0.3, 0.6, 0.4, 0.5]
        self.scda_id = "integration_test_scda"

    def test_problem_discovery_and_evaluation(self):
        """Test complete workflow: discover problem and evaluate solution."""
        problem = self.engine.discover_problem_from_knowledge(self.knowledge_vector)
        self.assertIsNotNone(problem)

        solution_text = "This is my solution to the discovered problem."
        evaluation = self.evaluator.evaluate_solution(
            problem_id=problem.problem_id,
            scda_id=self.scda_id,
            solution_text=solution_text
        )
        self.assertIsNotNone(evaluation)
        self.assertGreater(evaluation.overall_score, 0.0)


if __name__ == "__main__":
    unittest.main()
