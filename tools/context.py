"""
Data context management for EDA Agent.
Handles the current dataframe being analyzed.
"""
import pandas as pd

# Global dataframe that will be set per request
df = None


def set_dataframe(dataframe: pd.DataFrame):
    """Set the current dataframe for analysis."""
    global df
    df = dataframe


def get_dataframe() -> pd.DataFrame:
    """Get the current dataframe."""
    global df
    if df is None:
        raise ValueError("No dataframe loaded. Please load a dataset first.")
    return df
