-- ============================================================
-- Migration 001: Create async_tasks table
-- For 202 Accepted asynchronous match processing
-- ============================================================

CREATE TABLE IF NOT EXISTS async_tasks (
    id VARCHAR(64) NOT NULL PRIMARY KEY,
    
    -- This references the match being processed asynchronously
    match_id INT NOT NULL,

    -- Current state of async workload
    status VARCHAR(20) NOT NULL DEFAULT 'running',

    -- JSON result payload (nullable until completed)
    result JSON NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP
);

-- Helpful index if querying async tasks by match
CREATE INDEX IF NOT EXISTS idx_async_tasks_match
    ON async_tasks (match_id);

