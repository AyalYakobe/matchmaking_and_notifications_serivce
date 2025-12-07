-- ============================================================
-- Migration 2: Create async_tasks table (MySQL compatible)
-- ============================================================

CREATE TABLE IF NOT EXISTS async_tasks (
    id VARCHAR(64) NOT NULL PRIMARY KEY,
    match_id INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    result JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

-- MySQL does not support IF NOT EXISTS for indexes.
-- So we create the index only if it is not already present.

-- Check if index exists
SET @idx_exists := (
    SELECT COUNT(1)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE table_schema = DATABASE()
      AND table_name = 'async_tasks'
      AND index_name = 'idx_async_tasks_match'
);

-- Conditionally create the index
SET @sql := IF(@idx_exists = 0,
               'CREATE INDEX idx_async_tasks_match ON async_tasks (match_id);',
               'SELECT "Index already exists";');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
