"""
SCDA Editor utilities
=====================

In-memory editing helpers for SCDA (Single-Cell Digital Account) state. Used
by the cosmic-v8 extra router to allow the frontend to tweak DNA parameters,
the 8D knowledge vector, and to validate custom hard problems before they
are fed back into the SCDA evolutionary loop.

The editor is **non-persistent** — it mutates the live :class:`SingleCellDigitalAccount`
held by the :class:`ScdaManager`. There is no on-disk side effect; everything
is reverted to the in-memory model on process restart.

Author: cosmic-backend (Track B)
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from laniakea.intelligence.digital_dna import (
    DNAManager,
    Gene,
    GeneOrigin,
)
from laniakea.intelligence.scda_manager import ScdaManager
from laniakea.intelligence.scda_model import (
    INITIAL_COMPLEXITY,
    INITIAL_ENERGY,
    SingleCellDigitalAccount,
)

logger = logging.getLogger("laniakea.api.scda_editor")

#: Mapping of the 8D knowledge vector dimensions (see ScdaManager._DOMAIN_TO_DIM).
_KNOWLEDGE_DOMAINS: List[str] = [
    "mathematics",  # 0 — X
    "physics",      # 1 — Y
    "biology",      # 2 — Z
    "history",      # 3 — T
    "knowledge",    # 4 — K
    "energy",       # 5 — E
    "complexity",   # 6 — C
    "social",       # 7 — S
]


class SCDA_DNAEditor:
    """Stateless façade that applies *validated* edits to a live SCDA.

    Every edit method returns a JSON-friendly dict describing the new state
    (or raises :class:`ValueError` on bad input). The editor never persists
    anything: SCDA changes live in the process memory of
    :class:`ScdaManager`.
    """

    def __init__(self, manager: ScdaManager) -> None:
        self._manager = manager

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        """Clamp *value* into ``[lo, hi]``."""
        try:
            v = float(value)
        except (TypeError, ValueError):
            return lo
        if v != v:  # NaN
            return lo
        return max(lo, min(hi, v))

    @staticmethod
    def _dna_snapshot(scda: SingleCellDigitalAccount) -> Dict[str, Any]:
        """Return a JSON-safe dict of the SCDA's DNA."""
        try:
            return scda.dna.to_dict()
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("DNA snapshot failed: %s", exc)
            return {"genes": [], "generation": 0}

    @staticmethod
    def _state(scda: SingleCellDigitalAccount) -> Dict[str, Any]:
        """Return the SCDA's serialised state with 8D knowledge vector."""
        try:
            return ScdaManager._state_for(scda)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("SCDA state snapshot failed: %s", exc)
            return {
                "identity": scda.identity,
                "complexity_index": float(scda.complexity_index),
                "energy": float(scda.energy),
                "knowledge_count": len(scda.knowledge_vector),
                "problem_queue_size": len(scda.problem_queue),
                "genetic_diversity": 0.0,
                "generation": 0,
                "knowledge_vector_8d": [0.0] * 8,
            }

    # ------------------------------------------------------------------ DNA edits

    def update_gene(
        self,
        identity: str,
        domain: str,
        *,
        strength: Optional[float] = None,
        expression_level: Optional[float] = None,
        mutation_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update a single gene of the SCDA's DNA.

        Parameters
        ----------
        identity:
            Target SCDA identity. Created if it does not exist yet.
        domain:
            Knowledge domain to target (e.g. ``"mathematics"``).
        strength, expression_level, mutation_count:
            Optional new values. Unspecified fields are left untouched.
            ``strength`` and ``expression_level`` are clamped to ``[0, 1]``;
            ``mutation_count`` is clamped to ``[0, 10_000]``.

        Returns
        -------
        dict
            ``{"identity", "domain", "before", "after", "state", "dna"}``.
        """
        scda = self._manager.get_or_create(identity)
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("domain must be a non-empty string")
        domain = domain.strip().lower()

        gene = scda.dna.get_gene_by_domain(domain)
        if gene is None:
            # Allocate a brand-new gene for this domain so the editor does not
            # silently no-op when the user types a novel domain string.
            gene = Gene(
                domain=domain,
                strength=0.0,
                expression_level=0.0,
                mutations=0,
                origin=GeneOrigin.PRIMORDIAL,
            )
            scda.dna.genes.append(gene)

        before = gene.to_dict()
        if strength is not None:
            gene.strength = self._clamp(strength)
        if expression_level is not None:
            gene.expression_level = self._clamp(expression_level)
        if mutation_count is not None:
            gene.mutations = int(max(0, min(10_000, mutation_count)))
        # If the operator manually changes a gene, the origin is no longer
        # purely primordial.
        if gene.origin == GeneOrigin.PRIMORDIAL and (
            gene.strength > 0.0 or gene.expression_level > 0.0
        ):
            gene.origin = GeneOrigin.LEARNED

        after = gene.to_dict()
        logger.info(
            "SCDA %s DNA edit domain=%s strength=%.4f expr=%.4f",
            identity, domain, gene.strength, gene.expression_level,
        )
        return {
            "identity": identity,
            "domain": domain,
            "before": before,
            "after": after,
            "state": self._state(scda),
            "dna": self._dna_snapshot(scda),
        }

    def apply_overrides(
        self,
        identity: str,
        dna_overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply a batch of DNA overrides keyed by domain name.

        Parameters
        ----------
        dna_overrides:
            ``{domain: {strength?, expression_level?, mutations?}}``.
            Unknown domains are auto-created (origin = LEARNED).
        """
        if not isinstance(dna_overrides, dict):
            raise ValueError("dna_overrides must be a dict of {domain: {...}}")

        applied: List[Dict[str, Any]] = []
        for domain, payload in dna_overrides.items():
            if not isinstance(payload, dict):
                continue
            result = self.update_gene(
                identity,
                domain,
                strength=payload.get("strength"),
                expression_level=payload.get("expression_level"),
                mutation_count=payload.get("mutations"),
            )
            applied.append({"domain": domain, "after": result["after"]})

        scda = self._manager.get_or_create(identity)
        return {
            "identity": identity,
            "applied": applied,
            "dna": self._dna_snapshot(scda),
            "state": self._state(scda),
        }

    def force_mutation(self, identity: str) -> Dict[str, Any]:
        """Force a mutation event on the SCDA's DNA (debug/visualisation helper)."""
        scda = self._manager.get_or_create(identity)
        DNAManager.mutate_dna(scda.dna, force=True)
        return {
            "identity": identity,
            "mutated": True,
            "dna": self._dna_snapshot(scda),
            "state": self._state(scda),
        }

    # -------------------------------------------------------- knowledge vector

    def update_knowledge_vector(
        self,
        identity: str,
        vector: List[float],
    ) -> Dict[str, Any]:
        """Replace the SCDA's 8D knowledge vector with *vector*.

        The vector is clamped to ``[0, 1]`` per-component and padded / truncated
        to exactly 8 components. The discrete ``knowledge_vector`` dict is
        left untouched — it is a different (sparse) structure used by the
        SCDA's evolutionary loop.
        """
        if not isinstance(vector, (list, tuple)):
            raise ValueError("vector must be an 8-element list of floats")

        scda = self._manager.get_or_create(identity)
        # Coerce / clamp / resize
        norm: List[float] = []
        for i in range(8):
            raw = vector[i] if i < len(vector) else 0.0
            norm.append(self._clamp(raw))

        # Reset all entries; recreate one entry per non-zero dimension with a
        # synthetic problem_id that round-trips through ScdaManager._vector_for.
        scda.knowledge_vector = {}
        for i, weight in enumerate(norm):
            if weight <= 0.0:
                continue
            domain = _KNOWLEDGE_DOMAINS[i] if i < len(_KNOWLEDGE_DOMAINS) else "knowledge"
            scda.knowledge_vector[f"{domain}_v8_{i}"] = float(weight)

        return {
            "identity": identity,
            "vector": norm,
            "domain_map": _KNOWLEDGE_DOMAINS,
            "state": self._state(scda),
        }

    # --------------------------------------------------------------- custom SCDA

    def create_custom(
        self,
        identity: str,
        *,
        initial_complexity: float = INITIAL_COMPLEXITY,
        initial_energy: float = INITIAL_ENERGY,
        dna_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create (or recreate) a SCDA with custom initial state.

        If the identity is already known, the existing record is removed first
        so the operator gets a true reset.
        """
        if not isinstance(identity, str) or not identity.strip():
            raise ValueError("identity must be a non-empty string")
        identity = identity.strip()

        # Reset if exists
        self._manager.delete(identity)

        scda = SingleCellDigitalAccount(
            identity=identity,
            complexity_index=max(0.0, float(initial_complexity)),
            energy=max(0.0, float(initial_energy)),
        )

        if dna_overrides:
            for domain, payload in dna_overrides.items():
                if not isinstance(payload, dict):
                    continue
                gene = scda.dna.get_gene_by_domain(domain)
                if gene is None:
                    scda.dna.genes.append(
                        Gene(
                            domain=str(domain),
                            strength=0.0,
                            expression_level=0.0,
                            origin=GeneOrigin.PRIMORDIAL,
                        )
                    )
                    gene = scda.dna.get_gene_by_domain(domain)
                if gene is None:
                    continue
                if "strength" in payload:
                    gene.strength = self._clamp(payload["strength"])
                if "expression_level" in payload:
                    gene.expression_level = self._clamp(payload["expression_level"])
                if gene.origin == GeneOrigin.PRIMORDIAL and (
                    gene.strength > 0.0 or gene.expression_level > 0.0
                ):
                    gene.origin = GeneOrigin.LEARNED

        self._manager.register(scda)
        logger.info(
            "SCDA %s custom-created C0=%.4f E0=%.2f overrides=%s",
            identity, scda.complexity_index, scda.energy, bool(dna_overrides),
        )
        return {
            "identity": identity,
            "state": self._state(scda),
            "dna": self._dna_snapshot(scda),
        }

    # ----------------------------------------------------- custom problem eval

    @staticmethod
    def validate_custom_problem(problem: Dict[str, Any]) -> Tuple[bool, str]:
        """Return ``(ok, message)`` for a *custom_problem* payload.

        A custom problem is a free-form expression/equation the user wants
        the SCDA to attempt. We accept either ``equation`` (string) or
        ``difficulty`` + ``solution_quality`` numerics. No real symbolic
        solving happens here — we just refuse obviously malformed input so
        the operator doesn't accidentally push garbage into the manager.
        """
        if not isinstance(problem, dict):
            return False, "custom_problem must be a JSON object"
        if "equation" in problem and not isinstance(problem["equation"], str):
            return False, "equation must be a string"
        if "equation" in problem and len(problem["equation"].strip()) == 0:
            return False, "equation must not be empty"
        if "difficulty" in problem:
            try:
                d = float(problem["difficulty"])
            except (TypeError, ValueError):
                return False, "difficulty must be a number in [0, 1]"
            if not 0.0 <= d <= 1.0:
                return False, "difficulty must be in [0, 1]"
        if "solution_quality" in problem:
            try:
                q = float(problem["solution_quality"])
            except (TypeError, ValueError):
                return False, "solution_quality must be a number in [0, 1]"
            if not 0.0 <= q <= 1.0:
                return False, "solution_quality must be in [0, 1]"
        if "id" in problem and not isinstance(problem["id"], str):
            return False, "id must be a string"
        return True, "ok"

    def evolve(
        self,
        identity: str,
        *,
        problem_difficulty: Optional[float] = None,
        custom_problem: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Apply one evolution step with an optional *custom_problem*.

        Either ``problem_difficulty`` (and an internal default
        ``solution_quality``) or a full ``custom_problem`` dict may be passed.
        Returns a structured response including ``delta_c``, the new state
        and the raw attempt result.
        """
        scda = self._manager.get_or_create(identity)

        if custom_problem is not None:
            ok, msg = self.validate_custom_problem(custom_problem)
            if not ok:
                raise ValueError(f"invalid custom_problem: {msg}")
            difficulty = float(custom_problem.get("difficulty", problem_difficulty or 0.5))
            quality = float(custom_problem.get("solution_quality", 0.8))
            problem_id = str(custom_problem.get("id", f"custom_{uuid.uuid4().hex[:8]}"))
            is_valid = bool(custom_problem.get("is_valid", True))
            domain = custom_problem.get("domain")
        else:
            if problem_difficulty is None:
                raise ValueError("either problem_difficulty or custom_problem is required")
            difficulty = self._clamp(problem_difficulty)
            quality = 0.8  # synthetic default — matches the existing solve path
            problem_id = f"P_{uuid.uuid4().hex[:8]}"
            is_valid = True
            domain = None

        before_c = scda.complexity_index
        result = scda.attempt_solve_problem(
            problem_difficulty=difficulty,
            solution_quality=quality,
            is_valid=is_valid,
            problem_id=problem_id,
            relevant_domain=domain,
        )

        return {
            "identity": identity,
            "ok": result.success,
            "new_complexity": float(scda.complexity_index),
            "delta_c": float(scda.complexity_index - before_c),
            "new_state": self._state(scda),
            "attempt": {
                "success": result.success,
                "delta_c": result.delta_c,
                "energy_before": result.energy_before,
                "energy_after": result.energy_after,
                "message": result.message,
                "problem_id": problem_id,
            },
        }


# --- Hard-problem equation registry -----------------------------------------
# A tiny in-memory helper used by the cosmic-v8 algorithm lab endpoints to
# store custom hard-problem equations. The router keeps a Dict[str, dict]
# on ``app.state.cosmic_algorithms``; this class only validates payloads.

_SAFE_VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_,\s\.\+\-\*\/\^\(\)\[\]0-9]*$")


class HardProblemValidator:
    """Lightweight, side-effect-free validator for custom hard problems."""

    MAX_EQUATION_LENGTH = 4096
    ALLOWED_DOMAINS = {
        "mathematics", "physics", "biology", "history",
        "knowledge", "energy", "complexity", "social",
        "custom", "experimental",
    }

    @classmethod
    def validate(cls, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """Return ``(ok, message)`` for an algorithm-lab save payload."""
        if not isinstance(payload, dict):
            return False, "payload must be a JSON object"
        for field in ("name", "domain", "difficulty", "equation"):
            if field not in payload:
                return False, f"missing required field: {field}"

        if not isinstance(payload["name"], str) or not payload["name"].strip():
            return False, "name must be a non-empty string"
        if len(payload["name"]) > 256:
            return False, "name must be at most 256 characters"

        if not isinstance(payload["domain"], str):
            return False, "domain must be a string"
        if payload["domain"].lower() not in cls.ALLOWED_DOMAINS:
            return False, f"domain must be one of {sorted(cls.ALLOWED_DOMAINS)}"

        try:
            difficulty = float(payload["difficulty"])
        except (TypeError, ValueError):
            return False, "difficulty must be a number in [0, 1]"
        if not 0.0 <= difficulty <= 1.0:
            return False, "difficulty must be in [0, 1]"

        if not isinstance(payload["equation"], str):
            return False, "equation must be a string"
        equation = payload["equation"].strip()
        if not equation:
            return False, "equation must not be empty"
        if len(equation) > cls.MAX_EQUATION_LENGTH:
            return False, f"equation must be ≤ {cls.MAX_EQUATION_LENGTH} chars"

        # Very rough safety check: refuse obvious script injection or
        # import statements. We are NOT a CAS — this is just a heuristic
        # that keeps the runtime safe.
        lowered = equation.lower()
        for bad in ("import ", "exec(", "eval(", "open(", "__", "subprocess", "os.system"):
            if bad in lowered:
                return False, f"equation contains forbidden token: {bad!r}"

        if "rubric" in payload and not isinstance(payload["rubric"], dict):
            return False, "rubric must be a JSON object if provided"

        return True, "ok"


#: Schema returned by the router for an algorithm entry.
def algorithm_to_dict(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise a stored algorithm record to a stable JSON shape."""
    return {
        "id": str(record.get("id", "")),
        "name": str(record.get("name", "")),
        "domain": str(record.get("domain", "custom")),
        "difficulty": float(record.get("difficulty", 0.0)),
        "equation": str(record.get("equation", "")),
        "rubric": dict(record.get("rubric", {})),
        "created_at": float(record.get("created_at", time.time())),
    }
