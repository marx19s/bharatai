import logging
import os
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent

_logger = logging.getLogger(__name__)

class LUMINAAgent(BaseAgent):
    """Response Formatter Agent (LUMINA).

    Converts internal execution results (WorkflowResult or raw payload) into a concise,
    user‑friendly natural language response. When developer mode is enabled, it also
    appends execution details such as agent logs, timings and model usage.
    """

    def __init__(self):
        super().__init__(
            name="lumina",
            role="Response Formatter. Produces concise user‑facing output."
        )

    def format(self, workflow_result: Any, developer_mode: bool = False) -> str:
        """Format the given workflow result.

        Parameters
        ----------
        workflow_result: Any
            Expected to be an instance of ``core.workflow_engine.WorkflowResult`` or a
            dictionary payload containing the agents' raw results.
        developer_mode: bool, optional
            If True, include detailed execution metadata.
        """
        # Attempt to extract a final summary if present (e.g., from NEO's executive summary)
        try:
            payload = workflow_result.payload if hasattr(workflow_result, "payload") else workflow_result
            agents = payload.get("agents", [])
            # Look for an agent named 'NEO' with a result containing a summary
            for a in agents:
                if a.get("agent") == "NEOAgent" and isinstance(a.get("result"), str):
                    summary = a["result"]
                    break
            else:
                # Fallback: concatenate all agent results
                parts = []
                for a in agents:
                    res = a.get("result")
                    if isinstance(res, str):
                        parts.append(res)
                summary = "\n\n".join(parts) if parts else "No result produced."
        except Exception as e:
            _logger.error(f"LUMINA failed to format result: {e}")
            summary = "An error occurred while formatting the response."

        if developer_mode:
            # Append simple debug info
            debug_info = f"\n\n[DEBUG] Category: {payload.get('category', 'unknown')} | Agents executed: {[a.get('agent') for a in agents]}"
            summary = summary + debug_info
        return summary

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute formatting task by delegating to format()."""
        developer_mode = False
        workflow_result = None

        if isinstance(context, dict):
            developer_mode = context.get("developer_mode", False)
            workflow_result = context.get("workflow_result")

        if workflow_result is None:
            workflow_result = task

        return self.format(workflow_result, developer_mode=developer_mode)

