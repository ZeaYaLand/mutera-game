-- Evolution lineage persistence for Mutera.
-- Uses TEXT organism IDs so simulation IDs remain independent from DB UUIDs.

CREATE TABLE IF NOT EXISTS evolution_records (
    id BIGSERIAL PRIMARY KEY,
    world_id UUID REFERENCES worlds(id) ON DELETE CASCADE,
    child_id TEXT NOT NULL,
    parent_a_id TEXT NOT NULL,
    parent_b_id TEXT NOT NULL,
    generation INTEGER NOT NULL,
    genome TEXT NOT NULL,
    mutation_positions JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evolution_child ON evolution_records(child_id);
CREATE INDEX IF NOT EXISTS idx_evolution_generation ON evolution_records(world_id, generation);

CREATE TABLE IF NOT EXISTS evolution_mutations (
    id BIGSERIAL PRIMARY KEY,
    evolution_id BIGINT NOT NULL REFERENCES evolution_records(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    old_base TEXT NOT NULL,
    new_base TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evolution_mutations_record ON evolution_mutations(evolution_id);
