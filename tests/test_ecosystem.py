from mutera.core import Genome, Organism, Population, World
from mutera.ecosystem import ClimateCycle, Disease, Migration, infect, extinction_check
from mutera.engine import GameEngine


def test_migration_stays_on_map():
    m = Migration()
    p = m.move(Organism("a", Genome("ACGT")), 5, 5)
    assert 0 <= p[0] < 5 and 0 <= p[1] < 5


def test_disease_can_kill():
    o = Organism("a", Genome("ACGT"), health=2)
    assert infect(o, Disease("plague", damage=5, spread_chance=1))
    assert not o.alive
    assert extinction_check([o])


def test_engine_advances_game():
    world = World(populations=[Population([Organism("a", Genome("ACGT")), Organism("b", Genome("TGCA"))])])
    engine = GameEngine(world)
    snapshot = engine.tick()
    assert snapshot["world"]["turn"] == 1
    assert snapshot["progress"]["turns"] == 1
