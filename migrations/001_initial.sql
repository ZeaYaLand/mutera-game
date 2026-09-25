-- Mutera initial PostgreSQL schema.
-- Safe to run repeatedly: all objects use IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS worlds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    seed BIGINT,
    generation INTEGER NOT NULL DEFAULT 0,
    state JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS organisms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_id UUID NOT NULL REFERENCES worlds(id) ON DELETE CASCADE,
    owner_id TEXT REFERENCES players(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES organisms(id) ON DELETE SET NULL,
    species TEXT NOT NULL DEFAULT 'proto',
    generation INTEGER NOT NULL DEFAULT 0,
    genome JSONB NOT NULL DEFAULT '{}'::jsonb,
    traits JSONB NOT NULL DEFAULT '{}'::jsonb,
    energy DOUBLE PRECISION NOT NULL DEFAULT 100,
    health DOUBLE PRECISION NOT NULL DEFAULT 100,
    alive BOOLEAN NOT NULL DEFAULT TRUE,
    born_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    died_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_organisms_world ON organisms(world_id);
CREATE INDEX IF NOT EXISTS idx_organisms_owner ON organisms(owner_id);
CREATE INDEX IF NOT EXISTS idx_organisms_alive ON organisms(world_id, alive);

CREATE TABLE IF NOT EXISTS generations (
    id BIGSERIAL PRIMARY KEY,
    world_id UUID NOT NULL REFERENCES worlds(id) ON DELETE CASCADE,
    number INTEGER NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    population INTEGER NOT NULL DEFAULT 0,
    mutation_count INTEGER NOT NULL DEFAULT 0,
    UNIQUE(world_id, number)
);

CREATE TABLE IF NOT EXISTS mutations (
    id BIGSERIAL PRIMARY KEY,
    organism_id UUID NOT NULL REFERENCES organisms(id) ON DELETE CASCADE,
    generation_id BIGINT REFERENCES generations(id) ON DELETE SET NULL,
    gene TEXT NOT NULL,
    old_value JSONB,
    new_value JSONB,
    kind TEXT NOT NULL DEFAULT 'random',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mutations_organism ON mutations(organism_id);
CREATE INDEX IF NOT EXISTS idx_mutations_generation ON mutations(generation_id);

CREATE TABLE IF NOT EXISTS world_events (
    id BIGSERIAL PRIMARY KEY,
    world_id UUID NOT NULL REFERENCES worlds(id) ON DELETE CASCADE,
    generation INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    actor_id UUID REFERENCES organisms(id) ON DELETE SET NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_world_events_world_generation ON world_events(world_id, generation);

CREATE TABLE IF NOT EXISTS world_snapshots (
    id BIGSERIAL PRIMARY KEY,
    world_id UUID NOT NULL REFERENCES worlds(id) ON DELETE CASCADE,
    generation INTEGER NOT NULL,
    state JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(world_id, generation)
);

CREATE TABLE IF NOT EXISTS player_sessions (
    player_id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    state JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
