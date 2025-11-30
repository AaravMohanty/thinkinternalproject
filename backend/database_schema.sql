-- PurdueTHINK Internal Networking Tool - Database Schema
-- Run this in your Supabase SQL Editor after creating the project

-- Enable pgvector extension for AI embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- USER PROFILES TABLE
-- =====================================================
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,

  -- Basic Info
  full_name TEXT NOT NULL,
  profile_image_url TEXT,

  -- Academic Info
  major TEXT,
  graduation_year INTEGER,

  -- Professional Info
  current_company TEXT,
  current_title TEXT,
  location TEXT,

  -- Contact Info
  linkedin_url TEXT,
  personal_email TEXT,
  professional_email TEXT,
  phone TEXT,

  -- Resume & Bio
  resume_url TEXT,
  bio TEXT,
  raw_resume_text TEXT,

  -- Career Preferences (stored as JSONB arrays for flexibility)
  career_interests TEXT[],
  target_industries TEXT[],
  target_companies TEXT[],

  -- AI Embeddings for matching
  resume_embedding vector(768),

  -- User Status
  is_alumni BOOLEAN DEFAULT false,
  is_director BOOLEAN DEFAULT false,
  visibility TEXT DEFAULT 'members_only' CHECK (visibility IN ('public', 'members_only')),

  -- Audit Fields
  signup_referral_code TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- PLATFORM SETTINGS TABLE (Single Row)
-- =====================================================
CREATE TABLE platform_settings (
  id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1), -- Only allow one row
  active_referral_code TEXT NOT NULL,
  updated_by UUID REFERENCES auth.users(id),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial settings
INSERT INTO platform_settings (active_referral_code)
VALUES ('LAUNCH_2025');

-- =====================================================
-- ADMIN ACTIONS TABLE (Audit Log)
-- =====================================================
CREATE TABLE admin_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  director_user_id UUID REFERENCES auth.users(id) NOT NULL,
  action_type TEXT NOT NULL CHECK (action_type IN (
    'SET_REFERRAL_CODE',
    'REMOVE_MEMBER',
    'PROMOTE_DIRECTOR',
    'DEMOTE_DIRECTOR',
    'UPDATE_MEMBER_PROFILE'
  )),
  target_user_id UUID REFERENCES auth.users(id),
  details JSONB,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CONNECTIONS TABLE (Track networking activity)
-- =====================================================
CREATE TABLE connections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  target_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  email_drafted_at TIMESTAMP WITH TIME ZONE,
  connection_made_at TIMESTAMP WITH TIME ZONE,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CHAT SESSIONS & MESSAGES (Optional - for chat persistence)
-- =====================================================
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- User profiles
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_is_director ON user_profiles(is_director);
CREATE INDEX idx_user_profiles_graduation_year ON user_profiles(graduation_year);
CREATE INDEX idx_user_profiles_major ON user_profiles(major);

-- Vector similarity search (IVFFlat index for embeddings)
CREATE INDEX idx_user_profiles_embedding ON user_profiles
  USING ivfflat (resume_embedding vector_cosine_ops)
  WITH (lists = 100);

-- Admin actions
CREATE INDEX idx_admin_actions_director ON admin_actions(director_user_id);
CREATE INDEX idx_admin_actions_timestamp ON admin_actions(timestamp DESC);

-- Connections
CREATE INDEX idx_connections_user_id ON connections(user_id);
CREATE INDEX idx_connections_target_user_id ON connections(target_user_id);

-- Chat
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- USER PROFILES POLICIES
-- Anyone authenticated can view all profiles
CREATE POLICY "Authenticated users can view all profiles" ON user_profiles
  FOR SELECT
  USING (auth.role() = 'authenticated');

-- Users can insert their own profile (during signup)
CREATE POLICY "Users can create own profile" ON user_profiles
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can only update their own profile
CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE
  USING (auth.uid() = user_id);

-- Only Directors can delete profiles (remove members)
CREATE POLICY "Directors can delete profiles" ON user_profiles
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_id = auth.uid() AND is_director = true
    )
  );

-- PLATFORM SETTINGS POLICIES
-- Everyone can read platform settings (for referral code validation)
CREATE POLICY "Anyone can view platform settings" ON platform_settings
  FOR SELECT
  USING (true);

-- Only Directors can update platform settings
CREATE POLICY "Directors can update platform settings" ON platform_settings
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_id = auth.uid() AND is_director = true
    )
  );

-- ADMIN ACTIONS POLICIES
-- Only Directors can view audit log
CREATE POLICY "Directors can view audit log" ON admin_actions
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_id = auth.uid() AND is_director = true
    )
  );

-- Only Directors can insert admin actions
CREATE POLICY "Directors can log actions" ON admin_actions
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM user_profiles
      WHERE user_id = auth.uid() AND is_director = true
    )
  );

-- CONNECTIONS POLICIES
-- Users can view their own connections
CREATE POLICY "Users can view own connections" ON connections
  FOR SELECT
  USING (auth.uid() = user_id);

-- Users can create their own connections
CREATE POLICY "Users can create own connections" ON connections
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own connections
CREATE POLICY "Users can update own connections" ON connections
  FOR UPDATE
  USING (auth.uid() = user_id);

-- CHAT POLICIES
-- Users can view their own chat sessions
CREATE POLICY "Users can view own chat sessions" ON chat_sessions
  FOR SELECT
  USING (auth.uid() = user_id);

-- Users can create their own chat sessions
CREATE POLICY "Users can create own chat sessions" ON chat_sessions
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can view messages from their own sessions
CREATE POLICY "Users can view own chat messages" ON chat_messages
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM chat_sessions
      WHERE id = session_id AND user_id = auth.uid()
    )
  );

-- Users can create messages in their own sessions
CREATE POLICY "Users can create own chat messages" ON chat_messages
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM chat_sessions
      WHERE id = session_id AND user_id = auth.uid()
    )
  );

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for user_profiles
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for platform_settings
CREATE TRIGGER update_platform_settings_updated_at
  BEFORE UPDATE ON platform_settings
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Trigger for chat_sessions
CREATE TRIGGER update_chat_sessions_updated_at
  BEFORE UPDATE ON chat_sessions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- NOTES FOR SETUP
-- =====================================================

/*
SETUP INSTRUCTIONS:

1. Create a new Supabase project at https://supabase.com

2. Go to SQL Editor and run this entire script

3. Get your API keys from Settings > API:
   - Copy the "Project URL" (SUPABASE_URL)
   - Copy the "anon public" key (SUPABASE_KEY)
   - Copy the "service_role" key (SUPABASE_SERVICE_KEY) - KEEP SECRET!

4. Enable Email Auth in Authentication > Providers

5. (Optional) Configure email templates in Authentication > Email Templates

6. Create a Storage bucket named "resumes" for resume uploads:
   - Go to Storage
   - Create new bucket: "resumes"
   - Make it private (only accessible by authenticated users)

7. Create a Storage bucket named "profile-images":
   - Create new bucket: "profile-images"
   - Make it public (for displaying profile images)

8. Add these API keys to your .env file in the backend directory
*/
