"""
=================================================
BharatAI
Echo Agent (Mock Agent for Testing)
=================================================
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

class EchoAgent(BaseAgent):
    """
    A simple Echo Agent that echoes back the task it is assigned.
    Used for testing the Agent Registry and NEO coordination.
    """

    def __init__(self):
        super().__init__(
            name="echo",
            role="Echo Agent that repeats the task input. Perfect for testing coordination workflows."
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        self.logger.info(f"EchoAgent received task: '{task}'")
        return f"[ECHOED RESPONSE] I have processed the task: '{task}' successfully."
