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

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Google Drive configuration
GOOGLE_DRIVE_FILE_ID = "1-ZPmzBu6xat2qQxOti2vg7ricaAlzkn_"
GOOGLE_DRIVE_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"

# Fallback data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ALUMNI_CSV = os.path.join(DATA_DIR, "alumni.csv")

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
    """Download image from URL and cache it locally. Returns cached filename or None."""
    if not image_url or str(image_url).strip() in ['', 'nan', 'null', 'None']:
        return None

    try:
        # Generate cache filename from URL hash
        image_hash = get_image_hash(image_url)
        # Try common image extensions
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            cached_path = os.path.join(CACHE_DIR, f"{image_hash}{ext}")
            if os.path.exists(cached_path):
                print(f"Using cached image for {person_name}: {image_hash}{ext}")
                return f"{image_hash}{ext}"

        # If not cached, download it
        print(f"Downloading image for {person_name}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://www.linkedin.com/'
        }

        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Detect image format from content-type
        content_type = response.headers.get('Content-Type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            ext = '.jpg'
        elif 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            ext = '.jpg'  # Default fallback

        cached_filename = f"{image_hash}{ext}"
        cached_path = os.path.join(CACHE_DIR, cached_filename)

        # Save image to cache
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
    df["grad_year"] = df["Grad Yr"].fillna("").astype(str).replace("nan", "") if "Grad Yr" in df.columns else ""
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

    # Initialize profile_image_url column (will be populated with cached filenames)
    df["profile_image_url"] = ""

    def build_companies_list(row):
        companies = []
        if "companyName" in row and row["companyName"] and str(row["companyName"]).strip():
            companies.append(str(row["companyName"]).strip())
        if "previousCompanyName" in row and row["previousCompanyName"] and str(row["previousCompanyName"]).strip():
            companies.append(str(row["previousCompanyName"]).strip())
        return companies

    df["companies_list"] = df.apply(build_companies_list, axis=1)

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
    """Load alumni data from Google Drive, local CSV, or seed data."""
    df = None

    # Try Google Drive first
    if GOOGLE_DRIVE_FILE_ID:
        df = download_csv_from_google_drive(GOOGLE_DRIVE_URL)

    # Fall back to local CSV
    if df is None and os.path.exists(ALUMNI_CSV):
        df = pd.read_csv(ALUMNI_CSV)

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
            df["schools_list"] = [[]]
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
    custom_images = {
        "Aadit Bennur": "/assets/Aadit.jpeg"
    }

    # Apply custom image mappings
    for name, image_path in custom_images.items():
        df.loc[df["name"].str.contains(name, case=False, na=False), "profile_image_url"] = image_path

    # Cache LinkedIn profile images
    print("Caching profile images...")
    for idx, row in df.iterrows():
        # Skip if already has custom image
        if row["profile_image_url"] and str(row["profile_image_url"]).startswith("/assets/"):
            continue

        # Try to cache the LinkedIn image
        linkedin_image = row.get("linkedin_image_url", "")
        if linkedin_image and str(linkedin_image).strip() not in ['', 'nan', 'null', 'None']:
            cached_filename = download_and_cache_image(linkedin_image, row["name"])
            if cached_filename:
                df.at[idx, "profile_image_url"] = cached_filename

    print(f"Image caching complete. Total alumni: {len(df)}")
    return df


@app.route('/api/alumni', methods=['GET'])
def get_alumni():
    """Get all alumni or filtered alumni."""
    try:
        df = load_alumni_data()

        # Get query parameters
        name_query = request.args.get('name', '').lower()
        title_query = request.args.get('title', '').lower()
        major = request.args.get('major', '')
        grad_year = request.args.get('grad_year', '')
        company = request.args.get('company', '')
        industry = request.args.get('industry', '')

        # Apply filters
        if name_query:
            df = df[df['name'].str.lower().str.contains(name_query, na=False)]
        if title_query:
            df = df[df['role_title'].str.lower().str.contains(title_query, na=False) |
                   df['headline'].str.lower().str.contains(title_query, na=False)]
        if major:
            df = df[df['major'] == major]
        if grad_year:
            df = df[df['grad_year'] == grad_year]
        if company:
            df = df[df['companies_list'].apply(lambda x: company in x)]
        if industry:
            df = df[df['company_industry'] == industry]

        # Convert to JSON and replace NaN with None
        alumni_list = df.replace({pd.NA: None, float('nan'): None}).to_dict('records')

        return jsonify({
            'success': True,
            'count': len(alumni_list),
            'data': alumni_list
        })

    except Exception as e:
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


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
