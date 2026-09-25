from mutera.game import GameSession


def test_feed_and_heal_consume_resources():
    session = GameSession.new("p1")
    organism = session._origin()
    organism.energy = 50
    organism.health = 50
    result = session.feed()
    assert result["ok"]
    assert organism.energy == 62
    result = session.heal()
    assert result["ok"]
    assert organism.health == 60


def test_explore_discovers_a_biome():
    session = GameSession.new("p1")
    result = session.explore()
    assert result["ok"]
    assert result["biome"] in session.player.discovered_biomes


def test_inspect_contains_organism_state():
    state = GameSession.new("p1").inspect()
    assert state["organism"]["generation"] == 0
    assert len(state["organism"]["genome"]) == 16
