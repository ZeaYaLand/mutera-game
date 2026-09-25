"""PostgreSQL persistence adapter for Mutera.

The database URL is read from MUTERA_DATABASE_URL. No credentials are stored
in source control. The adapter is intentionally small so the game core stays
independent from PostgreSQL.
"""
import json
import os


class Database:
    def __init__(self, url=None):
        self.url = url or os.getenv("MUTERA_DATABASE_URL")
        if not self.url:
            raise RuntimeError("MUTERA_DATABASE_URL is not configured")

    def connect(self):
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Install psycopg[binary] to use PostgreSQL") from exc
        return psycopg.connect(self.url)

    def initialize(self):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS player_sessions (
                        player_id TEXT PRIMARY KEY,
                        player_name TEXT NOT NULL,
                        state JSONB NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                """)
            conn.commit()

    def save_session(self, player_id, player_name, state):
        payload = json.dumps(state, ensure_ascii=False)
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO player_sessions (player_id, player_name, state)
                    VALUES (%s, %s, %s::jsonb)
                    ON CONFLICT (player_id) DO UPDATE SET
                        player_name = EXCLUDED.player_name,
                        state = EXCLUDED.state,
                        updated_at = NOW()
                """, (str(player_id), player_name, payload))
            conn.commit()

    def load_session(self, player_id):
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT player_name, state FROM player_sessions WHERE player_id = %s",
                    (str(player_id),),
                )
                row = cur.fetchone()
        if not row:
            return None
        return {"player_name": row[0], "state": row[1]}
