# Alumni CSV Matching System

## Overview

This system automatically links new user signups with existing CSV alumni records to avoid duplicates and keep alumni cards up-to-date.

## How It Works

### 1. When a User Completes Onboarding

When a user completes their profile (sets `onboarding_completed=true`), the system:

1. **Loads the CSV alumni data**
2. **Attempts to match the user** with existing CSV records using this logic:
   - **Single name match** (similarity > 85%) → Links to that record
   - **Multiple name matches** → Tries to match by email to disambiguate
   - **No clear match** → User gets a new alumni card

### 2. Match Types

The system creates three types of matches:

| Match Type | Description | CSV Linked? | Creates New Card? |
|-----------|-------------|-------------|-------------------|
| `single_name_match` | One clear name match found | ✅ Yes | ❌ No |
| `name_and_email_match` | Multiple names matched, email confirmed | ✅ Yes | ❌ No |
| `ambiguous_multiple_matches` | Multiple names, no email match | ❌ No | ✅ Yes |
| No match | Name not found in CSV | ❌ No | ✅ Yes |

### 3. Data Priority

When a user profile is linked to a CSV record, the **user profile data takes priority**:

| Field | CSV Data | User Profile Data | Winner |
|-------|----------|-------------------|--------|
| Name | John Doe | John M. Doe | **User Profile** |
| Company | Google | Google, Microsoft | **User Profile** |
| Major | CS | Computer Science | **User Profile** |
| All fields | ❌ Static | ✅ Live updates | **User Profile** |

### 4. Database Fields

New fields added to `user_profiles`:

- `csv_source_id` - Index of the CSV row this profile links to
- `csv_match_type` - How the match was made
- `csv_match_confidence` - Match confidence (0-1)
- `is_csv_linked` - Boolean flag for quick lookups

## Examples

### Example 1: Single Name Match
```
CSV: "Jane Smith" <jane.smith@purdue.edu>
User signs up: "Jane Smith" <jane.smith@gmail.com>

Result: ✅ Linked (single_name_match, confidence 1.0)
Effect: Jane's profile updates now appear on her CSV alumni card
```

### Example 2: Multiple Names, Email Match
```
CSV:
  - "John Smith" <john.smith@purdue.edu>
  - "John Smith" <jsmith@purdue.edu>

User signs up: "John Smith" <jsmith@gmail.com>

Result: ❌ Not linked (emails don't match)
Effect: New alumni card created for this John Smith
```

### Example 3: Multiple Names, Email Disambiguates
```
CSV:
  - "John Doe" <john.doe@purdue.edu>
  - "John Doe" <jdoe@purdue.edu>

User signs up: "John Doe" <john.doe@gmail.com>

Match: Check if emails match...
  - john.doe@purdue.edu vs john.doe@gmail.com → Close but not exact

Result: ❌ Not linked (ambiguous)
Effect: New card created
```

### Example 4: New User
```
CSV: No "Sarah Johnson"

User signs up: "Sarah Johnson" <sarah.j@example.com>

Result: ❌ Not linked (no CSV record)
Effect: New alumni card created
```

## Setup Instructions

### 1. Run SQL Migration

Run this in Supabase SQL Editor:

```sql
-- Add CSV linking fields
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS csv_source_id INTEGER,
ADD COLUMN IF NOT EXISTS csv_match_type TEXT,
ADD COLUMN IF NOT EXISTS csv_match_confidence FLOAT,
ADD COLUMN IF NOT EXISTS is_csv_linked BOOLEAN DEFAULT FALSE;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_csv_source_id ON user_profiles(csv_source_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_is_csv_linked ON user_profiles(is_csv_linked);
```

### 2. Backend Changes

The matching happens automatically:
- **Trigger**: When user sets `onboarding_completed=true`
- **Location**: `backend/app.py` - `/api/profile` PUT endpoint
- **Service**: `backend/services/alumni_matcher.py`

### 3. Frontend Impact

**No changes needed** - matching happens transparently on the backend.

The `/api/alumni` endpoint now returns merged data:
- CSV records linked to profiles show profile data
- Unlinked CSV records show CSV data
- New users appear as new cards

## Testing

### Test Scenario 1: Match Existing User
1. Sign up with name that exists in CSV
2. Complete onboarding
3. Check Supabase: `csv_source_id` should be set
4. Check frontend: Your profile changes should appear on the alumni card

### Test Scenario 2: New User
1. Sign up with name NOT in CSV
2. Complete onboarding
3. Check Supabase: `csv_source_id` should be `NULL`
4. Check frontend: New alumni card should appear with your data

### Test Scenario 3: Ambiguous Match
1. Sign up with name that has multiple CSV matches
2. Use email that doesn't match any CSV email
3. Complete onboarding
4. Check: New card should be created (not linked)

## Monitoring

Check backend logs for matching results:

```
✓ Linked user abc123... to CSV record #42 (single_name_match)
⊙ No CSV match for user def456... - will create new card
```

## Future Enhancements

1. **Manual Linking**: Admin UI to manually link/unlink profiles
2. **Fuzzy Matching**: Better name similarity algorithms
3. **Merge Suggestions**: Show admins potential matches for review
4. **Batch Re-matching**: Re-run matching for all existing profiles
