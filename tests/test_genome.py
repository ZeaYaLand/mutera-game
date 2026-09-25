import random

import pytest

from src.genome import Genome


def test_random_genome_has_requested_length():
    genome = Genome.random(20, random.Random(1))
    assert len(genome.sequence) == 20
    assert set(genome.sequence) <= set("ACGT")


def test_mutation_creates_next_generation():
    genome = Genome("AAAAAAAAAA")
    child = genome.mutate(1.0, random.Random(1))
    assert child.generation == 1
    assert len(child.mutations) == 10
    assert child.sequence != genome.sequence


def test_invalid_sequence_is_rejected():
    with pytest.raises(ValueError):
        Genome("ABCX")
