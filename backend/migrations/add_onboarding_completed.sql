-- Add onboarding_completed column to user_profiles table
-- Run this in Supabase SQL Editor

ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;

-- Update existing users to have onboarding_completed = true if they have filled profile data
UPDATE user_profiles
SET onboarding_completed = TRUE
WHERE major IS NOT NULL AND graduation_year IS NOT NULL;

-- Add comment
COMMENT ON COLUMN user_profiles.onboarding_completed IS 'Indicates whether the user has completed the onboarding process';
