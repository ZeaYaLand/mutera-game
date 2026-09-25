"""Game lifecycle: turns, seasons, population records and save snapshots."""
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Season:
    name: str
    index: int
    modifiers: Dict[str, float] = field(default_factory=dict)

SEASONS = [
    Season("spring", 0, {"food": 1.25, "birth": 1.2}),
    Season("summer", 1, {"food": 1.1, "temperature": 1.1}),
    Season("autumn", 2, {"food": 0.9, "migration": 1.2}),
    Season("winter", 3, {"food": 0.55, "survival": 0.8}),
]

@dataclass
class WorldClock:
    turn: int = 0
    day: int = 1
    season_index: int = 0
    year: int = 1

    @property
    def season(self):
        return SEASONS[self.season_index]

    def advance(self):
        self.turn += 1
        self.day += 1
        if self.day > 30:
            self.day = 1
            self.season_index = (self.season_index + 1) % 4
            if self.season_index == 0:
                self.year += 1

@dataclass
class SpeciesHistory:
    records: List[Dict] = field(default_factory=list)

    def record(self, turn: int, species: str, population: int, generation: int):
        self.records.append({"turn": turn, "species": species, "population": population, "generation": generation})
        self.records = self.records[-1000:]

    def latest(self):
        return self.records[-1] if self.records else None
