# PurdueTHINK Internal Networking Tool - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Backend API Reference](#backend-api-reference)
6. [Database Schema](#database-schema)
7. [Authentication System](#authentication-system)
8. [Alumni Data Flow](#alumni-data-flow)
9. [Profile Image Caching System](#profile-image-caching-system)
10. [AI Features](#ai-features)
11. [Frontend Components](#frontend-components)
12. [Setup Instructions](#setup-instructions)
13. [Environment Variables](#environment-variables)
14. [Deployment Guide](#deployment-guide)
15. [Common Issues & Troubleshooting](#common-issues--troubleshooting)

---

## Project Overview

**THINKedIn** is an internal networking platform for PurdueTHINK Consulting members and alumni. It allows members to:

- Browse and search the alumni network
- View alumni profiles with their career information
- Sign up using referral codes (controlled by Directors of Operations)
- Upload resumes for AI-powered profile extraction
- Connect with alumni through LinkedIn and email

### Key Features
- **Alumni Directory**: Searchable database of 160+ alumni with filters for major, graduation year, company, and industry
- **Referral-Based Signups**: Only users with valid referral codes can create accounts
- **Director of Operations Role**: Admin users who can manage referral codes and members
- **AI Resume Parsing**: Gemini AI extracts profile information from uploaded resumes
- **Profile Image Caching**: LinkedIn profile images are cached locally to avoid expiration issues

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   HTML/CSS  │  │   Vanilla   │  │     React (WIP)         │ │
│  │   Pages     │  │   JavaScript│  │  frontend-react/        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND (Port 5001)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   app.py    │  │  middleware │  │      services/          │ │
│  │  (Routes)   │  │  (Auth)     │  │  auth.py, gemini.py     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Supabase      │ │   Local CSV     │ │   Gemini AI     │
│   (PostgreSQL)  │ │   Alumni Data   │ │   (Resume Parse)│
│   - Auth        │ │   gdrive_alumni │ │   - Embeddings  │
│   - Profiles    │ │   .csv          │ │   - Chat        │
│   - Storage     │ │                 │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Tech Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | Flask 3.0 | REST API server |
| Database | Supabase (PostgreSQL) | User auth, profiles, admin actions |
| Alumni Data | CSV (local file) | Primary alumni directory data |
| AI/ML | Google Gemini API | Resume parsing, embeddings, chat |
| Auth | Supabase Auth + JWT | User authentication |
| Image Storage | Local Cache + Supabase Storage | Profile images |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| HTML/CSS | Vanilla | Current production frontend |
| JavaScript | Vanilla ES6 | Client-side logic |
| React (WIP) | Vite + React | Future frontend (in development) |
| Styling | Custom CSS | Modern dark theme UI |

### Infrastructure
| Component | Technology | Purpose |
|-----------|------------|---------|
| Cloud Database | Supabase | Auth, profiles, storage |
| File Storage | Supabase Storage | Resumes, profile images |
| Version Control | Git/GitHub | Source code management |

---

## Project Structure

```
THINKInternalProject/
├── backend/
│   ├── app.py                    # Main Flask application (all routes)
│   ├── config.py                 # Environment config and constants
│   ├── middleware.py             # Auth decorators (@require_auth, @require_director)
│   ├── requirements.txt          # Python dependencies
│   ├── database_schema.sql       # Supabase database schema
│   ├── cached_images/            # Locally cached profile images
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py               # Supabase auth functions
│   │   ├── gemini_service.py     # AI features (resume parsing, embeddings)
│   │   └── alumni_matcher.py     # CSV-to-profile matching logic
│   ├── migrations/               # SQL migration scripts
│   │   ├── add_onboarding_completed.sql
│   │   ├── add_csv_linking_fields.sql
│   │   └── change_to_multiple_companies_roles.sql
│   └── scripts/                  # Utility scripts
│       ├── confirm_all_users.py
│       ├── check_user_status.py
│       └── migrate_alumni.py
│
├── frontend/                     # Production frontend
│   ├── home.html                 # Alumni directory page
│   ├── login.html                # Login page
│   ├── signup.html               # Signup page
│   ├── profile.html              # User profile page
│   ├── onboarding.html           # New user onboarding
│   ├── forgot-password.html      # Password reset request
│   ├── reset-password.html       # Password reset form
│   ├── auth.html                 # Auth callback handler
│   ├── styles/
│   │   ├── global.css            # Global styles
│   │   └── people.css            # Alumni cards styles
│   ├── scripts/
│   │   ├── auth.js               # Auth utility module
│   │   ├── alumni.js             # Alumni directory logic
│   │   ├── profile.js            # Profile page logic
│   │   ├── signup.js             # Signup form handling
│   │   └── main.js               # Common utilities
│   └── assets/                   # Images, logos
│
├── frontend-react/               # React frontend (WIP)
│   ├── src/
│   │   ├── styles/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
│
├── .env                          # Environment variables (not in git)
├── .env.example                  # Example environment file
├── gdrive_alumni.csv             # Alumni CSV data (from Google Drive)
└── documentation.md              # This file
```

---

## Backend API Reference

### Base URL
```
http://localhost:5001
```

### Public Endpoints

#### Health Check
```http
GET /api/health
```
Returns: `{"status": "healthy"}`

#### Get Alumni
```http
GET /api/alumni
GET /api/alumni?name=John&company=Google&major=CS&grad_year=2023
```
Returns list of alumni with optional filtering.

**Response:**
```json
{
  "success": true,
  "count": 164,
  "data": [
    {
      "name": "John Doe",
      "role_title": "Software Engineer",
      "company": "Google",
      "major": "Computer Science",
      "grad_year": "2023",
      "location": "San Francisco, CA",
      "profile_image_url": "abc123.jpg",
      "linkedin": "https://linkedin.com/in/johndoe",
      "email": "john@example.com"
    }
  ]
}
```

#### Get Filter Options
```http
GET /api/filters
```
Returns available filter values (majors, years, companies, industries).

#### Get Cached Image
```http
GET /api/cached-image/<filename>
```
Serves locally cached profile images.

#### Cache All Images (Admin)
```http
POST /api/cache-all-images
```
Downloads and caches all LinkedIn profile images from CSV. Call this when updating alumni data.

### Authentication Endpoints

#### Signup
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "referral_code": "LAUNCH_2025",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```
Returns JWT token in `user.session.access_token`.

#### Logout
```http
POST /auth/logout
Authorization: Bearer <token>
```

#### Forgot Password
```http
POST /auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Update Password
```http
POST /auth/update-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "newpassword"
}
```

### Protected Endpoints (Require Auth)

#### Get Profile
```http
GET /api/profile
Authorization: Bearer <token>
```

#### Update Profile
```http
PUT /api/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "major": "Computer Science",
  "graduation_year": 2023,
  "companies": ["Google", "Meta"],
  "roles": ["Software Engineer", "Intern"],
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "onboarding_completed": true
}
```

#### Upload Resume
```http
POST /api/resume/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

resume: <PDF file>
```
Uploads resume, parses with Gemini AI, and updates profile.

### Admin Endpoints (Require Director Role)

#### Get Platform Settings
```http
GET /admin/settings
Authorization: Bearer <token>
```

#### Update Referral Code
```http
PUT /admin/settings/referral-code
Authorization: Bearer <token>
Content-Type: application/json

{
  "referral_code": "NEW_CODE_2025"
}
```

#### Get All Members
```http
GET /admin/members
Authorization: Bearer <token>
```

#### Remove Member
```http
DELETE /admin/members/<user_id>
Authorization: Bearer <token>
```

#### Promote to Director
```http
POST /admin/promote-director/<user_id>
Authorization: Bearer <token>
```

#### Demote Director
```http
POST /admin/demote-director/<user_id>
Authorization: Bearer <token>
```

#### Get Audit Log
```http
GET /admin/audit-log?limit=100
Authorization: Bearer <token>
```

---

## Database Schema

### Supabase Tables

#### user_profiles
Main table for user profile data.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | References auth.users (unique) |
| full_name | TEXT | User's full name |
| profile_image_url | TEXT | Profile image URL or cached filename |
| major | TEXT | Academic major |
| graduation_year | INTEGER | Graduation year |
| current_company | TEXT | Current company (deprecated, use companies[]) |
| current_title | TEXT | Current job title (deprecated, use roles[]) |
| companies | TEXT[] | Array of companies |
| roles | TEXT[] | Array of job roles |
| location | TEXT | Current location |
| linkedin_url | TEXT | LinkedIn profile URL |
| personal_email | TEXT | Personal email |
| professional_email | TEXT | Work email |
| phone | TEXT | Phone number |
| resume_url | TEXT | Uploaded resume URL |
| bio | TEXT | User bio |
| raw_resume_text | TEXT | Extracted resume text |
| career_interests | TEXT[] | Career interest areas |
| target_industries | TEXT[] | Target industries |
| target_companies | TEXT[] | Target companies |
| resume_embedding | vector(768) | AI embedding for matching |
| is_alumni | BOOLEAN | Is this an alumni |
| is_director | BOOLEAN | Is Director of Operations |
| visibility | TEXT | Profile visibility setting |
| signup_referral_code | TEXT | Code used to sign up |
| onboarding_completed | BOOLEAN | Has completed onboarding |
| is_csv_linked | BOOLEAN | Linked to CSV record |
| csv_source_id | INTEGER | Index in CSV file |
| csv_match_type | TEXT | How the CSV match was found |
| csv_match_confidence | FLOAT | Match confidence score |
| created_at | TIMESTAMP | Account creation time |
| updated_at | TIMESTAMP | Last update time |

#### platform_settings
Single-row table for platform configuration.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Always 1 (enforced) |
| active_referral_code | TEXT | Current valid referral code |
| updated_by | UUID | Last user to update |
| updated_at | TIMESTAMP | Last update time |

#### admin_actions
Audit log for administrative actions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| director_user_id | UUID | Director who performed action |
| action_type | TEXT | Type of action (SET_REFERRAL_CODE, REMOVE_MEMBER, etc.) |
| target_user_id | UUID | User affected (if applicable) |
| details | JSONB | Additional action details |
| timestamp | TIMESTAMP | When action occurred |

#### connections
Track networking connections between users.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | User who initiated |
| target_user_id | UUID | User being connected to |
| email_drafted_at | TIMESTAMP | When email was drafted |
| connection_made_at | TIMESTAMP | When connection was made |
| notes | TEXT | User notes |

---

## Authentication System

### Flow
1. **Signup**: User provides email, password, referral code, and name
2. **Referral Validation**: System checks code against `platform_settings.active_referral_code` or special codes (OPS_CODE, SUPER_OPS_CODE)
3. **Account Creation**: Supabase creates auth user with auto-confirmed email
4. **Profile Creation**: User profile record created in `user_profiles`
5. **Login**: Returns JWT access token stored in localStorage

### Special Referral Codes
- `OPS_CODE` (env var): Creates Director of Operations account
- `SUPER_OPS_CODE` (env var): Creates Director of Operations account
- Platform code (in database): Creates regular member account

### Token Storage (Frontend)
```javascript
// Token stored in localStorage
localStorage.setItem('think_auth_token', token);
localStorage.setItem('think_user_data', JSON.stringify(userData));
```

### Auth Middleware (Backend)
```python
@require_auth        # Validates JWT, adds current_user to kwargs
@require_director    # Checks is_director flag
```

---

## Alumni Data Flow

### Data Sources
1. **CSV File** (`gdrive_alumni.csv`): Primary source with 160+ alumni records from LinkedIn scraping
2. **Supabase `user_profiles`**: User-created profiles with editable data

### How Alumni Data is Loaded

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Local CSV     │ ──► │  load_alumni_   │ ──► │  process_       │
│   (Priority 1)  │     │  data()         │     │  linkedin_csv() │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Google Drive  │     │  Merge with     │     │  Look up cached │
│   (Fallback)    │     │  user_profiles  │     │  images by hash │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### CSV Columns Used
| CSV Column | Mapped To | Description |
|------------|-----------|-------------|
| Name | name | Full name |
| linkedinProfileUrl | linkedin | LinkedIn URL |
| Personal Gmail | email | Personal email |
| professionalEmail | professional_email | Work email |
| Grad Yr | grad_year | Graduation year |
| Major | major | Academic major |
| linkedinJobTitle | role_title | Current job title |
| companyName | company | Current company |
| companyIndustry | company_industry | Industry |
| location | location | Location |
| linkedinHeadline | headline | LinkedIn headline |
| linkedinProfileImageUrl | linkedin_image_url | Profile image URL |

### CSV-to-Profile Linking

When a user completes onboarding, the system tries to match them with existing CSV records:

1. **Name Matching**: Finds records with >85% name similarity
2. **Email Disambiguation**: If multiple name matches, uses email to disambiguate
3. **Linking**: If match found, user profile is linked to CSV record via `csv_source_id`
4. **Display**: Linked profiles show user's editable data; unlinked show CSV data

---

## Profile Image Caching System

### Problem
LinkedIn profile image URLs contain expiration tokens and expire after ~30 days.

### Solution
Images are downloaded and cached locally when:
1. `POST /api/cache-all-images` is called
2. Custom URL overrides are processed in `load_alumni_data()`

### How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  LinkedIn URL   │ ──► │  MD5 Hash URL   │ ──► │  Download &     │
│  (with expiry)  │     │  → filename     │     │  Save to disk   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  cached_images/                                                 │
│  ├── 4c89237b960c3578fa9c15a5efe6b1e9.jpg                      │
│  ├── 318e50e5cbff42f16a70ecbfc3d81d4f.jpg                      │
│  └── ...                                                        │
└─────────────────────────────────────────────────────────────────┘
```

### Cache Workflow
1. **Hash URL**: `md5(linkedin_image_url)` → `abc123.jpg`
2. **Check Cache**: Look for `cached_images/abc123.jpg`
3. **Download if missing**: Fetch from LinkedIn with browser headers
4. **Serve**: `/api/cached-image/abc123.jpg`

### Frontend Integration
```javascript
// In alumni.js createAlumniCard()
if (isCachedImage) {
  const cachedImageUrl = `${API_BASE_URL}/cached-image/${profileImage}`;
  // Use this URL for img src
}
```

### Refreshing Cache
```bash
# Call this after updating CSV data
curl -X POST http://localhost:5001/api/cache-all-images
```

---

## AI Features

### Gemini Integration
The project uses Google Gemini API for AI-powered features.

### 1. Resume Parsing
```python
from services.gemini_service import parse_resume

result = parse_resume(resume_text)
# Returns structured data: name, email, major, skills, work_experience, etc.
```

### 2. Profile Embeddings
```python
from services.gemini_service import generate_profile_embedding

embedding = generate_profile_embedding(user_profile, resume_text)
# Returns 768-dimensional vector for similarity matching
```

### 3. Networking Email Generation
```python
from services.gemini_service import generate_networking_email

email = generate_networking_email(sender_profile, recipient_profile)
# Returns { subject: "...", body: "..." }
```

### 4. Chat Assistant (Future)
```python
from services.gemini_service import chat_response

response = chat_response(user_message, conversation_history, context)
```

### Configuration
```python
# config.py
GEMINI_MODEL = 'gemini-2.5-flash-lite'  # Free tier model
EMBEDDING_MODEL = 'models/text-embedding-004'
```

---

## Frontend Components

### Pages

| Page | File | Purpose |
|------|------|---------|
| Login | `login.html` | User authentication |
| Signup | `signup.html` | New user registration |
| Home/Alumni | `home.html` | Alumni directory with filters |
| Profile | `profile.html` | User profile management |
| Onboarding | `onboarding.html` | New user setup wizard |
| Forgot Password | `forgot-password.html` | Password reset request |
| Reset Password | `reset-password.html` | Password reset form |

### JavaScript Modules

#### auth.js
```javascript
const Auth = {
  setToken(token),
  getToken(),
  clearToken(),
  setUserData(userData),
  getUserData(),
  isAuthenticated(),
  isDirector(),
  async login(email, password),
  async signup(signupData),
  async logout(),
  async getCurrentUser(),
  async authenticatedFetch(endpoint, options),
  requireAuth(),
  requireDirector(),
  async init()
};
```

#### alumni.js
Handles the alumni directory:
- Fetches alumni data from API
- Implements filtering and sorting
- Renders alumni cards
- Handles profile image display with cache fallback

### CSS Architecture
- **global.css**: Base styles, colors, typography, animations
- **people.css**: Alumni cards, filters sidebar, grid layout

### Design System
- **Primary Color**: Gold (#CFB991)
- **Background**: Dark gradient (0a0b0f to 1a1b23)
- **Font**: Inter
- **Card Style**: Semi-transparent glass effect with blur

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ (for React frontend)
- Supabase account
- Google AI Studio account (for Gemini API)

### 1. Clone Repository
```bash
git clone https://github.com/AaravMohanty/THINKInternalProject.git
cd THINKInternalProject
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Set Up Supabase
1. Create project at https://supabase.com
2. Go to SQL Editor and run `backend/database_schema.sql`
3. Enable Email Auth in Authentication > Providers
4. Create storage buckets: `resumes`, `profile-images`

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 6. Cache Profile Images
```bash
# Start server first
source venv/bin/activate
cd backend
python app.py &

# Then cache images
curl -X POST http://localhost:5001/api/cache-all-images
```

### 7. Start Development
```bash
# Backend (in backend/)
python app.py

# Frontend (in frontend/)
# Use any static server, e.g.:
python -m http.server 8000
```

### 8. Access Application
- Frontend: http://localhost:8000
- Backend API: http://localhost:5001

---

## Environment Variables

Create `.env` in project root:

```bash
# Supabase Configuration (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Gemini AI Configuration (Required)
GEMINI_API_KEY=your-gemini-api-key

# Referral Code Configuration
OPS_CODE=OPS                    # Creates Director account
SUPER_OPS_CODE=SUPER_OPS_2025   # Creates Director account

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_DEBUG=True
```

### Getting API Keys

#### Supabase
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to Settings > API
4. Copy: Project URL, anon public key, service_role key

#### Gemini
1. Go to https://aistudio.google.com/
2. Get API key from API Keys section
3. Use `gemini-2.5-flash-lite` (free tier)

---

## Deployment Guide

### Production Considerations

1. **Environment**: Set `FLASK_ENV=production`, `FLASK_DEBUG=False`
2. **Secret Key**: Generate strong random `FLASK_SECRET_KEY`
3. **CORS**: Update CORS origins in `app.py` for your domain
4. **HTTPS**: Use reverse proxy (nginx) with SSL certificate
5. **Database**: Supabase handles this, ensure RLS policies are enabled
6. **Static Files**: Host frontend on CDN/static hosting (Vercel, Netlify)

### Deployment Options

#### Backend (Flask)
- **Heroku**: Add `Procfile` with `web: gunicorn app:app`
- **Railway**: Connect GitHub repo, set env vars
- **AWS/GCP**: Use App Engine or EC2

#### Frontend
- **Vercel**: Deploy frontend/ folder
- **Netlify**: Deploy frontend/ folder
- **GitHub Pages**: For static HTML

### Sample Procfile (Heroku)
```
web: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
```

---

## Common Issues & Troubleshooting

### Profile Images Not Loading
1. **Check cache**: `ls backend/cached_images/`
2. **Re-cache images**: `curl -X POST http://localhost:5001/api/cache-all-images`
3. **Verify CSV**: Ensure `linkedinProfileImageUrl` column has valid URLs

### Authentication Errors
1. **Check token**: Verify `think_auth_token` in localStorage
2. **Check Supabase**: Verify user exists in Authentication > Users
3. **Check profile**: Verify user_profiles record exists

### "No module named 'flask'" Error
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CORS Errors
Add your frontend URL to CORS config in `app.py`:
```python
CORS(app, origins=['http://localhost:8000', 'https://yourdomain.com'])
```

### Supabase Connection Issues
1. Check `.env` has correct `SUPABASE_URL` and keys
2. Verify RLS policies allow the operation
3. Check Supabase dashboard for rate limits

### CSV Data Not Updating
1. Download new CSV from Google Drive
2. Replace `gdrive_alumni.csv`
3. Re-cache images: `curl -X POST http://localhost:5001/api/cache-all-images`
4. Restart backend server

---

## Contributing

### Code Style
- Python: Follow PEP 8
- JavaScript: Use ES6+ features
- CSS: BEM naming convention

### Git Workflow
1. Create feature branch from `main`
2. Make changes
3. Test locally
4. Create pull request
5. Get review from team member

### Testing
```bash
# Backend
cd backend
python -m pytest tests/

# Manual API testing
curl http://localhost:5001/api/health
```

---

## Contact & Support

- **Project Lead**: Aarav Mohanty
- **Repository**: https://github.com/AaravMohanty/THINKInternalProject
- **Issues**: Create GitHub issue for bugs/features

---

*Last Updated: November 2025*
