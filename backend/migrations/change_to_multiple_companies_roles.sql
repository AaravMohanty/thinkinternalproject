-- Change from current_company/current_title to companies/roles (arrays)
-- Run this in Supabase SQL Editor

-- Add new columns for companies and roles as arrays
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS companies TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS roles TEXT[] DEFAULT '{}';

-- Migrate existing data from current_company to companies array
UPDATE user_profiles
SET companies = ARRAY[current_company]
WHERE current_company IS NOT NULL AND current_company != '';

-- Migrate existing data from current_title to roles array
UPDATE user_profiles
SET roles = ARRAY[current_title]
WHERE current_title IS NOT NULL AND current_title != '';

-- Drop old columns (optional - comment out if you want to keep them for backup)
-- ALTER TABLE user_profiles DROP COLUMN current_company;
-- ALTER TABLE user_profiles DROP COLUMN current_title;

-- Add comments
COMMENT ON COLUMN user_profiles.companies IS 'Array of all companies the user has worked at';
COMMENT ON COLUMN user_profiles.roles IS 'Array of all roles/titles the user has held';
