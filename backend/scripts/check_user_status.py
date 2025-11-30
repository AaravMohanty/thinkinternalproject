#!/usr/bin/env python3
"""
Check user email confirmation status
"""
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from supabase import create_client

def check_user_status(email):
    """Check if a user's email is confirmed"""
    print(f"🔍 Checking status for: {email}")
    print()

    try:
        # Use service key for admin access
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

        # Get user from user_profiles
        response = supabase.table('user_profiles').select('*').eq('personal_email', email).execute()

        if not response.data or len(response.data) == 0:
            print(f"❌ No user found with email: {email}")
            return

        user_profile = response.data[0]
        user_id = user_profile['user_id']

        print("✅ User Profile Found:")
        print(f"   - User ID: {user_id}")
        print(f"   - Name: {user_profile.get('full_name', 'N/A')}")
        print(f"   - Email: {user_profile.get('personal_email', 'N/A')}")
        print(f"   - Is Director: {user_profile.get('is_director', False)}")
        print()

        # Try to get auth user details via admin API
        try:
            auth_user = supabase.auth.admin.get_user_by_id(user_id)

            if auth_user and auth_user.user:
                print("✅ Auth User Found:")
                print(f"   - Email: {auth_user.user.email}")
                print(f"   - Email Confirmed At: {auth_user.user.email_confirmed_at}")
                print(f"   - Created At: {auth_user.user.created_at}")
                print()

                if auth_user.user.email_confirmed_at:
                    print("✅ Email is CONFIRMED - User should be able to login!")
                else:
                    print("❌ Email is NOT confirmed - User cannot login!")
                    print()
                    print("🔧 Running auto-confirm now...")

                    # Try to confirm
                    supabase.auth.admin.update_user_by_id(
                        user_id,
                        {"email_confirm": True}
                    )
                    print("✅ Email confirmed! User can now login.")
            else:
                print("❌ Auth user not found!")

        except Exception as e:
            print(f"❌ Error getting auth user: {str(e)}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_user_status.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    print("=" * 60)
    print("  User Status Checker")
    print("=" * 60)
    print()

    check_user_status(email)

    print()
    print("=" * 60)
