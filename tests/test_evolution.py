from mutera.core import Environment, Genome, Organism, Population, World
from mutera.evolution import Ecosystem, fitness, traits_from_genome, evolve
from mutera.ecology import compete, prey, symbiosis


def test_traits_are_deterministic():
    assert traits_from_genome(Genome("ACGT")) == traits_from_genome(Genome("ACGT"))


def test_fitness_is_non_negative():
    o = Organism("a", Genome("ACGT"))
    assert fitness(o, Environment()) >= 0


def test_evolution_creates_child():
    p = Population([Organism("a", Genome("ACGT")), Organism("b", Genome("TGCA"))])
    w = World(populations=[p])
    before = len(p.organisms)
    evolve(w, Ecosystem())
    assert len(p.organisms) == before + 1


def test_ecological_interactions():
    a = Organism("a", Genome("ACGT"), energy=100)
    b = Organism("b", Genome("TGCA"), energy=50)
    assert compete(a, b).success
    assert symbiosis(a, b).success
    assert prey(a, b).success
