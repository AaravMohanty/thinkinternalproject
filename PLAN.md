# ThinkDin Implementation Plan

**Project**: ThinkDin - AI-Powered Internal Networking Platform for Purdue Think
**Client**: PlotCode (Purdue's Consulting Club)
**Current Status**: ~40% Complete (Working alumni directory, auth backend ready, Supabase schema deployed)

---

## Architecture Decisions

### Tech Stack
- **Frontend**: Multi-page app (separate HTML files for each section)
- **Backend**: Flask REST API with Supabase
- **Database**: Supabase (PostgreSQL + pgvector for embeddings)
- **AI**: Google Gemini Free API (resume parsing, matching, email generation, chatbot)
- **Auth**: Supabase Auth with JWT tokens
- **Storage**: Supabase Storage (resumes + profile images)

### Key Design Choices
- **Multi-page app**: Separate HTML files (login.html, signup.html, home.html, profile.html, admin.html) - simpler than SPA router
- **All pages require authentication** (except login/signup)
- **Auto-migrate existing CSV alumni** to Supabase user_profiles table
- **Email generation**: AI-generated text pre-filled in mailto: links (opens default email client)
- **Liquid-glass aesthetic**: Futuristic design with glass-morphism effects, maintained across all pages

---

## Current Implementation Status

### ✅ What's Working
- Alumni directory with search and filters (CSV-based)
- Profile image caching system
- Beautiful UI with liquid-glass aesthetic
- Backend auth service (Supabase integration)
- Admin endpoints (backend only)
- Referral code system (backend only)
- Database schema deployed
- pgvector extension enabled

### ⚠️ Partially Complete
- Authentication system (backend ready, no frontend)
- Supabase database (tables created, not actively used)

### ❌ Not Built
- Login/signup pages
- Session management in frontend
- Resume upload & parsing
- Profile editor
- AI matching algorithm
- AI email generator
- AI chatbot
- Admin dashboard UI
- Data migration from CSV to Supabase

---

## Phase 1: Authentication & Data Migration (Foundation)

**Goal**: Users can sign up, log in, and existing alumni data is in Supabase

### 1.1 Create Login Page ✅ IN PROGRESS
- [x] Build `frontend/login.html` with email/password form
- [ ] Create `frontend/scripts/auth.js` for session management
- [ ] Add token storage (localStorage)
- [ ] Redirect to home.html on success
- [ ] Style consistent with liquid-glass aesthetic

**Files**: `frontend/login.html`, `frontend/scripts/auth.js`

### 1.2 Create Signup Flow
- Build `frontend/signup.html`:
  - **Step 1**: Email, password, referral code validation
  - **Step 2**: Resume upload (PDF)
  - **Step 3**: Profile completion form (pre-filled from parsed resume)
- Integrate with existing `/auth/signup` endpoint
- Auto-redirect to profile.html after signup
- Add loading states and error handling

**Files**: `frontend/signup.html`, `frontend/scripts/signup.js`

### 1.3 Session Management
- Create `frontend/scripts/auth.js`:
  - Store/retrieve JWT token (localStorage)
  - Check authentication on page load
  - Redirect to login if unauthenticated
  - Logout function
  - Get current user info
- Add session check to all pages except login/signup
- Add auth header to all API requests

**Files**: `frontend/scripts/auth.js` (shared utility)

### 1.4 CSV to Supabase Migration
- Create `backend/scripts/migrate_alumni.py`:
  - Download Google Drive CSV
  - Transform data to user_profiles schema mapping:
    - `Name` → `full_name`
    - `Personal Gmail` → `personal_email`
    - `Grad Yr` → `graduation_year`
    - `Major` → `major`
    - `linkedinProfileUrl` → `linkedin_url`
    - `linkedinJobTitle` → `current_title`
    - `companyName` → `current_company`
    - `companyIndustry` → career_interests array
    - `location` → `location`
    - `professionalEmail` → `professional_email`
    - `linkedinProfileImageUrl` → `profile_image_url`
  - Create auth users for each alumni (use Supabase Admin API)
  - Generate temporary passwords (or email verification links)
  - Batch insert to Supabase
  - Mark all as `is_alumni=true`
  - Log results (success/errors)
- Run migration once

**Files**: `backend/scripts/migrate_alumni.py`

**Deliverables**:
- Login page (login.html)
- Signup flow (signup.html)
- Auth utilities (auth.js)
- Migration script (migrate_alumni.py)
- All alumni data in Supabase

**Estimated Time**: 3-4 days

---

## Phase 2: Resume Parsing & Profile Management

**Goal**: Users can upload resumes, AI parses them, and users can edit profiles

### 2.1 Gemini API Integration
- Create `backend/services/gemini_service.py`:
  - Initialize Gemini client with API key
  - **Resume parsing function**:
    - Accept PDF file bytes
    - Extract text using PyPDF2
    - Send to Gemini with structured prompt
    - Prompt: "Extract structured information from this resume: work experience, education, skills, clubs, projects, courses. Return as JSON."
    - Parse Gemini response to JSON
    - Return: `{work_experience: [], education: {}, skills: [], clubs: [], projects: [], courses: [], industry_experience: []}`
  - Error handling and retry logic
  - Rate limiting awareness

**Files**: `backend/services/gemini_service.py`

### 2.2 Resume Upload Endpoint
- Add `POST /api/resume/upload` endpoint in `backend/app.py`:
  - Accept PDF file upload (multipart/form-data)
  - Validate file type (PDF only, max 5MB)
  - Upload to Supabase Storage (`resumes` bucket)
  - Get file URL
  - Parse resume using `gemini_service.parse_resume()`
  - Store `raw_resume_text` and `resume_url` in user_profiles
  - Return parsed data as JSON for form pre-fill
- Add authentication requirement (@require_auth)
- Return structured data for frontend

**Endpoint**: `POST /api/resume/upload`
**Files**: `backend/app.py`, update `backend/services/gemini_service.py`

### 2.3 Profile Editor Page
- Build `frontend/profile.html`:
  - Load current user profile data
  - **Editable sections**:
    - Basic Info: name, profile picture, email, phone
    - Academic: major, graduation year
    - Professional: current company, title, location, bio
    - Career: industries of interest, target companies
    - Work Experience: add/edit/remove entries
    - Clubs: add/remove
    - Courses: add/remove
    - Skills: add/remove tags
  - Profile image upload (drag-drop or click)
  - Resume re-upload option (triggers re-parsing)
  - Save button → `PUT /api/profile`
  - Cancel button (discard changes)
- Add `PUT /api/profile` endpoint:
  - Accept JSON with updated profile fields
  - Validate inputs
  - Update user_profiles table
  - Return updated profile

**Files**: `frontend/profile.html`, `frontend/scripts/profile.js`, `backend/app.py`

### 2.4 Live Card Preview Component
- Add real-time "Card Mockup" in profile.html sidebar:
  - Renders exactly as member card appears in home.html
  - Shows: profile picture, name, title, company, major, grad year, industries
  - Updates in real-time as user types in form fields
  - JavaScript event listeners on all form inputs
  - Preview stays fixed/sticky on scroll
- Use same card HTML/CSS as home.html for consistency

**Files**: `frontend/profile.html`, `frontend/scripts/profile.js`, `frontend/styles/profile.css`

**Deliverables**:
- Gemini resume parsing service
- Resume upload API endpoint
- Profile editor page with all fields
- Live card preview
- Profile image upload
- Profile update endpoint

**Estimated Time**: 3-5 days

---

## Phase 3: AI Matching & Networking Home

**Goal**: AI suggests top 8 matched members on Networking Home based on vector similarity + weighted scoring

### 3.1 Generate Embeddings
- Create `backend/services/embedding_service.py`:
  - **Function: `generate_embedding(user_profile)`**:
    - Combine profile data into text:
      ```
      Resume: {raw_resume_text}
      Skills: {skills}
      Industries: {career_interests}
      Experience: {work_experience}
      Clubs: {clubs}
      Major: {major}
      ```
    - Send to Gemini Embedding API (`models/embedding-001`)
    - Returns 768-dimensional vector
    - Store in `resume_embedding` column
  - Batch processing function for all users
- Add endpoint `POST /api/embeddings/generate`:
  - Trigger embedding generation for current user
  - Or batch generate for all users (admin only)
- Add background job or script to generate embeddings for all migrated alumni

**Files**: `backend/services/embedding_service.py`, `backend/app.py`

### 3.2 Matching Algorithm
- Create `backend/services/matching_service.py`:
  - **Function: `get_top_matches(user_id, limit=8)`**:
    - Get user's embedding vector
    - Use pgvector for cosine similarity search:
      ```sql
      SELECT *, resume_embedding <=> user_embedding AS distance
      FROM user_profiles
      WHERE user_id != current_user
      ORDER BY distance ASC
      LIMIT 50
      ```
    - **Weighted scoring system**:
      - Start with: `base_score = (1 - cosine_distance) * 40` (max 40 points from embeddings)
      - Add exact match bonuses:
        - Same target industry: +15 points
        - Same major: +10 points
        - Shared skills (3+ overlap): +10 points
        - Same/similar company: +10 points
        - Shared clubs (2+ overlap): +10 points
        - Class year proximity (within 2 years): +5 points
      - Total possible: 100 points
    - Sort by final score descending
    - Return top 8 members
  - Cache results (5-minute TTL)
- Add endpoint `GET /api/matches`:
  - Returns top 8 matched members for current user
  - Include match score and reasons (for display)

**Files**: `backend/services/matching_service.py`, `backend/app.py`

### 3.3 Transform to Authenticated Networking Home
- Rename `frontend/index.html` → `frontend/home.html`:
  - Add authentication check (redirect to login.html if not authenticated)
  - **New section at top**: "AI Matched For You"
    - Grid of 8 member cards (2x4 grid)
    - Each card shows match percentage and top match reason
    - Example: "85% Match - Same industry & major"
  - Keep existing sections:
    - Search bar
    - Filter sidebar (major, year, company, industry)
    - "All Members" grid (below AI matches)
  - Update API calls:
    - `/api/alumni` → `/api/members` (authenticated endpoint)
    - Add `/api/matches` call on page load
  - Add header navigation:
    - Logo + "ThinkDin" title
    - Nav links: Home | Profile | Admin (if director)
    - User dropdown: Profile, Logout
- Add `GET /api/members` endpoint:
  - Returns all user_profiles (authenticated users only)
  - Supports same filters as old /api/alumni
  - Excludes soft-deleted users

**Files**: `frontend/home.html` (renamed from index.html), `frontend/scripts/home.js` (renamed from alumni.js), `backend/app.py`

**Deliverables**:
- Embedding generation service
- Batch embedding generation for all users
- AI matching algorithm with weighted scoring
- Top 8 matches API endpoint
- Authenticated Networking Home page
- AI match recommendations UI
- Header navigation with user menu

**Estimated Time**: 4-6 days

---

## Phase 4: AI Email Generator

**Goal**: Click email button → AI generates personalized email → opens mailto: with pre-filled content

### 4.1 Email Generation Backend
- Create `backend/services/email_service.py`:
  - **Function: `generate_networking_email(sender_user, recipient_user)`**:
    - Load both user profiles
    - Construct prompt for Gemini:
      ```
      Generate a professional networking email from {sender_name} to {recipient_name}.
      Sender: {sender_title} at {sender_company}, {sender_major} major
      Recipient: {recipient_title} at {recipient_company}, {recipient_major} major

      Shared interests: {shared_industries}, {shared_clubs}

      Email should:
      - Be 3-4 sentences
      - Mention Purdue Think connection
      - Reference 1 specific shared interest or recipient's experience
      - Request a brief conversation/coffee chat
      - Be warm but professional

      Return JSON: {"subject": "...", "body": "..."}
      ```
    - Parse Gemini response
    - Return {subject, body}
  - **Rate limiting**: 10 emails per user per day (track in connections table)
  - Cache generated emails (same pair, 24-hour TTL)
- Add endpoint `POST /api/email/generate`:
  - Body: `{recipient_user_id}`
  - Validate recipient exists
  - Check rate limit
  - Generate email via `email_service`
  - Log in connections table (`email_drafted_at`)
  - Return {subject, body}

**Files**: `backend/services/email_service.py`, `backend/app.py`

### 4.2 Update Member Cards with AI Email
- Modify member card email button in `home.html`:
  - Change from direct mailto: link to click handler
  - **On click**:
    1. Show loading spinner on button
    2. Call `POST /api/email/generate` with recipient's user_id
    3. Wait for response
    4. Construct mailto: link:
       ```javascript
       const mailto = `mailto:${recipient.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
       window.location.href = mailto;
       ```
    5. Open mailto: link (user's default email client opens)
  - Show error toast if rate limit exceeded or generation fails
  - Add subtle animation/feedback

**Files**: `frontend/home.html`, `frontend/scripts/home.js`

**Deliverables**:
- Email generation service with Gemini
- Rate limiting (10/day per user)
- Email generation API endpoint
- Updated member card email buttons
- mailto: link with AI-generated content
- Loading and error states

**Estimated Time**: 1-2 days

---

## Phase 5: AI Chatbot - "Think Networking Advisor"

**Goal**: Floating chat widget on every page, AI answers networking questions and recommends connections

### 5.1 Chat Backend
- Create `backend/services/chat_service.py`:
  - **Initialize Gemini with system prompt**:
    ```
    You are the Think Networking Advisor, an AI assistant for Purdue Think members.

    You help members with:
    - Networking advice and strategies
    - Career guidance
    - Connection recommendations
    - Member profile summaries
    - General questions about Purdue Think

    You have access to:
    - All member profiles and their embeddings
    - Member skills, industries, companies, and experiences
    - Purdue Think networking guidelines

    Guidelines:
    - Be warm, professional, and encouraging
    - Give specific, actionable advice
    - When recommending connections, explain WHY they'd be a good match
    - Reference specific member details when relevant
    - Keep responses concise (3-5 sentences)
    ```
  - **Function: `chat(user_id, message, session_id=None)`**:
    - Create or retrieve chat session
    - Retrieve chat history (last 10 messages)
    - For connection recommendations:
      - Use vector search to find relevant members
      - Include member details in context
    - Send message + history to Gemini
    - Get response
    - Store message and response in chat_messages table
    - Return response
  - **Rate limiting**: 50 messages per user per day
- Add endpoints:
  - `POST /api/chat/message`:
    - Body: `{message, session_id (optional)}`
    - Returns: `{response, session_id}`
  - `GET /api/chat/history?session_id=xxx`:
    - Returns last N messages in session
  - `POST /api/chat/new-session`:
    - Creates new chat session
    - Returns session_id

**Files**: `backend/services/chat_service.py`, `backend/app.py`

### 5.2 Floating Chatbot UI Component
- Create `frontend/components/chatbot.html`:
  - **Floating chat bubble** (bottom-right corner):
    - Icon: speech bubble or robot icon
    - Shows unread indicator (blue dot)
    - Click to expand
  - **Expandable chat window**:
    - Header: "Think Networking Advisor" + minimize/close buttons
    - Message history area (scrollable, auto-scroll to bottom)
    - Input field + send button
    - Typing indicator when AI is responding
  - **Styling**:
    - Glass-morphism effect (consistent with app theme)
    - User messages: right-aligned, blue background
    - AI messages: left-aligned, dark background
    - Smooth animations (slide up/down)
- Create `frontend/scripts/chatbot.js`:
  - Manage chat state (session_id, messages)
  - Send message to `/api/chat/message`
  - Render messages
  - Handle expand/collapse
  - Store session_id in localStorage
  - Auto-load history on expand
- Include chatbot in all authenticated pages:
  - Add `<div id="chatbot-container"></div>` to each page
  - Load chatbot.js on each page
  - Initialize on page load

**Files**: `frontend/components/chatbot.html`, `frontend/scripts/chatbot.js`, `frontend/styles/chatbot.css`

**Deliverables**:
- Chat backend with Gemini integration
- System prompt with networking context
- Chat session management
- Chat message persistence
- Floating chatbot UI component
- Chat history
- Rate limiting
- Chatbot integrated on all pages

**Estimated Time**: 3-4 days

---

## Phase 6: Admin Dashboard

**Goal**: Directors can manage members, update referral codes, and view audit logs

### 6.1 Admin Dashboard Page
- Build `frontend/admin.html`:
  - **Header check**: If `!user.is_director` → redirect to home.html
  - **Tab navigation**:
    - Tab 1: Referral Code Management
    - Tab 2: Member Management
    - Tab 3: Audit Log
    - Tab 4: Platform Stats (optional: member count, activity, etc.)

  - **Tab 1: Referral Code Management**:
    - Display current active referral code (large, copyable)
    - Copy button (copies to clipboard)
    - "Generate New Code" button:
      - Opens modal with input field
      - Suggests random code (e.g., "THINK_SPRING_2026")
      - Confirm button
    - Shows update history (last 5 changes)

  - **Tab 2: Member Management**:
    - Searchable/sortable table of all users:
      - Columns: Profile Pic, Name, Email, Major, Grad Year, Role (Member/Director), Signup Date, Actions
    - Search bar (filters by name, email, major)
    - Sort by: name, signup date, graduation year
    - **Actions dropdown per member**:
      - View Profile (opens profile in modal or new tab)
      - Promote to Director (if member)
      - Demote to Member (if director, can't demote self)
      - Remove Member (soft delete, requires confirmation)
    - Show is_director badge
    - Color-code alumni vs current students

  - **Tab 3: Audit Log**:
    - Paginated table of admin_actions:
      - Columns: Timestamp, Director, Action Type, Target Member, Details
    - Filter by:
      - Action type (dropdown)
      - Date range (date picker)
      - Director (dropdown)
    - Export to CSV button (optional)
    - Auto-refresh every 30 seconds

  - **Styling**: Consistent with liquid-glass theme, professional admin aesthetic

**Files**: `frontend/admin.html`, `frontend/scripts/admin.js`, `frontend/styles/admin.css`

### 6.2 Connect to Existing Admin Endpoints
- Wire up frontend to existing backend endpoints:
  - **Referral Code Management**:
    - `GET /admin/settings` → fetch and display current code
    - `PUT /admin/settings/referral-code` → update code
  - **Member Management**:
    - `GET /admin/members` → populate member table
    - `DELETE /admin/members/<id>` → remove member (confirmation modal first)
    - `POST /admin/promote-director/<id>` → promote (confirmation modal)
    - `POST /admin/demote-director/<id>` → demote (confirmation modal, prevent self-demotion)
  - **Audit Log**:
    - `GET /admin/audit-log?action_type=xxx&start_date=xxx&end_date=xxx` → fetch logs
- Add confirmation modals for destructive actions (remove, promote, demote)
- Add success/error toasts for all actions
- Add loading states

**Files**: `frontend/scripts/admin.js`, `backend/app.py` (endpoints already exist)

### 6.3 Add Admin Link to Navigation
- Update header navigation in all authenticated pages (home.html, profile.html, admin.html):
  - Show "Admin" link only if `user.is_director === true`
  - Fetch user info from `/auth/session` on page load
  - Store is_director in localStorage or session
- Update `frontend/scripts/auth.js`:
  - Add `Auth.getCurrentUser()` function
  - Fetch from `/auth/session`
  - Return {user_id, email, full_name, is_director, profile_image_url}

**Files**: `frontend/home.html`, `frontend/profile.html`, `frontend/scripts/auth.js`

**Deliverables**:
- Admin dashboard page with 3 tabs
- Referral code management UI
- Member management table with actions
- Audit log viewer with filters
- Confirmation modals
- Admin link in navigation (director-only)
- All admin operations functional

**Estimated Time**: 2-3 days

---

## Phase 7: Polish, Testing & Deployment

**Goal**: Production-ready platform with good UX and no critical bugs

### 7.1 Error Handling & UX Improvements
- **Global error handling**:
  - Implement toast notification system:
    - Success (green)
    - Error (red)
    - Warning (yellow)
    - Info (blue)
  - Create `frontend/scripts/notifications.js`
  - Use across all pages
- **Loading states**:
  - Add loading spinners for all async operations
  - Disable buttons during submission
  - Show skeleton loaders for member cards
- **Form validation**:
  - Client-side validation with real-time feedback
  - Server-side validation (already done in backend)
  - Clear error messages
- **Empty states**:
  - No matches found: "No matches yet. Upload your resume to improve matching!"
  - No members: "No members match your filters."
  - No chat history: "Start a conversation with the Think Networking Advisor!"
- **Success confirmations**:
  - Profile updated: "Profile saved successfully!"
  - Referral code updated: "Referral code updated to [CODE]"
  - Member removed: "Member removed successfully"

**Files**: `frontend/scripts/notifications.js`, all existing pages

### 7.2 Mobile Responsiveness
- Test all pages on mobile devices (iPhone, Android)
- Adjustments needed:
  - **Home page**: Stack filters vertically, 1-column card grid on mobile
  - **Profile editor**: Stack form fields vertically
  - **Chatbot**: Adjust positioning for mobile (full-width on small screens)
  - **Admin dashboard**: Horizontal scroll for tables, stacked tabs on mobile
  - **Header navigation**: Hamburger menu for mobile
- Use CSS media queries (already in global.css)
- Test on real devices, not just browser DevTools

**Files**: All CSS files

### 7.3 Security & Performance
- **Security**:
  - Add rate limiting to all AI endpoints (already planned)
  - Input sanitization (escape HTML in user-generated content)
  - SQL injection prevention (use parameterized queries - already done with Supabase)
  - XSS protection (escape user input in frontend)
  - Validate file uploads (type, size limits)
  - Don't commit `.env` file (already in .gitignore)
- **Performance**:
  - Image optimization:
    - Compress profile images on upload (max 500KB)
    - Use WebP format if possible
    - Lazy load member cards (intersection observer)
  - API response caching:
    - Cache matches for 5 minutes
    - Cache member list for 1 minute
    - Cache embeddings (never expire unless profile changes)
  - Minimize API calls:
    - Batch operations where possible
    - Use pagination for large lists (admin member table)
  - Bundle and minify JS/CSS for production (optional)

**Files**: `backend/app.py`, all frontend files

### 7.4 Testing
- **Manual testing checklist**:
  - [ ] Complete signup flow (with resume upload)
  - [ ] Resume parsing accuracy (test with 5+ different resumes)
  - [ ] Login/logout flow
  - [ ] Profile editing (all fields)
  - [ ] AI matching (verify top 8 matches make sense)
  - [ ] Email generation (test with 5+ different pairs)
  - [ ] Chatbot responses (ask 10+ different questions)
  - [ ] Admin operations:
    - [ ] Update referral code
    - [ ] Promote/demote directors
    - [ ] Remove members
    - [ ] View audit log
  - [ ] Mobile responsiveness (all pages)
  - [ ] Error handling (network errors, invalid inputs, rate limits)
  - [ ] Session expiry (logout after token expires)

- **Test data**:
  - Create 10+ test users with varied profiles
  - Upload diverse resumes (different majors, industries, grad years)
  - Test edge cases (empty profile, no resume, etc.)

### 7.5 Documentation
- **Update README.md**:
  - Project overview
  - Features list
  - Tech stack
  - Setup instructions (for developers)
  - Running the app
  - Environment variables
  - Troubleshooting
- **Create USER_GUIDE.md**:
  - How to sign up
  - How to upload resume
  - How to edit profile
  - How to use AI matching
  - How to generate networking emails
  - How to use the chatbot
  - Director guide (admin operations)
- **Create DEPLOYMENT.md**:
  - Production deployment steps
  - Environment variables for production
  - Supabase production setup
  - Domain setup
  - SSL/TLS configuration
  - Monitoring and logging

**Files**: `README.md`, `USER_GUIDE.md`, `DEPLOYMENT.md`

**Deliverables**:
- Toast notification system
- Loading states everywhere
- Form validation
- Empty states
- Mobile responsive design
- Security hardening
- Performance optimizations
- Complete testing
- User documentation
- Developer documentation

**Estimated Time**: 2-3 days

---

## Total Timeline Estimate

**Full-time development (1 developer)**:
- Phase 1: 3-4 days
- Phase 2: 3-5 days
- Phase 3: 4-6 days
- Phase 4: 1-2 days
- Phase 5: 3-4 days
- Phase 6: 2-3 days
- Phase 7: 2-3 days

**Total: 18-27 days** (3.5-5.5 weeks full-time)

**Part-time development (10-20 hours/week)**:
- **Total: 6-10 weeks**

---

## Key Milestones

1. **Milestone 1** (End of Phase 1): Users can sign up and log in, all alumni data migrated
2. **Milestone 2** (End of Phase 2): Users can upload resumes and edit profiles
3. **Milestone 3** (End of Phase 3): AI matching is working, Networking Home is functional
4. **Milestone 4** (End of Phase 4): AI email generation is live
5. **Milestone 5** (End of Phase 5): Chatbot is integrated on all pages
6. **Milestone 6** (End of Phase 6): Admin dashboard is fully functional
7. **Milestone 7** (End of Phase 7): Production-ready platform ready to launch

---

## Risk Mitigation

### Technical Risks
- **Gemini API rate limits**: Implement caching, use batch processing where possible
- **Vector search performance**: Use pgvector indexes (already in schema), limit search space
- **Resume parsing accuracy**: Test with diverse resumes, provide manual edit option
- **Supabase free tier limits**: Monitor usage, plan upgrade if needed (likely needed at ~500+ users)

### Product Risks
- **User adoption**: Need marketing plan from PlotCode
- **Data privacy concerns**: Clear privacy policy, secure data handling
- **Match quality**: Iterate on scoring weights based on user feedback

### Process Risks
- **Scope creep**: Stick to this plan, add features after launch
- **Timeline slippage**: Prioritize Phase 1-4 (core features), Phase 5-6 can launch later

---

## Post-Launch Iterations (Future Enhancements)

After initial launch, consider:
- Email verification (currently disabled for development)
- Password reset flow
- User analytics dashboard (for directors)
- Advanced filters (skills, companies, industries)
- Favorites/bookmarks
- Connection status tracking (pending, accepted, rejected)
- In-app messaging (instead of just email)
- Event integration (Purdue Think events)
- Mobile app (React Native or PWA)
- Slack integration (bot notifications)
- Calendar integration (schedule coffee chats)

---

## Success Metrics

Track after launch:
- **Adoption**: % of Purdue Think members signed up
- **Engagement**: Daily active users, profiles viewed per session
- **Matching**: % of users who draft emails to AI matches
- **Chat**: Chatbot messages per user, satisfaction ratings
- **Retention**: Weekly active users, churn rate

---

## Notes

- **Supabase Setup**: See `SUPABASE_SETUP.md` for detailed Supabase configuration
- **Database Schema**: See `backend/database_schema.sql` for full schema (already deployed)
- **API Keys**: Ensure `.env` file has all required keys (Supabase, Gemini)
- **Git Workflow**: Create feature branches, commit frequently, merge to main when stable

---

**Last Updated**: 2025-11-18
**Status**: Phase 1.1 in progress (login.html created)
