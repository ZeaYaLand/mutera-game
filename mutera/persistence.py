"""JSON persistence for a Mutera world."""
import json
from dataclasses import asdict
from pathlib import Path

from .core import Environment, Genome, Organism, Population, World


def save_world(world: World, path):
    data = asdict(world)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_world(path) -> World:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    env = Environment(**data["environment"])
    populations = []
    for p in data["populations"]:
        organisms = []
        for item in p["organisms"]:
            item["genome"] = Genome(**item["genome"])
            organisms.append(Organism(**item))
        populations.append(Population(organisms))
    return World(env, populations)
