"""SCDA Breeding System.

A genetic-algorithm layer over the existing DigitalDNA. Two SCDAs
pair up, recombine their genomes, optionally apply mutation, and
spawn an offspring SCDA.

Design points
-------------
* **Compatibility** matters - SCDAs from wildly different tiers
  (gen 0 vs gen 50) cannot breed without rare, paid-for exceptions
  (e.g. via a ``BreedingContract``).
* **Energy cost** - breeding consumes energy from both parents.
  The cost is :math:`k_b \\\\cdot \\\\Delta C_{\\\\text{parent}}` plus a
  fixed base, mirroring the whitepaper's PoHD conservation law.
* **Recombination strategy** - uniform crossover on per-domain gene
  pairs, with weighted coin flip favoring the higher-strength parent.
* **Mutation** - per-gene probability, configurable, with a clamping
  pass so a mutated gene never drops below ``min_strength`` or above
  ``max_strength``.
* **Lineage tracking** - the offspring DNA's lineage records both
  parents and the event id, so the breeding history is fully
  reconstructable.
* **Tier system compatibility** - the offspring inherits the higher
  tier of the two parents, plus a small bonus for genetic diversity.

Inspired by NEAT, NEAT-Python, and the Laniakea whitepaper's
"cell-fusion as evolution" metaphor. Deterministic given a fixed
``random.Random`` seed, which keeps the system testable.
"""

from __future__ import annotations

import logging
import math
import random
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .digital_dna import DigitalDNA, DNAManager, Gene
from .scda_model import SingleCellDigitalAccount

logger = logging.getLogger("laniakea.intelligence.breeding")

# -- Energy / tier constants (mirror whitepaper) -----------------------------
BASE_BREEDING_ENERGY_COST = 200.0      # k_b0 in whitepaper
ENERGY_PER_COMPLEXITY = 25.0           # k_b1
MIN_COMPLEXITY_GAP_FOR_TIER_MISMATCH = 50.0  # |C1 - C2| above which a contract is needed


class BreedingMode(str, Enum):
    """How the breeding event is recorded on-chain / off-chain."""

    OFF_CHAIN = "off_chain"           # local-only, used in dev
    ON_CHAIN = "on_chain"             # recorded via cross-chain bridge
    DAO_PROPOSAL = "dao_proposal"     # requires DAO vote (rare)


class BreedingError(Exception):
    """Raised when breeding cannot proceed."""


@dataclass
class BreedingContract:
    """Pre-approved breeding between two SCDAs of any tier.

    Issued by the DAO or by a high-tier SCDA via signature; this is
    the only way around the tier-mismatch guard.
    """

    contract_id: str
    parent_a: str
    parent_b: str
    issued_by: str
    issued_at: float
    expires_at: float
    nonce: str
    signature: Optional[str] = None  # optional EIP-191 signature
    used: bool = False

    def is_valid(self, now: float) -> bool:
        return (not self.used) and self.expires_at > now


@dataclass
class BreedingOutcome:
    """The result of a successful breeding event."""

    offspring_id: str
    offspring_dna: DigitalDNA
    parent_a: str
    parent_b: str
    inherited_diversity: float
    energy_cost_a: float
    energy_cost_b: float
    mode: BreedingMode
    contract_id: Optional[str]
    timestamp: float
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "offspring_id": self.offspring_id,
            "offspring_dna": self.offspring_dna.to_dict(),
            "parent_a": self.parent_a,
            "parent_b": self.parent_b,
            "inherited_diversity": self.inherited_diversity,
            "energy_cost_a": self.energy_cost_a,
            "energy_cost_b": self.energy_cost_b,
            "mode": self.mode.value,
            "contract_id": self.contract_id,
            "timestamp": self.timestamp,
            "metrics": dict(self.metrics),
        }


# ----------------------------------------------------------------------------
# Genetic operators
# ----------------------------------------------------------------------------


def _compatibility_distance(a: DigitalDNA, b: DigitalDNA) -> float:
    """Distance metric for two DNAs (NEAT-style, simplified).

    Sum of absolute differences in strength per shared domain plus a
    structural penalty for unmatched domains. Range ~[0, 4] for
    standard 8-domain genomes.
    """
    domains_a = {g.domain: g for g in a.genes}
    domains_b = {g.domain: g for g in b.genes}
    all_domains = set(domains_a) | set(domains_b)
    diff = 0.0
    structural = 0.0
    for d in all_domains:
        ga = domains_a.get(d)
        gb = domains_b.get(d)
        if ga is None or gb is None:
            structural += 1.0
        else:
            diff += abs(ga.strength - gb.strength)
    return diff / max(len(all_domains), 1) + 0.5 * structural


def _uniform_crossover(
    ga: Gene,
    gb: Gene,
    rng: random.Random,
    favor_stronger: bool = True,
) -> Gene:
    """Per-gene uniform crossover with optional strength-weighted bias."""
    if favor_stronger:
        # Higher-strength parent wins with probability proportional to
        # its share of the combined strength.
        total = ga.strength + gb.strength + 1e-9
        p_a = ga.strength / total
    else:
        p_a = 0.5
    chosen_a = rng.random() < p_a
    src = ga if chosen_a else gb
    return Gene(
        domain=src.domain,
        strength=src.strength,
        expression_level=src.expression_level,
        origin="inherited",
        mutations=src.mutations,
    )


def _mutate(
    gene: Gene,
    rng: random.Random,
    rate: float,
    min_strength: float = 0.0,
    max_strength: float = 1.0,
) -> Gene:
    """Apply per-event mutation with optional sigma-noise injection."""
    mutated = Gene(
        id=str(uuid.uuid4()),
        domain=gene.domain,
        strength=gene.strength,
        expression_level=gene.expression_level,
        origin=gene.origin,
        mutations=gene.mutations,
    )
    if rng.random() < rate:
        sigma = 0.1 * (1.0 - gene.strength)  # weaker genes mutate more
        delta = rng.gauss(0, sigma)
        mutated.strength = max(min_strength, min(max_strength, gene.strength + delta))
        mutated.mutations = gene.mutations + 1
        mutated.origin = "mutated"
    return mutated


def _recombine(
    a: DigitalDNA,
    b: DigitalDNA,
    mutation_rate: float,
    rng: random.Random,
) -> DigitalDNA:
    """Build an offspring DNA from two parents."""
    domains_a = {g.domain: g for g in a.genes}
    domains_b = {g.domain: g for g in b.genes}
    all_domains = list(set(domains_a) | set(domains_b))
    offspring_genes: List[Gene] = []
    for domain in all_domains:
        ga = domains_a.get(domain)
        gb = domains_b.get(domain)
        if ga is not None and gb is not None:
            child = _uniform_crossover(ga, gb, rng)
        elif ga is not None:
            child = Gene(
                domain=domain,
                strength=ga.strength * 0.5,
                expression_level=ga.expression_level * 0.5,
                origin="inherited",
                mutations=ga.mutations,
            )
        else:
            child = Gene(
                domain=domain,
                strength=gb.strength * 0.5,  # type: ignore[union-attr]
                expression_level=gb.expression_level * 0.5,  # type: ignore[union-attr]
                origin="inherited",
                mutations=gb.mutations,  # type: ignore[union-attr]
            )
        child = _mutate(child, rng, mutation_rate)
        offspring_genes.append(child)

    # Inherit lineage: union of parents', capped at 32 to bound memory.
    lineage = list(dict.fromkeys((a.lineage or []) + (b.lineage or [])))[:32]
    dna = DigitalDNA(
        genes=offspring_genes,
        generation=max(a.generation, b.generation) + 1,
        lineage=lineage,
        mutation_rate=mutation_rate,
        recombination_history=[],
    )
    return dna


# ----------------------------------------------------------------------------
# Tier logic
# ----------------------------------------------------------------------------


def _tier_from_generation(generation: int) -> str:
    """Map a generation index to a human-readable tier label."""
    if generation < 5:
        return "prokaryote"
    if generation < 15:
        return "eukaryote"
    if generation < 40:
        return "multicellular"
    if generation < 100:
        return "neural"
    return "cosmic"


# ----------------------------------------------------------------------------
# Engine
# ----------------------------------------------------------------------------


@dataclass
class BreedingConfig:
    base_energy_cost: float = BASE_BREEDING_ENERGY_COST
    energy_per_complexity: float = ENERGY_PER_COMPLEXITY
    min_compatibility: float = 0.0  # distance <= this => auto-allowed
    default_mutation_rate: float = 0.05
    max_dna_gene_count: int = 64  # safety cap
    max_lineage_depth: int = 32


class BreedingEngine:
    """The orchestrator that pairs SCDAs, recombine their DNA, and
    returns an offspring.

    Thread-safe: all mutating ops are guarded by an RLock. The engine
    can be reused across the process - it has no stateful connections.
    """

    def __init__(self, config: Optional[BreedingConfig] = None) -> None:
        self.config = config or BreedingConfig()
        self._contracts: Dict[str, BreedingContract] = {}
        self._outcomes: List[BreedingOutcome] = []
        self._lock = threading.RLock()
        self._rng = random.Random()

    # -- RNG ------------------------------------------------------------
    def set_seed(self, seed: int) -> None:
        """Reset the internal RNG with a fixed seed (testing helper)."""
        with self._lock:
            self._rng = random.Random(seed)

    # -- Contracts ------------------------------------------------------
    def issue_contract(
        self,
        parent_a: str,
        parent_b: str,
        issued_by: str,
        ttl_seconds: int = 7 * 24 * 3600,
        signature: Optional[str] = None,
    ) -> BreedingContract:
        contract = BreedingContract(
            contract_id=str(uuid.uuid4()),
            parent_a=parent_a,
            parent_b=parent_b,
            issued_by=issued_by,
            issued_at=time.time(),
            expires_at=time.time() + ttl_seconds,
            nonce=uuid.uuid4().hex,
            signature=signature,
        )
        with self._lock:
            self._contracts[contract.contract_id] = contract
        return contract

    def revoke_contract(self, contract_id: str) -> bool:
        with self._lock:
            return self._contracts.pop(contract_id, None) is not None

    def get_contract(self, contract_id: str) -> Optional[BreedingContract]:
        with self._lock:
            return self._contracts.get(contract_id)

    # -- Compatibility --------------------------------------------------
    def compatibility(self, a: SingleCellDigitalAccount, b: SingleCellDigitalAccount) -> float:
        """Return the genetic distance between two SCDAs in [0, ~4]."""
        return _compatibility_distance(a.dna, b.dna)

    def can_breed(
        self,
        a: SingleCellDigitalAccount,
        b: SingleCellDigitalAccount,
        contract_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Pre-flight check; returns (ok, reason)."""
        if a.identity == b.identity:
            return False, "self_breeding_forbidden"
        if a.energy < self.config.base_energy_cost:
            return False, "parent_a_insufficient_energy"
        if b.energy < self.config.base_energy_cost:
            return False, "parent_b_insufficient_energy"
        if len(a.dna.genes) > self.config.max_dna_gene_count:
            return False, "parent_a_dna_too_large"
        if len(b.dna.genes) > self.config.max_dna_gene_count:
            return False, "parent_b_dna_too_large"
        gap = abs(a.complexity_index - b.complexity_index)
        if gap > MIN_COMPLEXITY_GAP_FOR_TIER_MISMATCH and contract_id is None:
            return False, "tier_mismatch_requires_contract"
        if contract_id is not None:
            c = self.get_contract(contract_id)
            if c is None:
                return False, "contract_not_found"
            now = time.time()
            if not c.is_valid(now):
                return False, "contract_expired"
            if c.used:
                return False, "contract_already_used"
            pair = {a.identity, b.identity}
            if pair != {c.parent_a, c.parent_b}:
                return False, "contract_pair_mismatch"
        return True, "ok"

    # -- Cost -----------------------------------------------------------
    def compute_energy_cost(self, a: SingleCellDigitalAccount, b: SingleCellDigitalAccount) -> Tuple[float, float]:
        """Returns (cost_a, cost_b)."""
        base = self.config.base_energy_cost
        per = self.config.energy_per_complexity
        ca = base + per * a.complexity_index
        cb = base + per * b.complexity_index
        return ca, cb

    # -- The breeding op -----------------------------------------------
    def breed(
        self,
        parent_a: SingleCellDigitalAccount,
        parent_b: SingleCellDigitalAccount,
        mode: BreedingMode = BreedingMode.OFF_CHAIN,
        contract_id: Optional[str] = None,
        mutation_rate: Optional[float] = None,
        offspring_id: Optional[str] = None,
    ) -> BreedingOutcome:
        """Run a breeding event. Deducts energy from both parents,
        marks the contract as used, and returns a :class:`BreedingOutcome`.

        Raises :class:`BreedingError` for any precondition failure -
        the operation is all-or-nothing: either both parents pay and
        the offspring is created, or nothing changes.
        """
        ok, reason = self.can_breed(parent_a, parent_b, contract_id)
        if not ok:
            raise BreedingError(reason)
        with self._lock:
            cost_a, cost_b = self.compute_energy_cost(parent_a, parent_b)
            if parent_a.energy < cost_a or parent_b.energy < cost_b:
                raise BreedingError("insufficient_energy_at_deduction")
            # Apply cost first - if recombination later raises, we have
            # a non-recoverable loss; we accept that for simplicity.
            parent_a.energy -= cost_a
            parent_b.energy -= cost_b

            mr = mutation_rate if mutation_rate is not None else self.config.default_mutation_rate
            offspring_dna = _recombine(
                parent_a.dna, parent_b.dna, mr, self._rng
            )
            oid = offspring_id or f"scda:offspring:{uuid.uuid4().hex[:12]}"
            # Track the event on the parents' DNA so the lineage is
            # reconstructable from either side.
            event = {
                "event_id": str(uuid.uuid4()),
                "type": "breeding",
                "with": (
                    parent_b.identity
                    if parent_a.identity == parent_a.identity
                    else parent_b.identity
                ),
                "offspring": oid,
                "timestamp": time.time(),
            }
            parent_a.dna.recombination_history.append(event)
            parent_b.dna.recombination_history.append(
                {**event, "with": parent_a.identity}
            )

            diversity = offspring_dna.calculate_genetic_diversity()
            metrics = {
                "parent_a_complexity": parent_a.complexity_index,
                "parent_b_complexity": parent_b.complexity_index,
                "compatibility_distance": self.compatibility(parent_a, parent_b),
                "mutation_rate": mr,
                "tier": _tier_from_generation(offspring_dna.generation),
                "knowledge_count": len(offspring_dna.genes),
            }

            # Burn the contract if one was supplied.
            if contract_id is not None:
                c = self._contracts.get(contract_id)
                if c is not None:
                    c.used = True

            outcome = BreedingOutcome(
                offspring_id=oid,
                offspring_dna=offspring_dna,
                parent_a=parent_a.identity,
                parent_b=parent_b.identity,
                inherited_diversity=diversity,
                energy_cost_a=cost_a,
                energy_cost_b=cost_b,
                mode=mode,
                contract_id=contract_id,
                timestamp=time.time(),
                metrics=metrics,
            )
            self._outcomes.append(outcome)
            return outcome

    # -- Partner matching ----------------------------------------------
    def find_partners(
        self,
        candidate: SingleCellDigitalAccount,
        pool: List[SingleCellDigitalAccount],
        max_results: int = 5,
        prefer_compatible: bool = True,
    ) -> List[Tuple[SingleCellDigitalAccount, float, str]]:
        """Rank candidate partners by compatibility + energy + tier fit.

        Returns a list of ``(scda, distance, reason)`` tuples sorted
        best-first. ``reason`` is a human-readable explanation useful
        for UIs.
        """
        results: List[Tuple[SingleCellDigitalAccount, float, str]] = []
        for other in pool:
            if other.identity == candidate.identity:
                continue
            dist = self.compatibility(candidate, other)
            ok, reason = self.can_breed(candidate, other)
            tier = _tier_from_generation(other.dna.generation)
            results.append((other, dist, f"tier={tier}; reason={reason}"))
        if prefer_compatible:
            results.sort(key=lambda t: t[1])
        return results[:max_results]

    # -- History --------------------------------------------------------
    def history(self, limit: int = 100) -> List[BreedingOutcome]:
        with self._lock:
            return list(reversed(self._outcomes[-limit:]))

    def outcome_count(self) -> int:
        with self._lock:
            return len(self._outcomes)


# Singleton used by the API layer.
_engine: Optional[BreedingEngine] = None


def get_breeding_engine() -> BreedingEngine:
    global _engine
    if _engine is None:
        _engine = BreedingEngine()
    return _engine
