from mutera.core import Environment, Genome, Organism, Population, World


def test_genome_mutation_is_valid():
    genome = Genome("ACGTACGT")
    mutated = genome.mutate(1.0)
    assert len(mutated.sequence) == 8
    assert all(base in "ACGT" for base in mutated.sequence)
    assert mutated.generation == 1


def test_organism_can_age_and_die():
    organism = Organism("a", Genome("ACGT"), energy=1)
    organism.tick(Environment(danger=0))
    assert not organism.alive


def test_world_statistics():
    world = World(populations=[Population([Organism("a", Genome("ACGT"))])])
    world.step()
    stats = world.statistics()
    assert stats["turn"] == 1
    assert stats["total"] == 1
