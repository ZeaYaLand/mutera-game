"""Persistent storage for Telegram game sessions."""
from pathlib import Path
import json
from .game import GameSession

class SessionStore:
    def __init__(self, directory="data/sessions"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, user_id):
        return self.directory / f"{user_id}.json"

    def save(self, user_id, session):
        session.save(self._path(user_id))

    def load(self, user_id):
        path = self._path(user_id)
        if not path.exists():
            return None
        return GameSession.load(path)
