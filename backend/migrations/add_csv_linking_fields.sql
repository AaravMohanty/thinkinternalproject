-- Add CSV linking fields to user_profiles
-- This allows us to link user profiles with their CSV alumni records

ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS csv_source_id INTEGER,
ADD COLUMN IF NOT EXISTS csv_match_type TEXT,
ADD COLUMN IF NOT EXISTS csv_match_confidence FLOAT,
ADD COLUMN IF NOT EXISTS is_csv_linked BOOLEAN DEFAULT FALSE;

-- Add index for faster CSV lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_csv_source_id ON user_profiles(csv_source_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_is_csv_linked ON user_profiles(is_csv_linked);

-- Add comments
COMMENT ON COLUMN user_profiles.csv_source_id IS 'Index of the CSV row this profile is linked to (if any)';
COMMENT ON COLUMN user_profiles.csv_match_type IS 'How the match was made: single_name_match, name_and_email_match, manual_link';
COMMENT ON COLUMN user_profiles.csv_match_confidence IS 'Confidence score of the match (0-1)';
COMMENT ON COLUMN user_profiles.is_csv_linked IS 'Whether this profile is linked to a CSV record';
