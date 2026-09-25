"""Core genome model for Mutera.

Stage 0: a dependency-free foundation for organisms, mutation and evolution.
"""

from dataclasses import dataclass, field
import random
from typing import List, Optional

BASES = ("A", "C", "G", "T")


@dataclass
class Genome:
    sequence: str
    generation: int = 0
    mutations: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.sequence = self.sequence.upper()
        if not self.sequence or any(base not in BASES for base in self.sequence):
            raise ValueError("Genome sequence must contain only A, C, G and T")

    def mutate(self, probability: float = 0.01, rng: Optional[random.Random] = None) -> "Genome":
        if not 0 <= probability <= 1:
            raise ValueError("probability must be between 0 and 1")
        rng = rng or random.Random()
        sequence = list(self.sequence)
        changed: List[int] = []
        for index, current in enumerate(sequence):
            if rng.random() < probability:
                choices = [base for base in BASES if base != current]
                sequence[index] = rng.choice(choices)
                changed.append(index)
        return Genome("".join(sequence), self.generation + 1, changed)

    @classmethod
    def random(cls, length: int, rng: Optional[random.Random] = None) -> "Genome":
        if length < 1:
            raise ValueError("length must be positive")
        rng = rng or random.Random()
        return cls("".join(rng.choice(BASES) for _ in range(length)))
