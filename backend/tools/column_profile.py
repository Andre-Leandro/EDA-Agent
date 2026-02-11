"""
Column Profile tool - Detailed profiling of individual columns.
"""
import json
import pandas as pd
from langchain_core.tools import tool
from .context import get_dataframe


@tool
def tool_column_profile(column: str) -> str:
    """
    Returns a detailed, neutral profile of a single column.
    No interpretation or recommendations included.
    """
    df = get_dataframe()
    
    if column not in df.columns:
        return json.dumps({
            "error": f"Column '{column}' not found",
            "available_columns": list(df.columns)
        })

    s = df[column]
    total = len(s)

    profile = {
        "column": column,
        "dtype": str(s.dtype),
        "missing": {
            "count": int(s.isna().sum()),
            "percentage": round(float(s.isna().mean() * 100), 2)
        },
        "cardinality": int(s.nunique(dropna=True))
    }

    # Top values
    value_counts = s.value_counts(dropna=True).head(10)
    profile["top_values"] = {
        str(k): int(v) for k, v in value_counts.items()
    }

    # Numeric-only stats
    if pd.api.types.is_numeric_dtype(s):
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        profile["numeric_stats"] = {
            "min": float(s.min()),
            "max": float(s.max()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "std": float(s.std()),
            "skewness": float(s.skew()),
            "outliers": {
                "count": int(((s < lower) | (s > upper)).sum()),
                "lower_bound": float(lower),
                "upper_bound": float(upper)
            }
        }

    return json.dumps(profile)
