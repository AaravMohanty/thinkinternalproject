"""
Supabase Storage Service
Handles profile image storage in Supabase Storage
"""
import os
import hashlib
import requests
from typing import Optional, Tuple
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

# Storage bucket name
PROFILE_IMAGES_BUCKET = "profile-images"

# Supabase Storage API base URL
STORAGE_API_URL = f"{SUPABASE_URL}/storage/v1"


def get_image_hash(url: str) -> str:
    """Generate a unique filename from image URL."""
    return hashlib.md5(url.encode()).hexdigest()


def get_public_url(filename: str) -> str:
    """Get the public URL for a stored image."""
    return f"{SUPABASE_URL}/storage/v1/object/public/{PROFILE_IMAGES_BUCKET}/{filename}"


def check_image_exists(filename: str) -> bool:
    """Check if an image already exists in Supabase Storage."""
    try:
        url = f"{STORAGE_API_URL}/object/info/public/{PROFILE_IMAGES_BUCKET}/{filename}"
        headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY
        }
        response = requests.head(url, headers=headers, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def upload_image_to_supabase(image_data: bytes, filename: str, content_type: str = "image/jpeg") -> Tuple[bool, Optional[str]]:
    """
    Upload an image to Supabase Storage.

    Args:
        image_data: Raw image bytes
        filename: Filename to store as (e.g., "abc123.jpg")
        content_type: MIME type of the image

    Returns:
        Tuple of (success, public_url or error_message)
    """
    try:
        url = f"{STORAGE_API_URL}/object/{PROFILE_IMAGES_BUCKET}/{filename}"

        headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "apikey": SUPABASE_SERVICE_KEY,
            "Content-Type": content_type,
            "x-upsert": "true"  # Overwrite if exists
        }

        response = requests.post(url, headers=headers, data=image_data, timeout=30)

        if response.status_code in [200, 201]:
            public_url = get_public_url(filename)
            return (True, public_url)
        else:
            error_msg = response.json().get('message', response.text)
            print(f"Supabase upload error: {error_msg}")
            return (False, error_msg)

    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        return (False, str(e))


def download_and_upload_image(image_url: str, name: str = "") -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Download an image from URL and upload to Supabase Storage.

    Args:
        image_url: Source image URL (e.g., LinkedIn profile image)
        name: Optional name for logging

    Returns:
        Tuple of (success, filename, public_url)
    """
    try:
        # Generate filename from URL hash
        image_hash = get_image_hash(image_url)

        # Check if already exists in Supabase
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            filename = f"{image_hash}{ext}"
            if check_image_exists(filename):
                print(f"Image already in Supabase for {name}: {filename}")
                return (True, filename, get_public_url(filename))

        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://www.linkedin.com/'
        }

        response = requests.get(image_url, headers=headers, timeout=15)
        response.raise_for_status()

        # Determine file extension from content type
        content_type = response.headers.get('Content-Type', 'image/jpeg')
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'
        else:
            ext = '.jpg'
            content_type = 'image/jpeg'

        filename = f"{image_hash}{ext}"

        # Upload to Supabase
        success, result = upload_image_to_supabase(response.content, filename, content_type)

        if success:
            print(f"Uploaded image to Supabase for {name}: {filename}")
            return (True, filename, result)
        else:
            print(f"Failed to upload to Supabase for {name}: {result}")
            return (False, None, None)

    except requests.RequestException as e:
        print(f"Failed to download image for {name}: {e}")
        return (False, None, None)
    except Exception as e:
        print(f"Error processing image for {name}: {e}")
        return (False, None, None)


def migrate_local_image_to_supabase(local_path: str, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Migrate a locally cached image to Supabase Storage.

    Args:
        local_path: Path to local image file
        filename: Filename to use in Supabase

    Returns:
        Tuple of (success, public_url)
    """
    try:
        # Check if already in Supabase
        if check_image_exists(filename):
            return (True, get_public_url(filename))

        # Read local file
        with open(local_path, 'rb') as f:
            image_data = f.read()

        # Determine content type from extension
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        content_type = content_types.get(ext, 'image/jpeg')

        # Upload to Supabase
        success, result = upload_image_to_supabase(image_data, filename, content_type)

        if success:
            return (True, result)
        else:
            return (False, None)

    except Exception as e:
        print(f"Error migrating {filename}: {e}")
        return (False, None)


def get_supabase_image_url(linkedin_url: str, verify_exists: bool = False) -> Optional[str]:
    """
    Get the Supabase public URL for a LinkedIn image.

    Args:
        linkedin_url: Original LinkedIn image URL
        verify_exists: If True, verify the image exists in Supabase (slow).
                      If False, just return expected URL (fast, relies on frontend fallback).

    Returns:
        Supabase public URL (if verify_exists=False) or verified URL (if verify_exists=True)
    """
    if not linkedin_url or str(linkedin_url).strip() in ['', 'nan', 'null', 'None']:
        return None

    image_hash = get_image_hash(str(linkedin_url))

    # Default to .jpg since that's what we use most
    filename = f"{image_hash}.jpg"

    if verify_exists:
        # Slow path - verify existence
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            test_filename = f"{image_hash}{ext}"
            if check_image_exists(test_filename):
                return get_public_url(test_filename)
        return None
    else:
        # Fast path - return expected URL, let frontend handle if missing
        return get_public_url(filename)
