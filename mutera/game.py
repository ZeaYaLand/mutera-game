"""Player game session and concrete gameplay actions."""
from dataclasses import dataclass
from pathlib import Path
import json

from .core import Genome, Organism, Population, World
from .db import Database
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

    def _origin(self):
        return self.engine.world.populations[0].organisms[0]

    def act(self):
        """Advance one simulation turn."""
        if not self.active:
            raise RuntimeError("Game session is inactive")
        self.player.increment("turns")
        return self.engine.tick()

    def feed(self):
        """Spend food from the environment to restore the origin organism."""
        organism = self._origin()
        env = self.engine.world.environment
        if not organism.alive:
            return {"ok": False, "message": "organism is dead"}
        if env.food < 5:
            return {"ok": False, "message": "not enough food"}
        env.food -= 5
        organism.energy = min(100.0, organism.energy + 12.0)
        self.player.increment("feeds")
        return {"ok": True, "energy": organism.energy, "food": env.food}

    def heal(self):
        """Spend water to restore a small amount of health."""
        organism = self._origin()
        env = self.engine.world.environment
        if not organism.alive:
            return {"ok": False, "message": "organism is dead"}
        if env.water < 5:
            return {"ok": False, "message": "not enough water"}
        env.water -= 5
        organism.health = min(100.0, organism.health + 10.0)
        self.player.increment("heals")
        return {"ok": True, "health": organism.health, "water": env.water}

    def explore(self):
        """Move the origin organism and discover its current biome."""
        organism = self._origin()
        position = self.engine.migration.move(organism, self.world_map.width, self.world_map.height)
        tile = next(t for t in self.world_map.tiles if (t.x, t.y) == position)
        self.player.discover_biome(tile.biome)
        self.player.increment("explorations")
        return {"ok": True, "position": position, "biome": tile.biome}

    def inspect(self):
        organism = self._origin()
        return {
            "player": self.player.summary(),
            "game": self.engine.snapshot(),
            "organism": {
                "id": organism.id,
                "alive": organism.alive,
                "age": organism.age,
                "energy": organism.energy,
                "health": organism.health,
                "generation": organism.genome.generation,
                "genome": organism.genome.sequence,
            },
            "map": {"width": self.world_map.width, "height": self.world_map.height},
            "active": self.active,
        }

    def save(self, path):
        Path(path).write_text(json.dumps(self.inspect(), ensure_ascii=False, indent=2), encoding="utf-8")

    def save_to_database(self, database=None):
        """Persist the complete player-facing session state in PostgreSQL."""
        db = database or Database()
        db.initialize()
        db.save_session(self.player.player_id, self.player.name, self.inspect())

    @classmethod
    def load_from_database(cls, player_id: str, database=None):
        """Restore a session from PostgreSQL, returning None when absent."""
        db = database or Database()
        data = db.load_session(player_id)
        if not data:
            return None
        state = data["state"]
        player_data = state.get("player", {})
        session = cls.new(player_id, data.get("player_name") or player_data.get("name", "Explorer"))
        session.player.statistics.update(player_data.get("statistics", {}))
        session.player.research_points = player_data.get("research", 0)
        return session

    @staticmethod
    def load(path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        p = data["player"]
        session = GameSession.new("restored", p.get("name", "Explorer"))
        session.player.statistics.update(p.get("statistics", {}))
        session.player.research_points = p.get("research", 0)
        return session
