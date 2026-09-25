"""Stage 1 population, inheritance, environment and natural selection.

The Stage 0 core remains backward compatible. This module adds a deterministic,
small-population simulation layer that can be exercised without a database.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Dict, List, Optional, Sequence

from .core import Environment, Genome, Organism


@dataclass(frozen=True)
class Stage1Config:
    """Rules controlling a Stage 1 population."""

    population_size: int = 20
    genome_length: int = 16
    mutation_rate: float = 0.02
    max_age: int = 50
    initial_energy: float = 100.0
    initial_health: float = 100.0
    reproduction_energy: float = 65.0
    birth_energy: float = 50.0
    selection_fraction: float = 0.5
    food_regeneration: float = 2.0
    water_regeneration: float = 1.0

    def __post_init__(self) -> None:
        if self.population_size < 2:
            raise ValueError("population_size must be at least 2")
        if self.genome_length < 2:
            raise ValueError("genome_length must be at least 2")
        if not 0 <= self.mutation_rate <= 1:
            raise ValueError("mutation_rate must be between 0 and 1")
        if self.max_age < 1:
            raise ValueError("max_age must be positive")
        if not 0 < self.selection_fraction <= 1:
            raise ValueError("selection_fraction must be in (0, 1]")


@dataclass
class PopulationStats:
    """Observable state of a Stage 1 simulation after a turn."""

    turn: int
    population: int
    births: int
    deaths: int
    generation: int
    average_age: float
    average_energy: float
    average_fitness: float


@dataclass
class Stage1Simulation:
    """A lightweight population simulator for Mutera Stage 1."""

    config: Stage1Config = field(default_factory=Stage1Config)
    environment: Environment = field(default_factory=Environment)
    rng: random.Random = field(default_factory=random.Random)
    organisms: List[Organism] = field(default_factory=list)
    turn: int = 0
    next_id: int = 0

    def seed(self, count: Optional[int] = None) -> List[Organism]:
        """Create the initial population and return it."""
        count = self.config.population_size if count is None else count
        if count < 2:
            raise ValueError("count must be at least 2")
        self.organisms = []
        self.next_id = 0
        for _ in range(count):
            self.organisms.append(self._new_organism(Genome.random(self.config.genome_length, self.rng)))
        return list(self.organisms)

    def _new_organism(self, genome: Genome) -> Organism:
        organism = Organism(
            id=f"org-{self.next_id}",
            genome=genome,
            energy=self.config.initial_energy,
            health=self.config.initial_health,
        )
        self.next_id += 1
        return organism

    def fitness(self, organism: Organism) -> float:
        """Return a non-negative fitness value used by natural selection."""
        if not organism.alive:
            return 0.0
        age_factor = max(0.0, 1.0 - organism.age / self.config.max_age)
        resource_factor = max(0.0, min(1.0, organism.energy / self.config.initial_energy))
        health_factor = max(0.0, min(1.0, organism.health / self.config.initial_health))
        return 0.5 * resource_factor + 0.4 * health_factor + 0.1 * age_factor

    def _eligible_parents(self) -> List[Organism]:
        living = [o for o in self.organisms if o.alive and o.energy >= self.config.reproduction_energy]
        living.sort(key=self.fitness, reverse=True)
        keep = max(2, int(len(living) * self.config.selection_fraction))
        return living[:keep]

    def _reproduce(self, parents: Sequence[Organism]) -> Optional[Organism]:
        if len(parents) < 2:
            return None
        parent_a, parent_b = self.rng.sample(list(parents), 2)
        child = parent_a.reproduce(
            parent_b,
            child_id=f"org-{self.next_id}",
            rng=self.rng,
            mutation_rate=self.config.mutation_rate,
        )
        self.next_id += 1
        child.energy = self.config.birth_energy
        return child

    def step(self) -> PopulationStats:
        """Advance one generation turn and apply selection/reproduction."""
        if not self.organisms:
            self.seed()

        before = sum(1 for o in self.organisms if o.alive)
        self.environment.turn += 1
        self.turn += 1

        # Environment supplies recover between turns, then living organisms
        # consume resources and pay the normal Stage 0 energy cost.
        self.environment.food += self.config.food_regeneration
        self.environment.water += self.config.water_regeneration
        self.environment.food = min(100.0, self.environment.food)
        self.environment.water = min(100.0, self.environment.water)
        for organism in self.organisms:
            organism.tick(self.environment)
            if organism.age >= self.config.max_age:
                organism.alive = False

        parents = self._eligible_parents()
        births = 0
        capacity = max(0, self.config.population_size - sum(o.alive for o in self.organisms))
        for _ in range(capacity):
            # Reproduction pressure follows the best adapted survivors, while
            # still allowing different pairs to contribute descendants.
            if len(parents) < 2 or self.rng.random() > 0.5:
                break
            child = self._reproduce(parents)
            if child is not None:
                self.organisms.append(child)
                births += 1

        deaths = max(0, before - sum(1 for o in self.organisms if o.alive))
        living = [o for o in self.organisms if o.alive]
        generation = max((o.genome.generation for o in living), default=0)
        average_age = sum(o.age for o in living) / len(living) if living else 0.0
        average_energy = sum(o.energy for o in living) / len(living) if living else 0.0
        average_fitness = sum(self.fitness(o) for o in living) / len(living) if living else 0.0
        return PopulationStats(
            turn=self.turn,
            population=len(living),
            births=births,
            deaths=deaths,
            generation=generation,
            average_age=average_age,
            average_energy=average_energy,
            average_fitness=average_fitness,
        )

    def run(self, turns: int) -> List[PopulationStats]:
        if turns < 0:
            raise ValueError("turns cannot be negative")
        if not self.organisms:
            self.seed()
        return [self.step() for _ in range(turns)]

    def snapshot(self) -> Dict[str, object]:
        living = [o for o in self.organisms if o.alive]
        return {
            "turn": self.turn,
            "population": len(living),
            "total_created": len(self.organisms),
            "generation": max((o.genome.generation for o in living), default=0),
            "food": self.environment.food,
            "water": self.environment.water,
            "organisms": [
                {
                    "id": o.id,
                    "generation": o.genome.generation,
                    "age": o.age,
                    "energy": o.energy,
                    "health": o.health,
                    "genome": o.genome.sequence,
                    "mutations": list(o.genome.mutations),
                }
                for o in living
            ],
        }
