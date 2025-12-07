"""
Authentication Service
Handles Supabase authentication and user profile management
"""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY, OPS_CODE, SUPER_OPS_CODE
from typing import Dict, Optional, Tuple

# Initialize Supabase clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def validate_referral_code(code: str) -> Tuple[bool, str, bool]:
    """
    Validate referral code and determine user type

    Returns:
        Tuple of (is_valid, error_message, is_director)
    """
    # Check if it's a special director code
    if code == OPS_CODE or code == SUPER_OPS_CODE:
        return (True, "", True)

    # Check if it matches the active platform referral code
    try:
        result = supabase.table('platform_settings').select('active_referral_code').eq('id', 1).execute()

        if result.data and len(result.data) > 0:
            active_code = result.data[0]['active_referral_code']
            if code == active_code:
                return (True, "", False)
            else:
                return (False, "Invalid referral code. Please get the current code from a Director of Operations.", False)
        else:
            return (False, "Platform not configured. Please contact an administrator.", False)

    except Exception as e:
        print(f"Error validating referral code: {str(e)}")
        return (False, "Error validating referral code. Please try again.", False)


def signup_user(email: str, password: str, referral_code: str, full_name: str, profile_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
    """
    Sign up a new user with Supabase Auth and create their profile

    Args:
        email: User's email
        password: User's password
        referral_code: Referral code used for signup
        full_name: User's full name
        profile_data: Additional profile data (major, grad_year, etc.)

    Returns:
        Tuple of (success, message, user_data)
    """
    try:
        # Validate referral code first
        is_valid, error_msg, is_director = validate_referral_code(referral_code)
        if not is_valid:
            return (False, error_msg, None)

        # Create auth user with admin client to auto-confirm email (for development)
        # Use admin client to bypass email verification
        auth_response = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True  # Auto-confirm email for development
        })

        if not auth_response.user:
            return (False, "Failed to create user account. Email may already be registered.", None)

        user_id = auth_response.user.id

        # Create user profile
        profile = {
            'user_id': user_id,
            'full_name': full_name,
            'is_director': is_director,
            'signup_referral_code': referral_code,
            **profile_data
        }

        # Use admin client to insert profile (bypasses RLS)
        profile_response = supabase_admin.table('user_profiles').insert(profile).execute()

        if not profile_response.data:
            # If profile creation fails, we should ideally delete the auth user
            # but for now, we'll return an error
            return (False, "Failed to create user profile.", None)

        # Log admin action if this is a director signup
        if is_director:
            log_admin_action(
                director_user_id=user_id,
                action_type='PROMOTE_DIRECTOR',
                details={
                    'reason': f'Signed up with {referral_code} code',
                    'email': email
                }
            )

        return (True, "Account created successfully!", {
            'user_id': user_id,
            'email': email,
            'full_name': full_name,
            'is_director': is_director
        })

    except Exception as e:
        error_msg = str(e)
        print(f"Signup error: {error_msg}")

        if "already registered" in error_msg or "already exists" in error_msg:
            return (False, "This email is already registered.", None)

        return (False, f"Signup failed: {error_msg}", None)


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Log in a user with Supabase Auth

    Returns:
        Tuple of (success, message, user_data)
    """
    try:
        # Sign in with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not auth_response.user:
            return (False, "Invalid email or password.", None)

        user_id = auth_response.user.id

        # Get user profile to check if they're a director
        profile_response = supabase.table('user_profiles').select('*').eq('user_id', user_id).execute()

        if not profile_response.data or len(profile_response.data) == 0:
            return (False, "User profile not found.", None)

        profile = profile_response.data[0]

        return (True, "Login successful!", {
            'user_id': user_id,
            'email': auth_response.user.email,
            'full_name': profile.get('full_name'),
            'is_director': profile.get('is_director', False),
            'profile': profile,
            'session': {
                'access_token': auth_response.session.access_token,
                'refresh_token': auth_response.session.refresh_token
            }
        })

    except Exception as e:
        error_msg = str(e)
        print(f"Login error for {email}: {error_msg}")

        if "Invalid login credentials" in error_msg:
            return (False, "Invalid email or password.", None)

        if "Email not confirmed" in error_msg:
            return (False, "Please verify your email before logging in. Check your inbox for a confirmation link.", None)

        # Return the actual error for debugging
        return (False, f"Login failed: {error_msg}", None)


def logout_user(access_token: str) -> Tuple[bool, str]:
    """
    Log out a user

    Returns:
        Tuple of (success, message)
    """
    try:
        supabase.auth.sign_out()
        return (True, "Logged out successfully!")
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return (False, "Logout failed.")


def refresh_session(refresh_token: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Refresh an expired session using the refresh token

    Args:
        refresh_token: The refresh token from the original login

    Returns:
        Tuple of (success, message, new_session_data)
    """
    try:
        # Use Supabase to refresh the session
        auth_response = supabase.auth.refresh_session(refresh_token)

        if not auth_response.session:
            return (False, "Failed to refresh session. Please log in again.", None)

        user_id = auth_response.user.id

        # Get user profile
        profile_response = supabase.table('user_profiles').select('*').eq('user_id', user_id).execute()

        if not profile_response.data or len(profile_response.data) == 0:
            return (False, "User profile not found.", None)

        profile = profile_response.data[0]

        return (True, "Session refreshed successfully!", {
            'user_id': user_id,
            'email': auth_response.user.email,
            'full_name': profile.get('full_name'),
            'is_director': profile.get('is_director', False),
            'profile': profile,
            'session': {
                'access_token': auth_response.session.access_token,
                'refresh_token': auth_response.session.refresh_token
            }
        })

    except Exception as e:
        error_msg = str(e)
        print(f"Session refresh error: {error_msg}")

        if "Invalid Refresh Token" in error_msg or "Refresh Token Not Found" in error_msg:
            return (False, "Session expired. Please log in again.", None)

        return (False, f"Failed to refresh session: {error_msg}", None)


def get_user_from_token(access_token: str) -> Optional[Dict]:
    """
    Get user data from access token

    Returns:
        User data dict or None if invalid token
    """
    try:
        # Set the session with the access token
        supabase.auth.set_session(access_token, "")  # Refresh token not needed for verification

        user = supabase.auth.get_user(access_token)

        if not user:
            return None

        user_id = user.user.id

        # Get user profile
        profile_response = supabase.table('user_profiles').select('*').eq('user_id', user_id).execute()

        if not profile_response.data or len(profile_response.data) == 0:
            return None

        profile = profile_response.data[0]

        return {
            'user_id': user_id,
            'email': user.user.email,
            'is_director': profile.get('is_director', False),
            'profile': profile
        }

    except Exception as e:
        print(f"Token validation error: {str(e)}")
        return None


def check_is_director(user_id: str) -> bool:
    """Check if a user is a Director of Operations"""
    try:
        result = supabase.table('user_profiles').select('is_director').eq('user_id', user_id).execute()

        if result.data and len(result.data) > 0:
            return result.data[0].get('is_director', False)

        return False
    except Exception as e:
        print(f"Error checking director status: {str(e)}")
        return False


def reset_password_request(email: str) -> Tuple[bool, str]:
    """
    Send password reset email

    Returns:
        Tuple of (success, message)
    """
    import os
    try:
        # Get frontend URL from environment or use default
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        redirect_url = f"{frontend_url}/reset-password"

        # Request password reset from Supabase with redirect URL
        # The redirect URL is where users will land after clicking the email link
        supabase.auth.reset_password_email(
            email,
            {
                "redirect_to": redirect_url
            }
        )

        # Note: Supabase doesn't throw an error if email doesn't exist (for security)
        return (True, "If an account exists with this email, you will receive a password reset link shortly.")

    except Exception as e:
        error_msg = str(e)
        print(f"Password reset error: {error_msg}")
        return (False, "Failed to send password reset email. Please try again.")


def update_password(access_token: str, new_password: str) -> Tuple[bool, str]:
    """
    Update user's password

    Returns:
        Tuple of (success, message)
    """
    try:
        # Set the session with the access token
        supabase.auth.set_session(access_token, "")

        # Update the password
        supabase.auth.update_user({"password": new_password})

        return (True, "Password updated successfully!")

    except Exception as e:
        error_msg = str(e)
        print(f"Password update error: {error_msg}")
        return (False, "Failed to update password. Please try again.")


def log_admin_action(director_user_id: str, action_type: str, target_user_id: Optional[str] = None, details: Optional[Dict] = None):
    """Log an admin action to the audit log"""
    try:
        action = {
            'director_user_id': director_user_id,
            'action_type': action_type,
            'target_user_id': target_user_id,
            'details': details or {}
        }

        supabase_admin.table('admin_actions').insert(action).execute()
    except Exception as e:
        print(f"Error logging admin action: {str(e)}")
