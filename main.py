"""Stage 0 entry point for Mutera."""

from src.genome import Genome
from src.organism import Organism


def main() -> None:
    organism = Organism(Genome.random(32))
    print("Mutera Stage 0")
    print(f"Genome: {organism.genome.sequence}")
    print(f"Generation: {organism.genome.generation}")
    print(f"Energy: {organism.energy}")


if __name__ == "__main__":
    main()
