# src\itsm_analysis\agents\base_agent.py
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def run(self, state: dict) -> dict:
        """Process input state and return updated state"""
        pass
