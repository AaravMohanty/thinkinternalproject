"""
PurdueTHINK Alumni Finder - Backend API
----------------------------------------
Flask backend to serve alumni data from Google Drive CSV
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import requests
from io import StringIO
import os
import hashlib
from pathlib import Path

# Import config and authentication services
try:
    import config
    from services.auth import (
        signup_user, login_user, logout_user, refresh_session,
        validate_referral_code, check_is_director, log_admin_action
    )
    from services.auth import supabase, supabase_admin
    from services.storage import (
        download_and_upload_image,
        get_supabase_image_url,
        get_public_url,
        check_image_exists,
        migrate_local_image_to_supabase,
        get_image_hash as storage_get_image_hash,
        PROFILE_IMAGES_BUCKET
    )
    from middleware import require_auth, require_director
    AUTH_ENABLED = True
    SUPABASE_STORAGE_ENABLED = True
except ImportError as e:
    print(f"Warning: Auth modules not available: {e}")
    print("Running in legacy mode without authentication")
    AUTH_ENABLED = False
    SUPABASE_STORAGE_ENABLED = False

app = Flask(__name__)

# CORS configuration - allow frontend origins
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173')
if ALLOWED_ORIGINS == '*':
    CORS(app, supports_credentials=False)  # Allow all origins
else:
    CORS(app, origins=ALLOWED_ORIGINS.split(','), supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

if AUTH_ENABLED:
    app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY

# Google Drive configuration
GOOGLE_DRIVE_FILE_ID = "17nWOQo424w0W6GCTsdP2UxbHQpuQXO5G"
GOOGLE_DRIVE_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"

# Fallback data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
# Use relative path so it works for all users
ALUMNI_CSV = os.path.join(os.path.dirname(__file__), "..", "gdrive_alumni.csv")

# Image cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cached_images")
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

# Seed data
SEED = [
    {
        "name": "Jordan Kim",
        "role_title": "Software Engineer",
        "company": "Stripe",
        "major": "Computer Science",
        "grad_year": "2024",
        "linkedin": "https://www.linkedin.com/in/jordan-kim",
        "email": "jordan.kim@example.com",
        "phone": "(555) 201-0001",
    },
    {
        "name": "Priya Shah",
        "role_title": "Data Scientist",
        "company": "Capital One",
        "major": "Data Science",
        "grad_year": "2023",
        "linkedin": "https://www.linkedin.com/in/priya-shah",
        "email": "priya.shah@example.com",
        "phone": "(555) 201-0002",
    },
    {
        "name": "Miguel Torres",
        "role_title": "Product Manager",
        "company": "Amazon",
        "major": "Industrial Engineering",
        "grad_year": "2022",
        "linkedin": "https://www.linkedin.com/in/miguel-torres",
        "email": "miguel.torres@example.com",
        "phone": "(555) 201-0003",
    },
]


def download_csv_from_google_drive(url):
    """Download CSV from Google Drive and return as DataFrame."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        csv_data = StringIO(response.text)
        return pd.read_csv(csv_data)
    except Exception as e:
        print(f"Failed to download CSV from Google Drive: {e}")
        return None


def get_image_hash(url):
    """Generate a unique filename from image URL."""
    return hashlib.md5(url.encode()).hexdigest()


def download_and_cache_image(image_url, person_name=""):
    """Download image from URL and upload to Supabase Storage. Returns public URL or None."""
    if not image_url or str(image_url).strip() in ['', 'nan', 'null', 'None']:
        return None

    # Use Supabase Storage if available
    if SUPABASE_STORAGE_ENABLED:
        success, filename, public_url = download_and_upload_image(image_url, person_name)
        if success:
            return public_url  # Return full Supabase URL
        return None

    # Fallback to local caching
    try:
        image_hash = get_image_hash(image_url)
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            cached_path = os.path.join(CACHE_DIR, f"{image_hash}{ext}")
            if os.path.exists(cached_path):
                print(f"Using cached image for {person_name}: {image_hash}{ext}")
                return f"{image_hash}{ext}"

        print(f"Downloading image for {person_name}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://www.linkedin.com/'
        }

        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            ext = '.jpg'

        cached_filename = f"{image_hash}{ext}"
        cached_path = os.path.join(CACHE_DIR, cached_filename)

        with open(cached_path, 'wb') as f:
            f.write(response.content)

        print(f"Successfully cached image for {person_name}: {cached_filename}")
        return cached_filename

    except Exception as e:
        print(f"Failed to cache image for {person_name}: {e}")
        return None


def process_linkedin_csv(df):
    """Process LinkedIn CSV format into standard format."""
    df["name"] = df["Name"].fillna("") if "Name" in df.columns else ""

    if "linkedinProfileUrl" in df.columns:
        df["linkedin"] = df["linkedinProfileUrl"].fillna("")
    elif "Linkedin" in df.columns:
        df["linkedin"] = df["Linkedin"].fillna("")
    else:
        df["linkedin"] = ""

    df["email"] = df["Personal Gmail"].fillna("") if "Personal Gmail" in df.columns else ""
    df["professional_email"] = df["professionalEmail"].fillna("") if "professionalEmail" in df.columns else ""
    # Convert grad year to int string (removes .0 from float values like 2026.0)
    if "Grad Yr" in df.columns:
        df["grad_year"] = df["Grad Yr"].apply(lambda x: str(int(float(x))) if pd.notna(x) and str(x).strip() and str(x) != 'nan' else "")
    else:
        df["grad_year"] = ""
    df["major"] = df["Major"].fillna("") if "Major" in df.columns else ""

    if "linkedinJobTitle" in df.columns:
        df["role_title"] = df["linkedinJobTitle"].fillna("")
        if df["role_title"].str.strip().eq("").all() and "linkedinHeadline" in df.columns:
            df["role_title"] = df["linkedinHeadline"].fillna("")
    elif "linkedinHeadline" in df.columns:
        df["role_title"] = df["linkedinHeadline"].fillna("")
    else:
        df["role_title"] = ""

    df["company"] = df["companyName"].fillna("") if "companyName" in df.columns else ""
    df["company_industry"] = df["companyIndustry"].fillna("") if "companyIndustry" in df.columns else ""

    if "location" in df.columns:
        df["location"] = df["location"].fillna("")
    elif "linkedinJobLocation" in df.columns:
        df["location"] = df["linkedinJobLocation"].fillna("")
    else:
        df["location"] = ""

    df["headline"] = df["linkedinHeadline"].fillna("") if "linkedinHeadline" in df.columns else ""

    # Store original LinkedIn image URLs
    if "linkedinProfileImageUrl" in df.columns:
        df["linkedin_image_url"] = df["linkedinProfileImageUrl"].fillna("")
    else:
        df["linkedin_image_url"] = ""

    # Initialize profile_image_url column and populate with cached image URLs
    df["profile_image_url"] = ""

    # Use pre-computed Supabase URLs from CSV if available (preferred method)
    # This ensures consistent URLs regardless of which CSV source is used
    if "supabaseProfileImageUrl" in df.columns:
        df["profile_image_url"] = df["supabaseProfileImageUrl"].fillna("")
    elif "linkedinProfileImageUrl" in df.columns:
        # Fallback: compute Supabase URL from LinkedIn URL (legacy method)
        def get_cached_image_url(image_url):
            if not image_url or str(image_url).strip() in ['', 'nan', 'null', 'None']:
                return ""

            # Use Supabase Storage - fast path (no verification to avoid 640+ API calls)
            # The caching script pre-populates Supabase, frontend handles fallback
            if SUPABASE_STORAGE_ENABLED:
                # verify_exists=False is fast - just generates expected URL
                supabase_url = get_supabase_image_url(str(image_url), verify_exists=False)
                if supabase_url:
                    return supabase_url

            # Fallback to local cache (legacy)
            image_hash = get_image_hash(str(image_url))
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                cached_path = os.path.join(CACHE_DIR, f"{image_hash}{ext}")
                if os.path.exists(cached_path):
                    return f"{image_hash}{ext}"
            return ""

        df["profile_image_url"] = df["linkedinProfileImageUrl"].apply(get_cached_image_url)

    def build_companies_list(row):
        companies = []
        if "companyName" in row and row["companyName"] and str(row["companyName"]).strip():
            companies.append(str(row["companyName"]).strip())
        if "previousCompanyName" in row and row["previousCompanyName"] and str(row["previousCompanyName"]).strip():
            companies.append(str(row["previousCompanyName"]).strip())
        return companies

    df["companies_list"] = df.apply(build_companies_list, axis=1)

    def build_roles_list(row):
        roles = []
        # Current job title
        if "linkedinJobTitle" in row and row["linkedinJobTitle"] and str(row["linkedinJobTitle"]).strip():
            roles.append(str(row["linkedinJobTitle"]).strip())
        # Previous job title
        if "linkedinPreviousJobTitle" in row and row["linkedinPreviousJobTitle"] and str(row["linkedinPreviousJobTitle"]).strip():
            roles.append(str(row["linkedinPreviousJobTitle"]).strip())
        # If no job titles found but we have headline, use that
        if not roles and "linkedinHeadline" in row and row["linkedinHeadline"] and str(row["linkedinHeadline"]).strip():
            roles.append(str(row["linkedinHeadline"]).strip())
        return roles

    df["roles_list"] = df.apply(build_roles_list, axis=1)

    def build_schools_list(row):
        schools = []
        if "linkedinSchoolName" in row and row["linkedinSchoolName"] and str(row["linkedinSchoolName"]).strip():
            schools.append(str(row["linkedinSchoolName"]).strip())
        if "linkedinPreviousSchoolName" in row and row["linkedinPreviousSchoolName"] and str(row["linkedinPreviousSchoolName"]).strip():
            schools.append(str(row["linkedinPreviousSchoolName"]).strip())
        return schools

    df["schools_list"] = df.apply(build_schools_list, axis=1)
    df["phone"] = ""


def load_alumni_data():
    """Load alumni data from local CSV, Google Drive, or seed data."""
    df = None

    # Try local CSV first (has stable URLs for cached images)
    if os.path.exists(ALUMNI_CSV):
        df = pd.read_csv(ALUMNI_CSV)

    # Fall back to Google Drive if local CSV not available
    if df is None and GOOGLE_DRIVE_FILE_ID:
        df = download_csv_from_google_drive(GOOGLE_DRIVE_URL)

    # Use seed data as last resort
    if df is None:
        df = pd.DataFrame(SEED)

    # Process the DataFrame
    if "Name" in df.columns:
        process_linkedin_csv(df)
    else:
        # Add compatibility columns for old format
        if "companies_list" not in df.columns:
            df["companies_list"] = df["company"].apply(lambda x: [x] if x else [])
        if "schools_list" not in df.columns:
            df["schools_list"] = [[] for _ in range(len(df))]
        if "professional_email" not in df.columns:
            df["professional_email"] = ""
        if "company_industry" not in df.columns:
            df["company_industry"] = ""
        if "location" not in df.columns:
            df["location"] = ""
        if "headline" not in df.columns:
            df["headline"] = ""
        if "profile_image_url" not in df.columns:
            df["profile_image_url"] = ""

    # Ensure all required columns exist
    cols = ["name", "role_title", "company", "major", "grad_year", "linkedin", "email", "phone"]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)

    # Remove duplicates
    df = df.drop_duplicates(subset=["name", "email"], keep="first")

    # Remove empty rows
    df = df[df["name"].str.strip() != ""]

    # Custom image mappings for specific alumni (these are local assets, not cached)
    custom_local_images = {
        "Aadit Bennur": "/assets/Aadit.jpeg"
    }

    # Custom LinkedIn URLs to override/add (for testing or fixing specific profiles)
    custom_linkedin_urls = {
        # Removed Aaditya Doiphode - using Supabase saved image instead
    }

    # Apply custom local image mappings
    for name, image_path in custom_local_images.items():
        df.loc[df["name"].str.contains(name, case=False, na=False), "profile_image_url"] = image_path

    # Apply and cache custom LinkedIn URL overrides only
    for name, linkedin_url in custom_linkedin_urls.items():
        mask = df["name"].str.contains(name, case=False, na=False)
        if mask.any():
            # Cache this specific image
            cached_filename = download_and_cache_image(linkedin_url, name)
            if cached_filename:
                df.loc[mask, "profile_image_url"] = cached_filename
                print(f"Cached custom image for {name}")

    return df


def clean_nan_values(data):
    """Recursively replace NaN values with None in data structures."""
    import math
    if isinstance(data, list):
        return [clean_nan_values(item) for item in data]
    elif isinstance(data, dict):
        return {key: clean_nan_values(value) for key, value in data.items()}
    elif isinstance(data, float):
        if math.isnan(data):
            return None
        return data
    elif pd.isna(data):
        return None
    else:
        return data


@app.route('/api/alumni', methods=['GET'])
def get_alumni():
    """Get all alumni or filtered alumni, merging CSV data with user profiles."""
    try:
        # Load CSV data
        csv_df = load_alumni_data()

        # Load all user profiles from Supabase
        try:
            profiles_response = supabase.table('user_profiles').select('*').execute()
            user_profiles = profiles_response.data if profiles_response.data else []
        except:
            user_profiles = []

        # Load deleted alumni IDs to filter them out
        deleted_csv_ids = set()
        try:
            deleted_response = supabase.table('deleted_alumni').select('csv_row_id').execute()
            if deleted_response.data:
                deleted_csv_ids = set(d['csv_row_id'] for d in deleted_response.data)
        except:
            pass  # Table might not exist yet

        # Create a mapping of csv_source_id -> user_profile
        csv_links = {}
        new_user_profiles = []

        for profile in user_profiles:
            if profile.get('is_csv_linked') and profile.get('csv_source_id') is not None:
                # This profile is linked to a CSV record
                csv_links[profile['csv_source_id']] = profile
            elif profile.get('onboarding_completed'):
                # This is a new user not in CSV
                new_user_profiles.append(profile)

        # Merge CSV data with linked profiles
        merged_alumni = []

        for idx, csv_row in csv_df.iterrows():
            # Skip deleted alumni entries
            if idx in deleted_csv_ids:
                continue

            if idx in csv_links:
                # Use user profile data instead of CSV
                profile = csv_links[idx]
                company_val = ', '.join(profile.get('companies', [])) if profile.get('companies') else csv_row.get('company_name', csv_row.get('company', ''))

                # Get profile image - prefer user's profile, fall back to CSV's cached Supabase URL
                # csv_row['profile_image_url'] is the Supabase URL (set by load_alumni_data)
                cached_csv_image = csv_row.get('profile_image_url', '')  # Supabase URL
                profile_img = profile.get('profile_image_url') or cached_csv_image

                merged_alumni.append({
                    'id': f'csv_{idx}',  # Unique ID for frontend key
                    'name': profile.get('full_name', csv_row.get('name')),
                    'role_title': ', '.join(profile.get('roles', [])) if profile.get('roles') else csv_row.get('role_title'),
                    'roles_list': profile.get('roles', []) if profile.get('roles') else csv_row.get('roles_list', []),
                    'headline': profile.get('current_title') or csv_row.get('headline'),
                    'company': company_val,
                    'company_name': company_val,
                    'companies_list': profile.get('companies', []) if profile.get('companies') else csv_row.get('companies_list', []),
                    'company_industry': csv_row.get('company_industry'),
                    'major': profile.get('major', csv_row.get('major')),
                    'grad_year': str(profile.get('graduation_year', csv_row.get('grad_year', ''))),
                    'location': profile.get('location', csv_row.get('location')),
                    'profile_image': profile_img,
                    'profile_image_url': profile_img,
                    'linkedin_url': profile.get('linkedin_url', csv_row.get('linkedin_url')),
                    'linkedin': profile.get('linkedin_url', csv_row.get('linkedin_url')),
                    'email': profile.get('personal_email', csv_row.get('email')),
                    'linkedinProfileImageUrl': '',  # Don't expose raw LinkedIn URLs
                    'linkedin_image_url': '',  # Use Supabase instead
                    'is_linked': True,
                    'source': 'user_profile'
                })
            else:
                # Use CSV data with normalized field names
                # Only use Supabase-cached profile images, not raw LinkedIn URLs (which expire)
                company_val = csv_row.get('company_name', csv_row.get('company', ''))
                cached_image = csv_row.get('profile_image_url', '')  # This is the Supabase URL
                merged_alumni.append({
                    'id': f'csv_{idx}',  # Unique ID for frontend key
                    'name': csv_row.get('name', csv_row.get('Name', '')),
                    'role_title': csv_row.get('role_title', ''),
                    'roles_list': csv_row.get('roles_list', []),
                    'headline': csv_row.get('headline', csv_row.get('linkedinHeadline', '')),
                    'company': company_val,
                    'company_name': company_val,
                    'companies_list': csv_row.get('companies_list', []),
                    'company_industry': csv_row.get('company_industry', csv_row.get('companyIndustry', '')),
                    'major': csv_row.get('major', csv_row.get('Major', '')),
                    'grad_year': str(csv_row.get('grad_year', csv_row.get('Grad Yr', ''))),
                    'location': csv_row.get('location', ''),
                    'profile_image': cached_image,
                    'profile_image_url': cached_image,
                    'linkedin_url': csv_row.get('linkedin_url', csv_row.get('linkedin', csv_row.get('Linkedin', ''))),
                    'linkedin': csv_row.get('linkedin', csv_row.get('Linkedin', '')),
                    'email': csv_row.get('email', csv_row.get('Personal Gmail', '')),
                    'linkedinProfileImageUrl': '',  # Don't expose raw LinkedIn URLs (they expire)
                    'linkedin_image_url': '',  # Use Supabase instead
                    'is_linked': False,
                    'source': 'csv'
                })

        # Add new user profiles (not in CSV)
        for profile in new_user_profiles:
            company_val = ', '.join(profile.get('companies', [])) if profile.get('companies') else ''
            merged_alumni.append({
                'id': f"user_{profile.get('user_id', profile.get('id', ''))}",  # Unique ID for frontend key
                'name': profile.get('full_name', ''),
                'role_title': ', '.join(profile.get('roles', [])) if profile.get('roles') else '',
                'roles_list': profile.get('roles', []) if profile.get('roles') else [],  # Add roles list
                'headline': profile.get('current_title', ''),
                'company': company_val,  # Add 'company' field for frontend compatibility
                'company_name': company_val,
                'companies_list': profile.get('companies', []),
                'company_industry': '',  # New users don't have this yet
                'major': profile.get('major', ''),
                'grad_year': str(profile.get('graduation_year', '')),
                'location': profile.get('location', ''),
                'profile_image': profile.get('profile_image_url', ''),
                'profile_image_url': profile.get('profile_image_url', ''),
                'linkedin_url': profile.get('linkedin_url', ''),
                'linkedin': profile.get('linkedin_url', ''),
                'email': profile.get('personal_email', ''),
                'linkedinProfileImageUrl': '',
                'linkedin_image_url': '',
                'is_linked': False,
                'source': 'new_user'
            })

        # Apply filters
        name_query = request.args.get('name', '').lower()
        title_query = request.args.get('title', '').lower()
        major_filter = request.args.get('major', '')
        grad_year_filter = request.args.get('grad_year', '')
        company_filter = request.args.get('company', '')
        industry_filter = request.args.get('industry', '')

        filtered_alumni = []
        for alumni in merged_alumni:
            # Apply name filter
            if name_query and name_query not in alumni.get('name', '').lower():
                continue

            # Apply title filter
            if title_query:
                if (title_query not in alumni.get('role_title', '').lower() and
                    title_query not in alumni.get('headline', '').lower()):
                    continue

            # Apply major filter
            if major_filter and alumni.get('major') != major_filter:
                continue

            # Apply grad year filter
            if grad_year_filter and alumni.get('grad_year') != grad_year_filter:
                continue

            # Apply company filter
            if company_filter:
                companies = alumni.get('companies_list', [])
                if company_filter not in companies:
                    continue

            # Apply industry filter
            if industry_filter and alumni.get('company_industry') != industry_filter:
                continue

            filtered_alumni.append(alumni)

        # Clean NaN values before sending response
        filtered_alumni = clean_nan_values(filtered_alumni)

        return jsonify({
            'success': True,
            'count': len(filtered_alumni),
            'data': filtered_alumni
        })

    except Exception as e:
        import traceback
        print(f"Error in get_alumni: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get available filter options."""
    try:
        df = load_alumni_data()

        # Get unique values for filters
        majors = sorted([m for m in df['major'].unique() if m])
        years = sorted([y for y in df['grad_year'].unique() if y and y != 'nan'])

        # Get all unique companies
        all_companies = set()
        for companies_list in df['companies_list']:
            all_companies.update(companies_list)
        companies = sorted([c for c in all_companies if c])

        industries = sorted([i for i in df['company_industry'].unique() if i])

        return jsonify({
            'success': True,
            'filters': {
                'majors': majors,
                'years': years,
                'companies': companies,
                'industries': industries
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cached-image/<filename>', methods=['GET'])
def get_cached_image(filename):
    """Serve cached profile images."""
    try:
        image_path = os.path.join(CACHE_DIR, filename)
        if os.path.exists(image_path):
            return send_file(image_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        print(f"Error serving cached image: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/proxy-image', methods=['GET'])
def proxy_image():
    """Legacy proxy endpoint - kept for backward compatibility."""
    try:
        image_url = request.args.get('url')
        if not image_url:
            return jsonify({'error': 'URL parameter required'}), 400

        # Fetch the image with appropriate headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://www.linkedin.com/'
        }

        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Return the image with appropriate content type
        from flask import Response
        return Response(response.content, mimetype=response.headers.get('Content-Type', 'image/jpeg'))

    except Exception as e:
        print(f"Error proxying image: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cache-all-images', methods=['POST'])
def cache_all_images():
    """Upload all LinkedIn profile images to Supabase Storage. Call this to refresh the image cache."""
    try:
        # Load the CSV directly
        if os.path.exists(ALUMNI_CSV):
            df = pd.read_csv(ALUMNI_CSV)
        else:
            df = download_csv_from_google_drive(GOOGLE_DRIVE_URL)
            if df is None:
                return jsonify({'error': 'Could not load CSV data'}), 500

        if 'linkedinProfileImageUrl' not in df.columns:
            return jsonify({'error': 'No linkedinProfileImageUrl column found'}), 400

        name_col = 'Name' if 'Name' in df.columns else 'name'
        storage_type = 'supabase' if SUPABASE_STORAGE_ENABLED else 'local'

        cached_count = 0
        failed_count = 0
        skipped_count = 0
        results = []

        for idx, row in df.iterrows():
            image_url = row.get('linkedinProfileImageUrl', '')
            name = row.get(name_col, f'Row {idx}')

            if not image_url or str(image_url).strip() in ['', 'nan', 'null', 'None']:
                skipped_count += 1
                continue

            # Check if already in Supabase (if enabled)
            if SUPABASE_STORAGE_ENABLED:
                existing_url = get_supabase_image_url(str(image_url))
                if existing_url:
                    results.append({'name': name, 'status': 'already_cached', 'url': existing_url})
                    cached_count += 1
                    continue
            else:
                # Check local cache
                image_hash = get_image_hash(str(image_url))
                existing_cached = None
                for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    cached_path = os.path.join(CACHE_DIR, f"{image_hash}{ext}")
                    if os.path.exists(cached_path):
                        existing_cached = f"{image_hash}{ext}"
                        break
                if existing_cached:
                    results.append({'name': name, 'status': 'already_cached', 'filename': existing_cached})
                    cached_count += 1
                    continue

            # Download and upload to Supabase (or cache locally)
            cached_result = download_and_cache_image(str(image_url), name)
            if cached_result:
                results.append({'name': name, 'status': 'cached', 'url': cached_result})
                cached_count += 1
            else:
                results.append({'name': name, 'status': 'failed'})
                failed_count += 1

        return jsonify({
            'success': True,
            'storage_type': storage_type,
            'message': f'Cached {cached_count} images to {storage_type}, {failed_count} failed, {skipped_count} skipped (no URL)',
            'cached': cached_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'details': results
        })

    except Exception as e:
        import traceback
        print(f"Error caching images: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/migrate-images-to-supabase', methods=['POST'])
def migrate_images_to_supabase():
    """Migrate existing local cached images to Supabase Storage."""
    if not SUPABASE_STORAGE_ENABLED:
        return jsonify({'error': 'Supabase Storage not configured'}), 400

    try:
        migrated = 0
        failed = 0
        already_exists = 0
        results = []

        # Get all local cached images
        for filename in os.listdir(CACHE_DIR):
            if not filename.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                continue

            local_path = os.path.join(CACHE_DIR, filename)

            # Check if already in Supabase
            if check_image_exists(filename):
                results.append({'filename': filename, 'status': 'already_exists'})
                already_exists += 1
                continue

            # Migrate to Supabase
            success, public_url = migrate_local_image_to_supabase(local_path, filename)
            if success:
                results.append({'filename': filename, 'status': 'migrated', 'url': public_url})
                migrated += 1
            else:
                results.append({'filename': filename, 'status': 'failed'})
                failed += 1

        return jsonify({
            'success': True,
            'message': f'Migrated {migrated} images, {already_exists} already existed, {failed} failed',
            'migrated': migrated,
            'already_exists': already_exists,
            'failed': failed,
            'details': results
        })

    except Exception as e:
        import traceback
        print(f"Error migrating images: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

if AUTH_ENABLED:

    @app.route('/auth/signup', methods=['POST'])
    def auth_signup():
        """Sign up a new user with referral code"""
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['email', 'password', 'referral_code', 'full_name']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400

            email = data['email']
            password = data['password']
            referral_code = data['referral_code']
            full_name = data['full_name']

            # Optional profile data
            profile_data = {
                'major': data.get('major', ''),
                'graduation_year': data.get('graduation_year'),
                'location': data.get('location', ''),
                'linkedin_url': data.get('linkedin_url', ''),
                'personal_email': email,  # Use signup email as personal email
                'phone': data.get('phone', ''),
            }

            # Sign up the user
            success, message, user_data = signup_user(
                email, password, referral_code, full_name, profile_data
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'user': user_data
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 400

        except Exception as e:
            print(f"Signup error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Signup failed: {str(e)}'
            }), 500


    @app.route('/auth/login', methods=['POST'])
    def auth_login():
        """Log in a user"""
        try:
            data = request.get_json()

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({
                    'success': False,
                    'error': 'Email and password required'
                }), 400

            success, message, user_data = login_user(email, password)

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'user': user_data
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 401

        except Exception as e:
            print(f"Login error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Login failed: {str(e)}'
            }), 500


    @app.route('/auth/logout', methods=['POST'])
    @require_auth
    def auth_logout(current_user):
        """Log out a user"""
        try:
            auth_header = request.headers.get('Authorization')
            token = auth_header.split(' ')[1] if auth_header else ''

            success, message = logout_user(token)

            return jsonify({
                'success': success,
                'message': message
            }), 200

        except Exception as e:
            print(f"Logout error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Logout failed: {str(e)}'
            }), 500


    @app.route('/auth/refresh', methods=['POST'])
    def auth_refresh():
        """Refresh an expired session using refresh token"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token')

            if not refresh_token:
                return jsonify({
                    'success': False,
                    'error': 'Refresh token is required'
                }), 400

            success, message, user_data = refresh_session(refresh_token)

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'user': user_data
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 401

        except Exception as e:
            print(f"Refresh error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Session refresh failed: {str(e)}'
            }), 500


    @app.route('/auth/forgot-password', methods=['POST'])
    def auth_forgot_password():
        """Request password reset email"""
        try:
            from services.auth import reset_password_request

            data = request.get_json()
            email = data.get('email')

            if not email:
                return jsonify({
                    'success': False,
                    'error': 'Email is required'
                }), 400

            success, message = reset_password_request(email)

            return jsonify({
                'success': success,
                'message': message
            }), 200

        except Exception as e:
            print(f"Forgot password error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to process password reset request'
            }), 500


    @app.route('/auth/update-password', methods=['POST'])
    def auth_update_password():
        """Update password with reset token"""
        try:
            from services.auth import update_password

            # Get access token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({
                    'success': False,
                    'error': 'Missing or invalid authorization token'
                }), 401

            access_token = auth_header.split(' ')[1]

            data = request.get_json()
            new_password = data.get('password')

            if not new_password:
                return jsonify({
                    'success': False,
                    'error': 'New password is required'
                }), 400

            if len(new_password) < 8:
                return jsonify({
                    'success': False,
                    'error': 'Password must be at least 8 characters'
                }), 400

            success, message = update_password(access_token, new_password)

            return jsonify({
                'success': success,
                'message': message
            }), 200 if success else 400

        except Exception as e:
            print(f"Update password error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to update password'
            }), 500


    @app.route('/auth/session', methods=['GET'])
    @require_auth
    def auth_session(current_user):
        """Get current user session"""
        return jsonify({
            'success': True,
            'user': current_user
        }), 200


    # ============================================================================
    # RESUME & PROFILE ENDPOINTS
    # ============================================================================

    @app.route('/api/resume/upload', methods=['POST'])
    @require_auth
    def upload_resume(current_user):
        """Upload and parse resume PDF"""
        try:
            from services.gemini_service import parse_resume
            import PyPDF2
            from werkzeug.utils import secure_filename

            # Check if file was uploaded
            if 'resume' not in request.files:
                return jsonify({'error': 'No resume file provided'}), 400

            file = request.files['resume']

            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'error': 'Only PDF files are allowed'}), 400

            # Validate file size (max 5MB)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > 5 * 1024 * 1024:  # 5MB
                return jsonify({'error': 'File size exceeds 5MB limit'}), 400

            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(file)
            resume_text = ""

            for page in pdf_reader.pages:
                resume_text += page.extract_text() + "\n"

            if not resume_text.strip():
                return jsonify({'error': 'Could not extract text from PDF'}), 400

            # Parse resume with Gemini
            parsed_data = parse_resume(resume_text)

            # Upload PDF to Supabase Storage
            file.seek(0)  # Reset file pointer
            filename = secure_filename(f"{current_user['user_id']}_{file.filename}")

            # Upload to Supabase storage bucket 'resumes'
            storage_response = supabase.storage.from_('resumes').upload(
                filename,
                file.read(),
                file_options={"content-type": "application/pdf"}
            )

            # Get public URL
            resume_url = supabase.storage.from_('resumes').get_public_url(filename)

            # Update user profile with resume data
            update_data = {
                'raw_resume_text': resume_text[:5000],  # Store first 5000 chars
                'resume_url': resume_url,
            }

            # Add parsed fields if available
            if parsed_data.get('major'):
                update_data['major'] = parsed_data['major']
            if parsed_data.get('graduation_year'):
                update_data['graduation_year'] = parsed_data['graduation_year']
            if parsed_data.get('linkedin_url'):
                update_data['linkedin_url'] = parsed_data['linkedin_url']
            if parsed_data.get('location'):
                update_data['location'] = parsed_data['location']
            if parsed_data.get('email'):
                update_data['personal_email'] = parsed_data['email']
            if parsed_data.get('phone'):
                update_data['phone'] = parsed_data['phone']
            if parsed_data.get('skills'):
                # Store as bio for now (can expand schema later)
                skills_text = ', '.join(parsed_data['skills'][:20])
                update_data['bio'] = f"Skills: {skills_text}"

            # Extract work experience - get all companies and roles
            if parsed_data.get('work_experience') and len(parsed_data['work_experience']) > 0:
                companies = [job.get('company') for job in parsed_data['work_experience'] if job.get('company')]
                roles = [job.get('title') for job in parsed_data['work_experience'] if job.get('title')]

                if companies:
                    update_data['companies'] = companies
                if roles:
                    update_data['roles'] = roles

            # Extract industries
            if parsed_data.get('industries'):
                update_data['career_interests'] = parsed_data['industries']

            # Update profile
            supabase.table('user_profiles').update(update_data).eq(
                'user_id', current_user['user_id']
            ).execute()

            return jsonify({
                'success': True,
                'message': 'Resume uploaded and parsed successfully',
                'parsed_data': parsed_data,
                'resume_url': resume_url
            }), 200

        except Exception as e:
            import traceback
            print(f"Error uploading resume: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'Failed to upload resume: {str(e)}'}), 500


    @app.route('/api/profile/upload-image', methods=['POST'])
    @require_auth
    def upload_profile_image(current_user):
        """Upload profile picture"""
        try:
            from werkzeug.utils import secure_filename
            from PIL import Image
            from services.storage import upload_image_to_supabase, get_public_url
            import io

            print(f"[PROFILE IMAGE UPLOAD] User: {current_user.get('user_id')}")
            print(f"[PROFILE IMAGE UPLOAD] Files in request: {list(request.files.keys())}")

            # Check if file was uploaded
            if 'image' not in request.files:
                print("[PROFILE IMAGE UPLOAD] Error: No image file in request")
                return jsonify({'error': 'No image file provided'}), 400

            file = request.files['image']

            if file.filename == '':
                print("[PROFILE IMAGE UPLOAD] Error: Empty filename")
                return jsonify({'error': 'No file selected'}), 400

            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

            if file_ext not in allowed_extensions:
                return jsonify({'error': 'Only image files (PNG, JPG, JPEG, GIF, WEBP) are allowed'}), 400

            # Validate file size (max 5MB)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > 5 * 1024 * 1024:  # 5MB
                return jsonify({'error': 'File size exceeds 5MB limit'}), 400

            # Read and validate image
            try:
                image = Image.open(file)
                image.verify()
                file.seek(0)  # Reset after verify
                image = Image.open(file)  # Reopen after verify
            except Exception as e:
                return jsonify({'error': 'Invalid image file'}), 400

            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # Resize image to reasonable dimensions (max 800x800) to save storage
            max_size = (800, 800)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to JPEG and compress
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
            img_bytes = img_byte_arr.getvalue()

            # Generate filename using user_id
            filename = f"{current_user['user_id']}_profile.jpg"
            print(f"[PROFILE IMAGE UPLOAD] Generated filename: {filename}")

            # Upload using the storage service (uses service key for proper permissions)
            print(f"[PROFILE IMAGE UPLOAD] Uploading to profile-images bucket using service key...")
            success, result = upload_image_to_supabase(img_bytes, filename, "image/jpeg")

            if not success:
                print(f"[PROFILE IMAGE UPLOAD] Upload failed: {result}")
                return jsonify({'error': f'Failed to upload image: {result}'}), 500

            image_url = result
            print(f"[PROFILE IMAGE UPLOAD] Upload successful! URL: {image_url}")

            # Add cache-busting timestamp to the URL
            import time
            cache_bust_url = f"{image_url}?t={int(time.time())}"

            # Update user profile with image URL using admin client
            print(f"[PROFILE IMAGE UPLOAD] Updating user profile with admin client...")
            update_result = supabase_admin.table('user_profiles').update({
                'profile_image_url': cache_bust_url
            }).eq('user_id', current_user['user_id']).execute()

            if not update_result.data:
                print(f"[PROFILE IMAGE UPLOAD] Warning: Profile update returned no data")
            else:
                print(f"[PROFILE IMAGE UPLOAD] Profile updated successfully")

            print(f"[PROFILE IMAGE UPLOAD] Success!")
            return jsonify({
                'success': True,
                'message': 'Profile image uploaded successfully',
                'image_url': cache_bust_url
            }), 200

        except Exception as e:
            print(f"[PROFILE IMAGE UPLOAD] FATAL ERROR: {e}")
            print(f"[PROFILE IMAGE UPLOAD] Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to upload profile image: {str(e)}'}), 500


    @app.route('/api/match-profile', methods=['POST'])
    @require_auth
    def match_profile(current_user):
        """Search for potential matching alumni profiles in CSV data.

        Used during onboarding to let users identify if they already exist
        in the alumni database and link their account to that card.
        """
        try:
            from services.alumni_matcher import AlumniMatcher

            data = request.get_json()
            full_name = data.get('full_name', '').strip()
            email = data.get('email', '').strip().lower()

            if not full_name:
                return jsonify({
                    'success': False,
                    'error': 'Full name is required'
                }), 400

            # Load CSV data
            csv_df = load_alumni_data()

            # Find potential matches with lower threshold (0.7) to show more candidates
            potential_matches = []

            for idx, row in csv_df.iterrows():
                csv_name = str(row.get('Name', row.get('name', '')))
                csv_email = str(row.get('Personal Gmail', row.get('email', ''))).lower().strip()

                # Calculate name similarity
                similarity = AlumniMatcher.name_similarity(full_name, csv_name)

                # Check for email match (high confidence)
                email_match = email and csv_email and email == csv_email

                # Include if name similarity > 0.6 or email matches
                if similarity > 0.6 or email_match:
                    # Build card data for display
                    profile_image = row.get('profile_image_url', '')

                    # Get companies and roles
                    companies_list = row.get('companies_list', [])
                    if not companies_list or not isinstance(companies_list, list):
                        company = row.get('company', row.get('company_name', ''))
                        companies_list = [company] if company else []

                    roles_list = row.get('roles_list', [])
                    if not roles_list or not isinstance(roles_list, list):
                        role = row.get('role_title', row.get('linkedinJobTitle', ''))
                        roles_list = [role] if role else []

                    potential_matches.append({
                        'csv_index': int(idx),
                        'name': csv_name,
                        'email': csv_email,
                        'similarity': round(similarity, 2),
                        'email_match': email_match,
                        'confidence': 1.0 if email_match else similarity,
                        # Card display data
                        'profile_image_url': profile_image,
                        'role_title': row.get('role_title', row.get('linkedinHeadline', '')),
                        'roles_list': roles_list,
                        'company': row.get('company', row.get('company_name', '')),
                        'companies_list': companies_list,
                        'major': row.get('major', row.get('Major', '')),
                        'grad_year': str(row.get('grad_year', row.get('Grad Yr', ''))),
                        'location': row.get('location', ''),
                        'linkedin': row.get('linkedin', row.get('linkedinProfileUrl', '')),
                    })

            # Sort by confidence (email match first, then by similarity)
            potential_matches.sort(key=lambda x: (-x['email_match'], -x['confidence']))

            # Limit to top 5 matches
            potential_matches = potential_matches[:5]

            return jsonify({
                'success': True,
                'matches': potential_matches,
                'count': len(potential_matches)
            }), 200

        except Exception as e:
            import traceback
            print(f"Error matching profile: {e}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Failed to search for matches: {str(e)}'
            }), 500


    @app.route('/api/link-profile', methods=['POST'])
    @require_auth
    def link_profile(current_user):
        """Link user's account to an existing CSV alumni record.

        Called when user confirms they are a specific person from the CSV.
        """
        try:
            data = request.get_json()
            csv_index = data.get('csv_index')

            if csv_index is None:
                return jsonify({
                    'success': False,
                    'error': 'CSV index is required'
                }), 400

            # Load CSV to get the record data
            csv_df = load_alumni_data()

            # Use .loc instead of .iloc since csv_index is the DataFrame index label
            # (not position) from match-profile's iterrows()
            if csv_index not in csv_df.index:
                return jsonify({
                    'success': False,
                    'error': f'Invalid CSV index: {csv_index}'
                }), 400

            csv_row = csv_df.loc[csv_index]

            # Update user profile with CSV linking data
            update_data = {
                'csv_source_id': int(csv_index),
                'csv_match_type': 'user_confirmed',
                'csv_match_confidence': 1.0,
                'is_csv_linked': True
            }

            # Also pre-fill some profile data from CSV if available
            if csv_row.get('major', csv_row.get('Major', '')):
                update_data['major'] = str(csv_row.get('major', csv_row.get('Major', '')))

            grad_year = csv_row.get('grad_year', csv_row.get('Grad Yr', ''))
            if grad_year and str(grad_year) not in ['', 'nan', 'None']:
                try:
                    update_data['graduation_year'] = int(float(str(grad_year)))
                except:
                    pass

            if csv_row.get('location', ''):
                update_data['location'] = str(csv_row.get('location', ''))

            if csv_row.get('linkedin', csv_row.get('linkedinProfileUrl', '')):
                update_data['linkedin_url'] = str(csv_row.get('linkedin', csv_row.get('linkedinProfileUrl', '')))

            # Get companies and roles from CSV
            companies_list = csv_row.get('companies_list', [])
            if isinstance(companies_list, list) and companies_list:
                update_data['companies'] = companies_list

            roles_list = csv_row.get('roles_list', [])
            if isinstance(roles_list, list) and roles_list:
                update_data['roles'] = roles_list

            # Copy profile image from CSV (LinkedIn profile image)
            profile_image = csv_row.get('profile_image_url', '')
            if profile_image and str(profile_image) not in ['', 'nan', 'None', 'null']:
                update_data['profile_image_url'] = str(profile_image)

            # Update profile
            response = supabase.table('user_profiles').update(update_data).eq(
                'user_id', current_user['user_id']
            ).execute()

            if response.data:
                return jsonify({
                    'success': True,
                    'message': 'Profile linked successfully',
                    'profile': response.data[0],
                    'csv_data': {
                        'name': csv_row.get('name', csv_row.get('Name', '')),
                        'major': update_data.get('major', ''),
                        'graduation_year': update_data.get('graduation_year', ''),
                        'companies': update_data.get('companies', []),
                        'roles': update_data.get('roles', [])
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to link profile'
                }), 500

        except Exception as e:
            import traceback
            print(f"Error linking profile: {e}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Failed to link profile: {str(e)}'
            }), 500


    @app.route('/api/profile', methods=['GET'])
    @require_auth
    def get_profile(current_user):
        """Get current user's profile"""
        try:
            response = supabase.table('user_profiles').select('*').eq(
                'user_id', current_user['user_id']
            ).execute()

            if response.data and len(response.data) > 0:
                return jsonify({
                    'success': True,
                    'profile': response.data[0]
                }), 200
            else:
                return jsonify({'error': 'Profile not found'}), 404

        except Exception as e:
            print(f"Error fetching profile: {e}")
            return jsonify({'error': 'Failed to fetch profile'}), 500


    @app.route('/api/profile', methods=['PUT'])
    @require_auth
    def update_profile(current_user):
        """Update current user's profile"""
        try:
            data = request.json

            # Only allow updating certain fields
            allowed_fields = [
                'full_name', 'major', 'graduation_year', 'companies', 'roles',
                'current_company', 'current_title',  # Keep old fields for backward compatibility
                'location', 'linkedin_url', 'personal_email',
                'professional_email', 'phone', 'bio', 'career_interests',
                'target_industries', 'target_companies', 'profile_image_url',
                'onboarding_completed', 'email_template'
            ]

            update_data = {}
            for field in allowed_fields:
                if field in data:
                    update_data[field] = data[field]

            if not update_data:
                return jsonify({'error': 'No valid fields to update'}), 400

            # If completing onboarding, try to match with CSV alumni data
            if data.get('onboarding_completed') == True:
                try:
                    from services.alumni_matcher import AlumniMatcher

                    # Get current profile data
                    profile_response = supabase.table('user_profiles').select('*').eq(
                        'user_id', current_user['user_id']
                    ).execute()

                    if profile_response.data:
                        current_profile = profile_response.data[0]

                        # Merge current profile with update data for matching
                        matching_data = {**current_profile, **update_data}

                        # Load CSV and try to find match
                        csv_df = load_alumni_data()
                        match_result = AlumniMatcher.find_csv_match(matching_data, csv_df)

                        if match_result:
                            linking_data = AlumniMatcher.get_csv_linking_data(match_result)
                            if linking_data:
                                # Add CSV linking fields to update
                                update_data.update(linking_data)
                                print(f"✓ Linked user {current_user['user_id']} to CSV record #{linking_data.get('csv_source_id')} ({match_result.get('match_type')})")
                            else:
                                print(f"⊙ No CSV match for user {current_user['user_id']} - will create new card")
                except Exception as match_error:
                    # Don't fail the update if matching fails
                    print(f"Warning: CSV matching failed: {match_error}")

            # Update profile
            response = supabase.table('user_profiles').update(update_data).eq(
                'user_id', current_user['user_id']
            ).execute()

            if response.data:
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'profile': response.data[0]
                }), 200
            else:
                return jsonify({'error': 'Failed to update profile'}), 500

        except Exception as e:
            print(f"Error updating profile: {e}")
            return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500


    @app.route('/api/account', methods=['DELETE'])
    @require_auth
    def delete_own_account(current_user):
        """Delete the current user's own account.

        This permanently deletes ALL user data from Supabase:
        - Auth user (allows email re-use)
        - User profile
        - Chat sessions and messages
        - Connections
        - Resume files from storage
        - Profile images from storage
        - Marks CSV entry as deleted (if linked)
        """
        try:
            user_id = current_user['user_id']
            print(f"=== DELETING ACCOUNT for user_id: {user_id} ===")

            # Get user profile info before deletion
            csv_source_id = None
            try:
                profile_check = supabase_admin.table('user_profiles').select('*').eq('user_id', user_id).execute()
                if profile_check.data:
                    csv_source_id = profile_check.data[0].get('csv_source_id')
                    print(f"User profile found. CSV link: {csv_source_id}")
            except Exception as e:
                print(f"Warning: Could not fetch profile: {e}")

            # 1. Clear foreign key references that don't have ON DELETE CASCADE
            try:
                supabase_admin.table('admin_actions').delete().eq('director_user_id', user_id).execute()
                supabase_admin.table('admin_actions').delete().eq('target_user_id', user_id).execute()
                supabase_admin.table('platform_settings').update({'updated_by': None}).eq('updated_by', user_id).execute()
                print("Cleared FK references")
            except Exception as e:
                print(f"Warning: Could not clear FK references: {e}")

            # 2. DELETE AUTH USER - THIS IS CRITICAL FOR EMAIL RE-USE
            # If this fails, abort the entire operation
            try:
                supabase_admin.auth.admin.delete_user(user_id)
                print("Deleted auth user successfully")
            except Exception as auth_error:
                print(f"Auth delete error: {auth_error}")
                # Try alternative method
                try:
                    supabase_admin.auth.admin.delete_user(uid=user_id)
                    print("Deleted auth user (alternative method)")
                except Exception as e2:
                    print(f"Alternative auth delete also failed: {e2}")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to delete authentication. Please try again or contact support.'
                    }), 500

            # 3. Delete resume files from storage
            try:
                resume_files = supabase_admin.storage.from_('resumes').list(path='', options={'search': user_id})
                if resume_files:
                    files_to_delete = [f['name'] for f in resume_files if f['name'].startswith(user_id)]
                    if files_to_delete:
                        supabase_admin.storage.from_('resumes').remove(files_to_delete)
                        print(f"Deleted {len(files_to_delete)} resume files")
            except Exception as e:
                print(f"Warning: Could not delete resumes: {e}")

            # 2. Delete profile images from storage
            try:
                profile_images = supabase_admin.storage.from_('profile-images').list(path='', options={'search': user_id})
                if profile_images:
                    img_files = [f['name'] for f in profile_images if f['name'].startswith(user_id)]
                    if img_files:
                        supabase_admin.storage.from_('profile-images').remove(img_files)
                        print(f"Deleted {len(img_files)} profile images")
            except Exception as e:
                print(f"Warning: Could not delete profile images: {e}")

            # 3. Delete chat sessions (messages will CASCADE)
            try:
                supabase_admin.table('chat_sessions').delete().eq('user_id', user_id).execute()
                print("Deleted chat sessions")
            except Exception as e:
                print(f"Warning: Could not delete chat sessions: {e}")

            # 4. Delete connections where user is either side
            try:
                supabase_admin.table('connections').delete().eq('user_id', user_id).execute()
                supabase_admin.table('connections').delete().eq('target_user_id', user_id).execute()
                print("Deleted connections")
            except Exception as e:
                print(f"Warning: Could not delete connections: {e}")

            # 5. Delete the user profile
            try:
                supabase_admin.table('user_profiles').delete().eq('user_id', user_id).execute()
                print("Deleted user profile")
            except Exception as e:
                print(f"Warning: Could not delete profile: {e}")

            # 6. If user was linked to a CSV entry, mark it as deleted
            if csv_source_id is not None:
                try:
                    supabase_admin.table('deleted_alumni').insert({
                        'csv_row_id': csv_source_id
                    }).execute()
                    print(f"Marked CSV row {csv_source_id} as deleted")
                except Exception as e:
                    print(f"Warning: Could not mark CSV as deleted (table may not exist): {e}")

            print(f"=== ACCOUNT DELETION COMPLETE for {user_id} ===")

            return jsonify({
                'success': True,
                'message': 'Account deleted successfully'
            }), 200

        except Exception as e:
            import traceback
            print(f"Error deleting account: {e}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Failed to delete account: {str(e)}'
            }), 500


    # ============================================================================
    # ADMIN ENDPOINTS (Director of Operations only)
    # ============================================================================

    @app.route('/admin/settings', methods=['GET'])
    @require_auth
    @require_director
    def get_admin_settings(current_user):
        """Get platform settings (current referral code)"""
        try:
            result = supabase.table('platform_settings').select('*').eq('id', 1).execute()

            if result.data and len(result.data) > 0:
                return jsonify({
                    'success': True,
                    'settings': result.data[0]
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Platform settings not found'
                }), 404

        except Exception as e:
            print(f"Error fetching settings: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    @app.route('/admin/settings/referral-code', methods=['PUT'])
    @require_auth
    @require_director
    def update_referral_code(current_user):
        """Update the active referral code"""
        try:
            data = request.get_json()
            new_code = data.get('referral_code')

            if not new_code or not new_code.strip():
                return jsonify({
                    'success': False,
                    'error': 'Referral code cannot be empty'
                }), 400

            # Update the platform settings
            result = supabase_admin.table('platform_settings').update({
                'active_referral_code': new_code.strip(),
                'updated_by': current_user['user_id']
            }).eq('id', 1).execute()

            # Log the admin action
            log_admin_action(
                director_user_id=current_user['user_id'],
                action_type='SET_REFERRAL_CODE',
                details={'new_code': new_code.strip()}
            )

            return jsonify({
                'success': True,
                'message': f'Referral code updated to: {new_code.strip()}'
            }), 200

        except Exception as e:
            print(f"Error updating referral code: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    @app.route('/admin/members', methods=['GET'])
    @require_auth
    @require_director
    def get_all_members(current_user):
        """Get all members (for Director dashboard)"""
        try:
            result = supabase.table('user_profiles').select('*').order('created_at', desc=True).execute()

            # Enrich with auth emails for users who don't have personal_email set
            members = result.data
            for member in members:
                # If no personal_email, try to get the auth email
                if not member.get('personal_email'):
                    try:
                        auth_user = supabase_admin.auth.admin.get_user_by_id(member['user_id'])
                        if auth_user and auth_user.user:
                            member['email'] = auth_user.user.email
                    except Exception as e:
                        print(f"Could not fetch auth email for {member['user_id']}: {e}")
                else:
                    member['email'] = member['personal_email']

            return jsonify({
                'success': True,
                'members': members,
                'count': len(members)
            }), 200

        except Exception as e:
            print(f"Error fetching members: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    @app.route('/admin/members/<user_id>', methods=['DELETE'])
    @require_auth
    @require_director
    def remove_member(current_user, user_id):
        """Remove a member from the platform completely.

        Deletes ALL traces of the user including:
        - Profile data
        - Resume files from storage
        - Chat sessions and messages (via CASCADE)
        - Connection records (via CASCADE)
        - Auth user account
        """
        try:
            # Get member info before deletion for logging
            member = supabase.table('user_profiles').select(
                'full_name, personal_email, resume_url, profile_image_url, csv_source_id'
            ).eq('user_id', user_id).execute()

            if not member.data:
                return jsonify({
                    'success': False,
                    'error': 'Member not found'
                }), 404

            member_info = member.data[0]
            deleted_items = []

            # 1. Delete chat sessions explicitly (messages will CASCADE)
            try:
                chat_delete = supabase_admin.table('chat_sessions').delete().eq('user_id', user_id).execute()
                if chat_delete.data:
                    deleted_items.append(f"chat sessions: {len(chat_delete.data)}")
            except Exception as chat_error:
                print(f"Warning: Could not delete chat sessions: {chat_error}")

            # 2. Delete connections where user is either side
            try:
                conn_delete_1 = supabase_admin.table('connections').delete().eq('user_id', user_id).execute()
                conn_delete_2 = supabase_admin.table('connections').delete().eq('target_user_id', user_id).execute()
                total_conn = len(conn_delete_1.data or []) + len(conn_delete_2.data or [])
                if total_conn > 0:
                    deleted_items.append(f"connections: {total_conn}")
            except Exception as conn_error:
                print(f"Warning: Could not delete connections: {conn_error}")

            # 3. Delete the user profile
            supabase_admin.table('user_profiles').delete().eq('user_id', user_id).execute()
            deleted_items.append("user profile")

            # 4. Delete admin_actions where this user is the director or target
            try:
                admin_delete_1 = supabase_admin.table('admin_actions').delete().eq('director_user_id', user_id).execute()
                admin_delete_2 = supabase_admin.table('admin_actions').delete().eq('target_user_id', user_id).execute()
                total_admin = len(admin_delete_1.data or []) + len(admin_delete_2.data or [])
                if total_admin > 0:
                    deleted_items.append(f"admin actions: {total_admin}")
            except Exception as admin_error:
                print(f"Warning: Could not delete admin actions: {admin_error}")

            # 5. Update platform_settings if this user updated it last
            try:
                supabase_admin.table('platform_settings').update({'updated_by': None}).eq('updated_by', user_id).execute()
            except Exception as settings_error:
                print(f"Warning: Could not clear platform_settings reference: {settings_error}")

            # 6. Delete resume files from storage
            try:
                # List all files with the user_id prefix in resumes bucket
                resume_files = supabase_admin.storage.from_('resumes').list(path='', options={
                    'search': user_id
                })

                if resume_files:
                    # Find files that start with this user_id
                    files_to_delete = [f['name'] for f in resume_files if f['name'].startswith(user_id)]
                    if files_to_delete:
                        supabase_admin.storage.from_('resumes').remove(files_to_delete)
                        deleted_items.append(f"resumes: {len(files_to_delete)} files")
                        print(f"Deleted {len(files_to_delete)} resume files for user {user_id}")
            except Exception as resume_error:
                print(f"Warning: Could not delete resumes: {resume_error}")

            # 7. Delete any user-uploaded profile images (not LinkedIn cached ones)
            # User profile images would be in profile-images bucket with user_id prefix
            try:
                profile_images = supabase_admin.storage.from_('profile-images').list(path='', options={
                    'search': user_id
                })

                if profile_images:
                    img_files_to_delete = [f['name'] for f in profile_images if f['name'].startswith(user_id)]
                    if img_files_to_delete:
                        supabase_admin.storage.from_('profile-images').remove(img_files_to_delete)
                        deleted_items.append(f"profile images: {len(img_files_to_delete)} files")
                        print(f"Deleted {len(img_files_to_delete)} profile images for user {user_id}")
            except Exception as img_error:
                print(f"Warning: Could not delete profile images: {img_error}")

            # 8. Delete from auth LAST (after all database references are removed)
            # This must succeed for the operation to be considered successful
            try:
                supabase_admin.auth.admin.delete_user(id=user_id)
                deleted_items.append("auth account")
                print(f"Deleted auth account for user {user_id}")
            except Exception as auth_error:
                print(f"Auth delete error: {auth_error}")
                import traceback
                print(f"Auth delete traceback: {traceback.format_exc()}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to delete auth user: {str(auth_error)}'
                }), 500

            # 9. If user was linked to a CSV entry, mark it as deleted so it doesn't show
            csv_source_id = member_info.get('csv_source_id')
            if csv_source_id is not None:
                try:
                    supabase_admin.table('deleted_alumni').insert({
                        'csv_row_id': csv_source_id
                    }).execute()
                    deleted_items.append("alumni card")
                    print(f"Marked CSV row {csv_source_id} as deleted")
                except Exception as del_error:
                    print(f"Warning: Could not mark CSV as deleted: {del_error}")

            # Log the action with details of what was deleted
            log_admin_action(
                director_user_id=current_user['user_id'],
                action_type='REMOVE_MEMBER',
                target_user_id=user_id,
                details={
                    'name': member_info.get('full_name'),
                    'email': member_info.get('personal_email'),
                    'deleted_items': deleted_items
                }
            )

            print(f"Successfully deleted all data for user {user_id}: {', '.join(deleted_items)}")

            return jsonify({
                'success': True,
                'message': f'Member {member_info.get("full_name")} completely removed',
                'deleted_items': deleted_items
            }), 200

        except Exception as e:
            import traceback
            print(f"Error removing member: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    @app.route('/admin/promote-director/<user_id>', methods=['POST'])
    @require_auth
    @require_director
    def promote_to_director(current_user, user_id):
        """Promote a member to Director of Operations"""
        try:
            # Get member info
            member = supabase.table('user_profiles').select('full_name, personal_email, is_director').eq('user_id', user_id).execute()

            if not member.data:
                return jsonify({
                    'success': False,
                    'error': 'Member not found'
                }), 404

            member_info = member.data[0]

            if member_info.get('is_director'):
                return jsonify({
                    'success': False,
                    'error': 'User is already a Director'
                }), 400

            # Promote to director
            supabase_admin.table('user_profiles').update({
                'is_director': True
            }).eq('user_id', user_id).execute()

            # Log the action
            log_admin_action(
                director_user_id=current_user['user_id'],
                action_type='PROMOTE_DIRECTOR',
                target_user_id=user_id,
                details={
                    'name': member_info.get('full_name'),
                    'email': member_info.get('personal_email')
                }
            )

            return jsonify({
                'success': True,
                'message': f'{member_info.get("full_name")} promoted to Director of Operations'
            }), 200

        except Exception as e:
            print(f"Error promoting to director: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    @app.route('/admin/demote-director/<user_id>', methods=['POST'])
    @require_auth
    @require_director
    def demote_director(current_user, user_id):
        """Demote a Director to regular member"""
        try:
            # Can't demote yourself
            if user_id == current_user['user_id']:
                return jsonify({
                    'success': False,
                    'error': 'Cannot demote yourself. Have another Director demote you.'
                }), 400

            # Get member info
            member = supabase.table('user_profiles').select('full_name, personal_email, is_director').eq('user_id', user_id).execute()

            if not member.data:
                return jsonify({
                    'success': False,
                    'error': 'Member not found'
                }), 404

            member_info = member.data[0]

            if not member_info.get('is_director'):
                return jsonify({
                    'success': False,
                    'error': 'User is not a Director'
                }), 400

            # Demote from director
            supabase_admin.table('user_profiles').update({
                'is_director': False
            }).eq('user_id', user_id).execute()

            # Log the action
            log_admin_action(
                director_user_id=current_user['user_id'],
                action_type='DEMOTE_DIRECTOR',
                target_user_id=user_id,
                details={
                    'name': member_info.get('full_name'),
                    'email': member_info.get('personal_email')
                }
            )

            return jsonify({
                'success': True,
                'message': f'{member_info.get("full_name")} demoted from Director of Operations'
            }), 200

        except Exception as e:
            print(f"Error demoting director: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    @app.route('/admin/audit-log', methods=['GET'])
    @require_auth
    @require_director
    def get_audit_log(current_user):
        """Get admin action audit log"""
        try:
            limit = request.args.get('limit', 100, type=int)

            result = supabase.table('admin_actions').select('*').order('timestamp', desc=True).limit(limit).execute()

            return jsonify({
                'success': True,
                'actions': result.data,
                'count': len(result.data)
            }), 200

        except Exception as e:
            print(f"Error fetching audit log: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


    # ============================================================================
    # AI RECOMMENDATIONS ENDPOINT
    # ============================================================================

    @app.route('/api/recommendations', methods=['POST'])
    @require_auth
    def get_recommendations(current_user):
        """Get AI-powered alumni recommendations based on user's profile.

        Request body:
            exclude_ids: list[int] - CSV row IDs to exclude (already shown)
            count: int - Number of recommendations (default 10)

        Returns top matching alumni based on profile similarity.
        """
        try:
            import google.generativeai as genai
            from config import GEMINI_API_KEY, EMBEDDING_MODEL

            from datetime import datetime
            current_year = datetime.now().year

            data = request.get_json() or {}
            exclude_ids = data.get('exclude_ids', [])
            count = min(data.get('count', 10), 20)  # Max 20

            # Get user's profile
            profile_response = supabase.table('user_profiles').select('*').eq(
                'user_id', current_user['user_id']
            ).execute()

            if not profile_response.data:
                return jsonify({'error': 'User profile not found'}), 404

            user_profile = profile_response.data[0]

            # Exclude user's own CSV record if linked
            if user_profile.get('csv_source_id') is not None:
                if user_profile['csv_source_id'] not in exclude_ids:
                    exclude_ids = list(exclude_ids) + [user_profile['csv_source_id']]

            # Build profile text for embedding
            profile_parts = []
            if user_profile.get('full_name'):
                profile_parts.append(f"Name: {user_profile['full_name']}")
            if user_profile.get('major'):
                profile_parts.append(f"Major: {user_profile['major']}")
            if user_profile.get('roles'):
                profile_parts.append(f"Roles: {', '.join(user_profile['roles'])}")
            if user_profile.get('companies'):
                profile_parts.append(f"Companies: {', '.join(user_profile['companies'])}")
            if user_profile.get('current_title'):
                profile_parts.append(f"Title: {user_profile['current_title']}")
            if user_profile.get('current_company'):
                profile_parts.append(f"Company: {user_profile['current_company']}")
            if user_profile.get('career_interests'):
                profile_parts.append(f"Interests: {', '.join(user_profile['career_interests'])}")
            if user_profile.get('target_industries'):
                profile_parts.append(f"Target Industries: {', '.join(user_profile['target_industries'])}")
            if user_profile.get('bio'):
                profile_parts.append(f"Bio: {user_profile['bio'][:500]}")
            if user_profile.get('location'):
                profile_parts.append(f"Location: {user_profile['location']}")

            profile_text = '\n'.join(profile_parts) if profile_parts else "Alumni member"

            # Generate embedding for user's profile
            genai.configure(api_key=GEMINI_API_KEY)
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=profile_text,
                task_type="retrieval_query"
            )
            query_embedding = result['embedding']

            # Query Supabase for similar alumni using RPC function
            # Fetch a larger pool (50+) to allow filtering while minimizing repetition
            try:
                # Get a large pool of matches (don't exclude in RPC - we'll filter in Python)
                match_response = supabase.rpc('match_alumni', {
                    'query_embedding': query_embedding,
                    'match_count': 100,  # Fetch many candidates
                    'exclude_ids': [user_profile.get('csv_source_id')] if user_profile.get('csv_source_id') else []  # Only exclude self
                }).execute()

                all_matches = match_response.data
            except Exception as rpc_error:
                print(f"RPC error (table may not exist yet): {rpc_error}")
                # Fallback: return empty recommendations if table doesn't exist
                return jsonify({
                    'success': True,
                    'recommendations': [],
                    'message': 'Recommendations not available yet. Run build_alumni_embeddings.py first.'
                }), 200

            if not all_matches:
                return jsonify({
                    'success': True,
                    'recommendations': [],
                    'message': 'No recommendations available'
                }), 200

            # Load CSV first to filter by grad_year BEFORE selecting
            csv_df = load_alumni_data()

            # Filter matches by grad_year first (remove future graduates)
            valid_matches = []
            for m in all_matches:
                csv_id = m['csv_row_id']
                if csv_id not in csv_df.index:
                    continue
                row = csv_df.loc[csv_id]
                grad_year_str = str(row.get('grad_year', row.get('Grad Yr', ''))).strip()
                if grad_year_str and grad_year_str not in ['', 'nan', 'None']:
                    try:
                        grad_year_int = int(float(grad_year_str))
                        if grad_year_int > current_year:
                            continue  # Skip future graduates
                    except (ValueError, TypeError):
                        pass  # If can't parse, include them
                valid_matches.append(m)

            # Now separate into new (not excluded) and already seen
            new_matches = [m for m in valid_matches if m['csv_row_id'] not in exclude_ids]
            seen_matches = [m for m in valid_matches if m['csv_row_id'] in exclude_ids]

            # Prefer new matches, but fill with seen ones if needed to always return `count`
            selected_matches = new_matches[:count]
            if len(selected_matches) < count:
                # Need to reuse some - add from seen matches (already sorted by similarity)
                needed = count - len(selected_matches)
                selected_matches.extend(seen_matches[:needed])

            matched_csv_ids = [m['csv_row_id'] for m in selected_matches]

            if not matched_csv_ids:
                return jsonify({
                    'success': True,
                    'recommendations': [],
                    'message': 'No recommendations available'
                }), 200

            # Build recommendation cards
            recommendations = []
            for csv_id in matched_csv_ids:
                row = csv_df.loc[csv_id]
                cached_image = row.get('profile_image_url', '')
                company_val = row.get('company_name', row.get('company', ''))

                recommendations.append({
                    'id': f'csv_{csv_id}',  # Unique ID for frontend key
                    'csv_row_id': int(csv_id),
                    'name': row.get('name', row.get('Name', '')),
                    'role_title': row.get('role_title', ''),
                    'roles_list': row.get('roles_list', []),
                    'headline': row.get('headline', row.get('linkedinHeadline', '')),
                    'company': company_val,
                    'company_name': company_val,
                    'companies_list': row.get('companies_list', []),
                    'company_industry': row.get('company_industry', row.get('companyIndustry', '')),
                    'major': row.get('major', row.get('Major', '')),
                    'grad_year': str(row.get('grad_year', row.get('Grad Yr', ''))),
                    'location': row.get('location', ''),
                    'profile_image': cached_image,
                    'profile_image_url': cached_image,
                    'linkedin_url': row.get('linkedin_url', row.get('linkedin', row.get('Linkedin', ''))),
                    'linkedin': row.get('linkedin', row.get('Linkedin', '')),
                    'email': row.get('email', row.get('Personal Gmail', '')),
                    'is_recommendation': True
                })

            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'count': len(recommendations)
            }), 200

        except Exception as e:
            import traceback
            print(f"Error getting recommendations: {e}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Failed to get recommendations: {str(e)}'
            }), 500

    # ============================================================================
    # AI Email Writer Endpoint
    # ============================================================================
    @app.route('/api/generate-email', methods=['POST'])
    @require_auth
    def generate_email(current_user):
        """Generate a personalized networking email using AI.

        Request body:
            alumni: dict - Alumni data (name, company, role, etc.)

        Returns generated email text.
        """
        try:
            import sys
            import google.generativeai as genai
            from config import GEMINI_API_KEY, GEMINI_MODEL

            print(f"[DEBUG] generate_email called, GEMINI_MODEL={GEMINI_MODEL}", flush=True)

            data = request.get_json() or {}
            alumni_data = data.get('alumni', {})

            if not alumni_data:
                return jsonify({'error': 'Alumni data required'}), 400

            # Get user's profile
            profile_response = supabase.table('user_profiles').select('*').eq(
                'user_id', current_user['user_id']
            ).execute()

            if not profile_response.data:
                return jsonify({'error': 'User profile not found'}), 404

            user_profile = profile_response.data[0]

            # Get user's custom template or use default
            custom_template = (user_profile.get('email_template') or '').strip()

            # Default template structure
            default_template = """Hi {alumni_name},

I'm {user_name}, a {user_major} student at Purdue University. I came across your profile through THINK and was excited to see your work at {company}.

I'm really interested in learning more about your career path and any advice you might have for someone exploring this field. Would you be open to a quick 15-minute call sometime?

Thanks so much,
{user_name}"""

            # Build context for the AI
            alumni_name = alumni_data.get('name', 'there')
            alumni_first_name = alumni_name.split()[0] if alumni_name else 'there'
            company = alumni_data.get('company') or alumni_data.get('company_name') or 'your company'
            role = alumni_data.get('role_title') or alumni_data.get('headline') or ''
            industry = alumni_data.get('company_industry') or ''

            user_name = user_profile.get('full_name', 'A THINK Member')
            user_first_name = user_name.split()[0] if user_name else 'A THINK Member'
            user_major = user_profile.get('major', 'a student')
            user_grad_year = user_profile.get('graduation_year')
            user_interests = user_profile.get('career_interests', [])
            user_target_industries = user_profile.get('target_industries', [])
            user_bio = user_profile.get('bio', '')

            # Configure Gemini
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)

            # Build the prompt
            if custom_template:
                # User has custom template - use it as the base
                prompt = f"""You are helping write a professional networking email. The user has provided a custom template.
Use their template as a guide but personalize it with the specific details provided.

USER'S CUSTOM TEMPLATE:
{custom_template}

SENDER INFO:
- Name: {user_name}
- Major: {user_major}
- Graduation Year: {user_grad_year or 'Current student'}
- Career Interests: {', '.join(user_interests) if user_interests else 'Not specified'}
- Bio: {user_bio or 'Not provided'}

RECIPIENT INFO:
- Name: {alumni_name}
- Company: {company}
- Role/Title: {role or 'Not specified'}
- Industry: {industry or 'Not specified'}

Write a personalized email based on the template. Replace placeholders like NAME with actual names.
Keep it professional but warm. Make it feel genuine, not generic.
Output ONLY the email text, no explanations or markdown."""
            else:
                # Use default template with AI enhancement
                prompt = f"""Write a professional networking email from a college student to an alumni.

SENDER INFO:
- Name: {user_name}
- Major: {user_major}
- University: Purdue University
- Graduation Year: {user_grad_year or 'Current student'}
- Career Interests: {', '.join(user_interests) if user_interests else 'Exploring career options'}
- Target Industries: {', '.join(user_target_industries) if user_target_industries else 'Various'}
- Bio: {user_bio or 'Eager to learn and connect'}

RECIPIENT INFO:
- Name: {alumni_name}
- Company: {company}
- Role/Title: {role or 'Professional'}
- Industry: {industry or 'Not specified'}

TEMPLATE TO FOLLOW (personalize it):
{default_template}

Instructions:
1. Start with "Hi {alumni_first_name},"
2. Keep it concise but warm - around 4-5 sentences, under 100 words
3. Introduce yourself, show genuine interest in their work, make a clear ask
4. Be professional but personable - not stiff or overly formal
5. If possible, mention something specific about their company or role
6. End with the sender's first name

Output ONLY the email text, no explanations or markdown."""

            # Generate the email
            response = model.generate_content(prompt)
            generated_email = response.text.strip()

            # Clean up any markdown artifacts
            if generated_email.startswith('```'):
                generated_email = '\n'.join(generated_email.split('\n')[1:-1])

            return jsonify({
                'success': True,
                'email': generated_email,
                'subject': f"Connecting from Purdue THINK - {user_first_name}"
            }), 200

        except Exception as e:
            import traceback
            print(f"[DEBUG] Error generating email: {e}", flush=True)
            print(traceback.format_exc(), flush=True)
            return jsonify({
                'success': False,
                'error': f'Failed to generate email: {str(e)}'
            }), 500

    # ============================================================================
    # AI Networking Advisor Chatbot Endpoint
    # ============================================================================
    @app.route('/api/chat', methods=['POST'])
    @require_auth
    def chat_advisor(current_user):
        """AI Networking Advisor Chatbot.

        Request body:
            message: str - User's message
            session_id: str (optional) - Existing session ID to continue conversation

        Returns AI response and optionally member cards if user asks to find someone.
        """
        try:
            import google.generativeai as genai
            from config import GEMINI_API_KEY, GEMINI_MODEL, EMBEDDING_MODEL

            data = request.get_json() or {}
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')

            if not user_message:
                return jsonify({'error': 'Message is required'}), 400

            # Get or create chat session
            if session_id:
                # Verify session belongs to user
                session_check = supabase.table('chat_sessions').select('id').eq(
                    'id', session_id
                ).eq('user_id', current_user['user_id']).execute()
                if not session_check.data:
                    session_id = None  # Invalid session, create new one

            if not session_id:
                # Create new session
                new_session = supabase.table('chat_sessions').insert({
                    'user_id': current_user['user_id']
                }).execute()
                session_id = new_session.data[0]['id']

            # Get conversation history (last 10 messages)
            history_response = supabase.table('chat_messages').select(
                'role, content'
            ).eq('session_id', session_id).order(
                'created_at', desc=False
            ).limit(10).execute()
            conversation_history = history_response.data if history_response.data else []

            # Get user's profile for context
            profile_response = supabase.table('user_profiles').select('*').eq(
                'user_id', current_user['user_id']
            ).execute()
            user_profile = profile_response.data[0] if profile_response.data else {}

            # Check if user is asking to find/search for members
            search_keywords = ['find', 'search', 'looking for', 'who works at', 'anyone at',
                              'members at', 'alumni at', 'someone at', 'people at', 'works in',
                              'who is', 'show me', 'recommend', 'suggest']
            is_member_search = any(kw in user_message.lower() for kw in search_keywords)

            member_cards = []

            if is_member_search:
                # Load CSV for searching
                csv_df = load_alumni_data()

                # First, try direct name search (case-insensitive)
                # Extract potential name from the message
                msg_lower = user_message.lower()
                name_found = False

                # Get the name column
                name_col = 'name' if 'name' in csv_df.columns else 'Name'

                # Search for any name in the CSV that appears in the user's message
                for idx, row in csv_df.iterrows():
                    alumni_name = str(row.get(name_col, '')).lower()
                    first_name = alumni_name.split()[0] if alumni_name else ''
                    last_name = alumni_name.split()[-1] if alumni_name and len(alumni_name.split()) > 1 else ''

                    # Check if first name, last name, or full name is mentioned
                    if (first_name and first_name in msg_lower) or \
                       (last_name and last_name in msg_lower) or \
                       (alumni_name and alumni_name in msg_lower):
                        cached_image = row.get('profile_image_url', '')
                        company_val = row.get('company_name', row.get('company', ''))

                        member_cards.append({
                            'id': f'csv_{idx}',  # Unique ID for frontend key
                            'csv_row_id': int(idx),
                            'name': row.get(name_col, ''),
                            'role_title': row.get('role_title', ''),
                            'roles_list': row.get('roles_list', []),
                            'headline': row.get('headline', row.get('linkedinHeadline', '')),
                            'company': company_val,
                            'company_name': company_val,
                            'companies_list': row.get('companies_list', []),
                            'major': row.get('major', row.get('Major', '')),
                            'grad_year': str(row.get('grad_year', row.get('Grad Yr', ''))),
                            'location': row.get('location', ''),
                            'profile_image_url': cached_image,
                            'linkedin': row.get('linkedin', row.get('Linkedin', '')),
                            'email': row.get('email', row.get('Personal Gmail', '')),
                            'similarity': 1.0  # Direct match
                        })
                        name_found = True

                # If no direct name match, try role/title/company search
                if not member_cards:
                    # Extract search terms (remove common words)
                    stop_words = {'find', 'search', 'looking', 'for', 'who', 'works', 'at', 'anyone',
                                  'members', 'alumni', 'someone', 'people', 'show', 'me', 'recommend',
                                  'suggest', 'in', 'the', 'a', 'an', 'is', 'are', 'can', 'you', 'i',
                                  'want', 'need', 'like', 'similar', 'to', 'else'}
                    search_terms = [word for word in msg_lower.split() if word not in stop_words and len(word) > 2]

                    # Search by role, headline, company, or major
                    for idx, row in csv_df.iterrows():
                        role = str(row.get('role_title', '') or row.get('linkedinJobTitle', '')).lower()
                        headline = str(row.get('headline', '') or row.get('linkedinHeadline', '')).lower()
                        company = str(row.get('company_name', '') or row.get('company', '')).lower()
                        major = str(row.get('major', '') or row.get('Major', '')).lower()

                        # Check if any search term matches role, headline, company, or major
                        match_score = 0
                        for term in search_terms:
                            if term in role:
                                match_score += 3  # Role match is most important
                            if term in headline:
                                match_score += 2
                            if term in company:
                                match_score += 2
                            if term in major:
                                match_score += 1

                        if match_score > 0:
                            cached_image = row.get('profile_image_url', '')
                            company_val = row.get('company_name', row.get('company', ''))

                            member_cards.append({
                                'id': f'csv_{idx}',  # Unique ID for frontend key
                                'csv_row_id': int(idx),
                                'name': row.get(name_col, ''),
                                'role_title': row.get('role_title', ''),
                                'roles_list': row.get('roles_list', []),
                                'headline': row.get('headline', row.get('linkedinHeadline', '')),
                                'company': company_val,
                                'company_name': company_val,
                                'companies_list': row.get('companies_list', []),
                                'major': row.get('major', row.get('Major', '')),
                                'grad_year': str(row.get('grad_year', row.get('Grad Yr', ''))),
                                'location': row.get('location', ''),
                                'profile_image_url': cached_image,
                                'linkedin': row.get('linkedin', row.get('Linkedin', '')),
                                'email': row.get('email', row.get('Personal Gmail', '')),
                                'similarity': match_score / 10.0  # Normalize score
                            })

                    # Sort by match score (highest first) and limit to top 10
                    member_cards.sort(key=lambda x: x['similarity'], reverse=True)
                    member_cards = member_cards[:10]

                # If still no matches, fall back to embeddings for semantic search
                if not member_cards:
                    genai.configure(api_key=GEMINI_API_KEY)
                    try:
                        result = genai.embed_content(
                            model=EMBEDDING_MODEL,
                            content=user_message,
                            task_type="retrieval_query"
                        )
                        query_embedding = result['embedding']

                        # Query for similar alumni
                        match_response = supabase.rpc('match_alumni', {
                            'query_embedding': query_embedding,
                            'match_count': 10,
                            'exclude_ids': [user_profile.get('csv_source_id')] if user_profile.get('csv_source_id') else []
                        }).execute()

                        if match_response.data:
                            for match in match_response.data[:10]:
                                csv_id = match['csv_row_id']
                                if csv_id in csv_df.index:
                                    row = csv_df.loc[csv_id]
                                    cached_image = row.get('profile_image_url', '')
                                    company_val = row.get('company_name', row.get('company', ''))

                                    member_cards.append({
                                        'id': f'csv_{csv_id}',  # Unique ID for frontend key
                                        'csv_row_id': int(csv_id),
                                        'name': row.get(name_col, ''),
                                        'role_title': row.get('role_title', ''),
                                        'roles_list': row.get('roles_list', []),
                                        'headline': row.get('headline', row.get('linkedinHeadline', '')),
                                        'company': company_val,
                                        'company_name': company_val,
                                        'companies_list': row.get('companies_list', []),
                                        'major': row.get('major', row.get('Major', '')),
                                        'grad_year': str(row.get('grad_year', row.get('Grad Yr', ''))),
                                        'location': row.get('location', ''),
                                        'profile_image_url': cached_image,
                                        'linkedin': row.get('linkedin', row.get('Linkedin', '')),
                                        'email': row.get('email', row.get('Personal Gmail', '')),
                                        'similarity': match.get('similarity', 0)
                                    })
                    except Exception as embed_error:
                        print(f"Embedding search failed: {embed_error}")

            # Build system prompt with THINK info and networking advice
            system_prompt = f"""You are the THINK Networking Advisor, an AI assistant for Purdue THINK members.

ABOUT THINK:
- THINK is a selective business organization at Purdue University
- Members are students and alumni with diverse backgrounds in tech, consulting, finance, and more
- The platform helps members network with alumni and other members

YOUR ROLE:
- Help members with networking advice and strategies
- Provide career guidance and professional development tips
- Answer questions about how to use the THINKedIn platform
- Help find and connect with relevant THINK members
- Give specific, actionable advice

PLATFORM FEATURES:
- Alumni Directory: Browse and filter alumni by company, major, year, industry
- AI Recommendations: Personalized alumni suggestions based on profile
- AI Email Writer: Generate professional networking emails with one click
- Profile Management: Update your profile, companies, roles, and interests

USER CONTEXT:
- Name: {user_profile.get('full_name', 'Member')}
- Major: {user_profile.get('major', 'Not specified')}
- Companies: {', '.join(user_profile.get('companies', [])) if user_profile.get('companies') else 'Not specified'}
- Career Interests: {', '.join(user_profile.get('career_interests', [])) if user_profile.get('career_interests') else 'Not specified'}

GUIDELINES:
- Be warm, professional, and encouraging
- Keep responses concise (3-5 sentences unless more detail is needed)
- Give specific examples and actionable steps
- When showing member results, briefly explain why they're relevant
- For out-of-scope questions, politely redirect to networking/career topics
- Do NOT use markdown formatting (no **, no *, no bullet points). Write in plain conversational text.

CRITICAL - MEMBER SEARCH RULES:
- ONLY mention members that appear in MEMBER SEARCH RESULTS below
- NEVER invent, make up, or hallucinate member names - this is extremely important
- If search results are empty or don't match what the user asked for, say "I couldn't find anyone matching that" and suggest using the Alumni Directory
- Do not reference any person who is not explicitly listed in the search results

{("MEMBER SEARCH RESULTS:" + chr(10) + chr(10).join([f"- {m['name']} ({m['role_title']} at {m['company']})" for m in member_cards])) if member_cards else "MEMBER SEARCH RESULTS: No members found matching this query."}"""

            # Build conversation for Gemini
            messages = [system_prompt]
            for msg in conversation_history[-8:]:  # Last 8 messages for context
                if msg['role'] == 'user':
                    messages.append(f"User: {msg['content']}")
                else:
                    messages.append(f"Assistant: {msg['content']}")
            messages.append(f"User: {user_message}")

            full_prompt = '\n\n'.join(messages) + '\n\nAssistant:'

            # Generate response
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(full_prompt)
            ai_response = response.text.strip()

            # Save messages to database
            supabase.table('chat_messages').insert([
                {'session_id': session_id, 'role': 'user', 'content': user_message},
                {'session_id': session_id, 'role': 'assistant', 'content': ai_response}
            ]).execute()

            # Update session timestamp
            supabase.table('chat_sessions').update({
                'updated_at': 'now()'
            }).eq('id', session_id).execute()

            return jsonify({
                'success': True,
                'response': ai_response,
                'session_id': session_id,
                'member_cards': member_cards if member_cards else None
            }), 200

        except Exception as e:
            import traceback
            print(f"Error in chat_advisor: {e}", flush=True)
            print(traceback.format_exc(), flush=True)
            return jsonify({
                'success': False,
                'error': f'Chat failed: {str(e)}'
            }), 500


    @app.route('/api/chat/history', methods=['GET'])
    @require_auth
    def get_chat_history(current_user):
        """Get chat history for the current user."""
        try:
            session_id = request.args.get('session_id')

            if session_id:
                # Get specific session's messages
                session_check = supabase.table('chat_sessions').select('id').eq(
                    'id', session_id
                ).eq('user_id', current_user['user_id']).execute()

                if not session_check.data:
                    return jsonify({'error': 'Session not found'}), 404

                messages = supabase.table('chat_messages').select(
                    'role, content, created_at'
                ).eq('session_id', session_id).order('created_at', desc=False).execute()

                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'messages': messages.data
                }), 200
            else:
                # Get most recent session
                sessions = supabase.table('chat_sessions').select('id').eq(
                    'user_id', current_user['user_id']
                ).order('updated_at', desc=True).limit(1).execute()

                if sessions.data:
                    session_id = sessions.data[0]['id']
                    messages = supabase.table('chat_messages').select(
                        'role, content, created_at'
                    ).eq('session_id', session_id).order('created_at', desc=False).execute()

                    return jsonify({
                        'success': True,
                        'session_id': session_id,
                        'messages': messages.data
                    }), 200
                else:
                    return jsonify({
                        'success': True,
                        'session_id': None,
                        'messages': []
                    }), 200

        except Exception as e:
            print(f"Error getting chat history: {e}")
            return jsonify({'error': 'Failed to get chat history'}), 500


    @app.route('/api/chat/new', methods=['POST'])
    @require_auth
    def new_chat_session(current_user):
        """Start a new chat session."""
        try:
            new_session = supabase.table('chat_sessions').insert({
                'user_id': current_user['user_id']
            }).execute()

            return jsonify({
                'success': True,
                'session_id': new_session.data[0]['id']
            }), 200

        except Exception as e:
            print(f"Error creating chat session: {e}")
            return jsonify({'error': 'Failed to create chat session'}), 500


    # ============================================================================
    # DEV-ONLY: Debug endpoint to clear stuck users
    # ============================================================================
    @app.route('/api/dev/clear-user', methods=['POST'])
    def dev_clear_user():
        """DEV ONLY: Clear a user by email (for testing account deletion)"""
        try:
            data = request.get_json()
            email = data.get('email')

            if not email:
                return jsonify({'error': 'Email required'}), 400

            print(f"DEV: Attempting to clear user with email: {email}")
            results = {'email': email, 'steps': []}

            # Find user in auth by listing users
            try:
                users_response = supabase_admin.auth.admin.list_users()
                target_user = None

                for user in users_response:
                    if user.email == email:
                        target_user = user
                        break

                if not target_user:
                    return jsonify({'error': 'User not found in auth', 'email': email}), 404

                user_id = target_user.id
                results['user_id'] = user_id
                results['steps'].append(f"Found user_id: {user_id}")
                print(f"DEV: Found user_id: {user_id}")
            except Exception as e:
                results['steps'].append(f"Error finding user: {str(e)}")
                return jsonify({'error': f'Error finding user: {str(e)}', 'results': results}), 500

            # Delete chat sessions
            try:
                supabase_admin.table('chat_sessions').delete().eq('user_id', user_id).execute()
                results['steps'].append("Deleted chat sessions")
            except Exception as e:
                results['steps'].append(f"Chat sessions: {str(e)}")

            # Delete connections
            try:
                supabase_admin.table('connections').delete().eq('user_id', user_id).execute()
                supabase_admin.table('connections').delete().eq('target_user_id', user_id).execute()
                results['steps'].append("Deleted connections")
            except Exception as e:
                results['steps'].append(f"Connections: {str(e)}")

            # Delete admin_actions referencing this user (no CASCADE on these FKs)
            try:
                supabase_admin.table('admin_actions').delete().eq('director_user_id', user_id).execute()
                supabase_admin.table('admin_actions').delete().eq('target_user_id', user_id).execute()
                results['steps'].append("Deleted admin actions")
            except Exception as e:
                results['steps'].append(f"Admin actions: {str(e)}")

            # Clear platform_settings.updated_by reference (no CASCADE)
            try:
                supabase_admin.table('platform_settings').update({'updated_by': None}).eq('updated_by', user_id).execute()
                results['steps'].append("Cleared platform_settings references")
            except Exception as e:
                results['steps'].append(f"Platform settings: {str(e)}")

            # Delete profile
            try:
                supabase_admin.table('user_profiles').delete().eq('user_id', user_id).execute()
                results['steps'].append("Deleted user profile")
            except Exception as e:
                results['steps'].append(f"Profile: {str(e)}")

            # Delete auth user - MOST IMPORTANT
            try:
                supabase_admin.auth.admin.delete_user(user_id)
                results['steps'].append("Deleted auth user")
                print(f"DEV: Auth delete successful")
            except Exception as e:
                print(f"DEV: Auth delete error: {e}")
                results['steps'].append(f"Auth delete error: {str(e)}")
                return jsonify({
                    'error': f'Failed to delete auth user: {str(e)}',
                    'results': results
                }), 500

            return jsonify({
                'success': True,
                'message': f'User {email} cleared successfully',
                'results': results
            }), 200

        except Exception as e:
            import traceback
            print(f"DEV: Error clearing user: {e}")
            print(traceback.format_exc())
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    if AUTH_ENABLED:
        try:
            config.validate_config()
            print("✓ Configuration validated successfully")
        except ValueError as e:
            print(f"✗ Configuration error: {e}")
            print("Please set up your .env file before running the server.")
            exit(1)

    app.run(debug=True, host='0.0.0.0', port=5001)
