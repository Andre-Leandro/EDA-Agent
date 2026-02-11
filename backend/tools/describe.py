"""
Describe tool - Returns statistical summary of data.
"""
from langchain_core.tools import tool
from .context import get_dataframe


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
    if input_str and input_str.strip():
        cols = [c.strip() for c in input_str.split(",") if c.strip() in df.columns]
    stats = df[cols].describe() if cols else df.describe()
    return stats.to_csv(index=True)
