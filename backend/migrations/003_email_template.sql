-- Migration: Add email_template field to user_profiles
-- This allows users to customize their outreach email template

ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS email_template TEXT;

-- Add a comment for documentation
COMMENT ON COLUMN user_profiles.email_template IS 'Custom email template for AI-generated outreach emails. If null, uses default template.';
