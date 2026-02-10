"""
Nulls tool - Returns missing values information.
"""
import json
from langchain_core.tools import tool
from .context import get_dataframe


@tool
def tool_nulls(input_str: str = "") -> str:
    """
    Returns columns with the number of missing values as JSON (only columns with >0 missing values).
    
    Args:
        input_str: Not used, can be empty string or any value.
        
    Returns:
        JSON with column names and their missing value counts.
        
    Example: Call with empty string: tool_nulls("")
    """
    df = get_dataframe()
    nulls = df.isna().sum()
    result = {col: int(n) for col, n in nulls.items() if n > 0}
    return json.dumps(result)
