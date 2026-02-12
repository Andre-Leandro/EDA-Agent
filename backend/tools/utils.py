"""
Utility functions for column name matching and validation.
"""
from difflib import get_close_matches
from typing import List, Tuple, Optional


def find_column_match(
    column_name: str, 
    available_columns: List[str], 
    cutoff: float = 0.6
) -> Optional[str]:
    """
    Find the best matching column name from available columns.
    Case-insensitive and tolerant to typos.
    
    Args:
        column_name: The column name to search for
        available_columns: List of available column names
        cutoff: Minimum similarity ratio (0-1)
        
    Returns:
        The best matching column name, or None if no good match found
    """
    if not column_name or not available_columns:
        return None
    
    # First try exact match (case-insensitive)
    for col in available_columns:
        if col.lower() == column_name.lower():
            return col
    
    # Try fuzzy matching with different strategies
    # Strategy 1: Direct fuzzy match
    matches = get_close_matches(column_name, available_columns, n=1, cutoff=cutoff)
    if matches:
        return matches[0]
    
    # Strategy 2: Case-insensitive fuzzy match
    lower_available = {col.lower(): col for col in available_columns}
    matches = get_close_matches(column_name.lower(), lower_available.keys(), n=1, cutoff=cutoff)
    if matches:
        return lower_available[matches[0]]
    
    # Strategy 3: Remove spaces and special characters
    normalized_input = ''.join(c for c in column_name.lower() if c.isalnum())
    normalized_available = {
        ''.join(c for c in col.lower() if c.isalnum()): col 
        for col in available_columns
    }
    matches = get_close_matches(normalized_input, normalized_available.keys(), n=1, cutoff=cutoff)
    if matches:
        return normalized_available[matches[0]]
    
    return None


def validate_and_match_columns(
    requested_columns: List[str], 
    available_columns: List[str],
    cutoff: float = 0.6
) -> Tuple[List[str], List[Tuple[str, str]], List[str]]:
    """
    Validate and match a list of requested columns against available columns.
    
    Args:
        requested_columns: List of column names requested by user
        available_columns: List of available column names in the dataframe
        cutoff: Minimum similarity ratio for fuzzy matching
        
    Returns:
        Tuple of (matched_columns, corrections, not_found):
            - matched_columns: List of actual column names that matched
            - corrections: List of tuples (requested, matched) for corrected names
            - not_found: List of requested columns that couldn't be matched
    """
    matched = []
    corrections = []
    not_found = []
    
    for req_col in requested_columns:
        match = find_column_match(req_col, available_columns, cutoff)
        
        if match:
            matched.append(match)
            # If the match is different from the request, record it as a correction
            if match != req_col:
                corrections.append((req_col, match))
        else:
            not_found.append(req_col)
    
    return matched, corrections, not_found


def get_correction_message(corrections: List[Tuple[str, str]]) -> str:
    """
    Generate a user-friendly message about column name corrections.
    
    Args:
        corrections: List of tuples (requested, matched)
        
    Returns:
        Human-readable correction message
    """
    if not corrections:
        return ""
    
    corrections_text = []
    for req, match in corrections:
        corrections_text.append(f"'{req}' → '{match}'")
    
    return f"Note: Corrected column names: {', '.join(corrections_text)}"
