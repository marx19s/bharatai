# """
# =================================================
# BharatAI
# Upgraded NEO Agent (CEO Orchestrator)
# =================================================
# """

import json
import logging
from typing import Dict, Any, Optional, List

from agents.base_agent import BaseAgent
from core.registry import registry
from core.context import ExecutionContext
from core.event_bus import event_bus
from core.task_category import TaskCategory
from config.settings import DEFAULT_MODEL, FAST_MODEL, FAST_TIMEOUT, SYNTHESIS_TIMEOUT
from memory.memory_manager import memory_manager

logger = logging.getLogger("bharatai.agents.neo")


class NEOAgent(BaseAgent):
    """
    NEO Agent (CEO). Coordinating high-level orchestration, leveraging ATLAS for planning,
    and managing centralized execution contexts, event bus messages, and shared memories.
    """

    def __init__(self):
        super().__init__(
            name="neo",
            role="CEO of BharatAI. Orchestrates execution plans, event dispatch, and shared memory."
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes a high-level user goal. Decomposes it via ATLAS for PLANNING category,
        otherwise directly resolves the goal using the appropriate model category.
        """
        self.logger.info(f"NEO initiating orchestration for goal: '{task}'")

        category = None
        context_obj = ExecutionContext(task)
        if context and "category" in context:
            category = context["category"]

        # Only use ATLAS planning when planning is actually required
        if category is not None and category != TaskCategory.PLANNING:
            self.logger.info(f"NEO bypassing ATLAS planning for non-planning category: {category}")
            task_type = "fast"
            model_name = None
            if category == TaskCategory.CODING:
                task_type = "coding"
            elif category == TaskCategory.RESEARCH:
                task_type = "research"
            elif category == TaskCategory.DEBUGGING:
                task_type = "debugging"
            elif category == TaskCategory.GENERAL_CHAT:
                task_type = "fast"

            response = self._call_model(prompt=task, task=task_type, model=model_name)
            return response.content

        # Check if plan already exists in session memory cache
        cache_key = f"plan_{task.strip().lower()}"
        cached_plan_str = memory_manager.session.get(cache_key)

        # 2. Invoke ATLAS Planner Agent to generate the prioritized dependency DAG if not cached
        if cached_plan_str:
            try:
                plan = json.loads(cached_plan_str)
                if category == TaskCategory.PLANNING:
                    self.logger.info("NEO using pre-calculated plan from session cache.")
                    return cached_plan_str
            except Exception as e:
                self.logger.warning(f"Failed to load cached plan JSON: {e}")

        self.logger.info("NEO invoking ATLAS Planner Agent...")
        atlas = registry.get_agent("atlas")
        try:
            plan_str = atlas.execute(task)
            if category == TaskCategory.PLANNING or category == "planning":
                return plan_str
            plan = json.loads(plan_str)
        except Exception as e:
            self.logger.error(f"ATLAS planning failed or timed out: {e}")
            raise

        # 3. Topological Sort to satisfy task dependencies
        ordered_tasks = self._topological_sort(plan)

        # 4. Register tasks in Context
        task_indices = {}
        for t in ordered_tasks:
            idx = context_obj.add_subtask(
                subtask=t["description"],
                agent=t["assigned_agent"],
                status="pending"
            )
            task_indices[t["id"]] = idx

        # 5. Execute subtasks in topological order
        execution_outputs = []
        for t in ordered_tasks:
            task_id = t["id"]
            desc = t["description"]
            assigned_agent_name = t["assigned_agent"]
            idx = task_indices[task_id]

            self.logger.info(f"NEO dispatching task '{task_id}': '{desc}' -> '{assigned_agent_name}'")
            context_obj.update_subtask(idx, status="running")
            context_obj.active_agent = assigned_agent_name
            context_obj.log_step(f"Dispatching task {task_id} to agent '{assigned_agent_name}'")

            event_bus.publish("TaskStarted", self.name, {"task_id": task_id, "agent": assigned_agent_name, "description": desc})

            result_content = ""
            agent_executed = False

            # Check if agent is registered and active
            try:
                available_agents = registry.list_agents()
            except Exception:
                available_agents = []

            if assigned_agent_name in available_agents and assigned_agent_name != "neo":
                try:
                    agent = registry.get_agent(assigned_agent_name)
                    def on_progress(event_type, payload):
                        if event_type in ("stage_started", "classification_complete", "research_complete", "formatting_complete", "final_answer", "end"):
                            event_bus.publish(event_type, self.name, payload)
                    if agent.is_active:
                        # Pass centralized context to agent
                        result_content = agent.run_task(desc, context=context_obj.variables)
                        agent_executed = True
                except Exception as e:
                    self.logger.error(f"Error executing agent {assigned_agent_name}: {e}")

            # Fallback to direct model manager invocation if agent is unavailable
            if not agent_executed:
                self.logger.info(f"No active agent '{assigned_agent_name}' found. Falling back to ModelManager...")
                # Use fast model for task execution
                response = self._call_model(prompt=desc, task="fast", model=FAST_MODEL, timeout=FAST_TIMEOUT)
                result_content = response.content
                agent_executed = True

            # Save result in context and subtasks
            context_obj.update_subtask(idx, status="completed", result=result_content)
            context_obj.set_variable(f"result_{task_id}", result_content)
            context_obj.log_step(f"Completed task {task_id} with agent '{assigned_agent_name}'")

            event_bus.publish("TaskCompleted", self.name, {"task_id": task_id, "result": result_content})

            # Save facts to Project Memory
            if "fact" in desc.lower() or "convention" in desc.lower() or "standard" in desc.lower():
                memory_manager.project.add_fact(f"Output of {task_id}: {result_content[:150]}...")

            execution_outputs.append({
                "id": task_id,
                "description": desc,
                "agent": assigned_agent_name,
                "result": result_content
            })

        # 6. Compile Final Executive Summary
        results_summary = ""
        for out in execution_outputs:
            results_summary += f"\n--- Task {out['id']}: {out['description']} (Executed by: {out['agent']}) ---\n{out['result']}\n"

        # Sprint 3 fast path
        final_report = results_summary

        memory_manager.conversation.add_message(
            "assistant",
            final_report,
            sender="neo",
        )

        # Perform final synthesis using the default model
        synthesis_response = self._call_model(
            prompt=final_report,
            task="synthesis",
            model=DEFAULT_MODEL,
            timeout=SYNTHESIS_TIMEOUT,
        )
        final_report = synthesis_response.content

        event_bus.publish(
            "GoalCompleted",
            self.name,
            {"result": final_report},
        )

        return final_report

    def _topological_sort(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort tasks topologically to satisfy dependency constraints."""
        resolved = []
        unresolved = list(tasks)

        # Max limit to prevent infinite loops in cyclic graphs
        max_attempts = len(tasks) * 2
        attempts = 0

        while unresolved and attempts < max_attempts:
            attempts += 1
            for task in list(unresolved):
                deps = task.get("dependencies", [])
                # Check if all dependencies are resolved
                resolved_ids = [t["id"] for t in resolved]
                if all(d in resolved_ids for d in deps):
                    resolved.append(task)
                    unresolved.remove(task)
                    break

        # Append remaining unresolved tasks as fallback
        if unresolved:
            self.logger.warning("Cycle or unresolved dependency detected in plan. Defaulting to priority sorting.")
            resolved.extend(unresolved)
            resolved.sort(key=lambda t: t.get("priority", 1))

        return resolved
