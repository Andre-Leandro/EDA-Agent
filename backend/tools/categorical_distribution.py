"""
Categorical Distribution tool - Frequency distribution for categorical columns.
"""
import json
from langchain_core.tools import tool
from .context import get_dataframe
from .utils import find_column_match

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

    # Use fuzzy matching to find the column
    matched_column = find_column_match(column, list(df.columns), cutoff=0.6)
    
    if not matched_column:
        # Try with lower cutoff for suggestions  
        suggestion = find_column_match(column, list(df.columns), cutoff=0.4)
        error_msg = f"Column '{column}' not found."
        if suggestion:
            error_msg += f" Did you mean '{suggestion}'?"
        return json.dumps({"error": error_msg})

    s = df[matched_column].dropna()
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
        "column": matched_column,  # Use the actual matched column name
        "cardinality": int(counts.size),
        "distribution": distribution
    })
