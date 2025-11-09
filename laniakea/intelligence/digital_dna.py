"""
Digital DNA System for LaniakeA Protocol V0.0.03
Simulates genetic information and evolution at the digital level
"""

import uuid
import random
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Gene:
    """
    Represents a single gene in the Digital DNA.
    Each gene corresponds to a knowledge domain.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = ""  # physics, biology, mathematics, etc.
    strength: float = 0.0  # 0-1, how strong this gene is
    mutations: int = 0  # number of mutations this gene has undergone
    origin: str = "primordial"  # primordial, learned, inherited, mutated
    expression_level: float = 0.1  # 0-1, how active this gene is
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert gene to dictionary"""
        return {
            "id": self.id,
            "domain": self.domain,
            "strength": self.strength,
            "mutations": self.mutations,
            "origin": self.origin,
            "expression_level": self.expression_level,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Gene':
        """Create gene from dictionary"""
        return cls(**data)


@dataclass
class DigitalDNA:
    """
    Represents the complete Digital DNA of an SCDA.
    Contains all genetic information and evolutionary history.
    """
    genes: List[Gene] = field(default_factory=list)
    generation: int = 0  # Which generation this DNA belongs to
    lineage: List[str] = field(default_factory=list)  # Ancestry (SCDA IDs)
    mutation_rate: float = 0.01  # Probability of mutation per event
    recombination_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DNA to dictionary"""
        return {
            "genes": [gene.to_dict() for gene in self.genes],
            "generation": self.generation,
            "lineage": self.lineage,
            "mutation_rate": self.mutation_rate,
            "recombination_history": self.recombination_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DigitalDNA':
        """Create DNA from dictionary"""
        dna = cls()
        dna.genes = [Gene.from_dict(g) for g in data.get("genes", [])]
        dna.generation = data.get("generation", 0)
        dna.lineage = data.get("lineage", [])
        dna.mutation_rate = data.get("mutation_rate", 0.01)
        dna.recombination_history = data.get("recombination_history", [])
        return dna
    
    def get_gene_by_domain(self, domain: str) -> Optional[Gene]:
        """Find gene by domain"""
        for gene in self.genes:
            if gene.domain == domain:
                return gene
        return None
    
    def get_dominant_genes(self, n: int = 3) -> List[Gene]:
        """Get top N genes by strength"""
        sorted_genes = sorted(self.genes, key=lambda g: g.strength, reverse=True)
        return sorted_genes[:n]
    
    def get_active_genes(self, threshold: float = 0.5) -> List[Gene]:
        """Get genes with expression level above threshold"""
        return [gene for gene in self.genes if gene.expression_level >= threshold]
    
    def calculate_genetic_diversity(self) -> float:
        """Calculate genetic diversity (0-1)"""
        if not self.genes:
            return 0.0
        
        # Shannon entropy of gene strengths
        strengths = np.array([gene.strength for gene in self.genes])
        strengths = strengths / (strengths.sum() + 1e-10)  # Normalize
        
        # Calculate entropy
        entropy = -np.sum(strengths * np.log(strengths + 1e-10))
        max_entropy = np.log(len(self.genes))
        
        diversity = entropy / max_entropy if max_entropy > 0 else 0.0
        return diversity


class DNAManager:
    """
    Manages Digital DNA operations including creation, mutation, and recombination.
    """
    
    # Knowledge domains (8D dimensions)
    KNOWLEDGE_DOMAINS = [
        "physics",
        "biology",
        "mathematics",
        "computer_science",
        "chemistry",
        "philosophy",
        "engineering",
        "cosmology"
    ]
    
    @staticmethod
    def create_initial_dna(scda_id: str) -> DigitalDNA:
        """
        Create initial DNA for a new SCDA.
        Genes start with low random strength.
        """
        dna = DigitalDNA()
        dna.generation = 0
        dna.lineage = [scda_id]
        
        # Create one gene for each knowledge domain
        for domain in DNAManager.KNOWLEDGE_DOMAINS:
            gene = Gene(
                domain=domain,
                strength=random.uniform(0.01, 0.1),
                mutations=0,
                origin="primordial",
                expression_level=0.1
            )
            dna.genes.append(gene)
        
        return dna
    
    @staticmethod
    def mutate_gene(gene: Gene) -> Gene:
        """
        Apply random mutation to a gene.
        """
        mutation_types = [
            "strength_increase",
            "strength_decrease",
            "expression_change",
            "domain_shift"  # Rare
        ]
        
        # Domain shift is rare
        weights = [0.4, 0.4, 0.19, 0.01]
        mutation_type = random.choices(mutation_types, weights=weights)[0]
        
        if mutation_type == "strength_increase":
            gene.strength += random.uniform(0.05, 0.15)
            gene.strength = min(gene.strength, 1.0)
        
        elif mutation_type == "strength_decrease":
            gene.strength -= random.uniform(0.05, 0.15)
            gene.strength = max(gene.strength, 0.0)
        
        elif mutation_type == "expression_change":
            gene.expression_level += random.uniform(-0.2, 0.2)
            gene.expression_level = np.clip(gene.expression_level, 0.0, 1.0)
        
        elif mutation_type == "domain_shift":
            # Very rare: gene changes domain
            new_domain = random.choice(DNAManager.KNOWLEDGE_DOMAINS)
            gene.domain = new_domain
        
        gene.mutations += 1
        gene.origin = "mutated"
        
        return gene
    
    @staticmethod
    def mutate_dna(dna: DigitalDNA, force: bool = False) -> DigitalDNA:
        """
        Apply mutations to DNA based on mutation rate.
        """
        for gene in dna.genes:
            # Check if mutation occurs
            if force or random.random() < dna.mutation_rate:
                DNAManager.mutate_gene(gene)
        
        return dna
    
    @staticmethod
    def recombine_dna(dna1: DigitalDNA, dna2: DigitalDNA, child_scda_id: str) -> DigitalDNA:
        """
        Genetic recombination: combine DNA from two SCDAs.
        Used in collaboration or "reproduction" scenarios.
        """
        new_dna = DigitalDNA()
        new_dna.generation = max(dna1.generation, dna2.generation) + 1
        new_dna.lineage = [child_scda_id] + dna1.lineage[:2] + dna2.lineage[:2]
        new_dna.mutation_rate = (dna1.mutation_rate + dna2.mutation_rate) / 2.0
        
        # Recombine genes (crossover)
        for i in range(len(DNAManager.KNOWLEDGE_DOMAINS)):
            domain = DNAManager.KNOWLEDGE_DOMAINS[i]
            
            # Randomly choose from parent 1 or parent 2
            if random.random() < 0.5:
                parent_gene = dna1.get_gene_by_domain(domain)
            else:
                parent_gene = dna2.get_gene_by_domain(domain)
            
            if parent_gene:
                # Create new gene based on parent
                new_gene = Gene(
                    domain=domain,
                    strength=parent_gene.strength,
                    mutations=parent_gene.mutations,
                    origin="inherited",
                    expression_level=parent_gene.expression_level
                )
                new_dna.genes.append(new_gene)
        
        # Record recombination
        new_dna.recombination_history.append({
            "timestamp": datetime.now().isoformat(),
            "parent1": dna1.lineage[0] if dna1.lineage else "unknown",
            "parent2": dna2.lineage[0] if dna2.lineage else "unknown",
            "generation": new_dna.generation
        })
        
        return new_dna
    
    @staticmethod
    def exchange_genes(dna1: DigitalDNA, dna2: DigitalDNA, domain: str) -> None:
        """
        Exchange genes between two DNAs (horizontal gene transfer).
        Simulates knowledge sharing in collaboration.
        """
        gene1 = dna1.get_gene_by_domain(domain)
        gene2 = dna2.get_gene_by_domain(domain)
        
        if gene1 and gene2:
            # Average the strengths
            avg_strength = (gene1.strength + gene2.strength) / 2.0
            
            # Both genes become stronger
            gene1.strength = min(1.0, avg_strength * 1.1)
            gene2.strength = min(1.0, avg_strength * 1.1)
            
            # Mark as exchanged
            gene1.origin = "exchanged"
            gene2.origin = "exchanged"
    
    @staticmethod
    def strengthen_gene(dna: DigitalDNA, domain: str, amount: float) -> None:
        """
        Strengthen a specific gene (learning).
        """
        gene = dna.get_gene_by_domain(domain)
        if gene:
            gene.strength += amount
            gene.strength = min(gene.strength, 1.0)
            gene.expression_level += amount * 0.5
            gene.expression_level = min(gene.expression_level, 1.0)
    
    @staticmethod
    def calculate_genetic_distance(dna1: DigitalDNA, dna2: DigitalDNA) -> float:
        """
        Calculate genetic distance between two DNAs.
        Returns value in [0, 1] where 0 = identical, 1 = completely different.
        """
        if not dna1.genes or not dna2.genes:
            return 1.0
        
        distances = []
        for domain in DNAManager.KNOWLEDGE_DOMAINS:
            gene1 = dna1.get_gene_by_domain(domain)
            gene2 = dna2.get_gene_by_domain(domain)
            
            if gene1 and gene2:
                # Euclidean distance in (strength, expression) space
                dist = np.sqrt(
                    (gene1.strength - gene2.strength) ** 2 +
                    (gene1.expression_level - gene2.expression_level) ** 2
                )
                distances.append(dist)
        
        if not distances:
            return 1.0
        
        avg_distance = np.mean(distances)
        # Normalize to [0, 1]
        normalized_distance = avg_distance / np.sqrt(2)
        
        return normalized_distance
    
    @staticmethod
    def visualize_dna(dna: DigitalDNA) -> str:
        """
        Create a text-based visualization of DNA.
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"Digital DNA - Generation {dna.generation}")
        lines.append("=" * 60)
        
        for gene in sorted(dna.genes, key=lambda g: g.strength, reverse=True):
            strength_bar = "█" * int(gene.strength * 20)
            expression_bar = "▓" * int(gene.expression_level * 20)
            
            lines.append(f"\n{gene.domain.upper()}")
            lines.append(f"  Strength:    {strength_bar} {gene.strength:.2f}")
            lines.append(f"  Expression:  {expression_bar} {gene.expression_level:.2f}")
            lines.append(f"  Mutations:   {gene.mutations}")
            lines.append(f"  Origin:      {gene.origin}")
        
        lines.append("\n" + "=" * 60)
        lines.append(f"Genetic Diversity: {dna.calculate_genetic_diversity():.3f}")
        lines.append(f"Mutation Rate: {dna.mutation_rate:.3f}")
        lines.append(f"Lineage: {' -> '.join(dna.lineage[:5])}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    print("🧬 Digital DNA System Demo\n")
    
    # Create initial DNA
    scda_id = "scda_001"
    dna = DNAManager.create_initial_dna(scda_id)
    
    print("Initial DNA:")
    print(DNAManager.visualize_dna(dna))
    
    # Simulate learning (strengthen genes)
    print("\n📚 Learning physics and mathematics...")
    DNAManager.strengthen_gene(dna, "physics", 0.3)
    DNAManager.strengthen_gene(dna, "mathematics", 0.4)
    
    print(DNAManager.visualize_dna(dna))
    
    # Simulate mutation
    print("\n🧪 Applying mutations...")
    DNAManager.mutate_dna(dna, force=True)
    
    print(DNAManager.visualize_dna(dna))
    
    # Create second DNA and recombine
    print("\n👥 Creating second SCDA and recombining DNA...")
    scda2_id = "scda_002"
    dna2 = DNAManager.create_initial_dna(scda2_id)
    DNAManager.strengthen_gene(dna2, "biology", 0.5)
    DNAManager.strengthen_gene(dna2, "chemistry", 0.3)
    
    child_id = "scda_003"
    child_dna = DNAManager.recombine_dna(dna, dna2, child_id)
    
    print("Child DNA:")
    print(DNAManager.visualize_dna(child_dna))
    
    # Calculate genetic distance
    distance = DNAManager.calculate_genetic_distance(dna, dna2)
    print(f"\n📊 Genetic distance between parent 1 and parent 2: {distance:.3f}")
