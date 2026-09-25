"""PostgreSQL persistence adapter for Mutera.

The database URL is read from MUTERA_DATABASE_URL. No credentials are stored
in source control. The adapter is intentionally small so the game core stays
independent from PostgreSQL.
"""
import json
import os
from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "migrations" / "001_initial.sql"
EVOLUTION_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "migrations" / "002_evolution_history.sql"


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
        """Create the complete Mutera schema if it does not already exist."""
        for path in (SCHEMA_PATH, EVOLUTION_SCHEMA_PATH):
            if not path.exists():
                raise RuntimeError(f"Database schema file is missing: {path}")
            schema = path.read_text(encoding="utf-8")
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(schema)
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

    def save_evolution(self, child_id, parent_a_id, parent_b_id, genome, mutation_positions, world_id=None):
        """Persist one reproduction event and its mutation positions atomically."""
        positions = list(mutation_positions or [])
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO evolution_records
                    (world_id, child_id, parent_a_id, parent_b_id, generation, genome, mutation_positions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    RETURNING id""",
                    (world_id, str(child_id), str(parent_a_id), str(parent_b_id),
                     int(genome.generation), genome.sequence, json.dumps(positions)),
                )
                evolution_id = cur.fetchone()[0]
                for position in positions:
                    cur.execute(
                        """INSERT INTO evolution_mutations
                        (evolution_id, position, old_base, new_base)
                        VALUES (%s, %s, %s, %s)""",
                        (evolution_id, int(position), "?", genome.sequence[position]),
                    )
            conn.commit()
        return evolution_id
