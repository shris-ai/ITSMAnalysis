# src/itsm_analysis/graphs/main_graph.py

import pandas as pd
from feast import FeatureStore
from langgraph.graph import StateGraph
from agents.supervisor_agent import SupervisorAgent
from agents.sla_agent import SLAPriorityAgent
from graphs.main_state import AgentGraphState  # Import the state model

def load_features_as_dataframe():
    # Initialize Feast FeatureStore (assumes feature_store.yaml is in the root directory)
    store = FeatureStore(repo_path="src/itsm_analysis/feature_repo")

    # Define entity rows for which features are to be retrieved
    # Here we assume you're loading all incident IDs from the offline data
    entity_df = pd.read_parquet(
        "src/itsm_analysis/feature_repo/data/itsm_cleaned.parquet"
        # parse_dates=['Open_Time']
    )

    # Optional: Limit rows for testing
    # entity_df = entity_df.head(100)

    print(f"Data type of Open_Time column after loading: {entity_df['Open_Time'].dtype}")
    print(f"First few values of Open_Time: {entity_df['Open_Time'].head()}")

    # Attempt to convert to datetime, coercing errors
    entity_df['Open_Time'] = pd.to_datetime(entity_df['Open_Time'], utc=True, errors="coerce")

    # Make the datetime objects timezone-aware in UTC
    # entity_df['Open_Time'] = entity_df['Open_Time'].dt.tz_localize('UTC', ambiguous='infer', nonexistent='raise')

    print(f"Data type of Open_Time column before conversion: {entity_df['Open_Time'].dtype}")

    if "event_timestamp" not in entity_df.columns:
        entity_df["event_timestamp"] = entity_df["Open_Time"]
    else:
        # If event_timestamp already exists and is datetime, convert to UTC
        if pd.api.types.is_datetime64_any_dtype(entity_df['event_timestamp']):
            entity_df["event_timestamp"] = entity_df["event_timestamp"].dt.tz_convert('UTC')
        else:
            entity_df["event_timestamp"] = pd.to_datetime(entity_df["event_timestamp"], utc=True, errors="coerce")

    print(f"Data type of Open_Time column after loading: {entity_df['Open_Time'].dtype}")
    print(f"First few values of Open_Time: {entity_df['Open_Time'].head()}")
    print(f"Data type of event_timestamp column: {entity_df['event_timestamp'].dtype}")
    print(f"First few values of event_timestamp: {entity_df['event_timestamp'].head()}")

    # Get features from the feature view
    feature_vector = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "itsm_features:Handle_Time_hrs",
            "itsm_features:CI_Name_enc",
            "itsm_features:CI_Cat_enc",
            "itsm_features:CI_Subcat_enc",
            "itsm_features:Closure_Code_enc",
            "itsm_features:Priority_enc",
            "itsm_features:Impact_enc",
            "itsm_features:Urgency_enc",
            "itsm_features:Resolution_SLA_Breach",
            "itsm_features:Has_KB",
        ]
    ).to_df()

    return feature_vector

def build_agent_graph():
    graph = StateGraph(AgentGraphState)
    supervisor = SupervisorAgent()

    graph.add_node("supervisor", supervisor.run)
    

    # In future: add more nodes for branching or routing
    graph.set_entry_point("supervisor")

    runnable = graph.compile()
    return runnable

def run_analysis(features_df: pd.DataFrame):
    # Build and compile LangGraph agent graph
    runnable = build_agent_graph()

    # Initial state to pass into the graph
    initial_state = {
        "features": features_df
    }

    # Run the graph and get output
    result = runnable.invoke(initial_state)
    print("FROM MAIN")
    print(result)
    return result

if __name__ == "__main__":
    # Load ITSM features
    df = load_features_as_dataframe()

    # Run the analysis and print the output (for direct execution)
    final_result = run_analysis(df)
    print(final_result.get("dashboard_output", final_result))  # Fallback to full result