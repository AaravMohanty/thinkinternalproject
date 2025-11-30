#!/usr/bin/env python3
"""
Script to auto-confirm all existing user emails
Run this once to fix any users created before the auto-confirm feature
"""
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from supabase import create_client

def confirm_all_users():
    """Auto-confirm all user emails in the database"""
    print("🔧 Auto-confirming all user emails...")

    try:
        # Use service key for admin access
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

        # Get all users from auth.users
        # Note: This requires direct database access or admin API
        # For now, we'll get users from user_profiles and update them

        response = supabase.table('user_profiles').select('user_id, full_name, personal_email').execute()

        if not response.data:
            print("❌ No users found")
            return

        users = response.data
        print(f"📊 Found {len(users)} users to confirm")

        confirmed_count = 0
        failed_count = 0

        for user in users:
            try:
                user_id = user['user_id']
                email = user.get('personal_email', 'Unknown')
                name = user.get('full_name', 'Unknown')

                # Update user via admin API
                supabase.auth.admin.update_user_by_id(
                    user_id,
                    {
                        "email_confirm": True
                    }
                )

                print(f"  ✅ Confirmed: {name} ({email})")
                confirmed_count += 1

            except Exception as e:
                print(f"  ❌ Failed for {name}: {str(e)}")
                failed_count += 1

        print(f"\n✅ Confirmation complete!")
        print(f"   - Confirmed: {confirmed_count}")
        print(f"   - Failed: {failed_count}")

        if confirmed_count > 0:
            print(f"\n✨ All users can now login without email verification!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("  Auto-Confirm User Emails")
    print("=" * 60)
    print()

    confirm_all_users()

    print()
    print("=" * 60)
