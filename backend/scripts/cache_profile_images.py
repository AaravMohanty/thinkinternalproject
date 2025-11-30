#!/usr/bin/env python3
"""
Profile Image Caching Script
============================
Downloads LinkedIn profile images and uploads them to Supabase Storage.

This ensures all profile images are permanently stored and won't expire
like LinkedIn's time-limited image URLs.

Usage:
    # Preview what would be cached (dry run)
    python cache_profile_images.py --dry-run

    # Cache all images
    python cache_profile_images.py

    # Cache only new/missing images (skip existing)
    python cache_profile_images.py --skip-existing

    # Force re-cache all images (overwrite existing)
    python cache_profile_images.py --force

    # Cache images for specific names only
    python cache_profile_images.py --names "John Doe" "Jane Smith"

Options:
    --dry-run       Preview without making changes
    --skip-existing Only cache images not already in Supabase (default)
    --force         Re-download and re-upload all images
    --names         Only process specific alumni by name
    --verbose       Show detailed progress for each image

When to run this script:
    1. After adding new members to the CSV file
    2. Periodically to ensure all images are cached
    3. When you notice missing profile images on the website

Note: LinkedIn image URLs expire after some time. Run this script while
the URLs are still valid (typically within a few weeks of the CSV being
generated).
"""

import os
import sys
import time
import argparse
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path to import config and services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from services.storage import (
    download_and_upload_image,
    check_image_exists,
    get_image_hash,
    get_public_url
)

# Path to the CSV file
CSV_PATH = "/Users/sreekargudipati/Coding Projects/THINKInternalProject/gdrive_alumni.csv"


def load_alumni_data():
    """Load alumni data from CSV file."""
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)

    # Normalize column names
    column_mapping = {
        'Name': 'name',
        'Linkedin': 'linkedin',
        'Major': 'major',
        'linkedinProfileImageUrl': 'linkedin_image_url'
    }

    for old_name, new_name in column_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df[new_name] = df[old_name]

    return df


def check_if_cached(linkedin_url):
    """Check if an image is already cached in Supabase."""
    if not linkedin_url or str(linkedin_url).strip() in ['', 'nan', 'null', 'None']:
        return True, None  # No image to cache

    image_hash = get_image_hash(str(linkedin_url))

    # Check for any extension
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        filename = f"{image_hash}{ext}"
        if check_image_exists(filename):
            return True, get_public_url(filename)

    return False, None


def cache_single_image(name, linkedin_url, force=False, verbose=False):
    """
    Cache a single profile image to Supabase.

    Returns:
        tuple: (name, status, message, supabase_url)
        status: 'cached', 'skipped', 'failed', 'no_image'
    """
    # Skip if no image URL
    if not linkedin_url or str(linkedin_url).strip() in ['', 'nan', 'null', 'None']:
        return (name, 'no_image', 'No LinkedIn image URL', None)

    linkedin_url = str(linkedin_url).strip()

    # Check if already cached
    if not force:
        is_cached, existing_url = check_if_cached(linkedin_url)
        if is_cached and existing_url:
            if verbose:
                print(f"  [SKIP] {name}: Already cached")
            return (name, 'skipped', 'Already in Supabase', existing_url)

    # Download and upload to Supabase
    try:
        success, filename, public_url = download_and_upload_image(linkedin_url, name)

        if success:
            if verbose:
                print(f"  [OK] {name}: Cached to {filename}")
            return (name, 'cached', f'Uploaded as {filename}', public_url)
        else:
            if verbose:
                print(f"  [FAIL] {name}: Failed to cache")
            return (name, 'failed', 'Upload failed', None)

    except Exception as e:
        error_msg = str(e)
        if '403' in error_msg:
            error_msg = 'LinkedIn URL expired (403)'
        elif '404' in error_msg:
            error_msg = 'Image not found (404)'

        if verbose:
            print(f"  [FAIL] {name}: {error_msg}")
        return (name, 'failed', error_msg, None)


def main():
    parser = argparse.ArgumentParser(
        description='Cache LinkedIn profile images to Supabase Storage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview without making changes')
    parser.add_argument('--force', action='store_true',
                       help='Re-download all images (overwrite existing)')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                       help='Skip images already in Supabase (default)')
    parser.add_argument('--names', nargs='+',
                       help='Only process specific alumni by name')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed progress')
    parser.add_argument('--parallel', type=int, default=5,
                       help='Number of parallel downloads (default: 5)')

    args = parser.parse_args()

    print("=" * 70)
    print("Profile Image Caching Script")
    print("=" * 70)
    print()

    if args.dry_run:
        print("MODE: Dry Run (no changes will be made)")
    elif args.force:
        print("MODE: Force (re-downloading all images)")
    else:
        print("MODE: Skip Existing (only cache new images)")
    print()

    # Load data
    print("Loading alumni data from CSV...")
    df = load_alumni_data()
    print(f"Found {len(df)} alumni records")
    print()

    # Filter by names if specified
    if args.names:
        name_filter = '|'.join(args.names)
        df = df[df['name'].str.contains(name_filter, case=False, na=False)]
        print(f"Filtered to {len(df)} alumni matching: {', '.join(args.names)}")
        print()

    # Get image URLs
    image_column = 'linkedin_image_url' if 'linkedin_image_url' in df.columns else 'linkedinProfileImageUrl'

    if image_column not in df.columns:
        print("Error: No LinkedIn image URL column found in CSV")
        sys.exit(1)

    # Prepare list of images to process
    to_process = []
    for idx, row in df.iterrows():
        name = row.get('name', row.get('Name', f'Unknown_{idx}'))
        linkedin_url = row.get(image_column, '')

        if linkedin_url and str(linkedin_url).strip() not in ['', 'nan', 'null', 'None']:
            to_process.append((name, str(linkedin_url).strip()))

    print(f"Found {len(to_process)} alumni with LinkedIn image URLs")
    print()

    if args.dry_run:
        # Dry run - just check what would be cached
        print("Checking which images need to be cached...")
        print("-" * 70)

        needs_caching = 0
        already_cached = 0

        for name, linkedin_url in to_process:
            is_cached, existing_url = check_if_cached(linkedin_url)
            if is_cached and existing_url:
                already_cached += 1
                if args.verbose:
                    print(f"  [EXISTS] {name}")
            else:
                needs_caching += 1
                print(f"  [NEEDS CACHING] {name}")

        print("-" * 70)
        print()
        print("Summary:")
        print(f"  Already cached: {already_cached}")
        print(f"  Needs caching:  {needs_caching}")
        print(f"  Total:          {len(to_process)}")
        print()
        print("Run without --dry-run to cache the images.")
        return

    # Actually cache images
    print(f"Caching images (parallel workers: {args.parallel})...")
    print("-" * 70)

    results = {
        'cached': [],
        'skipped': [],
        'failed': [],
        'no_image': []
    }

    start_time = time.time()

    # Use thread pool for parallel downloads
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = {
            executor.submit(
                cache_single_image,
                name,
                linkedin_url,
                args.force,
                args.verbose
            ): (name, linkedin_url)
            for name, linkedin_url in to_process
        }

        completed = 0
        for future in as_completed(futures):
            completed += 1
            name, status, message, url = future.result()
            results[status].append((name, message, url))

            # Progress indicator
            if not args.verbose:
                progress = completed / len(to_process) * 100
                status_char = {'cached': '+', 'skipped': '.', 'failed': 'X', 'no_image': '-'}
                print(f"\r  Progress: {completed}/{len(to_process)} ({progress:.1f}%) ", end='')
                sys.stdout.flush()

    if not args.verbose:
        print()  # New line after progress

    elapsed = time.time() - start_time

    print("-" * 70)
    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"  Successfully cached: {len(results['cached'])}")
    print(f"  Already in Supabase: {len(results['skipped'])}")
    print(f"  Failed to cache:     {len(results['failed'])}")
    print(f"  No image URL:        {len(results['no_image'])}")
    print(f"  --------------------------")
    print(f"  Total processed:     {len(to_process)}")
    print(f"  Time elapsed:        {elapsed:.1f}s")
    print()

    # Show failures if any
    if results['failed']:
        print("Failed images:")
        print("-" * 70)
        for name, message, _ in results['failed'][:20]:  # Show first 20
            print(f"  - {name}: {message}")
        if len(results['failed']) > 20:
            print(f"  ... and {len(results['failed']) - 20} more")
        print()
        print("Note: If images failed due to 'expired URL', the LinkedIn URLs in")
        print("your CSV may be too old. You may need to re-scrape LinkedIn data.")

    # Success message
    total_available = len(results['cached']) + len(results['skipped'])
    print()
    print("=" * 70)
    print(f"Done! {total_available} profile images are now available in Supabase.")
    print("=" * 70)


if __name__ == '__main__':
    main()
