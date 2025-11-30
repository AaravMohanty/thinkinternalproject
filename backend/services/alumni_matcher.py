"""
Alumni Matching Service
Matches new user signups with existing CSV alumni data
"""
from typing import Dict, List, Optional
import pandas as pd
from difflib import SequenceMatcher


class AlumniMatcher:
    """Service to match new users with existing CSV alumni records"""

    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize name for comparison (lowercase, remove extra spaces)"""
        return ' '.join(name.lower().strip().split())

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email for comparison"""
        return email.lower().strip()

    @staticmethod
    def name_similarity(name1: str, name2: str) -> float:
        """Calculate similarity between two names (0-1)"""
        norm1 = AlumniMatcher.normalize_name(name1)
        norm2 = AlumniMatcher.normalize_name(name2)
        return SequenceMatcher(None, norm1, norm2).ratio()

    @staticmethod
    def find_csv_match(user_data: Dict, csv_df: pd.DataFrame) -> Optional[Dict]:
        """
        Find matching CSV record for a new user.

        Returns:
            - Dict with match info if found
            - None if no match

        Match priority:
            1. Exact name match (single) → return match
            2. Multiple name matches → try email match
            3. No name match → return None
        """
        user_name = user_data.get('full_name', '').strip()
        user_email = user_data.get('personal_email', '').strip().lower()

        if not user_name:
            return None

        # Normalize user name for comparison
        norm_user_name = AlumniMatcher.normalize_name(user_name)

        # Find potential name matches (similarity > 0.85)
        name_matches = []
        for idx, row in csv_df.iterrows():
            csv_name = str(row.get('Name', ''))
            similarity = AlumniMatcher.name_similarity(user_name, csv_name)

            if similarity > 0.85:  # High similarity threshold
                name_matches.append({
                    'index': idx,
                    'row': row,
                    'similarity': similarity,
                    'name': csv_name
                })

        # Case 1: Single exact/near-exact name match
        if len(name_matches) == 1:
            match = name_matches[0]
            return {
                'csv_index': int(match['index']),
                'match_type': 'single_name_match',
                'confidence': match['similarity'],
                'csv_data': match['row'].to_dict()
            }

        # Case 2: Multiple name matches - try email disambiguation
        if len(name_matches) > 1:
            if user_email:
                for match in name_matches:
                    csv_email = AlumniMatcher.normalize_email(
                        str(match['row'].get('Personal Gmail', ''))
                    )

                    if csv_email and csv_email == user_email:
                        return {
                            'csv_index': int(match['index']),
                            'match_type': 'name_and_email_match',
                            'confidence': 1.0,  # High confidence with email match
                            'csv_data': match['row'].to_dict()
                        }

            # Multiple name matches but no email match - don't auto-link
            return {
                'csv_index': None,
                'match_type': 'ambiguous_multiple_matches',
                'confidence': 0.0,
                'possible_matches': [m['name'] for m in name_matches],
                'csv_data': None
            }

        # Case 3: No name match
        return None

    @staticmethod
    def should_create_new_card(match_result: Optional[Dict]) -> bool:
        """Determine if a new alumni card should be created"""
        if match_result is None:
            return True  # No match, create new card

        if match_result.get('match_type') == 'ambiguous_multiple_matches':
            return True  # Ambiguous, create new card to be safe

        return False  # Found a clear match, link to existing

    @staticmethod
    def get_csv_linking_data(match_result: Dict) -> Optional[Dict]:
        """
        Extract data to store for linking user to CSV record

        Returns:
            Dict with csv_source_id and other metadata
        """
        if not match_result or match_result.get('csv_index') is None:
            return None

        return {
            'csv_source_id': match_result['csv_index'],
            'csv_match_type': match_result['match_type'],
            'csv_match_confidence': match_result['confidence'],
            'is_csv_linked': True
        }
