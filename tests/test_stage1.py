import random

import pytest

from mutera.stage1 import Stage1Config, Stage1Simulation


def test_stage1_seeds_requested_population():
    sim = Stage1Simulation(
        Stage1Config(population_size=8, genome_length=12),
        rng=random.Random(1),
    )
    population = sim.seed()
    assert len(population) == 8
    assert all(len(o.genome.sequence) == 12 for o in population)
    assert len({o.id for o in population}) == 8


def test_stage1_inheritance_creates_next_generation():
    config = Stage1Config(
        population_size=6,
        genome_length=8,
        mutation_rate=0.0,
        reproduction_energy=0.0,
    )
    sim = Stage1Simulation(config, rng=random.Random(2))
    sim.seed(4)
    stats = sim.step()
    assert stats.births >= 1
    assert max(o.genome.generation for o in sim.organisms if o.alive) >= 1


def test_stage1_mutation_is_enabled_for_offspring():
    config = Stage1Config(
        population_size=4,
        genome_length=10,
        mutation_rate=1.0,
        reproduction_energy=0.0,
    )
    sim = Stage1Simulation(config, rng=random.Random(3))
    sim.seed(2)
    parent_sequences = {o.genome.sequence for o in sim.organisms}
    sim.step()
    children = [o for o in sim.organisms if o.genome.generation > 0]
    assert children
    assert all(o.genome.mutations for o in children)
    assert any(o.genome.sequence not in parent_sequences for o in children)


def test_stage1_age_limit_removes_old_organisms():
    config = Stage1Config(
        population_size=4,
        genome_length=8,
        max_age=1,
        reproduction_energy=101.0,
    )
    sim = Stage1Simulation(config, rng=random.Random(4))
    sim.seed()
    stats = sim.step()
    assert stats.population == 0
    assert stats.deaths == 4


def test_stage1_environment_regenerates_resources():
    config = Stage1Config(
        population_size=4,
        genome_length=8,
        reproduction_energy=101.0,
        food_regeneration=5.0,
        water_regeneration=3.0,
    )
    sim = Stage1Simulation(config, rng=random.Random(5))
    sim.environment.food = 90.0
    sim.environment.water = 80.0
    sim.seed()
    sim.step()
    assert sim.environment.food <= 95.0
    assert sim.environment.water <= 83.0
    assert sim.environment.food >= 90.0
    assert sim.environment.water >= 80.0


def test_stage1_fitness_prefers_healthy_energetic_survivors():
    sim = Stage1Simulation(Stage1Config(population_size=4), rng=random.Random(6))
    sim.seed()
    weak, strong = sim.organisms[:2]
    weak.energy, weak.health = 20.0, 30.0
    strong.energy, strong.health = 100.0, 100.0
    assert sim.fitness(strong) > sim.fitness(weak)


def test_stage1_selection_pressure_prefers_top_survivors():
    config = Stage1Config(
        population_size=6,
        selection_fraction=0.5,
        reproduction_energy=0.0,
    )
    sim = Stage1Simulation(config, rng=random.Random(7))
    sim.seed()
    sim.organisms[0].energy = 100.0
    sim.organisms[0].health = 100.0
    for organism in sim.organisms[1:]:
        organism.energy = 1.0
        organism.health = 1.0
    parents = sim._eligible_parents()
    assert parents[0] is sim.organisms[0]


def test_stage1_snapshot_contains_population_state():
    sim = Stage1Simulation(Stage1Config(population_size=5), rng=random.Random(8))
    sim.seed()
    sim.step()
    snapshot = sim.snapshot()
    assert snapshot["turn"] == 1
    assert snapshot["population"] >= 0
    assert snapshot["organisms"]
    assert {"id", "generation", "age", "energy", "health", "genome", "mutations"} <= set(snapshot["organisms"][0])


def test_stage1_run_rejects_negative_turns():
    sim = Stage1Simulation(rng=random.Random(9))
    with pytest.raises(ValueError):
        sim.run(-1)
