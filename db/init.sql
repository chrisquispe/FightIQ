-- This file runs automatically the FIRST time the db container starts.
-- It sets up every table the app needs.

-- ── STEP 1: enable pgvector ──────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;


-- ── STEP 2: fighters table ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fighters (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    nickname      TEXT,
    weight_class  TEXT,
    stance        TEXT,
    height_cm     NUMERIC(5,2),
    reach_cm      NUMERIC(5,2),
    wins          INTEGER DEFAULT 0,
    losses        INTEGER DEFAULT 0,
    draws         INTEGER DEFAULT 0,
    wins_by_ko    INTEGER DEFAULT 0,
    wins_by_sub   INTEGER DEFAULT 0,
    wins_by_dec   INTEGER DEFAULT 0,
    created_at    TIMESTAMP DEFAULT NOW()
);


-- ── STEP 3: fights table ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fights (
    id            SERIAL PRIMARY KEY,
    fighter1      TEXT NOT NULL,
    fighter2      TEXT NOT NULL,
    winner        TEXT,
    method        TEXT,
    round         INTEGER,
    time          TEXT,
    event_name    TEXT,
    event_date    DATE,
    weight_class  TEXT,
    created_at    TIMESTAMP DEFAULT NOW()
);


-- ── STEP 4: fight_embeddings table ───────────────────────────────────
CREATE TABLE IF NOT EXISTS fight_embeddings (
    id            SERIAL PRIMARY KEY,
    fight_id      INTEGER REFERENCES fights(id) ON DELETE CASCADE,
    summary       TEXT NOT NULL,
    embedding     vector(1536),
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS fight_embeddings_idx
    ON fight_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);


-- ── STEP 5: fighter_stats_cache table ────────────────────────────────
CREATE TABLE IF NOT EXISTS fighter_stats_cache (
    fighter_name       TEXT PRIMARY KEY,
    total_fights       INTEGER,
    win_rate           NUMERIC(5,4),
    ko_rate            NUMERIC(5,4),
    sub_rate           NUMERIC(5,4),
    avg_fight_time_sec INTEGER,
    last_updated       TIMESTAMP DEFAULT NOW()
);


-- ── STEP 6: confirmation message ─────────────────────────────────────
DO $$
BEGIN
    RAISE NOTICE 'MMA database initialized successfully.';
    RAISE NOTICE 'Tables created: fighters, fights, fight_embeddings, fighter_stats_cache';
    RAISE NOTICE 'pgvector extension enabled.';
END $$;