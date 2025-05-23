# agents/categorization_agent.py
import json
import pandas as pd
from agents.base_agent import BaseAgent

class CategorizationAgent(BaseAgent):
    def __init__(self, mapping_path="data/category_mappings.json"):
        super().__init__("CategorizationAgent")
        self.mapping_path = mapping_path

    def run(self, state: dict) -> dict:
        df = state.features

        print(f"CategorizationAgent received DataFrame with columns: {df.columns.tolist()}")

        with open(self.mapping_path) as f:
            mappings = json.load(f)

        df["CI_Cat"] = df["CI_Cat_enc"].map({int(k): v for k, v in mappings["CI_Cat"].items()})
        df["CI_Subcat"] = df["CI_Subcat_enc"].map({int(k): v for k, v in mappings["CI_Subcat"].items()})

        df["week"] = pd.to_datetime(df["Open_Time__"]).dt.to_period("W").dt.start_time
        weekly_trend = df.groupby("week").size().reset_index(name="incident_count")
        weekly_trend["rolling_avg"] = weekly_trend["incident_count"].rolling(window=3, min_periods=1).mean()
        weekly_trend["spike"] = weekly_trend["incident_count"] > (weekly_trend["rolling_avg"] * 1.5)

        return {
            #**state.model_dump(),  # Convert state to dictionary for unpacking,
            "categorization": {
                "top_categories": df["CI_Cat"].value_counts().head(5).to_dict(),
                "top_subcategories": df["CI_Subcat"].value_counts().head(5).to_dict(),
                "weekly_trend": weekly_trend.to_dict(orient="records"),
                "spike_weeks": weekly_trend[weekly_trend["spike"]]["week"].dt.strftime("%Y-%m-%d").tolist()
            }
        }
