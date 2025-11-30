# THINKedIn - Quick Start Guide

## Current Status
✅ **Phase 2.3 Complete** - Profile Editor fully implemented
- Authentication system ready
- Profile editing with live preview
- Resume upload backend ready
- Gemini AI integration ready
- Backend API endpoints complete

## Running the Application

### 1. Start the Backend Server

```bash
cd backend
source ../venv/bin/activate
python app.py
```

The backend will start on `http://localhost:5001`

### 2. Open the Frontend

Open `frontend/login.html` in your browser to access the application.

Available pages:
- `login.html` - Login page
- `signup.html` - Multi-step signup with resume upload
- `home.html` - Networking home (coming soon - currently shows alumni from CSV)
- `profile.html` - Profile editor with live preview ✨ NEW!

### 3. Test the Profile Editor

1. Go to `login.html` and login with your credentials
2. Navigate to `profile.html`
3. Edit your profile information
4. See the live preview update in real-time
5. Click "Save Changes" to persist your updates

## What's Working

### ✅ Backend (Phase 1-2)
- **Authentication**: Signup, login, logout, session management
- **Profile Management**: GET, PUT `/api/profile`
- **Resume Upload**: POST `/api/resume/upload` (with Gemini AI parsing)
- **Admin Endpoints**: Referral codes, member management, audit logs
- **Supabase Integration**: Database, storage, auth

### ✅ Frontend (Phase 1-2)
- **Login Page** (`login.html`) - Liquid-glass design
- **Signup Flow** (`signup.html`) - 3-step process
- **Profile Editor** (`profile.html`) - Full CRUD with live preview
- **Auth Utilities** (`auth.js`) - JWT management, session handling

## What's Next (Phase 3+)

According to PLAN.md, the next steps are:

### Phase 3: AI Matching & Networking Home
- Generate embeddings for all user profiles
- Build AI matching algorithm with weighted scoring
- Create "Top 8 Matches" feature
- Transform index.html to authenticated home.html
- Add member search and filters

### Phase 4: AI Email Generator
- Generate personalized networking emails
- mailto: integration with pre-filled content

### Phase 5: AI Chatbot
- Floating chat widget on all pages
- AI networking advisor

### Phase 6: Admin Dashboard
- Full admin UI for directors
- Member management interface
- Audit log viewer

### Phase 7: Polish & Launch
- Error handling and UX improvements
- Mobile responsiveness
- Testing and deployment

## Database Setup

Your Supabase database is already configured with:
- ✅ Tables created (`user_profiles`, `platform_settings`, etc.)
- ✅ Storage buckets (`resumes`, `profile-images`)
- ✅ API keys configured in `.env`

## Environment Variables

Your `.env` file is configured with:
```
SUPABASE_URL=https://umrtpxgumehnsbwmbknb.supabase.co
SUPABASE_KEY=<your-key>
SUPABASE_SERVICE_KEY=<your-service-key>
GEMINI_API_KEY=<your-gemini-key>
FLASK_SECRET_KEY=<generated>
```

## Troubleshooting

### Backend won't start
```bash
# Make sure you're in the venv
cd /path/to/project
source venv/bin/activate
cd backend
python app.py
```

### "Module not found" errors
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Profile won't save
- Check that backend is running on port 5001
- Check browser console for errors
- Verify JWT token in localStorage (`think_auth_token`)

## Development Notes

### File Structure
```
THINKInternalProject/
├── backend/
│   ├── app.py                 # Main Flask app
│   ├── config.py              # Environment config
│   ├── middleware.py          # Auth middleware
│   ├── services/
│   │   ├── auth.py            # Authentication service
│   │   └── gemini_service.py  # AI resume parsing
│   └── requirements.txt
├── frontend/
│   ├── login.html
│   ├── signup.html
│   ├── profile.html           # ✨ NEW
│   ├── scripts/
│   │   ├── auth.js            # Auth utilities
│   │   ├── signup.js          # Signup logic
│   │   └── profile.js         # ✨ NEW - Profile editor
│   └── styles/
│       └── global.css         # Shared styles
├── venv/                      # Python virtual environment
├── .env                       # Environment variables
├── PLAN.md                    # Full project roadmap
└── QUICKSTART.md             # This file
```

### API Endpoints

**Auth**
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `GET /auth/session` - Get current user

**Profile**
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `POST /api/resume/upload` - Upload & parse resume

**Admin** (Directors only)
- `GET /admin/settings` - Get platform settings
- `PUT /admin/settings/referral-code` - Update referral code
- `GET /admin/members` - List all members
- `DELETE /admin/members/<id>` - Remove member
- `POST /admin/promote-director/<id>` - Promote to director
- `POST /admin/demote-director/<id>` - Demote from director
- `GET /admin/audit-log` - View audit log

## Next Session Tasks

Ready to continue building! Here are the recommended next steps:

1. **Test the full auth flow**
   - Sign up a test user
   - Upload a resume
   - Edit profile

2. **Start Phase 3: AI Matching**
   - Create `embedding_service.py`
   - Generate embeddings for users
   - Build matching algorithm
   - Transform `index.html` to authenticated `home.html`

3. **Or continue with other features**
   - Admin dashboard UI
   - Email generation
   - Chatbot

See PLAN.md for detailed implementation steps for each phase!

---

**Last Updated**: 2025-11-18
**Current Phase**: Phase 2 Complete ✅
**Next Phase**: Phase 3 - AI Matching & Networking Home
