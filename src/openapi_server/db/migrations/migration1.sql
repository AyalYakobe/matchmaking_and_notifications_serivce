-- =====================================================
-- Remove duplicate MATCHES entries
-- =====================================================

DELETE m1 FROM matches m1
INNER JOIN matches m2
ON m1.donor_id = m2.donor_id
AND m1.recipient_id = m2.recipient_id
AND m1.id > m2.id;


-- =====================================================
-- Add UNIQUE constraint to MATCHES (safe)
-- =====================================================

SET @exists := (
    SELECT COUNT(*)
    FROM information_schema.table_constraints
    WHERE table_name = 'matches'
      AND constraint_name = 'unique_match_pair'
      AND table_schema = DATABASE()
);

SET @sql := IF(@exists = 0,
    'ALTER TABLE matches ADD CONSTRAINT unique_match_pair UNIQUE (donor_id, recipient_id);',
    'SELECT "unique_match_pair already exists";'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- =====================================================
-- Remove duplicate OFFERS entries
-- =====================================================

DELETE o1 FROM offers o1
INNER JOIN offers o2
ON o1.match_id = o2.match_id
AND o1.id > o2.id;


-- =====================================================
-- Add UNIQUE constraint to OFFERS (safe)
-- =====================================================

SET @exists := (
    SELECT COUNT(*)
    FROM information_schema.table_constraints
    WHERE table_name = 'offers'
      AND constraint_name = 'unique_offer_per_match'
      AND table_schema = DATABASE()
);

SET @sql := IF(@exists = 0,
    'ALTER TABLE offers ADD CONSTRAINT unique_offer_per_match UNIQUE (match_id);',
    'SELECT "unique_offer_per_match already exists";'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- =====================================================
-- Create MATCHES indexes (safe)
-- =====================================================

-- Drop index idx_matches_donor if exists
SET @exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_name = 'matches'
      AND index_name = 'idx_matches_donor'
      AND table_schema = DATABASE()
);
SET @sql := IF(@exists > 0,
    'DROP INDEX idx_matches_donor ON matches;',
    'SELECT "idx_matches_donor does not exist";'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE INDEX idx_matches_donor ON matches(donor_id);


-- Drop index idx_matches_recipient if exists
SET @exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_name = 'matches'
      AND index_name = 'idx_matches_recipient'
      AND table_schema = DATABASE()
);
SET @sql := IF(@exists > 0,
    'DROP INDEX idx_matches_recipient ON matches;',
    'SELECT "idx_matches_recipient does not exist";'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE INDEX idx_matches_recipient ON matches(recipient_id);


-- =====================================================
-- Create OFFERS indexes (safe)
-- =====================================================

SET @exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_name = 'offers'
      AND index_name = 'idx_offers_match'
      AND table_schema = DATABASE()
);
SET @sql := IF(@exists > 0,
    'DROP INDEX idx_offers_match ON offers;',
    'SELECT "idx_offers_match does not exist";'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

CREATE INDEX idx_offers_match ON offers(match_id);

-- Done 
