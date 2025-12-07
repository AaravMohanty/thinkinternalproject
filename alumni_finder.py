"""
PurdueTHINK — Alumni Finder (Streamlit, simple & polished UI)
-------------------------------------------------------------
Run:
    pip install streamlit pandas
    streamlit run app.py

- Single-file demo that reads from ./data/alumni.csv
- No auth. Sidebar filters + card grid results.
- Replace the CSV with your real alumni data later.
"""

from __future__ import annotations
import os
from typing import List, Tuple
import requests
from io import StringIO

import pandas as pd
import streamlit as st

APP_TITLE = "PurdueTHINK — Alumni Finder"
DATA_DIR = "data"
ALUMNI_CSV = os.path.join(DATA_DIR, "alumni.csv")

# Google Drive configuration
# To get the direct download link:
# 1. Share the file in Google Drive (Anyone with link can view)
# 2. Get the file ID from the share link
# 3. Use this format: https://drive.google.com/uc?export=download&id=FILE_ID
# Example: if share link is https://drive.google.com/file/d/1ABC123/view
# Then FILE_ID is 1ABC123
GOOGLE_DRIVE_FILE_ID = "1awF00O41QXsCYFWj2fb_nHr_ycuXGtCN"  # Updated with new alumni data
GOOGLE_DRIVE_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}" if GOOGLE_DRIVE_FILE_ID else None

# ----------------------------
# Seed data (no personal info)
# ----------------------------
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
    {
        "name": "Emily Zhao",
        "role_title": "Quant Research Analyst",
        "company": "Two Sigma",
        "major": "Mathematics",
        "grad_year": "2021",
        "linkedin": "https://www.linkedin.com/in/emily-zhao",
        "email": "emily.zhao@example.com",
        "phone": "(555) 201-0004",
    },
    {
        "name": "Noah Williams",
        "role_title": "Security Engineer",
        "company": "Cloudflare",
        "major": "Computer Engineering",
        "grad_year": "2020",
        "linkedin": "https://www.linkedin.com/in/noah-williams",
        "email": "noah.williams@example.com",
        "phone": "(555) 201-0005",
    },
    {
        "name": "Sofia Rossi",
        "role_title": "UX Designer",
        "company": "Airbnb",
        "major": "User Experience Design",
        "grad_year": "2024",
        "linkedin": "https://www.linkedin.com/in/sofia-rossi",
        "email": "sofia.rossi@example.com",
        "phone": "(555) 201-0006",
    },
    {
        "name": "Thomas Nguyen",
        "role_title": "Machine Learning Engineer",
        "company": "NVIDIA",
        "major": "Computer Science",
        "grad_year": "2025",
        "linkedin": "https://www.linkedin.com/in/thomas-nguyen",
        "email": "thomas.nguyen@example.com",
        "phone": "(555) 201-0007",
    },
]


# ----------------------------
# Data IO
# ----------------------------
def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    # Only create CSV from seed if CSV doesn't exist
    if not os.path.exists(ALUMNI_CSV):
        pd.DataFrame(SEED).to_csv(ALUMNI_CSV, index=False)


def parse_multiple_values(value: str, delimiter: str = ",") -> List[str]:
    """Parse comma-separated or semicolon-separated values."""
    if pd.isna(value) or value == "":
        return []
    # Try different delimiters
    if ";" in str(value):
        delimiter = ";"
    return [v.strip() for v in str(value).split(delimiter) if v.strip()]


def download_csv_from_google_drive(url: str) -> pd.DataFrame:
    """Download CSV from Google Drive and return as DataFrame."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Parse CSV from the response text
        csv_data = StringIO(response.text)
        return pd.read_csv(csv_data)
    except Exception as e:
        st.error(f"Failed to download CSV from Google Drive: {e}")
        return None


@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour
def load_alumni() -> pd.DataFrame:
    ensure_data()

    df = None

    # Try to load from Google Drive first if URL is configured
    if GOOGLE_DRIVE_URL and GOOGLE_DRIVE_FILE_ID:
        with st.spinner("Loading alumni data from Google Drive..."):
            df = download_csv_from_google_drive(GOOGLE_DRIVE_URL)
            if df is not None:
                st.success("✓ Data loaded from Google Drive", icon="✅")

    # Fall back to local CSV if Google Drive fails or not configured
    if df is None and os.path.exists(ALUMNI_CSV):
        # Load the local LinkedIn-enriched CSV
        df = pd.read_csv(ALUMNI_CSV)
        st.info("Using local CSV file")

    # If still no data, use seed data
    if df is None:
        df = pd.DataFrame(SEED)
        st.warning("Using sample data. Please configure Google Drive URL or add local CSV.")

    # Process the DataFrame regardless of source
    if "Name" in df.columns:  # New LinkedIn CSV format
        process_linkedin_csv(df)
    else:  # Old format or seed data
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

    # Ensure all required columns exist and are strings
    cols = ["name", "role_title", "company", "major", "grad_year", "linkedin", "email", "phone"]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)

    # Add a normalized grad year for numeric sorting
    def to_int_safe(x):
        try:
            return int(float(x))  # Handle both int and float strings
        except Exception:
            return None
    df["grad_year_int"] = df["grad_year"].apply(to_int_safe)

    # Remove duplicates based on name and email combination
    # Keep the first occurrence of each unique person
    df = df.drop_duplicates(subset=["name", "email"], keep="first")

    return df

def process_linkedin_csv(df: pd.DataFrame):
    """Process LinkedIn CSV format into standard format."""
    # Map the new columns to our internal names
    df["name"] = df["Name"].fillna("") if "Name" in df.columns else ""

    # Handle LinkedIn URL - check both possible column names
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

    # Handle job title - check both columns
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

    # Handle location - check multiple possible columns
    if "location" in df.columns:
        df["location"] = df["location"].fillna("")
    elif "linkedinJobLocation" in df.columns:
        df["location"] = df["linkedinJobLocation"].fillna("")
    else:
        df["location"] = ""

    df["headline"] = df["linkedinHeadline"].fillna("") if "linkedinHeadline" in df.columns else ""
    df["profile_image_url"] = df["linkedinProfileImageUrl"].fillna("") if "linkedinProfileImageUrl" in df.columns else ""

    # Build companies list from current and previous companies
    def build_companies_list(row):
        companies = []
        if "companyName" in row and row["companyName"] and str(row["companyName"]).strip():
            companies.append(str(row["companyName"]).strip())
        if "previousCompanyName" in row and row["previousCompanyName"] and str(row["previousCompanyName"]).strip():
            companies.append(str(row["previousCompanyName"]).strip())
        return companies

    df["companies_list"] = df.apply(build_companies_list, axis=1)

    # Build schools list from LinkedIn school fields
    def build_schools_list(row):
        schools = []
        if "linkedinSchoolName" in row and row["linkedinSchoolName"] and str(row["linkedinSchoolName"]).strip():
            schools.append(str(row["linkedinSchoolName"]).strip())
        if "linkedinPreviousSchoolName" in row and row["linkedinPreviousSchoolName"] and str(row["linkedinPreviousSchoolName"]).strip():
            schools.append(str(row["linkedinPreviousSchoolName"]).strip())
        return schools

    df["schools_list"] = df.apply(build_schools_list, axis=1)

    # Add phone column (not in new format)
    df["phone"] = ""


def mailto(email: str) -> str:
    return f"mailto:{email}" if email else "#"


# ----------------------------
# UI helpers / styling
# ----------------------------
CARD_CSS = """
<style>
/* Page polish */
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Contact Card - MASSIVE FLASHING NEON */
.contact-card {
  background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
  border: 8px solid;
  border-radius: 30px;
  padding: 60px;
  margin-bottom: 40px;
  box-shadow: 0 0 80px rgba(255, 0, 255, 0.8), 0 0 120px rgba(0, 255, 255, 0.6);
  text-align: center;
  animation: rainbow-border 3s infinite, card-pop 2s infinite, mega-glow 1.5s infinite;
  transform-origin: center;
}
@keyframes rainbow-border {
  0% { border-color: #ff0000; box-shadow: 0 0 80px rgba(255, 0, 0, 0.9), 0 0 120px rgba(255, 0, 0, 0.6), inset 0 0 60px rgba(255, 0, 0, 0.3); }
  14% { border-color: #ff7700; box-shadow: 0 0 80px rgba(255, 119, 0, 0.9), 0 0 120px rgba(255, 119, 0, 0.6), inset 0 0 60px rgba(255, 119, 0, 0.3); }
  28% { border-color: #ffff00; box-shadow: 0 0 80px rgba(255, 255, 0, 0.9), 0 0 120px rgba(255, 255, 0, 0.6), inset 0 0 60px rgba(255, 255, 0, 0.3); }
  42% { border-color: #00ff00; box-shadow: 0 0 80px rgba(0, 255, 0, 0.9), 0 0 120px rgba(0, 255, 0, 0.6), inset 0 0 60px rgba(0, 255, 0, 0.3); }
  57% { border-color: #00ffff; box-shadow: 0 0 80px rgba(0, 255, 255, 0.9), 0 0 120px rgba(0, 255, 255, 0.6), inset 0 0 60px rgba(0, 255, 255, 0.3); }
  71% { border-color: #0000ff; box-shadow: 0 0 80px rgba(0, 0, 255, 0.9), 0 0 120px rgba(0, 0, 255, 0.6), inset 0 0 60px rgba(0, 0, 255, 0.3); }
  85% { border-color: #ff00ff; box-shadow: 0 0 80px rgba(255, 0, 255, 0.9), 0 0 120px rgba(255, 0, 255, 0.6), inset 0 0 60px rgba(255, 0, 255, 0.3); }
  100% { border-color: #ff0000; box-shadow: 0 0 80px rgba(255, 0, 0, 0.9), 0 0 120px rgba(255, 0, 0, 0.6), inset 0 0 60px rgba(255, 0, 0, 0.3); }
}
@keyframes card-pop {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
@keyframes mega-glow {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.3); }
}
.contact-card h1 {
  font-size: 48px;
  font-weight: 900;
  margin: 0 0 30px 0;
  text-transform: uppercase;
  letter-spacing: 3px;
  line-height: 1.5;
}
.letter {
  display: inline-block;
  animation: letter-jump 0.8s infinite, letter-spin 1.2s infinite, letter-color 2s infinite;
}
@keyframes letter-jump {
  0%, 100% { transform: translateY(0) scale(1); }
  25% { transform: translateY(-30px) scale(1.2); }
  50% { transform: translateY(0) scale(1); }
  75% { transform: translateY(-15px) scale(1.1); }
}
@keyframes letter-spin {
  0% { transform: rotate(0deg) translateY(0); }
  25% { transform: rotate(180deg) translateY(-30px); }
  50% { transform: rotate(360deg) translateY(0); }
  75% { transform: rotate(540deg) translateY(-15px); }
  100% { transform: rotate(720deg) translateY(0); }
}
@keyframes letter-color {
  0% { color: #ff0000; text-shadow: 0 0 20px #ff0000, 0 0 40px #ff0000, 0 0 60px #ff0000, 0 0 80px #ff0000; }
  14% { color: #ff7700; text-shadow: 0 0 20px #ff7700, 0 0 40px #ff7700, 0 0 60px #ff7700, 0 0 80px #ff7700; }
  28% { color: #ffff00; text-shadow: 0 0 20px #ffff00, 0 0 40px #ffff00, 0 0 60px #ffff00, 0 0 80px #ffff00; }
  42% { color: #00ff00; text-shadow: 0 0 20px #00ff00, 0 0 40px #00ff00, 0 0 60px #00ff00, 0 0 80px #00ff00; }
  57% { color: #00ffff; text-shadow: 0 0 20px #00ffff, 0 0 40px #00ffff, 0 0 60px #00ffff, 0 0 80px #00ffff; }
  71% { color: #0000ff; text-shadow: 0 0 20px #0000ff, 0 0 40px #0000ff, 0 0 60px #0000ff, 0 0 80px #0000ff; }
  85% { color: #ff00ff; text-shadow: 0 0 20px #ff00ff, 0 0 40px #ff00ff, 0 0 60px #ff00ff, 0 0 80px #ff00ff; }
  100% { color: #ff0000; text-shadow: 0 0 20px #ff0000, 0 0 40px #ff0000, 0 0 60px #ff0000, 0 0 80px #ff0000; }
}
.contact-card .phone {
  font-size: 120px;
  font-weight: 900;
  margin: 30px 0;
  letter-spacing: 12px;
  font-family: 'Impact', 'Arial Black', sans-serif;
  text-decoration: none;
}
.phone-digit {
  display: inline-block;
  animation: digit-bounce 0.6s infinite, digit-rotate 1s infinite, digit-color 0.8s infinite;
}
@keyframes digit-bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  25% { transform: translateY(-50px) scale(1.3); }
  50% { transform: translateY(0) scale(1); }
  75% { transform: translateY(-25px) scale(1.15); }
}
@keyframes digit-rotate {
  0% { transform: rotate(0deg) translateY(0); }
  25% { transform: rotate(360deg) translateY(-50px); }
  50% { transform: rotate(720deg) translateY(0); }
  75% { transform: rotate(1080deg) translateY(-25px); }
  100% { transform: rotate(1440deg) translateY(0); }
}
@keyframes digit-color {
  0% { color: #ff0000; text-shadow: 0 0 40px #ff0000, 0 0 80px #ff0000, 0 0 120px #ff0000, 0 0 160px #ff0000; }
  12.5% { color: #ff7700; text-shadow: 0 0 40px #ff7700, 0 0 80px #ff7700, 0 0 120px #ff7700, 0 0 160px #ff7700; }
  25% { color: #ffff00; text-shadow: 0 0 40px #ffff00, 0 0 80px #ffff00, 0 0 120px #ffff00, 0 0 160px #ffff00; }
  37.5% { color: #00ff00; text-shadow: 0 0 40px #00ff00, 0 0 80px #00ff00, 0 0 120px #00ff00, 0 0 160px #00ff00; }
  50% { color: #00ffff; text-shadow: 0 0 40px #00ffff, 0 0 80px #00ffff, 0 0 120px #00ffff, 0 0 160px #00ffff; }
  62.5% { color: #0000ff; text-shadow: 0 0 40px #0000ff, 0 0 80px #0000ff, 0 0 120px #0000ff, 0 0 160px #0000ff; }
  75% { color: #ff00ff; text-shadow: 0 0 40px #ff00ff, 0 0 80px #ff00ff, 0 0 120px #ff00ff, 0 0 160px #ff00ff; }
  87.5% { color: #ffffff; text-shadow: 0 0 40px #ffffff, 0 0 80px #ffffff, 0 0 120px #ffffff, 0 0 160px #ffffff; }
  100% { color: #ff0000; text-shadow: 0 0 40px #ff0000, 0 0 80px #ff0000, 0 0 120px #ff0000, 0 0 160px #ff0000; }
}
.contact-card .subtext {
  font-size: 24px;
  font-weight: 700;
  margin-top: 20px;
  animation: subtext-glow 2s infinite;
}
@keyframes subtext-glow {
  0% { color: #ff00ff; text-shadow: 0 0 15px #ff00ff, 0 0 30px #ff00ff; }
  50% { color: #00ffff; text-shadow: 0 0 15px #00ffff, 0 0 30px #00ffff; }
  100% { color: #ff00ff; text-shadow: 0 0 15px #ff00ff, 0 0 30px #ff00ff; }
}

/* Massive SEX text */
.massive-text {
  text-align: center;
  margin: 40px 0;
  font-size: 200px;
  font-weight: 900;
  color: #ff0000;
  text-shadow: 0 0 40px #ff0000, 0 0 80px #ff0000;
  letter-spacing: 20px;
  font-family: 'Impact', 'Arial Black', sans-serif;
}

/* Card grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 16px;
}
@media (min-width: 720px) {
  .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (min-width: 1100px) {
  .card-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

/* Card - Dark Theme */
.card {
  border: 1px solid #374151;
  border-radius: 16px;
  padding: 24px;
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
  position: relative;
  overflow: hidden;
}
.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.3);
  border-color: #60a5fa;
}
.card-header {
  display: flex; align-items: center; gap: 16px; margin-bottom: 16px;
}
.avatar, img.avatar {
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: #ffffff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; letter-spacing: 0.5px; font-size: 18px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  object-fit: cover;
}
.name {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: #f9fafb;
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}
.role {
  margin: 0;
  color: #d1d5db;
  font-size: 15px;
  font-weight: 500;
}
.meta {
  display: flex; gap: 10px; flex-wrap: wrap; margin: 16px 0 12px 0;
  color: #9ca3af; font-size: 13px;
}
.meta .pill {
  border: 1px solid #4b5563;
  padding: 6px 14px;
  border-radius: 24px;
  background: rgba(55, 65, 81, 0.5);
  color: #e5e7eb;
  font-weight: 500;
  backdrop-filter: blur(8px);
}
.links {
  display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px;
  font-size: 14px;
}
.links a {
  text-decoration: none;
  color: #60a5fa;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  transition: all 0.2s ease;
  backdrop-filter: blur(8px);
}
.links a:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: #60a5fa;
  transform: translateY(-2px);
  text-decoration: none;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Company list display */
.company-list {
  color: #d1d5db;
  font-size: 13px;
  line-height: 1.4;
}
</style>
"""


def render_card(row: pd.Series) -> str:
    # Skip empty rows
    name = str(row.get("name", "")).strip()
    if not name:
        return ""  # Return empty string for blank entries

    initials = "".join([part[0].upper() for part in name.split()[:2] if part]) or "?"

    # Helper function to clean values and replace nan with N/A
    def clean_value(val, default="N/A"):
        val_str = str(val).strip()
        if not val_str or val_str.lower() in ["nan", "none", ""]:
            return default
        return val_str

    company = clean_value(row.get("company", ""))
    role = clean_value(row.get("role_title", ""))
    if role == "N/A":
        role = clean_value(row.get("headline", ""))
    major = clean_value(row.get("major", ""))
    gy = clean_value(row.get("grad_year", ""))
    linkedin = clean_value(row.get("linkedin", ""), "")
    email = clean_value(row.get("email", ""), "")
    professional_email = clean_value(row.get("professional_email", ""), "")
    location = clean_value(row.get("location", ""), "")
    industry = clean_value(row.get("company_industry", ""), "")
    profile_image = clean_value(row.get("profile_image_url", ""), "")

    # Use profile image if available, otherwise use initials
    # Check if profile_image is valid and not empty
    if profile_image and profile_image != "nan" and profile_image != "None" and profile_image != "" and profile_image.startswith("http"):
        # Show image with fallback to initials if image fails to load
        avatar_html = f'<div style="position: relative; width: 56px; height: 56px;"><img src="{profile_image}" class="avatar" alt="{name}" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'flex\';" onload="this.nextElementSibling.style.display=\'none\';"/><div class="avatar" style="display: none;">{initials}</div></div>'
    else:
        # No valid image URL, show initials
        avatar_html = f'<div class="avatar">{initials}</div>'

    links = []
    if linkedin:
        links.append(f'<a href="{linkedin}" target="_blank">🔗 LinkedIn</a>')
    if professional_email:
        links.append(f'<a href="{mailto(professional_email)}">📧 Work Email</a>')
    if email:
        links.append(f'<a href="{mailto(email)}">✉️ Personal</a>')

    # Add location and industry pills if available
    meta_pills = [f'<span class="pill">Major: {major}</span>']
    if gy != "N/A":
        meta_pills.append(f'<span class="pill">Class of {gy}</span>')
    if location:
        meta_pills.append(f'<span class="pill">📍 {location}</span>')
    if industry:
        meta_pills.append(f'<span class="pill">{industry}</span>')

    # Show all companies in the company history
    companies_list = row.get("companies_list", [])
    # Filter out any nan/None/empty values from companies list
    companies_list = [c for c in companies_list if c and str(c).strip().lower() not in ["nan", "none", ""]]

    if len(companies_list) > 1:
        # Display all companies separated by bullets
        company_display = ' • '.join(companies_list)
    elif len(companies_list) == 1:
        company_display = companies_list[0]
    else:
        company_display = company

    return f"""
    <div class="card">
      <div class="card-header">
        {avatar_html}
        <div>
          <p class="name">{name}</p>
          <p class="role"><strong>{role}</strong></p>
          <p class="role" style="font-size: 14px; margin-top: 2px;">@ {company_display}</p>
        </div>
      </div>
      <div class="meta">
        {' '.join(meta_pills)}
      </div>
      <div class="links">{'&nbsp;&nbsp;•&nbsp;&nbsp;'.join(links) if links else '<span style="color: #6b7280;">No contact info available</span>'}</div>
    </div>
    """


def filter_controls(df: pd.DataFrame) -> Tuple[str, str, List[str], List[str], List[str], List[str], List[str], List[str]]:
    with st.sidebar:
        st.title("🔎 Filters")
        st.caption("Use any combination. Leave blank to show all.")

        # Name search filter
        q_name = st.text_input("Search by name", placeholder="e.g., John, Smith")

        q_title = st.text_input("Job title contains", placeholder="e.g., software, analyst")
        majors = sorted([m for m in df["major"].unique() if m])
        sel_majors = st.multiselect("Major", majors)

        years = sorted({str(y) for y in df["grad_year"].tolist() if str(y).strip() and str(y) != "nan"})
        sel_years = st.multiselect("Graduation year", years)

        # Get all unique companies from the companies_list column
        all_companies = set()
        for companies_list in df["companies_list"]:
            all_companies.update(companies_list)
        companies = sorted([c for c in all_companies if c])
        sel_companies = st.multiselect("Companies worked at", companies)

        # Get all unique schools
        all_schools = set()
        for schools_list in df["schools_list"]:
            all_schools.update(schools_list)
        schools = sorted([s for s in all_schools if s])
        sel_schools = st.multiselect("Schools attended", schools)

        # Industry filter
        industries = sorted([i for i in df["company_industry"].unique() if i])
        sel_industries = st.multiselect("Industry", industries)

        st.markdown("---")
        st.caption("Sorting")
        sort_field_map = {
            "Name": "name",
            "Company": "company",
            "Job Title": "role_title",
            "Graduation Year": "grad_year_int",  # numeric sort
            "Major": "major",
        }
        sort_by_label = st.selectbox("Sort by", list(sort_field_map.keys()), index=0)
        ascending = st.toggle("Ascending", value=True)
        # Store chosen mapping for main page to use
        st.session_state["_sort_col"] = sort_field_map[sort_by_label]
        st.session_state["_sort_asc"] = ascending

        st.markdown("---")
        if st.button("Reset filters"):
            st.rerun()

        # Add refresh data button
        st.markdown("---")
        st.caption("Data Management")
        if st.button("🔄 Refresh Data from Google Drive"):
            st.cache_data.clear()
            st.success("Cache cleared! Reloading fresh data...")
            st.rerun()

    return q_name, q_title, sel_majors, sel_years, sel_companies, sel_schools, sel_industries


def row_matches(row: pd.Series, q_name: str, q_title: str, sel_majors: List[str], sel_years: List[str],
                sel_companies: List[str], sel_schools: List[str], sel_industries: List[str]) -> bool:
    # Name search
    ok_name = True
    if q_name.strip():
        ok_name = q_name.lower() in row.get("name", "").lower()

    ok_title = True
    if q_title.strip():
        # Search in both job title and headline
        ok_title = (q_title.lower() in row.get("role_title", "").lower() or
                   q_title.lower() in row.get("headline", "").lower())
    ok_major = (not sel_majors) or (row.get("major", "") in set(sel_majors))
    ok_year = (not sel_years) or (str(row.get("grad_year", "")) in set(sel_years))

    # Check if any selected company is in the person's companies list
    ok_company = True
    if sel_companies:
        person_companies = row.get("companies_list", [])
        ok_company = any(c in person_companies for c in sel_companies)

    # Check if any selected school is in the person's schools list
    ok_school = True
    if sel_schools:
        person_schools = row.get("schools_list", [])
        ok_school = any(s in person_schools for s in sel_schools)

    # Check industry
    ok_industry = (not sel_industries) or (row.get("company_industry", "") in set(sel_industries))

    return ok_name and ok_title and ok_major and ok_year and ok_company and ok_school and ok_industry


# ----------------------------
# App
# ----------------------------
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🤝", layout="wide")
    st.title(APP_TITLE)
    st.caption("Filter alumni by job title, major, graduation year, and companies worked at.")
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    df = load_alumni()
    q_name, q_title, sel_majors, sel_years, sel_companies, sel_schools, sel_industries = filter_controls(df)

    filtered = df[df.apply(lambda r: row_matches(r, q_name, q_title, sel_majors, sel_years, sel_companies, sel_schools, sel_industries), axis=1)].copy()

    # Sorting (handles string columns + numeric grad year via grad_year_int)
    sort_col = st.session_state.get("_sort_col", "name")
    sort_asc = st.session_state.get("_sort_asc", True)

    # If sorting by grad_year_int, None values should go last
    if sort_col == "grad_year_int":
        filtered["_sort_key"] = filtered["grad_year_int"].fillna(-10**9 if sort_asc else 10**9)
        filtered = filtered.sort_values(by="_sort_key", ascending=sort_asc, kind="mergesort").drop(columns=["_sort_key"])
    else:
        filtered = filtered.sort_values(by=sort_col, ascending=sort_asc, na_position="last", kind="mergesort")

    st.write(f"Showing **{len(filtered)}** of {len(df)} alumni")

    # Render as a responsive grid
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    if filtered.empty:
        st.info("No results. Try clearing or loosening your filters.")
    else:
        # Filter out empty cards
        html_cards = [render_card(row) for _, row in filtered.iterrows()]
        html_cards = [card for card in html_cards if card]  # Remove empty strings
        if html_cards:
            st.markdown("\n".join(html_cards), unsafe_allow_html=True)
        else:
            st.info("No valid alumni data to display.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.download_button(
        "Download current results (CSV)",
        filtered.drop(columns=["grad_year_int"]).to_csv(index=False).encode("utf-8"),
        file_name="alumni_results.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
