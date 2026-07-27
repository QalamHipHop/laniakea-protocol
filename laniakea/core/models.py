"""
LaniakeA Protocol - Core Domain Models (Pydantic v2)
Author: Qalam — Master Rebuild

This module defines the canonical data models for the Laniakea
multi-dimensional blockchain. All models are Pydantic v2 native
(JSON-friendly, type-safe, serialisable).

Design principles
-----------------
1. Pydantic v2 ``BaseModel`` everywhere — no raw dataclasses in the
   public API surface.
2. Tuple fields are normalised to ``List[float]`` so that ``model_dump()``
   produces JSON-serialisable output (tuples become lists).
3. Every model exposes a ``from_dict`` and ``to_dict`` helper for
   cross-version compatibility.
4. Field validators enforce domain invariants (ranges, non-empty ids, …).
5. Backwards-compatible re-exports for any consumer that imported
   ``CosmicCell`` / ``Transaction`` from this module before the rebuild.
"""

from __future__ import annotations

import math
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ValueDimension(str, Enum):
    """Dimensions of value within the Laniakea protocol.

    The eight dimensions together form the value vector of every
    solution and every node. Negative dimensions (environment, health)
    reflect potentially negative externalities.
    """

    KNOWLEDGE = "knowledge"
    COMPUTATION = "computation"
    ORIGINALITY = "originality"
    CONSCIOUSNESS = "consciousness"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"
    SCALABILITY = "scalability"
    ETHICAL_ALIGNMENT = "ethical_alignment"


class ProblemCategory(str, Enum):
    """Categories of hard problems that an SCDA can solve."""

    SCIENTIFIC = "scientific"
    PHILOSOPHICAL = "philosophical"
    MATHEMATICAL = "mathematical"
    COMPUTATIONAL = "computational"
    ARTISTIC = "artistic"
    COSMIC = "cosmic"
    SYSTEMIC_EVOLUTION = "systemic_evolution"


class ProposalType(str, Enum):
    """Types of governance proposal."""

    PROTOCOL_UPGRADE = "protocol_upgrade"
    PARAMETER_CHANGE = "parameter_change"
    NEW_FEATURE = "new_feature"
    RULE_MODIFICATION = "rule_modification"
    VALUE_DIMENSION_ADJUSTMENT = "value_dimension_adjustment"


class ProposalStatus(str, Enum):
    """Lifecycle of a governance proposal."""

    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"


class NodeSpecialty(str, Enum):
    """Specialisation of a network node."""

    MINING = "mining"
    SOLVING = "solving"
    VALIDATION = "validation"
    ORACLE = "oracle"
    SIMULATION = "simulation"
    AI_INFERENCE = "ai_inference"
    GOVERNANCE = "governance"
    GENERALIST = "generalist"


class CellState(str, Enum):
    """Lifecycle state of a CosmicCell / SCDA."""

    ALIVE = "alive"
    DORMANT = "dormant"
    DIVIDING = "dividing"
    APOPTOSIS = "apoptosis"  # programmed death
    TRANSCENDED = "transcended"  # evolved past cell metaphor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _new_id(prefix: str) -> str:
    """Mint a short, prefixed UUID for human-readable identifiers."""
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def _now() -> float:
    """Return wall-clock time as float (kept centralised for testability)."""
    return time.time()


def _normalise_position(value: Any, dims: int = 3) -> List[float]:
    """Coerce a position-like value into a JSON-friendly list of floats.

    Accepts tuples, lists, numpy arrays and ``None``. The output always
    has exactly ``dims`` components; missing components are padded with
    0.0 and overflowing ones are truncated.
    """
    if value is None:
        return [0.0] * dims
    if hasattr(value, "tolist"):  # numpy
        value = value.tolist()
    if isinstance(value, tuple):
        value = list(value)
    if not isinstance(value, list):
        raise ValueError(f"position must be a list/tuple, got {type(value).__name__}")
    out: List[float] = [float(v) for v in value[:dims]]
    if len(out) < dims:
        out.extend([0.0] * (dims - len(out)))
    return out


# ---------------------------------------------------------------------------
# ValueVector — the 8-dimensional value score
# ---------------------------------------------------------------------------


# Dimensions that may legitimately be negative (externalities).
_NEGATIVE_OK: Set[ValueDimension] = {ValueDimension.ENVIRONMENTAL, ValueDimension.HEALTH}


class ValueVector(BaseModel):
    """Multi-dimensional value vector (8 components).

    Most dimensions are bounded ``[0, 10]``; environmental and health
    are unbounded below to allow modelling of harm.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    knowledge: float = Field(default=0.0, ge=0.0, le=10.0)
    computation: float = Field(default=0.0, ge=0.0, le=10.0)
    originality: float = Field(default=0.0, ge=0.0, le=10.0)
    consciousness: float = Field(default=0.0, ge=0.0, le=10.0)
    environmental: float = Field(default=0.0)
    health: float = Field(default=0.0)
    scalability: float = Field(default=0.0, ge=0.0)
    ethical_alignment: float = Field(default=0.0, ge=0.0)

    # --------------------------------------------------------------- helpers

    def as_dict(self) -> Dict[ValueDimension, float]:
        """Return the vector as ``{dimension: value}``."""
        return {
            ValueDimension.KNOWLEDGE: self.knowledge,
            ValueDimension.COMPUTATION: self.computation,
            ValueDimension.ORIGINALITY: self.originality,
            ValueDimension.CONSCIOUSNESS: self.consciousness,
            ValueDimension.ENVIRONMENTAL: self.environmental,
            ValueDimension.HEALTH: self.health,
            ValueDimension.SCALABILITY: self.scalability,
            ValueDimension.ETHICAL_ALIGNMENT: self.ethical_alignment,
        }

    def magnitude(self) -> float:
        """Euclidean magnitude of the 8D vector."""
        return math.sqrt(sum(v * v for v in self.as_dict().values()))

    def total_value(self) -> float:
        """Sum of the *positive* components (the conventional "value" score).

        Negative externalities (environment, health) are clamped at 0 so
        that the total is a useful ranking metric.
        """
        d = self.as_dict()
        total = 0.0
        for dim, val in d.items():
            if dim in _NEGATIVE_OK:
                total += max(0.0, val)
            else:
                total += val
        return total

    def to_dict(self) -> Dict[str, float]:
        """Plain dict serialisation (Pydantic v2 ``model_dump``)."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValueVector":
        """Inverse of :meth:`to_dict` — silently ignores unknown keys."""
        known = {f for f in cls.model_fields}
        return cls(**{k: v for k, v in data.items() if k in known})

    def to_components(self) -> List[float]:
        """Return the canonical 8-component list (for hypercube math)."""
        return [
            self.knowledge,
            self.computation,
            self.originality,
            self.consciousness,
            self.environmental,
            self.health,
            self.scalability,
            self.ethical_alignment,
        ]

    def __add__(self, other: "ValueVector") -> "ValueVector":
        d = self.as_dict()
        for k, v in other.as_dict().items():
            d[k] = d[k] + v
        return ValueVector(**d)

    def __mul__(self, scalar: float) -> "ValueVector":
        d = {k: v * float(scalar) for k, v in self.as_dict().items()}
        return ValueVector(**d)


# ---------------------------------------------------------------------------
# Task / Solution
# ---------------------------------------------------------------------------


class Task(BaseModel):
    """A hard problem awaiting a solution."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(default_factory=lambda: _new_id("task"))
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    category: ProblemCategory
    author_id: str = Field(..., min_length=1)
    timestamp: float = Field(default_factory=_now)
    difficulty: float = Field(default=1.0, ge=0.1, le=10.0)
    required_dimensions: List[ValueDimension] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def _strip_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be empty")
        return v


class Solution(BaseModel):
    """A solution to a :class:`Task`, scored by :class:`ValueVector`."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(default_factory=lambda: _new_id("sol"))
    task_id: str = Field(..., min_length=1)
    solver_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1, max_length=50_000)
    value_vector: ValueVector = Field(default_factory=ValueVector)
    timestamp: float = Field(default_factory=_now)
    proof_of_work: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def _strip_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("content cannot be empty")
        return v


# ---------------------------------------------------------------------------
# Transaction / Block
# ---------------------------------------------------------------------------


class Transaction(BaseModel):
    """A transfer of value in a specific dimension."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(default_factory=lambda: _new_id("tx"))
    sender: str = Field(..., min_length=1)
    recipient: str = Field(..., min_length=1)
    amount: float = Field(..., ge=0.0)
    dimension: ValueDimension = ValueDimension.KNOWLEDGE
    timestamp: float = Field(default_factory=_now)
    signature: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check_distinct(self) -> "Transaction":
        if self.sender == self.recipient:
            raise ValueError("sender and recipient must differ")
        return self


class KnowledgeBlock(BaseModel):
    """A knowledge block in the Laniakea chain."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    index: int = Field(..., ge=0)
    timestamp: float = Field(default_factory=_now)
    transactions: List[Transaction] = Field(default_factory=list)
    solution: Optional[Solution] = None
    author_id: str = Field(..., min_length=1)
    previous_hash: str = Field(..., min_length=1)
    signature: str = Field(default="")
    nonce: int = Field(default=0, ge=0)
    difficulty: float = Field(default=1.0, ge=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Node info / P2P message
# ---------------------------------------------------------------------------


class NodeInfo(BaseModel):
    """Information about a peer node in the Laniakea network."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    node_id: str = Field(..., min_length=1)
    host: str = Field(..., min_length=1)
    p2p_port: int = Field(..., ge=1, le=65535)
    api_port: int = Field(..., ge=1, le=65535)
    is_authority: bool = False
    specialties: Set[NodeSpecialty] = Field(default_factory=set)
    reputation: float = Field(default=0.0, ge=0.0)
    total_value_created: ValueVector = Field(default_factory=ValueVector)


class P2PMessage(BaseModel):
    """A P2P message exchanged between nodes."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    type: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    sender_id: Optional[str] = None
    timestamp: float = Field(default_factory=_now)
    message_id: str = Field(default_factory=lambda: _new_id("msg"))


# ---------------------------------------------------------------------------
# Governance proposal
# ---------------------------------------------------------------------------


class Proposal(BaseModel):
    """A governance proposal subject to on-chain voting."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(default_factory=lambda: _new_id("prop"))
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    type: ProposalType
    proposer_id: str = Field(..., min_length=1)
    code: Optional[str] = None
    votes_for: float = Field(default=0.0, ge=0.0)
    votes_against: float = Field(default=0.0, ge=0.0)
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: float = Field(default_factory=_now)
    expires_at: float = Field(...)

    @model_validator(mode="after")
    def _check_window(self) -> "Proposal":
        if self.expires_at <= self.created_at:
            raise ValueError("expires_at must be after created_at")
        return self


# ---------------------------------------------------------------------------
# CosmicCell — JSON-friendly replacement for tuple-based position
# ---------------------------------------------------------------------------


class CosmicCell(BaseModel):
    """A single cosmic cell — the unit of Laniakea's simulation.

    The original implementation used ``tuple[float, float, float]`` for
    ``position`` and ``velocity``, which serialises to a list in JSON
    but cannot be re-hydrated via Pydantic v2 strict mode. We replace
    them with ``List[float]`` while keeping a 3-component invariant.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    id: str = Field(default_factory=lambda: _new_id("cell"))
    generation: int = Field(default=0, ge=0)
    energy: float = Field(default=100.0, ge=0.0)
    knowledge: float = Field(default=0.0, ge=0.0)
    position: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    velocity: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    genome: Dict[str, Any] = Field(default_factory=dict)
    state: CellState = CellState.ALIVE
    created_at: float = Field(default_factory=_now)

    @field_validator("position", "velocity")
    @classmethod
    def _check_3d(cls, v: Any) -> List[float]:
        return _normalise_position(v, dims=3)

    # ---------------------------------------------------------------- helpers

    def speed(self) -> float:
        """Current speed magnitude."""
        vx, vy, vz = self.velocity
        return math.sqrt(vx * vx + vy * vy + vz * vz)

    def to_legacy(self) -> Dict[str, Any]:
        """Return a dict in the legacy tuple-shape for older code paths."""
        return {
            "id": self.id,
            "generation": self.generation,
            "energy": self.energy,
            "knowledge": self.knowledge,
            "position": tuple(self.position),
            "velocity": tuple(self.velocity),
            "genome": dict(self.genome),
            "state": self.state.value,
        }


# ---------------------------------------------------------------------------
# Backwards-compat re-exports
# ---------------------------------------------------------------------------


__all__ = [
    "ValueDimension",
    "ProblemCategory",
    "ProposalType",
    "ProposalStatus",
    "NodeSpecialty",
    "CellState",
    "ValueVector",
    "Task",
    "Solution",
    "Transaction",
    "KnowledgeBlock",
    "NodeInfo",
    "P2PMessage",
    "Proposal",
    "CosmicCell",
]
