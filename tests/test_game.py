from mutera.game import GameSession


class FakeDatabase:
    def __init__(self):
        self.saved = None
        self.initialized = False

    def initialize(self):
        self.initialized = True

    def save_session(self, player_id, player_name, state):
        self.saved = (player_id, player_name, state)

    def load_session(self, player_id):
        if not self.saved or self.saved[0] != player_id:
            return None
        return {"player_name": self.saved[1], "state": self.saved[2]}


def test_new_game_creates_origin():
    session = GameSession.new("player-1", "Dan")
    state = session.inspect()
    assert state["player"]["name"] == "Dan"
    assert state["game"]["world"]["total"] == 1
    assert state["active"]


def test_game_action_advances_world():
    session = GameSession.new("player-1")
    state = session.act()
    assert state["world"]["turn"] == 1
    assert state["progress"]["turns"] == 1


def test_save_and_load_metadata(tmp_path):
    session = GameSession.new("player-1", "Explorer")
    path = tmp_path / "save.json"
    session.save(path)
    restored = GameSession.load(path)
    assert restored.player.name == "Explorer"


def test_database_persistence_bridge():
    database = FakeDatabase()
    session = GameSession.new("player-1", "Explorer")
    session.act()
    session.save_to_database(database)

    assert database.initialized
    assert database.saved[0] == "player-1"
    assert database.saved[1] == "Explorer"

    restored = GameSession.load_from_database("player-1", database)
    assert restored is not None
    assert restored.player.name == "Explorer"
    assert restored.player.statistics["turns"] == 1
