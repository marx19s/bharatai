"""
=================================================
BharatAI
Planner Agent - ATLAS
=================================================
"""

import json
import logging
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent
from config.settings import FAST_MODEL, PLANNING_TIMEOUT
from core.event_bus import event_bus
from core.registry import registry
from memory.memory_manager import memory_manager

logger = logging.getLogger("bharatai.agents.atlas")


class ATLASAgent(BaseAgent):
    """
    Planner Agent (ATLAS).

    Responsible for decomposing a goal into a JSON task plan.
    """

    def __init__(self, model_manager: Optional[Any] = None):
        super().__init__(
            name="atlas",
            role="Planning Specialist. Decomposes goals into execution plans.",
            model_manager=model_manager,
        )

    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a planning JSON.
        """

        cache_key = f"plan_{task.strip().lower()}"

        cached = memory_manager.session.get(cache_key)
        if cached:
            logger.info("Using cached planning result.")
            return cached

        logger.info(f"ATLAS planning goal: {task}")

        event_bus.publish(
            "TaskStarted",
            self.name,
            {
                "goal": task,
            },
        )

        try:
            available_agents = registry.list_agents()
        except Exception:
            available_agents = []

        agent_lines = []

        for name in available_agents:
            try:
                agent = registry.get_agent(name)
                agent_lines.append(f"- {name}: {agent.role}")
            except Exception:
                pass

        agents_text = "\n".join(agent_lines)

        planning_prompt = f"""
Create a task execution plan.

Goal:
{task}

Available Agents:
{agents_text}

Return ONLY valid JSON.

Example:

[
  {{
    "id":"task_1",
    "description":"First task",
    "priority":1,
    "dependencies":[],
    "assigned_agent":"default"
  }}
]
"""

        try:

            response = self._call_model(
                prompt=planning_prompt,
                task="planning",
                provider="ollama",
                model=FAST_MODEL,
                timeout=PLANNING_TIMEOUT,
            )

            plan_str = response.content.strip()

            try:
                parsed = json.loads(plan_str)

                if not isinstance(parsed, list):
                    raise ValueError("Plan is not a list.")

            except Exception:

                parsed = [
                    {
                        "id": "task_1",
                        "description": task,
                        "priority": 1,
                        "dependencies": [],
                        "assigned_agent": "default",
                    }
                ]

                plan_str = json.dumps(parsed)

            memory_manager.session.set(cache_key, plan_str)

            event_bus.publish(
                "TaskCompleted",
                self.name,
                {
                    "goal": task,
                    "plan": parsed,
                },
            )

            logger.info("ATLAS planning completed successfully.")

            return plan_str

        except Exception as exc:

            logger.exception("ATLAS failed.")

            fallback = [
                {
                    "id": "task_1",
                    "description": task,
                    "priority": 1,
                    "dependencies": [],
                    "assigned_agent": "default",
                }
            ]

            fallback_str = json.dumps(fallback)

            memory_manager.session.set(
                cache_key,
                fallback_str,
            )

            event_bus.publish(
                "TaskCompleted",
                self.name,
                {
                    "goal": task,
                    "plan": fallback,
                    "error": str(exc),
                },
            )

            return fallback_str