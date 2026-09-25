"""Research, achievements and long-term player progression."""
from dataclasses import dataclass, field
from typing import Dict, Set

@dataclass
class Research:
    points: int = 0
    discovered: Set[str] = field(default_factory=set)

    def earn(self, amount: int = 1):
        self.points += max(0, amount)

    def unlock(self, key: str, cost: int):
        if key in self.discovered:
            return True
        if self.points < cost:
            return False
        self.points -= cost
        self.discovered.add(key)
        return True

@dataclass
class Achievement:
    key: str
    title: str
    description: str
    unlocked: bool = False

@dataclass
class Progress:
    research: Research = field(default_factory=Research)
    achievements: Dict[str, Achievement] = field(default_factory=dict)
    lifetime_turns: int = 0
    discovered_species: int = 0

    def register_turn(self):
        self.lifetime_turns += 1
        if self.lifetime_turns >= 100:
            self.unlock("century")

    def unlock(self, key: str):
        achievement = self.achievements.get(key)
        if achievement:
            achievement.unlocked = True

    def stats(self):
        return {
            "turns": self.lifetime_turns,
            "species": self.discovered_species,
            "research": self.research.points,
            "achievements": sum(a.unlocked for a in self.achievements.values()),
        }
