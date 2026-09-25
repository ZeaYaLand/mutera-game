"""Predation, competition, symbiosis and world events."""
from dataclasses import dataclass
import random

from .core import Organism, World

@dataclass
class InteractionResult:
    kind: str
    success: bool
    message: str


def compete(a: Organism, b: Organism) -> InteractionResult:
    if not a.alive or not b.alive:
        return InteractionResult("competition", False, "inactive organisms")
    if a.energy >= b.energy:
        b.energy = max(0, b.energy - 10)
        return InteractionResult("competition", True, f"{a.id} outcompeted {b.id}")
    a.energy = max(0, a.energy - 10)
    return InteractionResult("competition", True, f"{b.id} outcompeted {a.id}")


def prey(predator: Organism, target: Organism) -> InteractionResult:
    if not predator.alive or not target.alive:
        return InteractionResult("predation", False, "inactive organisms")
    damage = max(5.0, predator.traits.get("strength", 1.0) * 10)
    target.health -= damage
    predator.energy += 15
    if target.health <= 0:
        target.alive = False
    return InteractionResult("predation", True, f"{predator.id} attacked {target.id}")


def symbiosis(a: Organism, b: Organism) -> InteractionResult:
    if not a.alive or not b.alive:
        return InteractionResult("symbiosis", False, "inactive organisms")
    a.health = min(100, a.health + 3)
    b.health = min(100, b.health + 3)
    return InteractionResult("symbiosis", True, f"{a.id} and {b.id} benefited")


def random_event(world: World, rng=None) -> str:
    rng = rng or random.Random()
    events = ["meteor shower", "resource bloom", "cold wave", "heat wave", "mutation storm"]
    event = rng.choice(events)
    if event == "resource bloom":
        world.environment.food += 30
        world.environment.water += 20
    elif event == "cold wave":
        world.environment.temperature -= 8
    elif event == "heat wave":
        world.environment.temperature += 8
    elif event == "meteor shower":
        world.environment.danger = min(1, world.environment.danger + 0.2)
    return event
