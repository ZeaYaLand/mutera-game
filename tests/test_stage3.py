import random

import pytest

from mutera.stage3 import Stage3Config, Stage3Simulation


def make_sim(seed=1):
    config = Stage3Config(
        population_size=8,
        genome_length=12,
        reproduction_energy=0.0,
        mutation_rate=0.05,
        species_count=2,
        predator_pressure=0.0,
        disease_pressure=0.0,
        climate_event_chance=0.0,
    )
    return Stage3Simulation(config=config, rng=random.Random(seed))


def test_stage3_creates_species():
    sim = make_sim()
    sim.seed()
    assert len(sim.species) == 2
    assert sum(len(s.members) for s in sim.species.values()) == 8


def test_stage3_records_ecosystem_stats():
    sim = make_sim(2)
    sim.seed()
    stats = sim.step()
    assert stats.turn == 1
    assert stats.population >= 0
    assert stats.species >= 1
    assert 0.0 <= stats.diversity <= 1.0


def test_stage3_disease_can_affect_population():
    config = Stage3Config(
        population_size=6,
        genome_length=8,
        reproduction_energy=101.0,
        disease_pressure=1.0,
        climate_event_chance=0.0,
    )
    sim = Stage3Simulation(config=config, rng=random.Random(3))
    sim.seed()
    stats = sim.step()
    assert stats.disease_cases == 6


def test_stage3_climate_event_is_recorded():
    config = Stage3Config(
        population_size=6,
        genome_length=8,
        reproduction_energy=101.0,
        climate_event_chance=1.0,
        climate_damage=0.1,
    )
    sim = Stage3Simulation(config=config, rng=random.Random(4))
    sim.seed()
    stats = sim.step()
    assert stats.climate_event is True


def test_stage3_snapshot_contains_ecosystem_state():
    sim = make_sim(5)
    sim.seed()
    sim.step()
    snapshot = sim.ecosystem_snapshot()
    assert snapshot["turn"] == 1
    assert snapshot["species"]
    assert len(snapshot["history"]) == 1


def test_stage3_rejects_invalid_ecosystem_parameters():
    with pytest.raises(ValueError):
        Stage3Config(predator_pressure=2.0)
