"""
Configuration module for PurdueTHINK Internal Networking Tool
Loads environment variables and provides configuration constants
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the root project directory (parent of backend/)
ROOT_DIR = Path(__file__).parent.parent

# Load environment variables from .env file in project root
load_dotenv(ROOT_DIR / '.env')

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Referral Code Configuration
OPS_CODE = os.getenv('OPS_CODE', 'OPS')
SUPER_OPS_CODE = os.getenv('SUPER_OPS_CODE', 'SUPER_OPS_2025')

# Flask Configuration
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'

# File Upload Configuration
MAX_RESUME_SIZE_MB = 5
ALLOWED_RESUME_EXTENSIONS = {'pdf', 'docx'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# AI Configuration
GEMINI_MODEL = 'gemini-2.5-flash'  # Gemini 2.5 Flash
EMBEDDING_MODEL = 'models/text-embedding-004'
MAX_EMAIL_DRAFTS_PER_DAY = 10
MAX_CHAT_MESSAGES_PER_DAY = 50

# Cache Configuration
SUGGESTION_CACHE_TTL = 86400  # 24 hours in seconds

def validate_config():
    """Validate that all required environment variables are set"""
    required_vars = {
        'SUPABASE_URL': SUPABASE_URL,
        'SUPABASE_KEY': SUPABASE_KEY,
        'SUPABASE_SERVICE_KEY': SUPABASE_SERVICE_KEY,
        'GEMINI_API_KEY': GEMINI_API_KEY,
    }

    missing = [key for key, value in required_vars.items() if not value]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please copy .env.example to .env and fill in your API keys."
        )

    return True

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
