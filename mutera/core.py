"""Core simulation models for Mutera."""
from dataclasses import dataclass, field
from typing import Dict, List
import random

BASES = "ACGT"

@dataclass
class Genome:
    sequence: str
    generation: int = 0
    mutations: List[int] = field(default_factory=list)

    def __post_init__(self):
        self.sequence = self.sequence.upper()
        if not self.sequence or any(x not in BASES for x in self.sequence):
            raise ValueError("Invalid genome")

    def mutate(self, rate=0.01, rng=None):
        rng = rng or random.Random()
        chars, changed = list(self.sequence), []
        for i, old in enumerate(chars):
            if rng.random() < rate:
                chars[i] = rng.choice([x for x in BASES if x != old])
                changed.append(i)
        return Genome(''.join(chars), self.generation + 1, changed)

    @classmethod
    def random(cls, length=16, rng=None):
        rng = rng or random.Random()
        return cls(''.join(rng.choice(BASES) for _ in range(length)))

@dataclass
class Environment:
    name: str = "Origin"
    temperature: float = 20.0
    food: float = 100.0
    water: float = 100.0
    danger: float = 0.1
    turn: int = 0

@dataclass
class Organism:
    id: str
    genome: Genome
    energy: float = 100.0
    health: float = 100.0
    age: int = 0
    alive: bool = True
    traits: Dict[str, float] = field(default_factory=dict)

    def tick(self, env: Environment):
        if not self.alive: return
        self.age += 1
        self.energy -= 2.0 + env.danger * 3
        if self.energy <= 0 or self.health <= 0:
            self.alive = False

    def reproduce(self, partner, child_id, rng=None, mutation_rate=0.05):
        rng = rng or random.Random()
        if not self.alive or not partner.alive:
            raise ValueError("Both parents must be alive")
        if len(self.genome.sequence) != len(partner.genome.sequence):
            raise ValueError("Parent genomes must have equal length")
        cut = rng.randrange(1, len(self.genome.sequence))
        seq = self.genome.sequence[:cut] + partner.genome.sequence[cut:]
        generation = max(self.genome.generation, partner.genome.generation) + 1
        # Reproduction advances the lineage by exactly one generation.
        # Mutation changes the sequence but does not create an extra generation.
        mutated = Genome(seq, generation).mutate(mutation_rate, rng)
        genome = Genome(mutated.sequence, generation, mutated.mutations)
        return Organism(child_id, genome, energy=50.0, health=100.0)

@dataclass
class Population:
    organisms: List[Organism] = field(default_factory=list)

    def living(self):
        return [o for o in self.organisms if o.alive]

    def tick(self, env):
        env.turn += 1
        for organism in self.organisms:
            organism.tick(env)
        env.food = max(0.0, env.food - len(self.living()) * 0.5)
        env.water = max(0.0, env.water - len(self.living()) * 0.3)

@dataclass
class World:
    environment: Environment = field(default_factory=Environment)
    populations: List[Population] = field(default_factory=list)

    def step(self):
        for population in self.populations:
            population.tick(self.environment)

    def statistics(self):
        organisms = [o for p in self.populations for o in p.organisms]
        living = [o for o in organisms if o.alive]
        return {"turn": self.environment.turn, "total": len(organisms), "living": len(living),
                "generations": max((o.genome.generation for o in organisms), default=0)}
