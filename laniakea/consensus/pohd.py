"""
LaniakeA Protocol — Proof of Human Development (PoHD)
=====================================================
Author: Qalam — Master Rebuild v4.0

PoHD is the application-level consensus layer of Laniakea: a "miner"
is rewarded when an SCDA successfully solves a *Hard Problem* (V_int
AND V_quant) and a corresponding :class:`PoHDProof` is recorded on
chain. This module is the **single source of truth** for the PoHD
validator, miner and supporting data structures.

The block-level consensus (hashes, mining, difficulty) lives in
:mod:`laniakea.core.hypercube_blockchain`; this module is purely
about *what constitutes a valid proof* and *how much it pays*.

Design notes
------------
* All log lines use the project logger.
* Validation is split into 5 small, named checks; each can be enabled
  or tuned via constants at the top of the file.
* Reward scaling matches the whitepaper: linear in (difficulty,
  complexity gain), with a fixed base.
* Difficulty adjustment mirrors the *block* difficulty adjustment
  in the hypercube blockchain (target block time, ±½× ⇒ ±1).
* The module exposes a Pydantic-friendly ``PoHDProof.to_dict()``
  and a public ``PoHDStats`` snapshot.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field

from laniakea.utils.logger import get_logger

logger = get_logger("laniakea.consensus.pohd")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POHD_MIN_DIFFICULTY: int = 1
POHD_MAX_DIFFICULTY: int = 10
POHD_TARGET_BLOCK_TIME: float = 60.0          # seconds
POHD_DIFFICULTY_ADJUSTMENT_INTERVAL: int = 10 # blocks

# Solution quality thresholds
MIN_SOLUTION_QUALITY: float = 0.5
MIN_ALIGNMENT_SCORE: float = 0.6
MIN_SOLUTION_LENGTH: int = 10
MIN_REASONING_LENGTH: int = 5

# Reward model
BASE_BLOCK_REWARD: float = 10.0
REWARD_SCALING_FACTOR: float = 1.5


# ---------------------------------------------------------------------------
# Pydantic schemas (API surface)
# ---------------------------------------------------------------------------


class HardProblemSchema(BaseModel):
    """JSON-serialisable view of :class:`HardProblem`."""

    model_config = ConfigDict(extra="forbid")

    problem_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    difficulty: float = Field(..., ge=0.0, le=1.0)
    knowledge_domains: Dict[str, float]
    sources: List[str] = Field(default_factory=list)
    entropy_of_consensus: float = Field(..., ge=0.0)
    timestamp: float


class PoHDProofSchema(BaseModel):
    """JSON-serialisable view of :class:`PoHDProof`."""

    model_config = ConfigDict(extra="forbid")

    proof_id: str
    scda_identity: str
    problem_id: str
    problem_difficulty: float
    solution_quality: float
    complexity_gain: float
    reward: float
    tier_transition: Optional[Dict[str, Any]] = None
    position_shift_8d: List[float] = Field(default_factory=lambda: [0.0] * 8)
    timestamp: float


class PoHDStats(BaseModel):
    """JSON-serialisable view of :meth:`PoHDMiner.get_stats`."""

    model_config = ConfigDict(extra="forbid")

    difficulty: int
    block_reward_base: float
    mining_history_size: int
    validation_history_size: int
    target_block_time: float
    accepted_proofs: int
    rejected_proofs: int


# ---------------------------------------------------------------------------
# Dataclasses (in-memory)
# ---------------------------------------------------------------------------


@dataclass
class HardProblem:
    """A Hard Problem P to be solved for PoHD credit."""

    problem_id: str
    question: str
    difficulty: float                                    # 0.0 .. 1.0
    knowledge_domains: Dict[int, float]                  # 8D knowledge requirements
    sources: List[str] = field(default_factory=list)
    entropy_of_consensus: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.difficulty = max(0.0, min(1.0, float(self.difficulty)))
        if not self.problem_id:
            raise ValueError("problem_id is required")
        if not self.question:
            raise ValueError("question is required")

    # ------------------------------------------------------------------ dict

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "question": self.question,
            "difficulty": float(self.difficulty),
            "knowledge_domains": {int(k): float(v) for k, v in self.knowledge_domains.items()},
            "sources": list(self.sources),
            "entropy_of_consensus": float(self.entropy_of_consensus),
            "timestamp": float(self.timestamp),
        }

    def calculate_hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()

    def to_schema(self) -> HardProblemSchema:
        return HardProblemSchema(
            problem_id=self.problem_id,
            question=self.question,
            difficulty=float(self.difficulty),
            knowledge_domains={str(k): float(v) for k, v in self.knowledge_domains.items()},
            sources=list(self.sources),
            entropy_of_consensus=float(self.entropy_of_consensus),
            timestamp=float(self.timestamp),
        )


@dataclass
class ProblemSolution:
    """A solution to a Hard Problem."""

    problem_id: str
    scda_identity: str
    solution_text: str
    solution_quality: float                             # 0.0 .. 1.0
    reasoning: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.solution_quality = max(0.0, min(1.0, float(self.solution_quality)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "scda_identity": self.scda_identity,
            "solution_text": self.solution_text,
            "solution_quality": float(self.solution_quality),
            "reasoning": self.reasoning,
            "timestamp": float(self.timestamp),
        }

    def calculate_hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()


@dataclass
class PoHDProof:
    """A Proof of Human Development, persisted on chain."""

    proof_id: str
    scda_identity: str
    problem: HardProblem
    solution: ProblemSolution
    complexity_gain: float
    reward: float = 0.0
    tier_transition: Optional[Dict[str, Any]] = None
    position_shift_8d: List[float] = field(default_factory=lambda: [0.0] * 8)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proof_id": self.proof_id,
            "scda_identity": self.scda_identity,
            "problem": self.problem.to_dict(),
            "solution": self.solution.to_dict(),
            "complexity_gain": float(self.complexity_gain),
            "reward": float(self.reward),
            "tier_transition": self.tier_transition,
            "position_shift_8d": [float(c) for c in self.position_shift_8d],
            "timestamp": float(self.timestamp),
        }

    def to_schema(self) -> PoHDProofSchema:
        return PoHDProofSchema(
            proof_id=self.proof_id,
            scda_identity=self.scda_identity,
            problem_id=self.problem.problem_id,
            problem_difficulty=float(self.problem.difficulty),
            solution_quality=float(self.solution.solution_quality),
            complexity_gain=float(self.complexity_gain),
            reward=float(self.reward),
            tier_transition=self.tier_transition,
            position_shift_8d=[float(c) for c in self.position_shift_8d],
            timestamp=float(self.timestamp),
        )

    def calculate_hash(self) -> str:
        return hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True).encode()
        ).hexdigest()


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


class PoHDValidator:
    """Validates solutions to Hard Problems.

    The five checks are kept small and named so they can be tuned
    independently in production.
    """

    def __init__(
        self,
        min_solution_quality: float = MIN_SOLUTION_QUALITY,
        min_alignment: float = MIN_ALIGNMENT_SCORE,
        min_solution_length: int = MIN_SOLUTION_LENGTH,
        min_reasoning_length: int = MIN_REASONING_LENGTH,
    ) -> None:
        self.min_solution_quality = float(min_solution_quality)
        self.min_alignment = float(min_alignment)
        self.min_solution_length = int(min_solution_length)
        self.min_reasoning_length = int(min_reasoning_length)
        self.validation_history: List[Dict[str, Any]] = []

    # ---------------------------------------------------------------- checks

    def validate_solution(
        self, problem: HardProblem, solution: ProblemSolution
    ) -> Tuple[bool, str]:
        """Return ``(is_valid, reason)`` for a problem/solution pair."""
        if solution.solution_quality < self.min_solution_quality:
            return False, f"quality_below_threshold({solution.solution_quality:.2f})"
        if len(solution.solution_text) < self.min_solution_length:
            return False, "solution_too_short"
        if not solution.reasoning or len(solution.reasoning) < self.min_reasoning_length:
            return False, "insufficient_reasoning"
        if solution.problem_id != problem.problem_id:
            return False, "problem_id_mismatch"
        alignment = self._check_alignment(problem, solution)
        if alignment < self.min_alignment:
            return False, f"alignment_low({alignment:.2f})"
        # Higher-difficulty problems require proportionally higher quality.
        required_quality = 0.5 + problem.difficulty * 0.3
        if solution.solution_quality < required_quality:
            return False, f"quality_below_difficulty({required_quality:.2f})"
        return True, "ok"

    def _check_alignment(
        self, problem: HardProblem, solution: ProblemSolution
    ) -> float:
        """Heuristic alignment score (placeholder for LLM-based scoring)."""
        problem_words = set(problem.question.lower().split())
        solution_words = set(solution.solution_text.lower().split())
        if not problem_words:
            return 0.0
        common = problem_words & solution_words
        alignment = len(common) / max(len(problem_words), 1)
        # Allow paraphrasing
        return min(alignment + 0.3, 1.0)

    # ---------------------------------------------------------------- audit

    def record_validation(self, problem_id: str, is_valid: bool, message: str) -> None:
        self.validation_history.append(
            {
                "problem_id": problem_id,
                "is_valid": is_valid,
                "message": message,
                "timestamp": time.time(),
            }
        )


# ---------------------------------------------------------------------------
# Miner
# ---------------------------------------------------------------------------


class PoHDMiner:
    """Produces and tracks PoHD proofs and adjusts mining difficulty."""

    def __init__(
        self,
        validator: Optional[PoHDValidator] = None,
        base_reward: float = BASE_BLOCK_REWARD,
    ) -> None:
        self.validator = validator or PoHDValidator()
        self.difficulty: int = POHD_MIN_DIFFICULTY
        self.base_reward: float = float(base_reward)
        self.mining_history: List[Dict[str, Any]] = []
        self._accepted: int = 0
        self._rejected: int = 0

    # ------------------------------------------------------------------ mine

    def create_pohd_proof(
        self,
        scda_identity: str,
        problem: HardProblem,
        solution: ProblemSolution,
        complexity_gain: float,
        position_shift_8d: Optional[List[float]] = None,
        tier_transition: Optional[Dict[str, Any]] = None,
    ) -> Optional[PoHDProof]:
        """Build a :class:`PoHDProof` if the solution is valid."""
        is_valid, message = self.validator.validate_solution(problem, solution)
        if not is_valid:
            logger.warning("PoHD solution rejected: %s", message)
            self._rejected += 1
            self.validator.record_validation(problem.problem_id, False, message)
            return None

        reward = self.calculate_block_reward(problem.difficulty, complexity_gain)
        proof_id = f"pohd_{int(time.time() * 1000)}"
        proof = PoHDProof(
            proof_id=proof_id,
            scda_identity=scda_identity,
            problem=problem,
            solution=solution,
            complexity_gain=float(complexity_gain),
            reward=reward,
            tier_transition=tier_transition,
            position_shift_8d=list(position_shift_8d or [0.0] * 8),
        )
        self.mining_history.append(
            {
                "proof_id": proof_id,
                "scda_identity": scda_identity,
                "problem_id": problem.problem_id,
                "timestamp": proof.timestamp,
                "complexity_gain": complexity_gain,
                "reward": reward,
            }
        )
        self._accepted += 1
        self.validator.record_validation(problem.problem_id, True, message)
        logger.info("✅ PoHD proof %s accepted (reward=%.2f)", proof_id, reward)
        return proof

    # ---------------------------------------------------------------- reward

    def calculate_block_reward(self, problem_difficulty: float, complexity_gain: float) -> float:
        """Reward = base × (1 + difficulty × scaling) × (1 + ΔC/10)."""
        difficulty_multiplier = 1.0 + (float(problem_difficulty) * REWARD_SCALING_FACTOR)
        complexity_multiplier = 1.0 + (float(complexity_gain) / 10.0)
        return self.base_reward * difficulty_multiplier * complexity_multiplier

    # ---------------------------------------------------------------- adjust

    def adjust_difficulty(self, average_block_time: float) -> None:
        """Adjust difficulty based on the running block-time average."""
        if average_block_time < POHD_TARGET_BLOCK_TIME / 2.0:
            self.difficulty = min(self.difficulty + 1, POHD_MAX_DIFFICULTY)
            logger.info("PoHD difficulty raised to %d", self.difficulty)
        elif average_block_time > POHD_TARGET_BLOCK_TIME * 2.0 and self.difficulty > POHD_MIN_DIFFICULTY:
            self.difficulty = max(self.difficulty - 1, POHD_MIN_DIFFICULTY)
            logger.info("PoHD difficulty lowered to %d", self.difficulty)

    # ---------------------------------------------------------------- stats

    def get_stats(self) -> PoHDStats:
        return PoHDStats(
            difficulty=self.difficulty,
            block_reward_base=self.base_reward,
            mining_history_size=len(self.mining_history),
            validation_history_size=len(self.validator.validation_history),
            target_block_time=POHD_TARGET_BLOCK_TIME,
            accepted_proofs=self._accepted,
            rejected_proofs=self._rejected,
        )


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def create_hard_problem(
    problem_id: str,
    question: str,
    difficulty: float,
    knowledge_domains: Dict[int, float],
    sources: Optional[List[str]] = None,
    entropy_of_consensus: float = 0.0,
) -> HardProblem:
    """Factory for :class:`HardProblem`."""
    return HardProblem(
        problem_id=problem_id,
        question=question,
        difficulty=difficulty,
        knowledge_domains=knowledge_domains,
        sources=list(sources or []),
        entropy_of_consensus=entropy_of_consensus,
    )


def create_problem_solution(
    problem_id: str,
    scda_identity: str,
    solution_text: str,
    solution_quality: float,
    reasoning: str = "",
) -> ProblemSolution:
    """Factory for :class:`ProblemSolution`."""
    return ProblemSolution(
        problem_id=problem_id,
        scda_identity=scda_identity,
        solution_text=solution_text,
        solution_quality=solution_quality,
        reasoning=reasoning,
    )


__all__ = [
    "POHD_MIN_DIFFICULTY",
    "POHD_MAX_DIFFICULTY",
    "POHD_TARGET_BLOCK_TIME",
    "POHD_DIFFICULTY_ADJUSTMENT_INTERVAL",
    "BASE_BLOCK_REWARD",
    "REWARD_SCALING_FACTOR",
    "HardProblemSchema",
    "PoHDProofSchema",
    "PoHDStats",
    "HardProblem",
    "ProblemSolution",
    "PoHDProof",
    "PoHDValidator",
    "PoHDMiner",
    "create_hard_problem",
    "create_problem_solution",
]
