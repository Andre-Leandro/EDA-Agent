"""
Outliers tool - Detects outliers in numeric columns.
"""
import json
import pandas as pd
from langchain_core.tools import tool
from .context import get_dataframe


@tool
def tool_outliers(input_str: str) -> str:
    """
    Detects outliers for a numeric column.
    Input JSON:
    {
        "column": "fare",
        "method": "iqr" | "zscore"
    }
    """
    df = get_dataframe()
    params = json.loads(input_str)
    column = params.get("column")
    method = params.get("method", "iqr")

    if column not in df.columns:
        return json.dumps({"error": f"Column '{column}' not found"})

    s = df[column].dropna()

    if not pd.api.types.is_numeric_dtype(s):
        return json.dumps({"error": f"Column '{column}' is not numeric"})

    result = {
        "column": column,
        "method": method
    }

    if method == "iqr":
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (s < lower) | (s > upper)

        result["bounds"] = {
            "lower": float(lower),
            "upper": float(upper)
        }

    elif method == "zscore":
        mean = s.mean()
        std = s.std()
        z = (s - mean) / std
        mask = z.abs() > 3

        result["zscore_threshold"] = 3.0

    else:
        return json.dumps({"error": "Method must be 'iqr' or 'zscore'"})

    outliers = s[mask]

    result["outliers"] = {
        "count": int(len(outliers)),
        "percentage": round(float(len(outliers) / len(s) * 100), 2),
        "min": float(outliers.min()) if not outliers.empty else None,
        "max": float(outliers.max()) if not outliers.empty else None
    }

    return json.dumps(result)
