"""Organism model built on top of a genome."""

from dataclasses import dataclass

from .genome import Genome


@dataclass
class Organism:
    """A minimal simulated lifeform for Stage 0."""

    genome: Genome
    energy: float = 100.0
    age: int = 0

    def tick(self, energy_cost: float = 1.0) -> None:
        if energy_cost < 0:
            raise ValueError("energy_cost cannot be negative")
        self.age += 1
        self.energy = max(0.0, self.energy - energy_cost)

    @property
    def alive(self) -> bool:
        return self.energy > 0

    def reproduce(self, mutation_probability: float = 0.01) -> "Organism":
        return Organism(self.genome.mutate(mutation_probability))
