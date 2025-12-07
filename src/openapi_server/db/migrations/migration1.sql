-- =====================================================
-- Remove duplicate MATCHES entries
-- =====================================================

-- Delete duplicates but keep the lowest id
DELETE m1 FROM matches m1
INNER JOIN matches m2
ON m1.donor_id = m2.donor_id
AND m1.recipient_id = m2.recipient_id
AND m1.id > m2.id;

-- Add unique constraint for future inserts
ALTER TABLE matches
ADD CONSTRAINT unique_match_pair
UNIQUE (donor_id, recipient_id);


-- =====================================================
-- Remove duplicate OFFERS entries
-- =====================================================

-- Delete duplicates but keep the lowest id
DELETE o1 FROM offers o1
INNER JOIN offers o2
ON o1.match_id = o2.match_id
AND o1.id > o2.id;

-- Add unique constraint for future inserts
ALTER TABLE offers
ADD CONSTRAINT unique_offer_per_match
UNIQUE (match_id);


-- =====================================================
-- Indexes for performance (optional but recommended)
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_matches_donor ON matches(donor_id);
CREATE INDEX IF NOT EXISTS idx_matches_recipient ON matches(recipient_id);

CREATE INDEX IF NOT EXISTS idx_offers_match ON offers(match_id);

-- Done 
