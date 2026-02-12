"""
Schema tool - Returns column names and data types.
"""
import json
from langchain_core.tools import tool
from .context import get_dataframe
from .utils import validate_and_match_columns, get_correction_message

@tool
def tool_schema(input_str: str) -> str:
    """
    Returns column names and data types as JSON.
    Optional: input_str can contain a number N to return only the first N columns,
    or a comma-separated list of column names to filter specific columns.
    Examples: "3" returns first 3 columns, "age, fare" returns only those columns.
    If empty, returns all columns.
    """
    df = get_dataframe()
    schema = {col: str(dtype) for col, dtype in df.dtypes.items()}
    corrections = []
    
    if input_str and input_str.strip():
        input_str = input_str.strip()
        if input_str.isdigit():
            n = int(input_str)
            cols = list(df.columns[:n])
            schema = {col: schema[col] for col in cols}
        else:
            requested_cols = [c.strip() for c in input_str.split(",") if c.strip()]
            # Use fuzzy matching for column names
            matched_cols, corrections, not_found = validate_and_match_columns(
                requested_cols, list(df.columns), cutoff=0.6
            )
            
            if matched_cols:
                schema = {col: schema[col] for col in matched_cols}
    
    result = {"schema": schema}
    if corrections:
        result["note"] = get_correction_message(corrections)
    
    return json.dumps(result)
