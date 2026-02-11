"""
Correlation tool - Computes correlation matrices.
"""
import json
from langchain_core.tools import tool
from .context import get_dataframe


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

    missing = [c for c in columns if c not in df.columns]
    if missing:
        return json.dumps({"error": f"Columns not found: {missing}"})

    numeric_df = df[columns].select_dtypes(include="number")

    if numeric_df.empty:
        return json.dumps({"error": "No numeric columns available for correlation"})

    corr = numeric_df.corr(method=method)

    return json.dumps({
        "method": method,
        "columns": list(corr.columns),
        "correlation_matrix": corr.round(4).to_dict()
    })
