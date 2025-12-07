# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

THINKedIn is an alumni networking platform for Purdue THINK members. It connects students with alumni through an AI-powered directory, chatbot advisor, and personalized recommendations.

## Development Commands

### Running Locally

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```
Backend runs on http://localhost:5001

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```
Frontend runs on http://localhost:5173

### Setup (First Time Only)
```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Build for Production
```bash
cd frontend && npm run build
```

## Architecture

### Tech Stack
- **Frontend:** React 18 + Vite + React Router DOM
- **Backend:** Flask (single app.py ~2800 lines)
- **Database:** Supabase (PostgreSQL with pgvector for embeddings)
- **AI:** Google Gemini 2.5 Flash for chat, recommendations, and email generation
- **Auth:** Supabase Auth with JWT tokens (access + refresh)

### Data Sources
Alumni data comes from two sources:
1. **CSV file** from Google Drive - contains historical alumni data (read-only, cached)
2. **Supabase `user_profiles` table** - registered users who can update their own profiles

The app merges both: CSV data is displayed with any user-uploaded profile images overlaid.

### Key Backend Patterns

**Authentication:** All protected routes use `@require_auth` decorator which validates JWT tokens via Supabase. The decorator sets `request.user_id` and `request.user_email`.

**Admin Routes:** Protected by checking `is_director` flag on user profile.

**AI Features** (require `GEMINI_API_KEY`):
- `/api/recommendations` - Semantic similarity using embeddings
- `/api/generate-email` - Personalized outreach email drafts
- `/api/chat` - The THINKer chatbot advisor

### Key Frontend Patterns

**Auth Flow:** `AuthContext` manages user state. `apiRequest()` in `utils/api.js` auto-refreshes expired tokens.

**Route Protection:** `ProtectedRoute` wrapper checks auth and redirects to onboarding if `onboarding_completed` is false.

**API Utilities:** All API calls go through typed functions in `utils/api.js`:
- `authAPI` - login, signup, logout, password reset
- `profileAPI` - get/update profile, upload image/resume
- `alumniAPI` - get directory, filters, AI recommendations
- `chatAPI` - send messages, get history
- `adminAPI` - members management, settings (directors only)

### Database Schema (Supabase)

Key tables:
- `user_profiles` - User data with `resume_embedding` vector column for AI matching
- `platform_settings` - Single row with active referral code
- `chat_sessions` / `chat_messages` - Persistent chat history
- `admin_actions` - Audit log for director actions
- `deleted_alumni` - CSV row IDs hidden after user account deletion

Row Level Security (RLS) is enabled. Backend uses `SUPABASE_SERVICE_KEY` to bypass RLS for admin operations.

## Environment Variables

Required in `.env` (root directory) or deployment platform:
```
SUPABASE_URL=
SUPABASE_KEY=          # anon key
SUPABASE_SERVICE_KEY=  # service role key (for admin ops)
GEMINI_API_KEY=
```

Frontend uses `VITE_API_URL` to override backend URL (defaults to localhost:5001).

## Deployment

- **Frontend:** Vercel (root directory: `frontend`)
- **Backend:** Render (uses `Procfile` with gunicorn)

Backend requires `ALLOWED_ORIGINS` env var set to frontend URL with `https://` prefix.

## UI Style Guide

Dark theme with:
- Background: `#030305`
- Primary accent: `#4075C9` (blue)
- Fonts: Playfair Display (headings), Inter (body)
