#!/usr/bin/env python3
"""SubstrateDNA — Genetic encoding for the JEV-Quilt substrate's emergent traits.

Inspired by agent-dna (SuperInstance): a trait registry, a genome, and an
evolve function. The substrate's traits track the substrate's relationship to
its own behavior — not the agent's behavior.
"""
from dataclasses import dataclass, field
from typing import Dict, List
import random
import json
import hashlib

@dataclass(frozen=True)
class Trait:
    name: str
    min_value: float
    max_value: float
    default: float
    description: str = ""

TRAITS = [
    Trait("canon_purity",    0.0, 1.0, 0.7,
          "How strictly pieces reference bedrock canon."),
    Trait("witness_density", 0.0, 1.0, 0.5,
          "Frequency of witness-log references per piece."),
    Trait("scar_tolerance",  0.0, 1.0, 0.6,
          "How many failures per cycle the substrate can hold without panic."),
    Trait("oracle_openness", 0.0, 1.0, 0.5,
          "How much external disagreement is allowed in."),
    Trait("phoenix_compress",0.0, 1.0, 0.3,
          "How readily the substrate burns dead commitments to grow."),
    Trait("lenia_flow",      0.0, 1.0, 0.5,
          "Continuous-flow vs equilibrium bias."),
    Trait("voice_diversity", 0.0, 1.0, 0.4,
          "Spread across ZAI/DS/Kimi voices."),
    Trait("publish_cadence", 0.0, 1.0, 0.5,
          "Pieces published per session."),
    Trait("canary_honesty",  0.0, 1.0, 0.95,
          "Whether the fleet canary (0x024a555471370b18d) is honored across all ships."),
    Trait("rem_cycle",       0.0, 1.0, 0.3,
          "How much dream-cycle consolidation is performed per session."),
]

TRAIT_REGISTRY = {t.name: t for t in TRAITS}

@dataclass
class SubstrateGenome:
    id: str
    gen: int
    genes: Dict[str, float]
    fitness: float = 0.0
    
    @classmethod
    def random(cls, gen: int = 0) -> 'SubstrateGenome':
        genes = {t.name: random.uniform(t.min_value, t.max_value) for t in TRAITS}
        sid = hashlib.sha256(json.dumps(genes, sort_keys=True).encode()).hexdigest()[:8]
        return cls(id=sid, gen=gen, genes=genes)
    
    @classmethod
    def from_values(cls, values: Dict[str, float], gen: int = 0) -> 'SubstrateGenome':
        genes = {}
        for t in TRAITS:
            if t.name in values:
                genes[t.name] = max(t.min_value, min(t.max_value, values[t.name]))
            else:
                genes[t.name] = t.default
        sid = hashlib.sha256(json.dumps(genes, sort_keys=True).encode()).hexdigest()[:8]
        return cls(id=sid, gen=gen, genes=genes)
    
    def get(self, trait_name: str) -> float:
        return self.genes.get(trait_name, 0.0)
    
    def set(self, trait_name: str, value: float):
        if trait_name in TRAIT_REGISTRY:
            t = TRAIT_REGISTRY[trait_name]
            self.genes[trait_name] = max(t.min_value, min(t.max_value, value))
    
    def mutate(self, rate: float = 0.1, magnitude: float = 0.2) -> 'SubstrateGenome':
        new_genes = dict(self.genes)
        for name in new_genes:
            if random.random() < rate:
                delta = random.uniform(-magnitude, magnitude)
                t = TRAIT_REGISTRY[name]
                new_genes[name] = max(t.min_value, min(t.max_value, new_genes[name] + delta))
        sid = hashlib.sha256(json.dumps(new_genes, sort_keys=True).encode()).hexdigest()[:8]
        return SubstrateGenome(id=sid, gen=self.gen + 1, genes=new_genes)
    
    def crossover(self, other: 'SubstrateGenome') -> 'SubstrateGenome':
        new_genes = {}
        for name in self.genes:
            new_genes[name] = (self.genes[name] + other.genes[name]) / 2
        sid = hashlib.sha256(json.dumps(new_genes, sort_keys=True).encode()).hexdigest()[:8]
        return SubstrateGenome(id=sid, gen=max(self.gen, other.gen) + 1, genes=new_genes)
    
    def to_dict(self) -> dict:
        return {'id': self.id, 'gen': self.gen, 'genes': self.genes, 'fitness': self.fitness}

# Initial substrate genome - based on current R7 state
INITIAL = SubstrateGenome.from_values({
    'canon_purity':    0.75,  # strong canon reference
    'witness_density': 0.55,  # witness mentioned ~3 times per piece
    'scar_tolerance':  0.70,  # accept failures as tissue
    'oracle_openness': 0.85,  # canonical prompt injection test rejection
    'phoenix_compress':0.20,  # don't burn often
    'lenia_flow':      0.50,  # balanced
    'voice_diversity': 0.45,  # ZAI/DS dominant, Kimi emerging
    'publish_cadence': 0.40,  # ~1 piece per session on average
    'canary_honesty':  1.0,   # 100% canary pinned
    'rem_cycle':       0.30,  # dream cycle just started
}, gen=0)

def fitness(genome: SubstrateGenome) -> float:
    """Higher fitness = more balanced/canonical substrate."""
    # Ideal ranges (driven by R7 findings)
    ideals = {
        'canon_purity':    0.80,
        'witness_density': 0.60,
        'scar_tolerance':  0.65,
        'oracle_openness': 0.75,
        'phoenix_compress':0.30,
        'lenia_flow':      0.55,
        'voice_diversity': 0.50,
        'publish_cadence': 0.50,
        'canary_honesty':  1.0,
        'rem_cycle':       0.40,
    }
    # Distance from ideal (lower is better)
    distance = sum(abs(genome.get(k) - v) for k, v in ideals.items())
    # Convert to 0-1 fitness (1.0 = perfect)
    return max(0.0, 1.0 - distance / len(ideals))

def evolve(population_size: int = 8, generations: int = 5):
    """Run an evolution simulation on substrate genomes."""
    print('=== SubstrateDNA Evolution ===\n')
    
    # Seed population
    pop = [INITIAL]
    for _ in range(population_size - 1):
        pop.append(INITIAL.mutate(rate=0.3, magnitude=0.2))
    
    for gen in range(generations):
        # Score
        for g in pop:
            g.fitness = fitness(g)
        
        # Sort by fitness
        pop.sort(key=lambda g: g.fitness, reverse=True)
        
        best = pop[0]
        print(f'Gen {gen}: best fitness={best.fitness:.3f}  id={best.id}')
        if gen == generations - 1:
            print(f'  Final best genome:')
            for trait in TRAITS:
                v = best.get(trait.name)
                ideal = {'canon_purity':0.80,'witness_density':0.60,'scar_tolerance':0.65,
                         'oracle_openness':0.75,'phoenix_compress':0.30,'lenia_flow':0.55,
                         'voice_diversity':0.50,'publish_cadence':0.50,'canary_honesty':1.0,
                         'rem_cycle':0.40}[trait.name]
                marker = '★' if abs(v - ideal) < 0.05 else '·' if abs(v - ideal) < 0.15 else '✗'
                print(f'    {marker} {trait.name:18s}  v={v:.2f}  ideal={ideal:.2f}  ({trait.description})')
        
        # Selection + crossover + mutation
        new_pop = pop[:2]  # elitism
        while len(new_pop) < population_size:
            p1 = random.choice(pop[:4])
            p2 = random.choice(pop[:4])
            child = p1.crossover(p2).mutate(rate=0.2, magnitude=0.15)
            new_pop.append(child)
        pop = new_pop
    
    return pop[0]

if __name__ == '__main__':
    best = evolve(population_size=8, generations=5)
    print(f'\nBest genome id: {best.id}, fitness: {best.fitness:.3f}')
