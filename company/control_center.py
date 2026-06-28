"""
=================================================
BharatAI - Control Center
=================================================
"""

import time
import logging
from typing import Dict, Any, Optional

from core.registry import registry
from core.event_bus import event_bus
from memory.memory_manager import memory_manager
from company.agent_scheduler import AgentScheduler

logger = logging.getLogger("bharatai.company.control_center")


class ControlCenter:
    """
    ControlCenter coordinates all mutation operations on agents and task scheduler queues.
    This encapsulates actions away from the read-only OfficeAPI.
    """

    def __init__(self, scheduler: Optional[AgentScheduler] = None):
        self.scheduler = scheduler or AgentScheduler()

    def _update_agent_status_in_memory(self, agent_name: str, status: str, current_task: Optional[str] = None) -> None:
        """Helper to modify agent status directly in the persistent company state memory."""
        try:
            # We can update the status directly in the memory state so OfficeManager and API load it
            from company.office_manager import OfficeManager
            om = OfficeManager()
            if agent_name in om.agents_state:
                om.agents_state[agent_name]["status"] = status
                if current_task is not None:
                    om.agents_state[agent_name]["current_task"] = current_task
                om.agents_state[agent_name]["last_activity"] = time.time()
                om.persist_state()
        except Exception as e:
            logger.error(f"ControlCenter: Failed to update agent status in memory: {e}")

    def pause_agent(self, agent_name: str) -> bool:
        """Pause a registered agent by deactivating it in the registry and setting status."""
        try:
            registry.deactivate_agent(agent_name)
            self._update_agent_status_in_memory(agent_name, "Paused")
            event_bus.publish("AgentPaused", "control_center", {"agent": agent_name})
            return True
        except Exception as e:
            logger.error(f"ControlCenter: Failed to pause agent '{agent_name}': {e}")
            return False

    def resume_agent(self, agent_name: str) -> bool:
        """Resume a paused agent by activating it in the registry and restoring status."""
        try:
            registry.activate_agent(agent_name)
            self._update_agent_status_in_memory(agent_name, "Idle")
            event_bus.publish("AgentResumed", "control_center", {"agent": agent_name})
            return True
        except Exception as e:
            logger.error(f"ControlCenter: Failed to resume agent '{agent_name}': {e}")
            return False

    def stop_agent(self, agent_name: str) -> bool:
        """Stop agent and clear its current task."""
        try:
            registry.deactivate_agent(agent_name)
            self._update_agent_status_in_memory(agent_name, "Stopped", current_task="None")
            event_bus.publish("AgentStopped", "control_center", {"agent": agent_name})
            return True
        except Exception as e:
            logger.error(f"ControlCenter: Failed to stop agent '{agent_name}': {e}")
            return False

    def restart_agent(self, agent_name: str) -> bool:
        """Restart agent (reactivate and set to Idle)."""
        try:
            registry.activate_agent(agent_name)
            self._update_agent_status_in_memory(agent_name, "Idle", current_task="None")
            event_bus.publish("AgentRestarted", "control_center", {"agent": agent_name})
            return True
        except Exception as e:
            logger.error(f"ControlCenter: Failed to restart agent '{agent_name}': {e}")
            return False

    def retry_task(self, job_id: str) -> bool:
        """Force retry a task in the scheduler queue."""
        try:
            if job_id in self.scheduler.queue:
                job = self.scheduler.queue[job_id]
                job["status"] = "Queued"
                job["started_at"] = 0.0
                job["completed_at"] = 0.0
                self.scheduler.persist_state()
                event_bus.publish("TaskRetried", "control_center", {"job_id": job_id})
                return True
            return False
        except Exception as e:
            logger.error(f"ControlCenter: Failed to retry task '{job_id}': {e}")
            return False

    def cancel_task(self, job_id: str) -> bool:
        """Cancel a queued/running task in the scheduler."""
        try:
            res = self.scheduler.cancel_job(job_id)
            if res:
                event_bus.publish("TaskCancelled", "control_center", {"job_id": job_id})
            return res
        except Exception as e:
            logger.error(f"ControlCenter: Failed to cancel task '{job_id}': {e}")
            return False

    def change_priority(self, job_id: str, priority: str) -> bool:
        """Modify task priority in the scheduler queue."""
        try:
            if job_id in self.scheduler.queue:
                self.scheduler.queue[job_id]["priority"] = priority
                self.scheduler.persist_state()
                event_bus.publish("TaskPriorityChanged", "control_center", {"job_id": job_id, "priority": priority})
                return True
            return False
        except Exception as e:
            logger.error(f"ControlCenter: Failed to change priority of task '{job_id}': {e}")
            return False

    def move_task(self, job_id: str, new_agent: str) -> bool:
        """Reassign task to a different agent in the scheduler queue."""
        try:
            if job_id in self.scheduler.queue:
                self.scheduler.queue[job_id]["assigned_agent"] = new_agent
                self.scheduler.persist_state()
                event_bus.publish("TaskMoved", "control_center", {"job_id": job_id, "assigned_agent": new_agent})
                return True
            return False
        except Exception as e:
            logger.error(f"ControlCenter: Failed to reassign task '{job_id}': {e}")
            return False
