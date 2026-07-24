"""
Laniakea Protocol - SCDA Manager
=================================

A process-wide registry of :class:`SingleCellDigitalAccount` instances that
wraps the raw evolutionary model with the small amount of bookkeeping the
HTTP layer needs:

* deterministic lookups by ``identity``
* per-SCDA 8D knowledge vectors (used by the diplomacy / knowledge-market
  subsystems) computed from the discrete knowledge dict
* aggregated metrics so the dashboard endpoint can report active SCDAs
  without scanning every user

The manager is intentionally a thin layer over the existing ``scda_model``
module - the evolutionary math, DNA, and validation all live there.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Dict, List, Optional

from .scda_model import SingleCellDigitalAccount


# --- Constants used to convert the SCDA's discrete knowledge dict into a
# continuous 8-dimensional vector (X, Y, Z, T, K, E, C, S). The mapping is
# domain -> dimension index. Domains outside this list are folded into K
# (Knowledge) so we never lose information.
_DOMAIN_TO_DIM = {
    "mathematics": 0,
    "physics": 1,
    "biology": 2,
    "history": 3,
    "knowledge": 4,
    "energy": 5,
    "complexity": 6,
    "social": 7,
}


class ScdaManager:
    """Singleton-style registry of SCDAs with thread-safe access."""

    def __init__(self) -> None:
        self._scdas: Dict[str, SingleCellDigitalAccount] = {}
        self._lock = threading.RLock()
        self._created_at: Dict[str, float] = {}

    # -- CRUD ----------------------------------------------------------------
    def create(self, identity: str) -> SingleCellDigitalAccount:
        """Create a new SCDA, or return the existing one if identity is known."""
        with self._lock:
            existing = self._scdas.get(identity)
            if existing is not None:
                return existing
            scda = SingleCellDigitalAccount(identity=identity)
            self._scdas[identity] = scda
            self._created_at[identity] = time.time()
            return scda

    def get(self, identity: str) -> Optional[SingleCellDigitalAccount]:
        with self._lock:
            return self._scdas.get(identity)

    def get_or_create(self, identity: str) -> SingleCellDigitalAccount:
        return self.get(identity) or self.create(identity)

    def list_identities(self) -> List[str]:
        with self._lock:
            return list(self._scdas.keys())

    def all_states(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [self._state_for(scda) for scda in self._scdas.values()]

    def total_complexity(self) -> float:
        with self._lock:
            return sum(s.complexity_index for s in self._scdas.values())

    def total_energy(self) -> float:
        with self._lock:
            return sum(s.energy for s in self._scdas.values())

    def delete(self, identity: str) -> bool:
        """Remove a SCDA from the registry. Returns True if removed."""
        with self._lock:
            if identity not in self._scdas:
                return False
            del self._scdas[identity]
            self._created_at.pop(identity, None)
            return True

    # -- Domain operations ---------------------------------------------------
    def attempt_solve(
        self,
        identity: str,
        problem_difficulty: float,
        solution_quality: float,
        is_valid: bool,
    ) -> Dict[str, Any]:
        """Attempt to solve a problem and return the updated SCDA state."""
        scda = self.get_or_create(identity)
        ok = scda.attempt_solve_problem(
            problem_difficulty=problem_difficulty,
            solution_quality=solution_quality,
            is_valid=is_valid,
        )
        return {
            "identity": scda.identity,
            "solved": ok,
            "state": self._state_for(scda),
        }

    def passive_update(self, identity: str) -> Dict[str, Any]:
        """Run the SCDA's passive (background) update."""
        scda = self.get_or_create(identity)
        scda.passive_update()
        return self._state_for(scda)

    def compute_knowledge_vector(self, identity: str) -> List[float]:
        """Convert the SCDA's discrete knowledge dict into an 8D vector."""
        scda = self.get_or_create(identity)
        return self._vector_for(scda)

    def leaderboard(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Return the top-N SCDAs ranked by complexity_index."""
        with self._lock:
            ranked = sorted(
                self._scdas.values(),
                key=lambda s: s.complexity_index,
                reverse=True,
            )[:top_n]
            return [
                {
                    "identity": s.identity,
                    "complexity_index": s.complexity_index,
                    "energy": s.energy,
                    "knowledge_count": len(s.knowledge_vector),
                }
                for s in ranked
            ]

    # -- Helpers -------------------------------------------------------------
    @staticmethod
    def _state_for(scda: SingleCellDigitalAccount) -> Dict[str, Any]:
        """Augment the model state with a derived 8D knowledge vector."""
        return {
            **scda.get_state(),
            "knowledge_vector_8d": ScdaManager._vector_for(scda),
        }

    @staticmethod
    def _vector_for(scda: SingleCellDigitalAccount) -> List[float]:
        """Fold ``scda.knowledge_vector`` (Dict[problem_id, weight]) into an 8D vec.

        The fold is intentionally simple and stable: each knowledge entry's
        weight is added to the dimension matching its (heuristic) problem
        prefix, defaulting to the Knowledge (4) dimension. The vector is
        normalised by the number of entries so a brand-new SCDA returns
        ``[0, 0, 0, 0, 0, 0, 0, 0]`` rather than a noisy unit vector.
        """
        vec = [0.0] * 8
        if not scda.knowledge_vector:
            return vec
        for problem_id, weight in scda.knowledge_vector.items():
            domain = str(problem_id).split("_", 1)[0].lower() if problem_id else ""
            idx = _DOMAIN_TO_DIM.get(domain, 4)
            vec[idx] += float(weight)
        n = float(len(scda.knowledge_vector))
        return [round(v / n, 6) for v in vec]


# --- Module-level singleton -------------------------------------------------
_manager: Optional[ScdaManager] = None


def get_scda_manager() -> ScdaManager:
    """Return the process-wide :class:`ScdaManager` (lazy init)."""
    global _manager
    if _manager is None:
        _manager = ScdaManager()
    return _manager
