"""
Nulls tool - Returns missing values information.
"""
import json
from langchain_core.tools import tool
from .context import get_dataframe


@tool
def tool_nulls(dummy: str) -> str:
    """Returns columns with the number of missing values as JSON (only columns with >0 missing values)."""
    df = get_dataframe()
    nulls = df.isna().sum()
    result = {col: int(n) for col, n in nulls.items() if n > 0}
    return json.dumps(result)
