"""
Describe tool - Returns statistical summary of data.
"""
from langchain_core.tools import tool
from .context import get_dataframe
from .utils import validate_and_match_columns, get_correction_message

@tool
def tool_describe(input_str: str) -> str:
    """
    Returns statistical summary (describe()) of numeric columns.
    
    If input_str is empty or not provided: Returns statistics for ALL numeric columns automatically.
    If input_str contains column names: Returns statistics only for those specific columns (comma-separated).
    
    Examples:
    - "" or empty → All numeric columns (count, mean, std, min, 25%, 50%, 75%, max)
    - "age, fare" → Only statistics for age and fare columns
    - "survived" → Only statistics for survived column
    
    Returns: CSV-formatted table with statistical summary.
    """
    df = get_dataframe()
    cols = None
    corrections = []
    
    if input_str and input_str.strip():
        requested_cols = [c.strip() for c in input_str.split(",") if c.strip()]
        # Use fuzzy matching for column names
        matched_cols, corrections, not_found = validate_and_match_columns(
            requested_cols, list(df.columns), cutoff=0.6
        )
        
        if matched_cols:
            cols = matched_cols
        else:
            cols = None  # Fall back to all columns if nothing matched
    
    stats = df[cols].describe() if cols else df.describe()
    result = stats.to_csv(index=True)
    
    # Add note about corrections if any
    if corrections:
        result += f"\n# {get_correction_message(corrections)}"
    
    return result
