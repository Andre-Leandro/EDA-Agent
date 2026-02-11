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
    Detects outliers for a numeric column using statistical methods.
    
    Input format (JSON string):
    {
        "column": "column_name",  # Required: name of the numeric column to analyze
        "method": "iqr" | "zscore"  # Optional: detection method (default: "iqr")
    }
    
    Methods:
    - "iqr": Interquartile Range method (recommended, detects values beyond 1.5*IQR from Q1/Q3)
    - "zscore": Z-score method (detects values with |z-score| > 3)
    
    Examples:
    - {"column": "age"} → Uses IQR method by default
    - {"column": "fare", "method": "iqr"} → Uses IQR method explicitly
    - {"column": "age", "method": "zscore"} → Uses Z-score method
    
    Returns: JSON with outlier count, percentage, bounds, and min/max outlier values.
    """
    df = get_dataframe()
    
    try:
        params = json.loads(input_str)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON input. Expected format: {\"column\": \"column_name\", \"method\": \"iqr\"}"})
    
    column = params.get("column")
    method = params.get("method", "iqr").lower()

    if not column:
        return json.dumps({
            "error": "Column parameter is required",
            "hint": "Specify a numeric column name, e.g., {\"column\": \"age\"}"
        })

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
