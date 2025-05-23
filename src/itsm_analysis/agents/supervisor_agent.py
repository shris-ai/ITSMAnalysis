# src\itsm_analysis\agents\supervisor_agent.py
#from graphs.main_state import AgentGraphState
from agents.base_agent import BaseAgent
from agents.categorization_agent import CategorizationAgent
from agents.sla_agent import SLAPriorityAgent
#from agents.closure_agent import ClosureAgent
#from agents.kb_agent import KBAgent
import concurrent.futures

class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__("SupervisorAgent")
        self.agents = [
            CategorizationAgent(),
            SLAPriorityAgent(),
            #ClosureAgent(),
            #KBAgent()
        ]

    def run_agent(self, agent, state):
        try:
            return agent.run(state)
        except Exception as e:
            return {agent.name: {"error": str(e)}}

    def run(self, state: dict) -> dict:
        combined_output = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.run_agent, agent, state) for agent in self.agents]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                print("RESULT")
                print(result)
                print("OVERRRRR")
                combined_output.update(result)
                print("COMBINED OUTPUT")
                print(combined_output)
        
        # Convert AgentGraphState to a dictionary before unpacking
        state_dict = state.model_dump()

        # Optional: aggregate or reshape for Grafana (JSON-friendly)
        return {**state_dict, "dashboard_output": combined_output}
