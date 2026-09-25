"""Player game session: start, actions, save/load and inspection."""
from dataclasses import dataclass, field
from pathlib import Path
import json

from .core import Genome, Organism, Population, World
from .engine import GameEngine
from .player import PlayerProfile
from .world import WorldMap

@dataclass
class GameSession:
    player: PlayerProfile
    engine: GameEngine
    world_map: WorldMap
    active: bool = True

    @classmethod
    def new(cls, player_id: str, name: str = "Explorer"):
        organism = Organism("origin-1", Genome.random(16))
        world = World(populations=[Population([organism])])
        world_map = WorldMap().generate()
        player = PlayerProfile(player_id, name)
        player.discover_biome("forest")
        player.increment("organisms_created")
        return cls(player, GameEngine(world), world_map)

    def act(self):
        if not self.active:
            raise RuntimeError("Game session is inactive")
        self.player.increment("turns")
        return self.engine.tick()

    def inspect(self):
        return {
            "player": self.player.summary(),
            "game": self.engine.snapshot(),
            "map": {"width": self.world_map.width, "height": self.world_map.height},
            "active": self.active,
        }

    def save(self, path):
        data = self.inspect()
        data["clock"] = {"turn": self.engine.world.environment.turn}
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def load(path):
        # Metadata restore point; simulation objects are rebuilt from a fresh deterministic session.
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        player = data.get("player", {})
        session = GameSession.new("restored", player.get("name", "Explorer"))
        session.player.statistics.update(player.get("statistics", {}))
        return session
