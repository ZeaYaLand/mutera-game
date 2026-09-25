"""Stage 2 evolutionary simulation: traits, selection, environment and generations."""
from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Dict, List

from .stage1 import Stage1Config, Stage1Simulation, PopulationStats


@dataclass(frozen=True)
class TraitWeights:
    foraging: float = 0.34
    resilience: float = 0.33
    reproduction: float = 0.33


@dataclass(frozen=True)
class Stage2Config(Stage1Config):
    resource_pressure: float = 0.04
    climate_pressure: float = 0.02
    selection_strength: float = 0.5
    trait_weights: TraitWeights = field(default_factory=TraitWeights)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.resource_pressure < 0 or self.climate_pressure < 0:
            raise ValueError("environment pressures cannot be negative")
        if not 0 <= self.selection_strength <= 1:
            raise ValueError("selection_strength must be between 0 and 1")


@dataclass
class EvolutionStats(PopulationStats):
    mean_fitness: float = 0.0
    diversity: float = 0.0
    selection_cutoff: float = 0.0


@dataclass
class Stage2Simulation(Stage1Simulation):
    config: Stage2Config = field(default_factory=Stage2Config)
    generation_history: List[EvolutionStats] = field(default_factory=list)

    def trait_values(self, organism) -> Dict[str, float]:
        seq = organism.genome.sequence
        if not seq:
            return {"foraging": 0.0, "resilience": 0.0, "reproduction": 0.0}
        values = [int(ch) for ch in seq]
        n = len(values)
        thirds = max(1, n // 3)
        return {
            "foraging": sum(values[:thirds]) / (9 * len(values[:thirds])),
            "resilience": sum(values[thirds:2 * thirds]) / (9 * len(values[thirds:2 * thirds] or [1])),
            "reproduction": sum(values[2 * thirds:]) / (9 * len(values[2 * thirds:] or [1])),
        }

    def adaptive_fitness(self, organism) -> float:
        base = self.fitness(organism)
        traits = self.trait_values(organism)
        w = self.config.trait_weights
        trait_score = (
            traits["foraging"] * w.foraging
            + traits["resilience"] * w.resilience
            + traits["reproduction"] * w.reproduction
        )
        pressure = self.config.resource_pressure * (1 - traits["foraging"])
        climate = self.config.climate_pressure * (1 - traits["resilience"])
        return max(0.0, base * (1 - pressure - climate) + trait_score)

    def _eligible_parents(self):
        living = [o for o in self.organisms if o.alive and o.energy >= self.config.reproduction_energy]
        living.sort(key=self.adaptive_fitness, reverse=True)
        keep = max(2, int(len(living) * (1 - self.config.selection_strength)))
        return living[:keep]

    def diversity(self) -> float:
        living = [o.genome.sequence for o in self.organisms if o.alive]
        if not living:
            return 0.0
        unique = len(set(living))
        return unique / len(living)

    def step(self) -> EvolutionStats:
        stats = super().step()
        living = [o for o in self.organisms if o.alive]
        mean_fitness = sum(self.adaptive_fitness(o) for o in living) / len(living) if living else 0.0
        cutoff = min((self.adaptive_fitness(o) for o in self._eligible_parents()), default=0.0)
        result = EvolutionStats(
            **stats.__dict__,
            mean_fitness=mean_fitness,
            diversity=self.diversity(),
            selection_cutoff=cutoff,
        )
        self.generation_history.append(result)
        return result

    def run_generations(self, generations: int) -> List[EvolutionStats]:
        if generations < 0:
            raise ValueError("generations cannot be negative")
        if not self.organisms:
            self.seed()
        return [self.step() for _ in range(generations)]

    def evolution_tree(self) -> Dict[str, object]:
        return {
            "generations": len(self.generation_history),
            "history": [s.__dict__.copy() for s in self.generation_history],
            "organisms": [
                {"id": o.id, "generation": o.genome.generation, "genome": o.genome.sequence}
                for o in self.organisms
            ],
        }
