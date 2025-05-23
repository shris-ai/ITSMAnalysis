# agents/sla_priority_agent.py
from agents.base_agent import BaseAgent
from typing import Dict
from graphs.main_state import AgentGraphState
import pandas as pd
from datetime import timedelta

class SLAPriorityAgent(BaseAgent):
    def __init__(self, sla_definitions=None):
        super().__init__("SLAPriorityAgent")
        if sla_definitions is None:
            self.sla_definitions = {
                (3, 3): timedelta(hours=4),  # Low Impact, Low Urgency: 4 hours
                (3, 2): timedelta(hours=2),  # Low Impact, Medium Urgency: 2 hours
                (3, 1): timedelta(hours=1),  # Low Impact, High Urgency: 1 hour
                (2, 3): timedelta(hours=2),  # Medium Impact, Low Urgency: 2 hours
                (2, 2): timedelta(hours=1),  # Medium Impact, Medium Urgency: 1 hour
                (2, 1): timedelta(minutes=30), # Medium Impact, High Urgency: 30 minutes
                (1, 3): timedelta(hours=1),  # High Impact, Low Urgency: 1 hour
                (1, 2): timedelta(minutes=30), # High Impact, Medium Urgency: 30 minutes
                (1, 1): timedelta(minutes=15), # High Impact, High Urgency: 15 minutes
            }
        else:
            self.sla_definitions = {
                (int(impact), int(urgency)): timedelta(hours=hours)
                for (impact, urgency), hours in sla_definitions.items()
            }
        self.valid_priority_values = {1, 2, 3}

    def run(self, state: AgentGraphState) -> Dict:
        df = state.features.copy()

        inconsistencies = []
        breached_count = 0
        total_applicable = 0

        for index, row in df.iterrows():
            impact = row['Impact_enc']
            urgency = row['Urgency_enc']
            priority = row['Priority_enc']
            open_time_raw = row['Open_Time__']  # Get the raw Open_Time value
            handle_time_hrs = row['Handle_Time_hrs']
            resolution_sla_breach = row['Resolution_SLA_Breach']

            # Validate Priority Value
            if priority not in self.valid_priority_values:
                print(f"Warning: Invalid Priority value ({priority}) found for Incident ID {row['Incident_ID']}. Skipping inconsistency check for this row.")
                continue  # Skip inconsistency check for invalid priority

            # Check for inconsistencies
            if (impact == 3 and urgency == 1 and priority != 1) or \
               (impact == 1 and urgency == 3 and priority != 3):
                inconsistencies.append({
                    "Incident_ID": row['Incident_ID'],
                    "Impact": impact,
                    "Urgency": urgency,
                    "Priority": priority,
                    "Description": "Potential misalignment between Impact, Urgency, and Priority."
                })

            # Track SLA breaches
            if pd.notna(open_time_raw) and pd.notna(handle_time_hrs):
                try:
                    open_time = pd.to_datetime(open_time_raw) # Explicitly convert to datetime
                    total_applicable += 1
                    if resolution_sla_breach:
                        breached_count += 1
                    elif (impact, urgency) in self.sla_definitions:
                        sla_duration = self.sla_definitions.get((impact, urgency))
                        if sla_duration:
                            resolution_time = open_time + timedelta(hours=handle_time_hrs)
                            # Assuming a 'Resolved_Time' column exists or can be inferred
                            # For simplicity, we'll use handle time as a proxy for now.
                            if timedelta(hours=handle_time_hrs) > sla_duration:
                                # This is a simplified check, a real scenario would need a 'Resolved_Time'
                                breached_count += 1
                except ValueError:
                    print(f"Warning: Could not convert Open_Time for Incident ID {row['Incident_ID']} to datetime. Skipping SLA check.")
            else:
                print(f"Warning: Skipping SLA breach check for Incident ID {row['Incident_ID']} due to missing Open_Time or Handle_Time_hrs.")

        breach_percentage = (breached_count / total_applicable) * 100 if total_applicable > 0 else 0

        return {
            #**state.model_dump(),
            "sla_priority_analysis": {
                "inconsistencies": inconsistencies,
                "sla_breach_percentage": breach_percentage,
                "total_incidents_analyzed": total_applicable,
                "total_sla_breaches": breached_count,
            }
        }

if __name__ == "__main__":
    # Example usage (requires a sample DataFrame)
    data = {
        'Incident_ID': [1, 2, 3, 4, 5, 6],
        'Impact_enc': [3, 1, 2, 3, 1, 2],
        'Urgency_enc': [1, 3, 2, 2, 1, 1],
        'Priority_enc': [2, 1, 2, 3, 5, 1],
        'Open_Time__': ['2025-05-17 00:00:00', None, '2025-05-17 01:00:00', '2025-05-17 02:00:00', '2025-05-17 03:00:00', 'invalid date'],
        'Handle_Time_hrs': [3, 0.4, None, 5, 0.2, 1],
        'Resolution_SLA_Breach': [False, True, False, True, False, False],
    }
    sample_df = pd.DataFrame(data)
    state = AgentGraphState(features=sample_df)
    agent = SLAPriorityAgent()
    result = agent.run(state)
    print(result['sla_priority_analysis'])