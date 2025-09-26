-- Add document column to users and unique index
ALTER TABLE users ADD COLUMN IF NOT EXISTS document VARCHAR(20) NULL;
-- MySQL before 8.0.19 doesn't support IF NOT EXISTS in ADD COLUMN; handle error if exists

-- Create unique index/constraint for document
ALTER TABLE users ADD CONSTRAINT uq_users_document UNIQUE (document);


