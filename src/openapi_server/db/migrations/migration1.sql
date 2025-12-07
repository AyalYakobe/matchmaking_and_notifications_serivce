-- =====================================================
-- Remove duplicate MATCHES entries
-- =====================================================

DELETE m1 FROM matches m1
INNER JOIN matches m2
ON m1.donor_id = m2.donor_id
AND m1.recipient_id = m2.recipient_id
AND m1.id > m2.id;


-- =====================================================
-- Add UNIQUE constraint to MATCHES safely
-- =====================================================

SET @exists := (
    SELECT COUNT(*)
    FROM information_schema.table_constraints
    WHERE table_name = 'matches'
      AND constraint_name = 'unique_match_pair'
);

-- Only add constraint if NOT already present
SET @sql := IF(@exists = 0,
    'ALTER TABLE matches ADD CONSTRAINT unique_match_pair UNIQUE (donor_id, recipient_id);',
    'SELECT "unique_match_pair already exists"'
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
-- Add UNIQUE constraint to OFFERS safely
-- =====================================================

SET @exists := (
    SELECT COUNT(*)
    FROM information_schema.table_constraints
    WHERE table_name = 'offers'
      AND constraint_name = 'unique_offer_per_match'
);

SET @sql := IF(@exists = 0,
    'ALTER TABLE offers ADD CONSTRAINT unique_offer_per_match UNIQUE (match_id);',
    'SELECT "unique_offer_per_match already exists"'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- =====================================================
-- Indexes for performance (MySQL-compatible)
-- =====================================================

DROP INDEX IF EXISTS idx_matches_donor ON matches;
CREATE INDEX idx_matches_donor ON matches(donor_id);

DROP INDEX IF EXISTS idx_matches_recipient ON matches;
CREATE INDEX idx_matches_recipient ON matches(recipient_id);

DROP INDEX IF EXISTS idx_offers_match ON offers;
CREATE INDEX idx_offers_match ON offers(match_id);
