"""Biomes, map tiles, resources and species classification."""
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Biome:
    name: str
    temperature: float
    food: float
    water: float
    danger: float

BIOMES = {
    "forest": Biome("forest", 18, 120, 100, 0.15),
    "desert": Biome("desert", 32, 35, 20, 0.25),
    "tundra": Biome("tundra", -5, 25, 70, 0.12),
    "swamp": Biome("swamp", 24, 100, 150, 0.30),
    "ocean": Biome("ocean", 16, 80, 200, 0.20),
}

@dataclass
class Tile:
    x: int
    y: int
    biome: str = "forest"
    resources: Dict[str, float] = field(default_factory=lambda: {"food": 100.0, "water": 100.0, "minerals": 20.0})

@dataclass
class WorldMap:
    width: int = 8
    height: int = 8
    tiles: List[Tile] = field(default_factory=list)

    def generate(self):
        names = list(BIOMES)
        self.tiles = [Tile(x, y, names[(x * 3 + y * 5) % len(names)]) for y in range(self.height) for x in range(self.width)]
        return self

@dataclass
class SpeciesRecord:
    species_id: str
    name: str
    generation: int = 0
    population: int = 0
    dominant_traits: Dict[str, float] = field(default_factory=dict)

@dataclass
class Discovery:
    key: str
    title: str
    description: str
    unlocked: bool = False
