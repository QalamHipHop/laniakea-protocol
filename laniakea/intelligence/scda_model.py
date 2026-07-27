"""SCDA (Single-Cell Digital Account) — The Cosmic Evolution Engine.

This module implements the core evolutionary state model for the Laniakea
Protocol. Each SCDA is a digital organism whose state evolves by solving
Hard Problems according to the PoHD (Proof of Human Development) law:

    ΔC = D(P) / C(t)^α

Where:
    ΔC  : the complexity gain from a single successful problem attempt
    D(P): the difficulty of the problem P  (0 ≤ D(P) ≤ 1)
    C(t): the current complexity index at time t
    α   : the evolutionary resistance coefficient (α > 1)

The model also tracks:
    * Energy  E(t) — burnt on attempts, refilled on success + passive tick
    * Knowledge vector K(t) — sparse dict of integrated knowledge IDs
    * Digital DNA — the genetic substrate (see :mod:`.digital_dna`)

This file is the **single source of truth** for SCDA dynamics. All
duplicate legacy copies have been removed; all `print()` calls have
been replaced with the project logger; type hints are complete.

Author: Qalam
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import BaseModel, Field, NonNegativeFloat, field_validator

from laniakea.utils.logger import logger

from .digital_dna import DNAManager, DigitalDNA, Gene


# ---------------------------------------------------------------------------
# Constants — single source of truth (matches the whitepaper)
# ---------------------------------------------------------------------------

#: Evolution resistance coefficient. α > 1 guarantees diminishing returns
#: so that complexity growth slows as the SCDA becomes more complex.
EVOLUTIONARY_RESISTANCE_COEFFICIENT: float = 1.5

#: Initial complexity at t=0.
INITIAL_COMPLEXITY: float = 1.0

#: Initial energy at t=0.
INITIAL_ENERGY: float = 100.0

#: k₁ — energy cost per unit difficulty of an attempt.
ENERGY_CONSUMPTION_FACTOR: float = 10.0

#: k₂ — energy reward per unit difficulty on success (scaled by C(t)).
ENERGY_REPLENISHMENT_FACTOR: float = 50.0

#: Passive energy regeneration per tick.
PASSIVE_ENERGY_REPLENISHMENT: float = 1.0

#: Mutation probability on a successful attempt.
SUCCESS_MUTATION_PROBABILITY: float = 0.05

#: Maximum energy cap to avoid unbounded growth.
MAX_ENERGY: float = 10_000.0

#: Maximum complexity cap (numerical safety).
MAX_COMPLEXITY: float = 1.0e12


# ---------------------------------------------------------------------------
# Pydantic schemas — used by the API and the breeding engine
# ---------------------------------------------------------------------------

class SCDAState(BaseModel):
    """Serializable snapshot of an SCDA's state at time t."""

    identity: str
    complexity_index: NonNegativeFloat
    energy: NonNegativeFloat
    knowledge_count: int = Field(ge=0)
    problem_queue_size: int = Field(ge=0)
    genetic_diversity: float = Field(ge=0.0, le=1.0)
    generation: int = Field(ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "identity": "scda-7f2c…",
                "complexity_index": 1.245,
                "energy": 87.4,
                "knowledge_count": 12,
                "problem_queue_size": 3,
                "genetic_diversity": 0.81,
                "generation": 4,
            }
        }


class ProblemAttemptResult(BaseModel):
    """Outcome of a single attempt to solve a Hard Problem."""

    scda_id: str
    success: bool
    delta_c: float
    new_complexity: NonNegativeFloat
    energy_before: NonNegativeFloat
    energy_after: NonNegativeFloat
    message: str = ""


class BreedingPrediction(BaseModel):
    """Predicted traits of an offspring of two parent SCDAs."""

    predicted_initial_complexity: float
    predicted_genetic_diversity: float
    dominant_knowledge_traits: List[str]
    evolutionary_resistance_coefficient: float
    generation: int


# ---------------------------------------------------------------------------
# Problem dataclass
# ---------------------------------------------------------------------------

class ProblemDomain(str, Enum):
    """Eight knowledge domains — matches the 8D hypercube axes."""

    PHYSICS = "physics"
    BIOLOGY = "biology"
    MATHEMATICS = "mathematics"
    COMPUTER_SCIENCE = "computer_science"
    CHEMISTRY = "chemistry"
    PHILOSOPHY = "philosophy"
    ENGINEERING = "engineering"
    COSMOLOGY = "cosmology"


@dataclass
class HardProblem:
    """A single Hard Problem P to be solved by an SCDA.

    Attributes
    ----------
    problem_id:
        Stable identifier (used as a key in the knowledge vector).
    domain:
        One of the eight 8D knowledge domains.
    difficulty:
        D(P) ∈ [0, 1] — the difficulty factor.
    question:
        The natural-language statement of the problem.
    required_sources:
        Reference sources for the problem.
    required_knowledge:
        Pre-requisite knowledge tags.
    """

    problem_id: str
    domain: ProblemDomain
    difficulty: float
    question: str
    required_sources: List[str] = field(default_factory=list)
    required_knowledge: List[str] = field(default_factory=list)

    @field_validator("difficulty")
    @classmethod
    def _clamp_difficulty(cls, v: float) -> float:
        return float(np.clip(v, 0.0, 1.0))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem_id": self.problem_id,
            "domain": self.domain.value,
            "difficulty": self.difficulty,
            "question": self.question,
            "required_sources": list(self.required_sources),
            "required_knowledge": list(self.required_knowledge),
        }


# ---------------------------------------------------------------------------
# SCDA — the core engine
# ---------------------------------------------------------------------------

class SingleCellDigitalAccount:
    """The core evolutionary state of a digital organism in Laniakea.

    The SCDA is described by the state vector S(t) = (C(t), E(t), K(t), Q(t))
    where C is the complexity index, E is the available energy, K is the
    knowledge vector and Q is the pending problem queue. The dynamics follow
    the PoHD law with diminishing returns (α > 1).
    """

    # Class-level constants (also re-exported as module constants)
    EVOLUTIONARY_RESISTANCE_COEFFICIENT: float = EVOLUTIONARY_RESISTANCE_COEFFICIENT
    INITIAL_COMPLEXITY: float = INITIAL_COMPLEXITY
    INITIAL_ENERGY: float = INITIAL_ENERGY
    ENERGY_CONSUMPTION_FACTOR: float = ENERGY_CONSUMPTION_FACTOR
    ENERGY_REPLENISHMENT_FACTOR: float = ENERGY_REPLENISHMENT_FACTOR
    PASSIVE_ENERGY_REPLENISHMENT: float = PASSIVE_ENERGY_REPLENISHMENT

    def __init__(
        self,
        identity: Optional[str] = None,
        dna: Optional[DigitalDNA] = None,
        complexity_index: float = INITIAL_COMPLEXITY,
        energy: float = INITIAL_ENERGY,
    ) -> None:
        self.identity: str = identity or str(uuid.uuid4())
        self.dna: DigitalDNA = dna or DNAManager.create_initial_dna(self.identity)
        self.complexity_index: float = float(complexity_index)
        self.energy: float = float(energy)
        self.knowledge_vector: Dict[str, float] = {}
        self.problem_queue: List[Dict[str, Any]] = []
        self.attempt_log: List[ProblemAttemptResult] = []
        logger.info("SCDA created id=%s C0=%.4f E0=%.2f", self.identity, self.complexity_index, self.energy)

    # ------------------------------------------------------------------ State

    def get_state(self) -> SCDAState:
        """Return a typed, serialisable snapshot of the current state."""
        return SCDAState(
            identity=self.identity,
            complexity_index=self.complexity_index,
            energy=self.energy,
            knowledge_count=len(self.knowledge_vector),
            problem_queue_size=len(self.problem_queue),
            genetic_diversity=self.dna.calculate_genetic_diversity(),
            generation=self.dna.generation,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain-dict representation suitable for JSON storage."""
        return {
            **self.get_state().model_dump(),
            "dna": self.dna.to_dict(),
            "knowledge_vector": dict(self.knowledge_vector),
            "problem_queue": list(self.problem_queue),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "SingleCellDigitalAccount":
        """Reconstruct an SCDA from a dict produced by :meth:`to_dict`."""
        dna = DigitalDNA.from_dict(payload["dna"])
        scda = cls(identity=payload["identity"], dna=dna)
        scda.complexity_index = float(payload["complexity_index"])
        scda.energy = float(payload["energy"])
        scda.knowledge_vector = dict(payload.get("knowledge_vector", {}))
        scda.problem_queue = list(payload.get("problem_queue", []))
        return scda

    # ---------------------------------------------------------- Internal maths

    def _calculate_complexity_gain(self, problem_difficulty: float) -> float:
        """ΔC = D(P) / C(t)^α  (with safe C(t) ≤ MAX_COMPLEXITY)."""
        if self.complexity_index <= 0.0:
            return 0.0
        c = min(self.complexity_index, MAX_COMPLEXITY)
        return problem_difficulty / (c ** self.EVOLUTIONARY_RESISTANCE_COEFFICIENT)

    def _update_knowledge_vector(self, problem_id: str, solution_quality: float) -> None:
        """Update K(t) on a successful integration. Higher quality ⇒ stronger weight."""
        weight = float(np.clip(solution_quality, 0.0, 1.0))
        # Recency-weighted: keep the better of old vs new
        prev = self.knowledge_vector.get(problem_id, 0.0)
        self.knowledge_vector[problem_id] = max(prev, weight)

    # ---------------------------------------------------------- Public API

    def attempt_solve_problem(
        self,
        problem_difficulty: float,
        solution_quality: float,
        is_valid: bool,
        problem_id: Optional[str] = None,
        relevant_domain: Optional[ProblemDomain] = None,
    ) -> ProblemAttemptResult:
        """Attempt to solve a Hard Problem.

        Parameters
        ----------
        problem_difficulty:
            D(P) ∈ [0, 1].
        solution_quality:
            A measure of solution quality ∈ [0, 1].
        is_valid:
            Result of Validation(A, P) — the dual validator output.
        problem_id:
            Optional stable ID; generated if missing.
        relevant_domain:
            Optional 8D knowledge domain for the learning step.
        """
        problem_difficulty = float(np.clip(problem_difficulty, 0.0, 1.0))
        solution_quality = float(np.clip(solution_quality, 0.0, 1.0))
        energy_before = self.energy

        # 1. Energy consumption
        self.energy -= self.ENERGY_CONSUMPTION_FACTOR * problem_difficulty

        if self.energy < 0.0:
            # Hibernation logic — biological strength rescues the cell
            bio_strength = 0.0
            bio_gene = self.dna.get_gene_by_domain(ProblemDomain.BIOLOGY.value)
            if bio_gene is not None:
                bio_strength = bio_gene.strength
            if bio_strength < 0.2:
                logger.warning(
                    "SCDA %s hibernating: depleted energy with low bio strength=%.2f",
                    self.identity, bio_strength,
                )
            self.energy = 0.0
            result = ProblemAttemptResult(
                scda_id=self.identity,
                success=False,
                delta_c=0.0,
                new_complexity=self.complexity_index,
                energy_before=energy_before,
                energy_after=0.0,
                message="Energy depleted. SCDA entered hibernation.",
            )
            self.attempt_log.append(result)
            return result

        if not is_valid:
            logger.info("SCDA %s failed validation at C=%.4f", self.identity, self.complexity_index)
            result = ProblemAttemptResult(
                scda_id=self.identity,
                success=False,
                delta_c=0.0,
                new_complexity=self.complexity_index,
                energy_before=energy_before,
                energy_after=self.energy,
                message="Validation(A, P) failed.",
            )
            self.attempt_log.append(result)
            return result

        # 2. Successful evolution ------------------------------------------------
        delta_c = self._calculate_complexity_gain(problem_difficulty)
        self.complexity_index = min(self.complexity_index + delta_c, MAX_COMPLEXITY)

        # 3. Energy reward
        reward = self.ENERGY_REPLENISHMENT_FACTOR * problem_difficulty * self.complexity_index
        self.energy = min(self.energy + reward, MAX_ENERGY)

        # 4. Knowledge vector
        if problem_id is None:
            problem_id = f"P_{uuid.uuid4().hex[:8]}"
        self._update_knowledge_vector(problem_id, solution_quality)

        # 5. Genetic learning — strengthen the relevant domain
        if relevant_domain is None:
            domain_value = np.random.choice(DNAManager.KNOWLEDGE_DOMAINS)
        else:
            domain_value = relevant_domain.value
        DNAManager.strengthen_gene(self.dna, domain_value, delta_c * 0.1)

        # 6. Evolutionary pressure — small chance of mutation
        if np.random.rand() < SUCCESS_MUTATION_PROBABILITY:
            DNAManager.mutate_dna(self.dna, force=True)
            logger.info("Mutation in SCDA %s domain=%s", self.identity, domain_value)

        result = ProblemAttemptResult(
            scda_id=self.identity,
            success=True,
            delta_c=delta_c,
            new_complexity=self.complexity_index,
            energy_before=energy_before,
            energy_after=self.energy,
            message=f"ΔC={delta_c:.6f}",
        )
        self.attempt_log.append(result)
        logger.info(
            "SCDA %s solved: ΔC=%.6f C=%.4f E=%.2f",
            self.identity, delta_c, self.complexity_index, self.energy,
        )
        return result

    def passive_update(self) -> None:
        """Apply one passive tick: energy regen, complexity decay, gene expression drift."""
        # 1. Passive energy regeneration
        self.energy = min(self.energy + self.PASSIVE_ENERGY_REPLENISHMENT, MAX_ENERGY)

        # 2. Complexity decay (kept as the legacy inverse-strength formula)
        math_gene = self.dna.get_gene_by_domain(ProblemDomain.MATHEMATICS.value)
        math_strength = math_gene.strength if math_gene is not None else 0.0
        decay_rate = 0.001 / (math_strength + 0.1)
        self.complexity_index = max(
            self.INITIAL_COMPLEXITY,
            self.complexity_index - decay_rate,
        )

        # 3. Gene expression drift — keep within [0, 1]
        for gene in self.dna.genes:
            gene.expression_level = float(
                np.clip(gene.expression_level + (gene.strength * 0.01) - 0.005, 0.0, 1.0)
            )


# ---------------------------------------------------------------------------
# KEA — Knowledge Extraction Agent (placeholder for LLM integration)
# ---------------------------------------------------------------------------

def generate_hard_problem(current_complexity: float) -> Dict[str, Any]:
    """Generate a placeholder Hard Problem P scaled by current complexity.

    Replace this with an LLM-driven KEA in production. The function still
    respects the difficulty scaling so the simulation behaves correctly.
    """
    base_difficulty = float(np.random.uniform(0.1, 1.0))
    scaled_difficulty = min(1.0, base_difficulty * (current_complexity / 5.0))
    return {
        "Q": "A complex question about the Lanika universe.",
        "D": scaled_difficulty,
        "S_ref": ["Source A", "Source B"],
        "K_req": ["Basic Math", "Basic Physics"],
    }


def validate_solution(
    scda: SingleCellDigitalAccount,
    problem: Dict[str, Any],
    user_solution: Any,
) -> bool:
    """Placeholder dual validation (V_int AND V_quant).

    V_int: complexity threshold check.
    V_quant: probabilistic Truth-Manifold alignment (higher C(t) ⇒ better).
    """
    min_complexity_needed = float(problem["D"]) * 1.5
    internal_check = scda.complexity_index >= min_complexity_needed
    truth_probability = min(1.0, scda.complexity_index / 10.0)
    quantum_check = bool(np.random.rand() < truth_probability)
    return internal_check and quantum_check


# ---------------------------------------------------------------------------
# Breeding — the Genetic Operations (single, deduped implementation)
# ---------------------------------------------------------------------------

def breed_scdas(
    parent1: SingleCellDigitalAccount,
    parent2: SingleCellDigitalAccount,
) -> SingleCellDigitalAccount:
    """Create a new SCDA by recombining the DNA of two parents.

    Implements the Advanced Breeding Laboratory: Mendelian crossover +
    post-recombination mutation. The child inherits an initial complexity
    bonus proportional to its genetic diversity.
    """
    child_id = str(uuid.uuid4())
    child_dna = DNAManager.recombine_dna(parent1.dna, parent2.dna, child_id)
    DNAManager.mutate_dna(child_dna, force=True)

    child_scda = SingleCellDigitalAccount(identity=child_id, dna=child_dna)

    avg_parent_complexity = (parent1.complexity_index + parent2.complexity_index) / 2.0
    genetic_bonus = child_dna.calculate_genetic_diversity() * 0.5  # max 50 % bonus
    child_scda.complexity_index = (
        SingleCellDigitalAccount.INITIAL_COMPLEXITY + avg_parent_complexity * genetic_bonus
    )
    logger.info(
        "Bred SCDA %s from %s x %s → C0=%.4f",
        child_id, parent1.identity, parent2.identity, child_scda.complexity_index,
    )
    return child_scda


def predict_child_traits(
    parent1: SingleCellDigitalAccount,
    parent2: SingleCellDigitalAccount,
) -> BreedingPrediction:
    """Predict the offspring's traits from two parents without materialising it."""
    avg_parent_complexity = (parent1.complexity_index + parent2.complexity_index) / 2.0

    temp_dna = DNAManager.recombine_dna(parent1.dna, parent2.dna, "temp")
    DNAManager.mutate_dna(temp_dna, force=True)
    predicted_diversity = temp_dna.calculate_genetic_diversity()

    genetic_bonus = predicted_diversity * 0.5
    predicted_complexity = (
        SingleCellDigitalAccount.INITIAL_COMPLEXITY + avg_parent_complexity * genetic_bonus
    )

    predicted_strengths: Dict[str, float] = {}
    for domain in DNAManager.KNOWLEDGE_DOMAINS:
        g1 = parent1.dna.get_gene_by_domain(domain)
        g2 = parent2.dna.get_gene_by_domain(domain)
        if g1 is not None and g2 is not None:
            predicted_strengths[domain] = (g1.strength + g2.strength) / 2.0

    dominant = sorted(predicted_strengths.items(), key=lambda kv: kv[1], reverse=True)[:3]
    return BreedingPrediction(
        predicted_initial_complexity=predicted_complexity,
        predicted_genetic_diversity=predicted_diversity,
        dominant_knowledge_traits=[f"{d} ({s:.2f})" for d, s in dominant],
        evolutionary_resistance_coefficient=SingleCellDigitalAccount.EVOLUTIONARY_RESISTANCE_COEFFICIENT,
        generation=temp_dna.generation,
    )


__all__ = [
    "EVOLUTIONARY_RESISTANCE_COEFFICIENT",
    "INITIAL_COMPLEXITY",
    "INITIAL_ENERGY",
    "ENERGY_CONSUMPTION_FACTOR",
    "ENERGY_REPLENISHMENT_FACTOR",
    "PASSIVE_ENERGY_REPLENISHMENT",
    "SCDAState",
    "ProblemAttemptResult",
    "BreedingPrediction",
    "ProblemDomain",
    "HardProblem",
    "SingleCellDigitalAccount",
    "generate_hard_problem",
    "validate_solution",
    "breed_scdas",
    "predict_child_traits",
]
