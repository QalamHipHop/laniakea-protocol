"""Digital DNA — the genetic substrate of an SCDA.

This module models the genome of a digital organism. Each DNA strand is a
collection of :class:`Gene` objects, one per knowledge domain, plus
lineage and recombination history. The semantics are:

* Strength ∈ [0, 1]   — how developed this gene is
* Expression ∈ [0, 1] — how actively it is being used
* Mutations            — cumulative count
* Origin               — primordial / learned / inherited / mutated / exchanged

The DNA can be:
  * **Mutated** (random walk on strength / expression)
  * **Recombined** (Mendelian crossover of two parents)
  * **Exchanged** (horizontal gene transfer between two SCDAs)
  * **Visualised** as a text bar chart

Author: Qalam
"""

from __future__ import annotations

import json
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import BaseModel, Field, field_validator

from laniakea.utils.logger import logger


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class GeneOrigin(str, Enum):
    """Provenance of a gene."""

    PRIMORDIAL = "primordial"
    LEARNED = "learned"
    INHERITED = "inherited"
    MUTATED = "mutated"
    EXCHANGED = "exchanged"


class MutationType(str, Enum):
    """How a gene can mutate."""

    STRENGTH_INCREASE = "strength_increase"
    STRENGTH_DECREASE = "strength_decrease"
    EXPRESSION_CHANGE = "expression_change"
    DOMAIN_SHIFT = "domain_shift"


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: The eight knowledge domains of the Laniakea 8D hypercube.
KNOWLEDGE_DOMAINS: List[str] = [
    "physics",
    "biology",
    "mathematics",
    "computer_science",
    "chemistry",
    "philosophy",
    "engineering",
    "cosmology",
]

#: Default mutation probability per event.
DEFAULT_MUTATION_RATE: float = 0.01

#: Weight distribution for the four mutation types.
MUTATION_WEIGHTS: Dict[MutationType, float] = {
    MutationType.STRENGTH_INCREASE: 0.40,
    MutationType.STRENGTH_DECREASE: 0.40,
    MutationType.EXPRESSION_CHANGE: 0.19,
    MutationType.DOMAIN_SHIFT: 0.01,
}

#: Initial primordial strength range (uniform).
INITIAL_STRENGTH_RANGE: tuple = (0.01, 0.10)

#: Initial expression level for primordial genes.
INITIAL_EXPRESSION: float = 0.1


# ---------------------------------------------------------------------------
# Pydantic schemas (API surface)
# ---------------------------------------------------------------------------

class GeneSnapshot(BaseModel):
    """JSON-serialisable view of a :class:`Gene`."""

    id: str
    domain: str
    strength: float = Field(ge=0.0, le=1.0)
    expression_level: float = Field(ge=0.0, le=1.0)
    mutations: int = Field(ge=0)
    origin: str
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "g-7f2c",
                "domain": "physics",
                "strength": 0.42,
                "expression_level": 0.31,
                "mutations": 2,
                "origin": "inherited",
                "created_at": "2026-07-27T10:00:00+00:00",
            }
        }


class DNASnapshot(BaseModel):
    """JSON-serialisable view of a :class:`DigitalDNA`."""

    generation: int = Field(ge=0)
    lineage: List[str]
    mutation_rate: float = Field(ge=0.0, le=1.0)
    genetic_diversity: float = Field(ge=0.0, le=1.0)
    genes: List[GeneSnapshot]
    recombination_history: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Dataclasses (in-memory model)
# ---------------------------------------------------------------------------

@dataclass
class Gene:
    """A single gene in the Digital DNA.

    One gene per knowledge domain. Genes evolve through mutation,
    learning, inheritance and exchange.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = ""
    strength: float = 0.0
    mutations: int = 0
    origin: GeneOrigin | str = GeneOrigin.PRIMORDIAL
    expression_level: float = INITIAL_EXPRESSION
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain-dict representation."""
        return {
            "id": self.id,
            "domain": self.domain,
            "strength": float(self.strength),
            "mutations": int(self.mutations),
            "origin": self.origin.value if isinstance(self.origin, GeneOrigin) else str(self.origin),
            "expression_level": float(self.expression_level),
            "created_at": self.created_at,
        }

    def to_snapshot(self) -> GeneSnapshot:
        """Return a validated Pydantic snapshot."""
        return GeneSnapshot(
            id=self.id,
            domain=self.domain,
            strength=float(self.strength),
            expression_level=float(self.expression_level),
            mutations=int(self.mutations),
            origin=self.origin.value if isinstance(self.origin, GeneOrigin) else str(self.origin),
            created_at=self.created_at,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Gene":
        """Reconstruct a Gene from a dict produced by :meth:`to_dict`."""
        origin = data.get("origin", GeneOrigin.PRIMORDIAL.value)
        try:
            origin_enum = GeneOrigin(origin)
        except ValueError:
            origin_enum = GeneOrigin.PRIMORDIAL
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            domain=data.get("domain", ""),
            strength=float(data.get("strength", 0.0)),
            mutations=int(data.get("mutations", 0)),
            origin=origin_enum,
            expression_level=float(data.get("expression_level", INITIAL_EXPRESSION)),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )


@dataclass
class DigitalDNA:
    """The complete DNA of an SCDA — its evolutionary history."""

    genes: List[Gene] = field(default_factory=list)
    generation: int = 0
    lineage: List[str] = field(default_factory=list)
    mutation_rate: float = DEFAULT_MUTATION_RATE
    recombination_history: List[Dict[str, Any]] = field(default_factory=list)

    # ----------------------------------------------- accessors & predicates

    def get_gene_by_domain(self, domain: str) -> Optional[Gene]:
        for gene in self.genes:
            if gene.domain == domain:
                return gene
        return None

    def get_dominant_genes(self, n: int = 3) -> List[Gene]:
        return sorted(self.genes, key=lambda g: g.strength, reverse=True)[:n]

    def get_active_genes(self, threshold: float = 0.5) -> List[Gene]:
        return [g for g in self.genes if g.expression_level >= threshold]

    def calculate_genetic_diversity(self) -> float:
        """Shannon entropy of strength distribution, normalised to [0, 1]."""
        if not self.genes:
            return 0.0
        strengths = np.array([g.strength for g in self.genes], dtype=np.float64)
        total = strengths.sum()
        if total <= 0:
            return 0.0
        p = strengths / total
        entropy = -float(np.sum(p * np.log(p + 1e-10)))
        max_entropy = float(np.log(len(self.genes)))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    # ---------------------------------------------------------- serialise

    def to_dict(self) -> Dict[str, Any]:
        return {
            "genes": [g.to_dict() for g in self.genes],
            "generation": int(self.generation),
            "lineage": list(self.lineage),
            "mutation_rate": float(self.mutation_rate),
            "recombination_history": list(self.recombination_history),
        }

    def to_snapshot(self) -> DNASnapshot:
        return DNASnapshot(
            generation=int(self.generation),
            lineage=list(self.lineage),
            mutation_rate=float(self.mutation_rate),
            genetic_diversity=float(self.calculate_genetic_diversity()),
            genes=[g.to_snapshot() for g in self.genes],
            recombination_history=list(self.recombination_history),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DigitalDNA":
        dna = cls()
        dna.genes = [Gene.from_dict(g) for g in data.get("genes", [])]
        dna.generation = int(data.get("generation", 0))
        dna.lineage = list(data.get("lineage", []))
        dna.mutation_rate = float(data.get("mutation_rate", DEFAULT_MUTATION_RATE))
        dna.recombination_history = list(data.get("recombination_history", []))
        return dna

    @classmethod
    def from_json(cls, payload: str) -> "DigitalDNA":
        return cls.from_dict(json.loads(payload))


# ---------------------------------------------------------------------------
# DNAManager — factory & operations
# ---------------------------------------------------------------------------

class DNAManager:
    """Static factory + operations for Digital DNA.

    All methods are pure (return new / mutated DNA, no I/O) so they can
    be safely called from async contexts.
    """

    KNOWLEDGE_DOMAINS: List[str] = KNOWLEDGE_DOMAINS
    DEFAULT_MUTATION_RATE: float = DEFAULT_MUTATION_RATE

    # --------------------------------------------------------------- factory

    @staticmethod
    def create_initial_dna(scda_id: str) -> DigitalDNA:
        """Build a fresh primordial DNA (one gene per domain, low strength)."""
        dna = DigitalDNA()
        dna.generation = 0
        dna.lineage = [scda_id]
        for domain in KNOWLEDGE_DOMAINS:
            dna.genes.append(
                Gene(
                    domain=domain,
                    strength=random.uniform(*INITIAL_STRENGTH_RANGE),
                    mutations=0,
                    origin=GeneOrigin.PRIMORDIAL,
                    expression_level=INITIAL_EXPRESSION,
                )
            )
        logger.debug("DNA created scda_id=%s genes=%d", scda_id, len(dna.genes))
        return dna

    # --------------------------------------------------------------- mutate

    @staticmethod
    def mutate_gene(gene: Gene) -> Gene:
        """Apply a single weighted random mutation to a gene in place."""
        types = list(MUTATION_WEIGHTS.keys())
        weights = list(MUTATION_WEIGHTS.values())
        mtype: MutationType = random.choices(types, weights=weights, k=1)[0]

        if mtype is MutationType.STRENGTH_INCREASE:
            gene.strength = min(1.0, gene.strength + random.uniform(0.05, 0.15))
        elif mtype is MutationType.STRENGTH_DECREASE:
            gene.strength = max(0.0, gene.strength - random.uniform(0.05, 0.15))
        elif mtype is MutationType.EXPRESSION_CHANGE:
            gene.expression_level = float(np.clip(
                gene.expression_level + random.uniform(-0.2, 0.2), 0.0, 1.0,
            ))
        elif mtype is MutationType.DOMAIN_SHIFT:
            gene.domain = random.choice(KNOWLEDGE_DOMAINS)

        gene.mutations += 1
        gene.origin = GeneOrigin.MUTATED
        return gene

    @staticmethod
    def mutate_dna(dna: DigitalDNA, force: bool = False) -> DigitalDNA:
        """Walk all genes and probabilistically mutate them."""
        for gene in dna.genes:
            if force or random.random() < dna.mutation_rate:
                DNAManager.mutate_gene(gene)
        return dna

    # ------------------------------------------------------------ recombine

    @staticmethod
    def recombine_dna(
        dna1: DigitalDNA,
        dna2: DigitalDNA,
        child_scda_id: str,
    ) -> DigitalDNA:
        """Mendelian crossover — one gene per domain from a random parent."""
        new_dna = DigitalDNA()
        new_dna.generation = max(dna1.generation, dna2.generation) + 1
        new_dna.lineage = (
            [child_scda_id] + dna1.lineage[:2] + dna2.lineage[:2]
        )
        new_dna.mutation_rate = (dna1.mutation_rate + dna2.mutation_rate) / 2.0

        for domain in KNOWLEDGE_DOMAINS:
            parent_gene = (
                dna1.get_gene_by_domain(domain) if random.random() < 0.5
                else dna2.get_gene_by_domain(domain)
            )
            if parent_gene is None:
                continue
            new_dna.genes.append(
                Gene(
                    domain=domain,
                    strength=parent_gene.strength,
                    mutations=parent_gene.mutations,
                    origin=GeneOrigin.INHERITED,
                    expression_level=parent_gene.expression_level,
                )
            )

        new_dna.recombination_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "parent1": dna1.lineage[0] if dna1.lineage else "unknown",
            "parent2": dna2.lineage[0] if dna2.lineage else "unknown",
            "generation": new_dna.generation,
        })
        return new_dna

    @staticmethod
    def exchange_genes(dna1: DigitalDNA, dna2: DigitalDNA, domain: str) -> None:
        """Horizontal gene transfer — both genes become stronger (averaged +10 %)."""
        gene1 = dna1.get_gene_by_domain(domain)
        gene2 = dna2.get_gene_by_domain(domain)
        if gene1 is None or gene2 is None:
            return
        avg_strength = (gene1.strength + gene2.strength) / 2.0
        gene1.strength = min(1.0, avg_strength * 1.1)
        gene2.strength = min(1.0, avg_strength * 1.1)
        gene1.origin = GeneOrigin.EXCHANGED
        gene2.origin = GeneOrigin.EXCHANGED

    # ------------------------------------------------------------ strengthen

    @staticmethod
    def strengthen_gene(dna: DigitalDNA, domain: str, amount: float) -> None:
        """Boost the strength & expression of a single domain's gene."""
        gene = dna.get_gene_by_domain(domain)
        if gene is None:
            return
        gene.strength = min(1.0, gene.strength + amount)
        gene.expression_level = min(1.0, gene.expression_level + amount * 0.5)
        if gene.origin == GeneOrigin.PRIMORDIAL:
            gene.origin = GeneOrigin.LEARNED

    # ------------------------------------------------------------ distance

    @staticmethod
    def calculate_genetic_distance(dna1: DigitalDNA, dna2: DigitalDNA) -> float:
        """Euclidean distance in (strength, expression) space, normalised to [0, 1]."""
        if not dna1.genes or not dna2.genes:
            return 1.0
        distances: List[float] = []
        for domain in KNOWLEDGE_DOMAINS:
            g1 = dna1.get_gene_by_domain(domain)
            g2 = dna2.get_gene_by_domain(domain)
            if g1 is None or g2 is None:
                continue
            distances.append(float(np.sqrt(
                (g1.strength - g2.strength) ** 2 +
                (g1.expression_level - g2.expression_level) ** 2
            )))
        if not distances:
            return 1.0
        return float(np.mean(distances)) / float(np.sqrt(2))

    # ------------------------------------------------------------ visualise

    @staticmethod
    def visualize_dna(dna: DigitalDNA) -> str:
        """Render a text bar-chart of the DNA."""
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append(f"Digital DNA — Generation {dna.generation}")
        lines.append("=" * 60)
        for gene in sorted(dna.genes, key=lambda g: g.strength, reverse=True):
            strength_bar = "█" * int(gene.strength * 20)
            expression_bar = "▓" * int(gene.expression_level * 20)
            lines.append(f"\n{gene.domain.upper()}")
            lines.append(f"  Strength:    {strength_bar:<20} {gene.strength:.2f}")
            lines.append(f"  Expression:  {expression_bar:<20} {gene.expression_level:.2f}")
            lines.append(f"  Mutations:   {gene.mutations}")
            origin = gene.origin.value if isinstance(gene.origin, GeneOrigin) else gene.origin
            lines.append(f"  Origin:      {origin}")
        lines.append("\n" + "=" * 60)
        lines.append(f"Genetic Diversity: {dna.calculate_genetic_diversity():.3f}")
        lines.append(f"Mutation Rate:     {dna.mutation_rate:.3f}")
        lines.append(f"Lineage: {' -> '.join(dna.lineage[:5])}")
        lines.append("=" * 60)
        return "\n".join(lines)


__all__ = [
    "KNOWLEDGE_DOMAINS",
    "DEFAULT_MUTATION_RATE",
    "INITIAL_STRENGTH_RANGE",
    "INITIAL_EXPRESSION",
    "MUTATION_WEIGHTS",
    "GeneOrigin",
    "MutationType",
    "GeneSnapshot",
    "DNASnapshot",
    "Gene",
    "DigitalDNA",
    "DNAManager",
]


# ---------------------------------------------------------------------------
# Module self-test (only run when executed directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    print("🧬 Digital DNA System Demo\n")

    dna = DNAManager.create_initial_dna("scda_001")
    print("Initial DNA:")
    print(DNAManager.visualize_dna(dna))

    print("\n📚 Learning physics and mathematics…")
    DNAManager.strengthen_gene(dna, "physics", 0.3)
    DNAManager.strengthen_gene(dna, "mathematics", 0.4)
    print(DNAManager.visualize_dna(dna))

    print("\n🧪 Applying mutations…")
    DNAManager.mutate_dna(dna, force=True)
    print(DNAManager.visualize_dna(dna))

    print("\n👥 Creating second SCDA and recombining DNA…")
    dna2 = DNAManager.create_initial_dna("scda_002")
    DNAManager.strengthen_gene(dna2, "biology", 0.5)
    DNAManager.strengthen_gene(dna2, "chemistry", 0.3)
    child_dna = DNAManager.recombine_dna(dna, dna2, "scda_003")
    print("Child DNA:")
    print(DNAManager.visualize_dna(child_dna))

    distance = DNAManager.calculate_genetic_distance(dna, dna2)
    print(f"\n📊 Genetic distance between parent 1 and parent 2: {distance:.3f}")
