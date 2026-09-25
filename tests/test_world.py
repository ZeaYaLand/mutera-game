from mutera.world import BIOMES, WorldMap
from mutera.progression import Achievement, Progress


def test_map_generation():
    world = WorldMap(4, 4).generate()
    assert len(world.tiles) == 16
    assert all(tile.biome in BIOMES for tile in world.tiles)


def test_research_unlock():
    p = Progress()
    p.research.earn(10)
    assert p.research.unlock("adaptation", 10)
    assert "adaptation" in p.research.discovered


def test_achievement_unlock():
    p = Progress(achievements={"first": Achievement("first", "First Life", "Create life")})
    p.unlock("first")
    assert p.achievements["first"].unlocked
