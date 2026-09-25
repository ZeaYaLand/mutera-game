"""Database connectivity helpers for Mutera."""

from __future__ import annotations

import os

import psycopg


def check_database_connection() -> bool:
    """Open the configured PostgreSQL connection and run a minimal query."""
    database_url = os.getenv("MUTERA_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("MUTERA_DATABASE_URL is not configured")

    with psycopg.connect(database_url, connect_timeout=10) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone() == (1,)


if __name__ == "__main__":
    if not check_database_connection():
        raise SystemExit("Database connectivity check failed")
    print("Mutera PostgreSQL connection: OK")
