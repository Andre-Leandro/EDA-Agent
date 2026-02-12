"""
Correlation tool - Computes correlation matrices.
"""
import json
from langchain_core.tools import tool
from .context import get_dataframe
from .utils import validate_and_match_columns, get_correction_message

@tool
def tool_correlation(input_str: str) -> str:
    """
    Computes correlation matrix for selected numeric columns.
    Input JSON:
    {
        "columns": ["age", "fare", "sibsp"],
        "method": "pearson" | "spearman"
    }
    """
    df = get_dataframe()
    params = json.loads(input_str)
    columns = params.get("columns")
    method = params.get("method", "pearson")

    if not columns or not isinstance(columns, list):
        return json.dumps({"error": "A list of columns is required"})

    # Use fuzzy matching for column names
    matched_cols, corrections, not_found = validate_and_match_columns(
        columns, list(df.columns), cutoff=0.6
    )
    
    if not_found:
        # Try with lower cutoff for suggestions
        suggestions = []
        for nf in not_found:
            sugg, _, _ = validate_and_match_columns([nf], list(df.columns), cutoff=0.4)
            if sugg:
                suggestions.append("'{}' -> maybe '{}'".format(nf, sugg[0]))
            else:
                suggestions.append("'{}' (no match found)".format(nf))
        
        suggestions_text = ", ".join(suggestions)
        return json.dumps({
            "error": f"Some columns could not be matched: {suggestions_text}",
            "available_columns": list(df.columns)
        })
    
    columns = matched_cols  # Use the matched column names

    numeric_df = df[columns].select_dtypes(include="number")

    if numeric_df.empty:
        return json.dumps({"error": "No numeric columns available for correlation"})

    corr = numeric_df.corr(method=method)
    
    result = {
        "method": method,
        "columns": list(corr.columns),
        "correlation_matrix": corr.round(4).to_dict()
    }
    
    # Add correction message if columns were fuzzy matched
    if corrections:
        result["note"] = get_correction_message(corrections)

    return json.dumps(result)
