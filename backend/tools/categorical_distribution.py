"""
Categorical Distribution tool - Frequency distribution for categorical columns.
"""
import json
from langchain_core.tools import tool
from .context import get_dataframe


@tool
def tool_categorical_distribution(input_str: str) -> str:
    """
    Returns frequency distribution for a categorical column.
    Input JSON:
    {
        "column": "sex",
        "top_k": 10
    }
    """
    df = get_dataframe()
    params = json.loads(input_str)
    column = params.get("column")
    top_k = int(params.get("top_k", 10))

    if column not in df.columns:
        return json.dumps({"error": f"Column '{column}' not found"})

    s = df[column].dropna()
    total = len(s)

    counts = s.value_counts()
    top = counts.head(top_k)
    other_count = counts.iloc[top_k:].sum()

    distribution = {
        str(k): {
            "count": int(v),
            "percentage": round(float(v / total * 100), 2)
        }
        for k, v in top.items()
    }

    if other_count > 0:
        distribution["__other__"] = {
            "count": int(other_count),
            "percentage": round(float(other_count / total * 100), 2)
        }

    return json.dumps({
        "column": column,
        "cardinality": int(counts.size),
        "distribution": distribution
    })
