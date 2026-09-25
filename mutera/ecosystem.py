"""Food webs, migration, diseases, extinction and climate cycles."""
from dataclasses import dataclass, field
import random
from typing import Dict, List

from .core import Organism, World

@dataclass
class FoodWeb:
    prey_by_predator: Dict[str, List[str]] = field(default_factory=dict)

    def add_link(self, predator: str, prey: str):
        self.prey_by_predator.setdefault(predator, [])
        if prey not in self.prey_by_predator[predator]:
            self.prey_by_predator[predator].append(prey)

@dataclass
class ClimateCycle:
    phase: int = 0
    period: int = 20

    def advance(self, world: World):
        self.phase = (self.phase + 1) % self.period
        world.environment.temperature += 2.0 if self.phase < self.period / 2 else -2.0
        world.environment.temperature = max(-30, min(50, world.environment.temperature))

@dataclass
class Migration:
    positions: Dict[str, tuple] = field(default_factory=dict)

    def move(self, organism: Organism, width: int, height: int, rng=None):
        rng = rng or random.Random()
        x, y = self.positions.get(organism.id, (width // 2, height // 2))
        x = max(0, min(width - 1, x + rng.choice((-1, 0, 1))))
        y = max(0, min(height - 1, y + rng.choice((-1, 0, 1))))
        self.positions[organism.id] = (x, y)
        return self.positions[organism.id]

@dataclass
class Disease:
    name: str
    damage: float = 5.0
    spread_chance: float = 0.15


def infect(organism: Organism, disease: Disease, rng=None) -> bool:
    rng = rng or random.Random()
    if rng.random() < disease.spread_chance:
        organism.health -= disease.damage
        if organism.health <= 0:
            organism.alive = False
        return True
    return False


def extinction_check(organisms: List[Organism]) -> bool:
    return not any(o.alive for o in organisms)
