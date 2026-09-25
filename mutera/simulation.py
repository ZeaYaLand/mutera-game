"""High-level world simulation helpers."""
from .core import Genome, Organism, Population, World


def create_world(size=10):
    organisms = [Organism(f"org-{i+1}", Genome.random(16)) for i in range(size)]
    return World(populations=[Population(organisms)])


def run(world, turns=1):
    for _ in range(turns):
        world.step()
    return world.statistics()
