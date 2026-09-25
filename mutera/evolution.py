"""Evolution, traits, selection and ecological interactions."""
from dataclasses import dataclass, field
from typing import Dict, List
import random

from .core import Genome, Organism, Population, World

TRAITS = ("speed", "strength", "vision", "metabolism", "resilience")


def traits_from_genome(genome: Genome) -> Dict[str, float]:
    values = {name: 0.0 for name in TRAITS}
    for i, base in enumerate(genome.sequence):
        values[TRAITS[i % len(TRAITS)]] += ("ACGT".index(base) + 1) / 4
    scale = max(1, len(genome.sequence) / len(TRAITS))
    return {k: round(v / scale, 3) for k, v in values.items()}


def fitness(organism: Organism, environment) -> float:
    t = traits_from_genome(organism.genome)
    temperature_bonus = max(0.0, 1.0 - abs(environment.temperature - 20.0) / 40.0)
    resource_bonus = (environment.food + environment.water) / 200.0
    survival = organism.health / 100.0
    return round((t["resilience"] * 0.3 + t["metabolism"] * 0.2 + temperature_bonus * 0.2 + resource_bonus * 0.3) * survival, 4)


def select(population: Population, environment, fraction: float = 0.5) -> List[Organism]:
    living = population.living()
    count = max(1, int(len(living) * fraction)) if living else 0
    return sorted(living, key=lambda o: fitness(o, environment), reverse=True)[:count]


def reproduce_pair(a: Organism, b: Organism, child_id: str, mutation_rate=0.02, rng=None) -> Organism:
    rng = rng or random.Random()
    child = a.reproduce(b, child_id, rng)
    child.genome = child.genome.mutate(mutation_rate, rng)
    child.traits = traits_from_genome(child.genome)
    return child

@dataclass
class Species:
    name: str
    organism_ids: List[str] = field(default_factory=list)
    generation: int = 0

@dataclass
class Ecosystem:
    species: List[Species] = field(default_factory=list)
    events: List[str] = field(default_factory=list)

    def record(self, event: str):
        self.events.append(event)
        self.events = self.events[-100:]


def evolve(world: World, ecosystem: Ecosystem, rng=None):
    rng = rng or random.Random()
    for population in world.populations:
        survivors = select(population, world.environment)
        if len(survivors) >= 2:
            parent_a, parent_b = survivors[0], survivors[1]
            child = reproduce_pair(parent_a, parent_b, f"gen-{world.environment.turn}-{len(population.organisms)+1}", rng=rng)
            population.organisms.append(child)
            ecosystem.record(f"Generation {child.genome.generation}: {child.id} born")
    return world.statistics()
