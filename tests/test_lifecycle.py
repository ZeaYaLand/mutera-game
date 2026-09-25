from mutera.lifecycle import WorldClock
from mutera.player import PlayerProfile


def test_clock_reaches_next_season():
    clock = WorldClock(day=30)
    clock.advance()
    assert clock.season.name == "summer"


def test_profile_tracks_discoveries():
    profile = PlayerProfile("p1")
    profile.discover_species("species-a")
    profile.discover_biome("forest")
    profile.increment("births", 3)
    assert profile.summary()["species"] == 1
    assert profile.summary()["biomes"] == 1
    assert profile.summary()["statistics"]["births"] == 3
