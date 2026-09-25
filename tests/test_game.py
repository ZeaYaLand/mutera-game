from mutera.game import GameSession


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
