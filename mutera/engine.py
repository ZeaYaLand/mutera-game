"""Single entry point for advancing a complete Mutera world."""
from dataclasses import dataclass, field

from .core import World
from .ecosystem import ClimateCycle, FoodWeb, Migration
from .evolution import Ecosystem, evolve
from .progression import Progress

@dataclass
class GameEngine:
    world: World
    ecosystem: Ecosystem = field(default_factory=Ecosystem)
    food_web: FoodWeb = field(default_factory=FoodWeb)
    climate: ClimateCycle = field(default_factory=ClimateCycle)
    migration: Migration = field(default_factory=Migration)
    progress: Progress = field(default_factory=Progress)

    def tick(self):
        self.world.step()
        self.climate.advance(self.world)
        evolve(self.world, self.ecosystem)
        self.progress.register_turn()
        self.progress.research.earn(1)
        return self.snapshot()

    def snapshot(self):
        return {
            "world": self.world.statistics(),
            "progress": self.progress.stats(),
            "events": list(self.ecosystem.events[-10:]),
            "temperature": self.world.environment.temperature,
        }
