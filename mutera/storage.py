"""Persistent storage for Telegram game sessions.

PostgreSQL is preferred when MUTERA_DATABASE_URL is configured; JSON remains
as a local fallback for development and recovery.
"""
import json
import os
from pathlib import Path
from .game import GameSession
from .db import Database


class SessionStore:
    def __init__(self, directory="data/sessions", database=None):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.database = database
        if self.database is None and os.getenv("MUTERA_DATABASE_URL"):
            self.database = Database()
            self.database.initialize()

    def _path(self, user_id):
        return self.directory / f"{user_id}.json"

    def save(self, user_id, session):
        if self.database:
            self.database.save_session(user_id, session.player.name, session.inspect())
        session.save(self._path(user_id))

    def load(self, user_id):
        if self.database:
            record = self.database.load_session(user_id)
            if record:
                return GameSession.load(self._write_temp_state(user_id, record["state"]))
        path = self._path(user_id)
        if path.exists():
            return GameSession.load(path)
        return None

    def _write_temp_state(self, user_id, state):
        path = self._path(user_id)
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
