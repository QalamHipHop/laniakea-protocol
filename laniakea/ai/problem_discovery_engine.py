"""AI Problem Discovery Engine
Discovers, generates, and recommends Hard Problems based on SCDA knowledge vectors.
Integrates with LLM APIs for intelligent problem generation."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class ProblemDifficulty(Enum):
    """Problem difficulty levels."""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXTREME = 4
    LEGENDARY = 5

class ProblemCategory(Enum):
    """Problem categories based on 8D knowledge domains."""
    PHYSICS = "physics"
    BIOLOGY = "biology"
    MATHEMATICS = "mathematics"
    CHEMISTRY = "chemistry"
    ENGINEERING = "engineering"
    COMPUTER_SCIENCE = "computer_science"
    PHILOSOPHY = "philosophy"
    COSMOLOGY = "cosmology"
    INTERDISCIPLINARY = "interdisciplinary"

@dataclass
class HardProblem:
    """Represents a Hard Problem."""
    problem_id: str
    title: str
    description: str
    category: str
    difficulty: int  # 1-5
    required_knowledge: List[float]  # 8D vector
    reward_points: int
    time_estimate: int  # minutes
    created_at: str
    source: str  # "discovered", "generated", "user_submitted"
    hint: str = ""
    solution_outline: str = ""
    related_problems: List[str] = None

@dataclass
class ProblemAttempt:
    """Records an attempt to solve a problem."""
    attempt_id: str
    scda_id: str
    problem_id: str
    solution_text: str
    knowledge_gained: List[float]  # 8D vector
    success: bool
    time_spent: int  # seconds
    attempted_at: str
    ai_feedback: str = ""

class ProblemDiscoveryEngine:
    """
    AI-powered engine for discovering, generating, and recommending problems.
    Uses LLM APIs to create contextually relevant challenges.
    """
    
    def __init__(self, llm_client=None):
        """Initialize the Problem Discovery Engine."""
        self.llm_client = llm_client  # OpenAI or compatible client
        self.problems: Dict[str, HardProblem] = {}
        self.attempts: Dict[str, List[ProblemAttempt]] = {}
        self.problem_counter = 0
        
        # Initialize default problems
        self._initialize_default_problems()
        
        logger.info("Problem Discovery Engine initialized")
    
    def _initialize_default_problems(self):
        """Initialize a set of default Hard Problems."""
        
        default_problems = [
            HardProblem(
                problem_id="HARD_PROB_001",
                title="Quantum Entanglement and Information Transfer",
                description="Investigate the theoretical limits of quantum entanglement for information transfer. Can quantum entanglement be used to transmit information faster than light? Analyze the constraints imposed by quantum mechanics and relativity.",
                category=ProblemCategory.PHYSICS.value,
                difficulty=4,
                required_knowledge=[0.7, 0.2, 0.8, 0.3, 0.2, 0.5, 0.4, 0.6],
                reward_points=500,
                time_estimate=180,
                created_at=datetime.now().isoformat(),
                source="discovered",
                hint="Consider the no-communication theorem and Bell's inequalities.",
                solution_outline="Quantum entanglement cannot transmit information faster than light due to the no-communication theorem. While entangled particles show correlations, these correlations cannot be used to send classical information."
            ),
            HardProblem(
                problem_id="HARD_PROB_002",
                title="CRISPR Ethics and Genetic Modification",
                description="Develop a comprehensive ethical framework for CRISPR gene editing in humans. Consider germline vs somatic cell modifications, designer babies, equity of access, and long-term ecological impacts.",
                category=ProblemCategory.BIOLOGY.value,
                difficulty=4,
                required_knowledge=[0.3, 0.8, 0.5, 0.6, 0.4, 0.3, 0.9, 0.2],
                reward_points=450,
                time_estimate=150,
                created_at=datetime.now().isoformat(),
                source="discovered",
                hint="Consider stakeholder perspectives: scientists, patients, society, future generations.",
                solution_outline="A balanced framework must consider: (1) Medical necessity vs enhancement, (2) Informed consent, (3) Equity and access, (4) Ecological and evolutionary implications, (5) International governance."
            ),
            HardProblem(
                problem_id="HARD_PROB_003",
                title="P vs NP Problem - Computational Complexity",
                description="Provide a rigorous analysis of the P vs NP problem. If P=NP, what would be the implications for cryptography, optimization, and artificial intelligence? Discuss current approaches and barriers to solving this millennium problem.",
                category=ProblemCategory.MATHEMATICS.value,
                difficulty=5,
                required_knowledge=[0.4, 0.1, 0.95, 0.2, 0.3, 0.9, 0.5, 0.3],
                reward_points=1000,
                time_estimate=240,
                created_at=datetime.now().isoformat(),
                source="discovered",
                hint="Review NP-completeness, polynomial-time reductions, and current proof techniques.",
                solution_outline="P vs NP remains open. If P=NP: cryptography breaks, optimization becomes tractable. Current barriers: proof techniques seem insufficient, relativization, natural proofs."
            ),
            HardProblem(
                problem_id="HARD_PROB_004",
                title="Climate Change Mitigation Strategies",
                description="Design a comprehensive, economically viable strategy for global climate change mitigation. Consider carbon pricing, renewable energy transition, carbon capture, geoengineering, and international cooperation mechanisms.",
                category=ProblemCategory.ENGINEERING.value,
                difficulty=4,
                required_knowledge=[0.5, 0.6, 0.6, 0.7, 0.8, 0.4, 0.7, 0.8],
                reward_points=600,
                time_estimate=200,
                created_at=datetime.now().isoformat(),
                source="discovered",
                hint="Consider both technological and socio-economic factors.",
                solution_outline="Multi-faceted approach: (1) Carbon pricing and market mechanisms, (2) Renewable energy infrastructure, (3) Energy efficiency, (4) Carbon capture and storage, (5) Geoengineering as last resort, (6) International agreements."
            ),
            HardProblem(
                problem_id="HARD_PROB_005",
                title="Artificial General Intelligence Safety",
                description="Develop a comprehensive framework for ensuring the safety and alignment of Artificial General Intelligence (AGI) systems. Address value alignment, interpretability, robustness, and containment strategies.",
                category=ProblemCategory.COMPUTER_SCIENCE.value,
                difficulty=5,
                required_knowledge=[0.5, 0.3, 0.7, 0.2, 0.4, 0.95, 0.8, 0.4],
                reward_points=800,
                time_estimate=220,
                created_at=datetime.now().isoformat(),
                source="discovered",
                hint="Consider value alignment problem, interpretability, and containment.",
                solution_outline="AGI safety requires: (1) Value alignment techniques, (2) Interpretability and explainability, (3) Robustness testing, (4) Containment strategies, (5) International governance frameworks."
            ),
        ]
        
        for problem in default_problems:
            self.problems[problem.problem_id] = problem
        
        logger.info(f"Initialized {len(default_problems)} default problems")
    
    def discover_problem_from_knowledge(self, knowledge_vector: List[float]) -> Optional[HardProblem]:
        """
        Discover a problem that matches the SCDA's current knowledge vector.
        Returns a problem that is challenging but solvable for the SCDA.
        """
        knowledge_array = np.array(knowledge_vector)
        
        best_problem = None
        best_score = -1
        
        for problem in self.problems.values():
            required = np.array(problem.required_knowledge)
            
            # Calculate match score
            # Problems should be slightly above current knowledge level
            match_score = self._calculate_problem_match_score(knowledge_array, required)
            
            if match_score > best_score and match_score > 0.5:
                best_score = match_score
                best_problem = problem
        
        if best_problem:
            logger.info(f"Discovered problem {best_problem.problem_id} for knowledge vector")
        
        return best_problem
    
    def _calculate_problem_match_score(self, current_knowledge: np.ndarray, required_knowledge: np.ndarray) -> float:
        """
        Calculate how well a problem matches the SCDA's knowledge.
        Score should be high when problem is challenging but solvable.
        """
        # Calculate cosine similarity
        cosine_sim = np.dot(current_knowledge, required_knowledge) / (
            np.linalg.norm(current_knowledge) * np.linalg.norm(required_knowledge) + 1e-8
        )
        
        # Calculate difficulty factor
        # Problems should require slightly more knowledge than currently possessed
        difficulty_factor = np.mean(required_knowledge) / (np.mean(current_knowledge) + 0.1)
        
        # Optimal difficulty is around 1.2-1.5x current knowledge
        if 1.1 < difficulty_factor < 1.8:
            difficulty_score = 1.0
        elif 0.8 < difficulty_factor <= 1.1:
            difficulty_score = 0.7
        elif 1.8 <= difficulty_factor < 2.5:
            difficulty_score = 0.7
        else:
            difficulty_score = 0.3
        
        # Combined score
        match_score = (cosine_sim * 0.6) + (difficulty_score * 0.4)
        
        return float(match_score)
    
    def generate_problem_with_llm(
        self,
        category: str,
        difficulty: int,
        context: str,
        knowledge_vector: Optional[List[float]] = None
    ) -> Optional[HardProblem]:
        """
        Generate a new Hard Problem using LLM.
        Requires LLM client to be configured.
        """
        if not self.llm_client:
            logger.warning("LLM client not configured for problem generation")
            return None
        
        try:
            # Prepare prompt for LLM
            prompt = self._prepare_generation_prompt(category, difficulty, context, knowledge_vector)
            
            # Call LLM
            response = self.llm_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert problem designer for the LaniakeA Protocol. Create challenging, thought-provoking problems that promote deep learning and evolution."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            problem_data = json.loads(response.choices[0].message.content)
            
            # Create problem object
            self.problem_counter += 1
            problem = HardProblem(
                problem_id=f"HARD_PROB_GEN_{self.problem_counter:04d}",
                title=problem_data.get("title", "Generated Problem"),
                description=problem_data.get("description", ""),
                category=category,
                difficulty=difficulty,
                required_knowledge=problem_data.get("required_knowledge", [0.5] * 8),
                reward_points=problem_data.get("reward_points", 100 * difficulty),
                time_estimate=problem_data.get("time_estimate", 60 * difficulty),
                created_at=datetime.now().isoformat(),
                source="generated",
                hint=problem_data.get("hint", ""),
                solution_outline=problem_data.get("solution_outline", "")
            )
            
            self.problems[problem.problem_id] = problem
            logger.info(f"Generated problem {problem.problem_id} using LLM")
            
            return problem
        
        except Exception as e:
            logger.error(f"Error generating problem with LLM: {e}")
            return None
    
    def _prepare_generation_prompt(self, category: str, difficulty: int, context: str, knowledge_vector: Optional[List[float]]) -> str:
        """
        Prepare a detailed prompt for LLM problem generation.
        """
        difficulty_descriptions = {
            1: "easy, suitable for beginners",
            2: "medium, requires some expertise",
            3: "hard, requires deep understanding",
            4: "very hard, cutting-edge knowledge",
            5: "legendary, research-level difficulty"
        }
        
        knowledge_str = ""
        if knowledge_vector:
            domains = ["Physics", "Biology", "Mathematics", "Chemistry", "Engineering", "CS", "Philosophy", "Cosmology"]
            knowledge_str = "\nCurrent knowledge profile:\n"
            for domain, value in zip(domains, knowledge_vector):
                knowledge_str += f"- {domain}: {value:.2f}\n"
        
        prompt = f"""
Generate a challenging Hard Problem for the LaniakeA Protocol with the following specifications:

Category: {category}
Difficulty Level: {difficulty} ({difficulty_descriptions.get(difficulty, 'unknown')})
Context: {context}
{knowledge_str}

Return the problem as a JSON object with the following structure:
{{
    "title": "Problem title",
    "description": "Detailed problem description",
    "required_knowledge": [0.5, 0.6, ...],  // 8D knowledge vector
    "reward_points": 500,
    "time_estimate": 120,
    "hint": "A helpful hint",
    "solution_outline": "Brief outline of the solution approach"
}}

Ensure the problem:
1. Is intellectually challenging and promotes deep thinking
2. Requires interdisciplinary knowledge
3. Has practical or theoretical significance
4. Is solvable but requires effort and creativity
5. Contributes to SCDA evolution
"""
        
        return prompt
    
    def record_problem_attempt(
        self,
        scda_id: str,
        problem_id: str,
        solution_text: str,
        success: bool,
        time_spent: int,
        knowledge_gained: Optional[List[float]] = None
    ) -> ProblemAttempt:
        """
        Record an attempt to solve a problem.
        """
        attempt_id = f"ATTEMPT_{len(self.attempts)}_{datetime.now().timestamp()}"
        
        if knowledge_gained is None:
            knowledge_gained = [0.0] * 8
        
        attempt = ProblemAttempt(
            attempt_id=attempt_id,
            scda_id=scda_id,
            problem_id=problem_id,
            solution_text=solution_text,
            knowledge_gained=knowledge_gained,
            success=success,
            time_spent=time_spent,
            attempted_at=datetime.now().isoformat()
        )
        
        if scda_id not in self.attempts:
            self.attempts[scda_id] = []
        
        self.attempts[scda_id].append(attempt)
        logger.info(f"Recorded attempt {attempt_id} for SCDA {scda_id} on problem {problem_id}")
        
        return attempt

    def get_problem(self, problem_id: str) -> Optional[HardProblem]:
        """
        Retrieve a problem by its ID.
        """
        return self.problems.get(problem_id)

    def get_attempts(self, scda_id: str) -> List[ProblemAttempt]:
        """
        Retrieve all attempts for a given SCDA.
        """
        return self.attempts.get(scda_id, [])

    def get_problem_categories(self) -> List[str]:
        """
        Return a list of all available problem categories.
        """
        return [category.value for category in ProblemCategory]

    def get_problem_difficulties(self) -> List[int]:
        """
        Return a list of all available problem difficulties.
        """
        return [difficulty.value for difficulty in ProblemDifficulty]
