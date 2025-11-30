#!/usr/bin/env python3
"""
Build Alumni Embeddings
Generates embeddings for all alumni in the CSV and stores them in Supabase.

Usage:
  python3 scripts/build_alumni_embeddings.py           # Build all
  python3 scripts/build_alumni_embeddings.py --check   # Check status only
  python3 scripts/build_alumni_embeddings.py --rebuild # Force rebuild all
"""

import sys
import os
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import google.generativeai as genai
from supabase import create_client
from config import GEMINI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, EMBEDDING_MODEL

# Initialize clients
genai.configure(api_key=GEMINI_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Rate limiting for Gemini API (free tier: 15 requests/min for embeddings)
RATE_LIMIT_DELAY = 0.5  # seconds between requests (conservative)

def get_csv_path():
    """Get path to alumni CSV"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'gdrive_alumni.csv'
    )

def load_alumni_csv():
    """Load alumni from CSV"""
    csv_path = get_csv_path()
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} alumni from CSV")
    return df

def create_profile_text(row):
    """Create text representation of alumni profile for embedding"""
    parts = []

    # Name
    name = str(row.get('Name', '')).strip()
    if name and name != 'nan':
        parts.append(f"Name: {name}")

    # Current job
    title = str(row.get('linkedinJobTitle', '')).strip()
    company = str(row.get('companyName', '')).strip()
    if title and title != 'nan':
        parts.append(f"Current Role: {title}")
    if company and company != 'nan':
        parts.append(f"Company: {company}")

    # Industry
    industry = str(row.get('companyIndustry', '')).strip()
    if industry and industry != 'nan':
        parts.append(f"Industry: {industry}")

    # Headline (often contains good summary)
    headline = str(row.get('linkedinHeadline', '')).strip()
    if headline and headline != 'nan':
        parts.append(f"Headline: {headline}")

    # Major
    major = str(row.get('Major', '')).strip()
    if major and major != 'nan':
        parts.append(f"Major: {major}")

    # Location
    location = str(row.get('location', '')).strip()
    if location and location != 'nan':
        parts.append(f"Location: {location}")

    # Skills
    skills = str(row.get('linkedinSkillsLabel', '')).strip()
    if skills and skills != 'nan':
        parts.append(f"Skills: {skills}")

    # Job description (truncate to avoid token limits)
    job_desc = str(row.get('linkedinJobDescription', '')).strip()
    if job_desc and job_desc != 'nan':
        parts.append(f"Experience: {job_desc[:500]}")

    # Previous job for more context
    prev_title = str(row.get('linkedinPreviousJobTitle', '')).strip()
    prev_company = str(row.get('previousCompanyName', '')).strip()
    if prev_title and prev_title != 'nan':
        parts.append(f"Previous Role: {prev_title}")
    if prev_company and prev_company != 'nan':
        parts.append(f"Previous Company: {prev_company}")

    return '\n'.join(parts) if parts else f"Alumni: {name}"

def generate_embedding(text):
    """Generate embedding for text using Gemini"""
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"  Error generating embedding: {e}")
        return None

def get_existing_embeddings():
    """Get list of csv_row_ids that already have embeddings"""
    try:
        response = supabase.table('alumni_embeddings').select('csv_row_id').execute()
        return set(row['csv_row_id'] for row in response.data)
    except Exception as e:
        print(f"Note: Could not fetch existing embeddings: {e}")
        return set()

def upsert_embedding(csv_row_id, name, embedding, profile_text):
    """Insert or update embedding in Supabase"""
    try:
        supabase.table('alumni_embeddings').upsert({
            'csv_row_id': csv_row_id,
            'name': name,
            'embedding': embedding,
            'profile_text': profile_text[:1000],  # Truncate for storage
            'updated_at': 'now()'
        }, on_conflict='csv_row_id').execute()
        return True
    except Exception as e:
        print(f"  Error upserting embedding: {e}")
        return False

def build_embeddings(force_rebuild=False):
    """Build embeddings for all alumni"""
    df = load_alumni_csv()

    # Check existing embeddings
    existing = get_existing_embeddings() if not force_rebuild else set()
    print(f"Existing embeddings: {len(existing)}")

    # Filter to only new alumni
    to_process = []
    for idx, row in df.iterrows():
        if idx not in existing:
            to_process.append((idx, row))

    if not to_process:
        print("All alumni already have embeddings!")
        return

    print(f"\nProcessing {len(to_process)} alumni...")

    success_count = 0
    error_count = 0

    for i, (idx, row) in enumerate(to_process):
        name = str(row.get('Name', f'Row {idx}')).strip()

        # Create profile text
        profile_text = create_profile_text(row)

        # Generate embedding
        print(f"[{i+1}/{len(to_process)}] {name}...", end=' ', flush=True)
        embedding = generate_embedding(profile_text)

        if embedding:
            # Store in Supabase
            if upsert_embedding(idx, name, embedding, profile_text):
                print("✓")
                success_count += 1
            else:
                print("✗ (db error)")
                error_count += 1
        else:
            print("✗ (embedding error)")
            error_count += 1

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

    print(f"\nDone! Success: {success_count}, Errors: {error_count}")

def check_status():
    """Check embedding status"""
    df = load_alumni_csv()
    existing = get_existing_embeddings()

    print(f"\nEmbedding Status:")
    print(f"  Total alumni in CSV: {len(df)}")
    print(f"  Alumni with embeddings: {len(existing)}")
    print(f"  Missing embeddings: {len(df) - len(existing)}")

    if len(existing) > 0:
        # Test query
        print("\nTesting similarity search...")
        try:
            test_text = "Software Engineer interested in AI and Machine Learning"
            test_embedding = generate_embedding(test_text)

            response = supabase.rpc('match_alumni', {
                'query_embedding': test_embedding,
                'match_count': 3,
                'exclude_ids': []
            }).execute()

            print(f"  Top 3 matches for '{test_text}':")
            for match in response.data:
                print(f"    - {match['name']} (similarity: {match['similarity']:.3f})")
        except Exception as e:
            print(f"  Search test failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='Build alumni embeddings')
    parser.add_argument('--check', action='store_true', help='Check status only')
    parser.add_argument('--rebuild', action='store_true', help='Force rebuild all')
    args = parser.parse_args()

    if args.check:
        check_status()
    else:
        build_embeddings(force_rebuild=args.rebuild)

if __name__ == "__main__":
    main()
