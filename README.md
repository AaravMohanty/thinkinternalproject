# THINKedIn

The exclusive alumni networking platform for Purdue THINK members. Connect, learn, and grow your professional network.

## Quick Start

### One-Time Setup for Auto-Updates ⚡

Run this **ONCE** after cloning to enable automatic dependency installation:

**Mac/Linux:**
```bash
./setup-hooks.sh
```

**Windows:**
```bash
setup-hooks.bat
```

After this setup, **every time you `git pull`**, dependencies will automatically install if they changed! 🚀

#### Manual Update (if you prefer)
If you don't want auto-updates, you can manually run:
```bash
./update.sh     # Mac/Linux
update.bat      # Windows
```

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### 1. Clone the repository
```bash
git clone https://github.com/AaravMohanty/THINKInternalProject.git
cd THINKInternalProject
```

### 2. Set up the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up the Frontend
```bash
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```
Backend runs on http://localhost:5001

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on http://localhost:5173

### 5. Open in Browser
Navigate to http://localhost:5173

## Features

- **Alumni Directory** - Browse and search THINK alumni with advanced filters
- **AI-Powered Matching** - Get personalized alumni recommendations
- **The THINKer Chatbot** - AI networking advisor for guidance
- **AI Email Generator** - Generate personalized outreach emails
- **Profile Management** - Update your information and photo
- **Admin Dashboard** - Manage members and referral codes (Directors only)

## Tech Stack

- **Frontend:** React + Vite
- **Backend:** Flask (Python)
- **Database:** Supabase (PostgreSQL)
- **AI:** Google Gemini 2.5 Flash
- **Styling:** Custom CSS with dark theme

## Environment Variables

The `.env` file is included with shared API keys. If you need to use your own:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
GEMINI_API_KEY=your_gemini_api_key
```

## Project Structure

```
THINKInternalProject/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── services/           # Business logic services
│   ├── migrations/         # Database migrations
│   └── scripts/            # Utility scripts
├── frontend/
│   ├── src/
│   │   ├── pages/          # React page components
│   │   ├── components/     # Reusable components
│   │   ├── styles/         # CSS stylesheets
│   │   ├── context/        # React context (Auth)
│   │   └── utils/          # API utilities
│   └── public/             # Static assets
└── README.md
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test locally
4. Push and create a pull request

## Team

Built by Purdue THINK
