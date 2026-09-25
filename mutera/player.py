"""Player-facing state independent from the simulation engine."""
from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class PlayerProfile:
    player_id: str
    name: str = "Explorer"
    discovered_species: Set[str] = field(default_factory=set)
    discovered_biomes: Set[str] = field(default_factory=set)
    research_points: int = 0
    achievements: Set[str] = field(default_factory=set)
    statistics: Dict[str, int] = field(default_factory=dict)

    def discover_species(self, species_id: str):
        self.discovered_species.add(species_id)

    def discover_biome(self, biome: str):
        self.discovered_biomes.add(biome)

    def increment(self, key: str, amount: int = 1):
        self.statistics[key] = self.statistics.get(key, 0) + amount

    def summary(self):
        return {
            "name": self.name,
            "species": len(self.discovered_species),
            "biomes": len(self.discovered_biomes),
            "research": self.research_points,
            "achievements": len(self.achievements),
            "statistics": dict(self.statistics),
        }
