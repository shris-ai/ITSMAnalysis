# tools/tools.py

import pandas as pd
from typing import Dict, Any
from langchain.tools import tool

@tool
def decode_categories(data: Dict[str, Any], mappings: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """Decode category and subcategory encoded integers to labels using a mapping."""
    df = pd.DataFrame(data)
    df["CI_Cat"] = df["CI_Cat_enc"].map({int(k): v for k, v in mappings["CI_Cat"].items()})
    df["CI_Subcat"] = df["CI_Subcat_enc"].map({int(k): v for k, v in mappings["CI_Subcat"].items()})
    return df.to_dict(orient="list")

@tool
def compute_weekly_trend(data: Dict[str, Any], date_column: str = "Open_Time__") -> Dict[str, Any]:
    """Compute weekly incident trends and flag spike weeks based on 1.5x rolling average."""
    df = pd.DataFrame(data)
    df["week"] = pd.to_datetime(df[date_column]).dt.to_period("W").dt.start_time
    weekly = df.groupby("week").size().reset_index(name="incident_count")
    weekly["rolling_avg"] = weekly["incident_count"].rolling(window=3, min_periods=1).mean()
    weekly["spike"] = weekly["incident_count"] > (weekly["rolling_avg"] * 1.5)
    return weekly.to_dict(orient="records")

@tool
def get_top_n(data: Dict[str, Any], column: str, n: int = 5) -> Dict[str, int]:
    """Return the top N most frequent values in the specified column."""
    df = pd.DataFrame(data)
    top_values = df[column].value_counts().head(n).to_dict()
    return top_values

@tool
def explain_spike_weeks(spike_weeks: list) -> str:
    """Provide a natural language explanation of spike weeks."""
    if not spike_weeks:
        return "No spikes were detected in incident volume."
    return f"Spikes were detected during the following weeks: {', '.join(spike_weeks)}."
