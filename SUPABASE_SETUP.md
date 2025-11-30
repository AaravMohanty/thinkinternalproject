# Supabase Setup Guide for PurdueTHINK Networking Tool

## Step 1: Create a New Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" or "New Project" (sign up/login if needed)
3. Create a new organization if you don't have one:
   - Name: "PurdueTHINK" (or whatever you prefer)
   - Click "Create organization"
4. Click "New project" and fill in:
   - **Name**: `thinkedin` (or `purduethink-network`)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you (e.g., `US East` for Purdue)
   - **Pricing Plan**: Free tier is fine for now
5. Click "Create new project"
6. Wait 2-3 minutes for project to provision

---

## Step 2: Get Your API Keys

1. Once project is ready, go to **Settings** (gear icon on left sidebar)
2. Click **API** in the settings menu
3. You'll see:
   - **Project URL** - Copy this (it looks like `https://xxxxx.supabase.co`)
   - **Project API keys**:
     - **anon public** key - Copy this (starts with `eyJ...`)
     - **service_role** key - Copy this (starts with `eyJ...`) - **KEEP SECRET!**

4. Save these three values:
   ```
   SUPABASE_URL=https://umrtpxgumehnsbwmbknb.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVtcnRweGd1bWVobnNid21ia25iIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0MjQzMjMsImV4cCI6MjA3OTAwMDMyM30.q-Z4dcnJeBAJopjFLCf--bAbZIN8SynsqY9UcqyLwhw
   SUPABASE_SERVICE_KEY=sb_secret_ImRJKhxl2lkk-urbFSln6w_nzN6mt96
   ```

---

## Step 3: Create the Database Schema

1. In your Supabase project, click **SQL Editor** (on left sidebar)
2. Click **"New query"**
3. Copy the entire contents of `backend/database_schema.sql` (the file I just created)
4. Paste it into the SQL editor
5. Click **"Run"** (or press Cmd/Ctrl + Enter)
6. You should see a success message: "Success. No rows returned"
7. Verify tables were created:
   - Click **Table Editor** on left sidebar
   - You should see tables: `user_profiles`, `platform_settings`, `admin_actions`, `connections`, `chat_sessions`, `chat_messages`

---

## Step 4: Set Up Storage Buckets

### Create Resume Bucket (Private)
1. Click **Storage** on left sidebar
2. Click **"New bucket"**
3. Settings:
   - **Name**: `resumes`
   - **Public bucket**: **OFF** (keep it private)
4. Click "Create bucket"

### Create Profile Images Bucket (Public)
1. Click **"New bucket"** again
2. Settings:
   - **Name**: `profile-images`
   - **Public bucket**: **ON** (so images can be displayed)
3. Click "Create bucket"

---

## Step 5: Configure Authentication

1. Click **Authentication** on left sidebar
2. Click **Providers**
3. Make sure **Email** is enabled (should be by default)
4. Scroll down to **Email Auth**:
   - **Enable email confirmations**: You can leave this **OFF** for development (turn on later)
   - **Secure email change**: Leave as is
5. Click **Save**

### Optional: Customize Email Templates
1. Go to **Authentication** > **Email Templates**
2. You can customize:
   - Confirm signup email
   - Magic link email
   - Change email address
   - Reset password
3. For now, defaults are fine

---

## Step 6: Create .env File with Your Keys

1. In your project root directory, create a file called `.env` (not `.env.example`)
2. Copy the contents of `.env.example` and fill in your actual values:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # anon public key
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # service_role key

# Gemini AI Configuration (we'll get this next)
GEMINI_API_KEY=your-gemini-api-key-here

# Referral Code Configuration (these are fine as is)
OPS_CODE=OPS
SUPER_OPS_CODE=SUPER_OPS_2025

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here  # Generate a random string
FLASK_ENV=development
FLASK_DEBUG=True
```

3. **IMPORTANT**: Add `.env` to your `.gitignore` file so you don't commit your secrets!

---

## Step 7: Get Google Gemini API Key (Free)

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select **"Create API key in new project"** (or use existing project)
5. Copy the API key
6. Paste it into your `.env` file as `GEMINI_API_KEY=xxx`
7. Free tier limits:
   - 15 requests per minute
   - 1 million tokens per minute
   - 1,500 requests per day
   - This is plenty for initial launch!

---

## Step 8: Verify Everything is Set Up

Your `.env` file should now look like this (with real values):

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxx...
SUPABASE_SERVICE_KEY=eyJxxx...
GEMINI_API_KEY=AIzaSxxx...
OPS_CODE=OPS
SUPER_OPS_CODE=SUPER_OPS_2025
FLASK_SECRET_KEY=some-random-secret-key-12345
FLASK_ENV=development
FLASK_DEBUG=True
```

---

## Step 9: Verify Database Setup

Go to Supabase **Table Editor** and check:

✅ `user_profiles` table exists
✅ `platform_settings` table exists with 1 row (active_referral_code = "LAUNCH_2025")
✅ `admin_actions` table exists (empty)
✅ `connections` table exists (empty)
✅ `chat_sessions` table exists (empty)
✅ `chat_messages` table exists (empty)

---

## Step 10: Verify Storage Buckets

Go to Supabase **Storage** and check:

✅ `resumes` bucket exists (private)
✅ `profile-images` bucket exists (public)

---

## Troubleshooting

### "Cannot read property 'anon' of undefined"
- Make sure you ran the full SQL schema in the SQL Editor
- Check that pgvector extension was enabled

### "Invalid API key"
- Double-check you copied the full key (they're very long!)
- Make sure there are no extra spaces before/after the key in .env

### "Row Level Security policy violation"
- The RLS policies are set up in the schema
- If you get this error, verify the schema ran successfully

---

## What's Next?

Once you've completed all these steps and confirmed your `.env` file has all the API keys, let me know and we'll continue with:

1. Installing the Python dependencies
2. Creating the Flask auth endpoints
3. Building the login/signup pages
4. Testing the authentication flow

**Ready to continue? Just say "Done with Supabase setup!" and we'll move forward.**
