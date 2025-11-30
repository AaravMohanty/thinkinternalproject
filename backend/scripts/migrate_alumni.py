#!/usr/bin/env python3
"""
Alumni Data Migration Script
Migrates alumni data from Google Drive CSV to Supabase

Usage:
    python migrate_alumni.py [--dry-run]

Options:
    --dry-run    Preview the migration without making changes
"""

import os
import sys
import csv
import requests
import secrets
import string
from datetime import datetime

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SUPABASE_URL, SUPABASE_SERVICE_KEY, GOOGLE_DRIVE_FILE_ID
from supabase import create_client, Client

# Initialize Supabase client with service role key (bypasses RLS)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Google Drive CSV URL
GOOGLE_DRIVE_CSV_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"


def generate_temp_password(length=16):
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def download_csv():
    """Download CSV from Google Drive"""
    print(f"📥 Downloading CSV from Google Drive...")

    try:
        response = requests.get(GOOGLE_DRIVE_CSV_URL, timeout=30)
        response.raise_for_status()

        # Save to temp file
        csv_path = '/tmp/gdrive_alumni.csv'
        with open(csv_path, 'wb') as f:
            f.write(response.content)

        print(f"✅ CSV downloaded to {csv_path}")
        return csv_path

    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading CSV: {e}")
        sys.exit(1)


def parse_csv(csv_path):
    """Parse CSV and return list of alumni data"""
    print(f"\n📊 Parsing CSV data...")

    alumni = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip rows with missing critical data
                if not row.get('Name') or not row.get('Personal Gmail'):
                    continue

                # Map CSV columns to user_profiles schema
                alumni_data = {
                    'full_name': row.get('Name', '').strip(),
                    'personal_email': row.get('Personal Gmail', '').strip().lower(),
                    'professional_email': row.get('professionalEmail', '').strip().lower() if row.get('professionalEmail') else None,
                    'graduation_year': int(row.get('Grad Yr', 0)) if row.get('Grad Yr') and row.get('Grad Yr').isdigit() else None,
                    'major': row.get('Major', '').strip() if row.get('Major') else None,
                    'linkedin_url': row.get('linkedinProfileUrl', '').strip() if row.get('linkedinProfileUrl') else None,
                    'current_title': row.get('linkedinJobTitle', '').strip() if row.get('linkedinJobTitle') else None,
                    'current_company': row.get('companyName', '').strip() if row.get('companyName') else None,
                    'location': row.get('location', '').strip() if row.get('location') else None,
                    'profile_image_url': row.get('linkedinProfileImageUrl', '').strip() if row.get('linkedinProfileImageUrl') else None,
                    'is_alumni': True,
                    'visibility': 'members_only',
                }

                # Parse industry into career_interests array
                if row.get('companyIndustry'):
                    industries = [ind.strip() for ind in row.get('companyIndustry', '').split(',') if ind.strip()]
                    alumni_data['career_interests'] = industries
                else:
                    alumni_data['career_interests'] = []

                # Add previous company to target_companies if exists
                if row.get('previousCompanyName'):
                    alumni_data['target_companies'] = [row.get('previousCompanyName', '').strip()]
                else:
                    alumni_data['target_companies'] = []

                alumni.append(alumni_data)

        print(f"✅ Parsed {len(alumni)} alumni records")
        return alumni

    except Exception as e:
        print(f"❌ Error parsing CSV: {e}")
        sys.exit(1)


def create_auth_user(email, full_name, temp_password):
    """Create a Supabase auth user"""
    try:
        # Use Supabase Admin API to create user
        response = supabase.auth.admin.create_user({
            'email': email,
            'password': temp_password,
            'email_confirm': True,  # Auto-confirm email
            'user_metadata': {
                'full_name': full_name,
            }
        })

        return response.user.id if response.user else None

    except Exception as e:
        # User might already exist
        if 'already registered' in str(e).lower():
            # Try to get existing user by email
            try:
                users = supabase.auth.admin.list_users()
                for user in users:
                    if user.email == email:
                        return user.id
            except:
                pass

        print(f"  ⚠️  Error creating auth user for {email}: {e}")
        return None


def migrate_alumni(alumni_list, dry_run=False):
    """Migrate alumni to Supabase"""
    print(f"\n🚀 Starting migration {'(DRY RUN)' if dry_run else ''}...")
    print(f"   Found {len(alumni_list)} alumni to migrate\n")

    success_count = 0
    error_count = 0
    skipped_count = 0

    for i, alumni in enumerate(alumni_list, 1):
        email = alumni['personal_email']
        full_name = alumni['full_name']

        print(f"[{i}/{len(alumni_list)}] Processing: {full_name} ({email})")

        if dry_run:
            print(f"  ✓ Would create user and profile")
            success_count += 1
            continue

        try:
            # Check if profile already exists
            existing = supabase.table('user_profiles').select('*').eq('personal_email', email).execute()

            if existing.data and len(existing.data) > 0:
                print(f"  ⊙ Profile already exists, skipping")
                skipped_count += 1
                continue

            # Generate temporary password
            temp_password = generate_temp_password()

            # Create auth user
            user_id = create_auth_user(email, full_name, temp_password)

            if not user_id:
                print(f"  ✗ Failed to create auth user")
                error_count += 1
                continue

            # Create user profile
            profile_data = {
                **alumni,
                'user_id': user_id,
                'signup_referral_code': 'MIGRATED_FROM_CSV',
            }

            response = supabase.table('user_profiles').insert(profile_data).execute()

            if response.data:
                print(f"  ✓ Created profile (user_id: {user_id[:8]}...)")
                success_count += 1
            else:
                print(f"  ✗ Failed to create profile")
                error_count += 1

        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"📊 Migration Summary:")
    print(f"   ✓ Successful: {success_count}")
    print(f"   ⊙ Skipped:    {skipped_count}")
    print(f"   ✗ Errors:     {error_count}")
    print(f"   Total:        {len(alumni_list)}")
    print(f"{'=' * 60}\n")

    if not dry_run and success_count > 0:
        print("⚠️  IMPORTANT NOTES:")
        print("   1. All migrated alumni have temporary passwords")
        print("   2. They should use 'Forgot Password' flow to set their own password")
        print("   3. Consider sending welcome emails with instructions")
        print("   4. Alumni profiles are marked as is_alumni=true")
        print("   5. All profiles have visibility='members_only'\n")


def main():
    """Main migration function"""
    dry_run = '--dry-run' in sys.argv

    print("=" * 60)
    print("🎓 PurdueTHINK Alumni Migration Script")
    print("=" * 60)

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    else:
        print("⚠️  PRODUCTION MODE - Changes will be committed to Supabase")
        confirm = input("   Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Migration cancelled.")
            sys.exit(0)
        print()

    # Download CSV
    csv_path = download_csv()

    # Parse CSV
    alumni_list = parse_csv(csv_path)

    # Migrate alumni
    migrate_alumni(alumni_list, dry_run=dry_run)

    print("✅ Migration complete!")

    if dry_run:
        print("\n💡 To run the actual migration, run without --dry-run:")
        print("   python migrate_alumni.py\n")


if __name__ == '__main__':
    main()
