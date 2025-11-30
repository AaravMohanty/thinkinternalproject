-- ==========================================
-- CLEAR ALL DATA - Fresh Start Script
-- ==========================================
-- WARNING: This will DELETE ALL user data
-- Run this ONLY in development/testing
-- ==========================================

-- Step 1: Delete all user profiles and related data
-- This will cascade delete connections and other related records
DELETE FROM user_profiles;

-- Step 2: Delete all connections (if not cascaded)
DELETE FROM connections;

-- Step 3: Delete all chat sessions and messages
DELETE FROM chat_messages;
DELETE FROM chat_sessions;

-- Step 4: Delete all resumes from storage
-- Note: This requires running a storage cleanup, or you can manually delete
-- the 'resumes' bucket contents from Supabase Storage UI

-- Step 5: Delete all auth users
-- IMPORTANT: In Supabase, you need to use the auth.users table
-- This will permanently delete all signed-up users
DELETE FROM auth.users;

-- Step 6: Reset any sequences (optional - ensures IDs start from 1 again)
-- Uncomment if you want to reset auto-increment IDs
-- ALTER SEQUENCE user_profiles_id_seq RESTART WITH 1;

-- ==========================================
-- Verification Queries
-- ==========================================
-- Run these to verify everything is cleared:

-- Check user_profiles (should return 0)
-- SELECT COUNT(*) FROM user_profiles;

-- Check auth users (should return 0)
-- SELECT COUNT(*) FROM auth.users;

-- Check connections (should return 0)
-- SELECT COUNT(*) FROM connections;

-- ==========================================
-- NOTES
-- ==========================================
-- 1. This does NOT delete the database schema
-- 2. All tables and columns remain intact
-- 3. Only the DATA is deleted
-- 4. Resume files in storage are NOT automatically deleted
--    You need to manually clear the 'resumes' bucket in Supabase Storage UI
