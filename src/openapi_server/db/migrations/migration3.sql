-- Convert match_id from INT → VARCHAR(64)
ALTER TABLE offers
    MODIFY COLUMN match_id VARCHAR(64) NOT NULL;

-- Drop old unique constraint tied to the INT column
ALTER TABLE offers
    DROP INDEX unique_offer_per_match;

-- Recreate correct unique constraint on VARCHAR
ALTER TABLE offers
    ADD UNIQUE KEY unique_offer_per_match (match_id);
