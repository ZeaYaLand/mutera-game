from mutera.game import GameSession


class FakeEvolutionDatabase:
    def __init__(self):
        self.initialized = False
        self.record = None

    def initialize(self):
        self.initialized = True

    def save_evolution(self, child_id, parent_a_id, parent_b_id, genome, mutation_positions):
        self.record = {
            "child_id": child_id,
            "parent_a_id": parent_a_id,
            "parent_b_id": parent_b_id,
            "generation": genome.generation,
            "genome": genome.sequence,
            "mutation_positions": list(mutation_positions),
        }
        return 1


def test_reproduction_persists_lineage():
    session = GameSession.new("player-1")
    # Add a second living parent with a compatible genome.
    origin = session.engine.world.populations[0].organisms[0]
    from mutera.core import Organism
    second = Organism("origin-2", origin.genome)
    session.engine.world.populations[0].organisms.append(second)

    db = FakeEvolutionDatabase()
    result = session.reproduce(parent_a_id="origin-1", parent_b_id="origin-2", child_id="child-1", database=db)

    assert db.initialized
    assert db.record["child_id"] == "child-1"
    assert db.record["parent_a_id"] == "origin-1"
    assert db.record["parent_b_id"] == "origin-2"
    assert db.record["generation"] == origin.genome.generation + 1
    assert result["evolution_id"] == 1
