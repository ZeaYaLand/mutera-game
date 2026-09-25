import random

import pytest

from mutera.stage2 import Stage2Config, Stage2Simulation


def make_sim(seed=1):
    config = Stage2Config(
        population_size=8,
        genome_length=12,
        reproduction_energy=0.0,
        mutation_rate=0.1,
    )
    return Stage2Simulation(config=config, rng=random.Random(seed))


def test_stage2_produces_evolution_stats():
    sim = make_sim()
    sim.seed()
    stats = sim.step()
    assert stats.population > 0
    assert 0.0 <= stats.mean_fitness <= 2.0
    assert 0.0 <= stats.diversity <= 1.0


def test_stage2_traits_are_bounded():
    sim = make_sim(2)
    sim.seed()
    for organism in sim.organisms:
        traits = sim.trait_values(organism)
        assert all(0.0 <= value <= 1.0 for value in traits.values())


def test_stage2_selection_cutoff_is_non_negative():
    sim = make_sim(3)
    sim.seed()
    stats = sim.step()
    assert stats.selection_cutoff >= 0.0


def test_stage2_history_tracks_generations():
    sim = make_sim(4)
    sim.seed()
    history = sim.run_generations(3)
    assert len(history) == 3
    assert len(sim.generation_history) == 3
    assert [x.turn for x in history] == [1, 2, 3]


def test_stage2_evolution_tree_contains_history_and_organisms():
    sim = make_sim(5)
    sim.seed()
    sim.run_generations(2)
    tree = sim.evolution_tree()
    assert tree["generations"] == 2
    assert len(tree["history"]) == 2
    assert tree["organisms"]


def test_stage2_rejects_invalid_pressure():
    with pytest.raises(ValueError):
        Stage2Config(resource_pressure=-0.1)
