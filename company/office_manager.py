"""
=================================================
BharatAI - Office Simulation Backend (OfficeManager)
=================================================
"""

import time
import logging
from typing import Dict, Any, List, Optional

from core.event_bus import event_bus
from core.registry import registry

logger = logging.getLogger("bharatai.company.office")


class OfficeManager:
    """
    Tracks state of the BharatAI virtual headquarters, including
    Company-wide status, Departments (CEO, Engineering, Research, QA, Operations),
    and active registered Agent workloads.
    """

    def __init__(self):
        self.start_time = time.time()
        self.company_status = "Working"
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.active_projects = []

        # Initialize department states
        self.departments = {
            "CEO": {"status": "Idle", "current_task": "None", "progress": 0, "last_update": time.time()},
            "Engineering": {"status": "Idle", "current_task": "None", "progress": 0, "last_update": time.time()},
            "Research": {"status": "Idle", "current_task": "None", "progress": 0, "last_update": time.time()},
            "QA": {"status": "Idle", "current_task": "None", "progress": 0, "last_update": time.time()},
            "Operations": {"status": "Idle", "current_task": "None", "progress": 0, "last_update": time.time()},
        }

        # Initialize agent states dict
        self.agents_state = {}
        self._initialize_agents()
        self._setup_subscriptions()
        self.load_from_memory()

    def load_from_memory(self) -> None:
        """Load state from Company Memory."""
        try:
            from memory.memory_manager import memory_manager
            entries = memory_manager.company.search("dashboard_state")
            if entries:
                entries.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
                data = entries[0].get("data", {})
                self.company_status = data.get("status", "Working")
                stats = data.get("statistics", {})
                self.completed_tasks = stats.get("completed_tasks", 0)
                self.failed_tasks = stats.get("failed_tasks", 0)
                
                for agent in data.get("agents", []):
                    name = agent.get("name")
                    if name in self.agents_state:
                        self.agents_state[name]["status"] = agent.get("status", "Idle")
                        self.agents_state[name]["current_task"] = agent.get("current_task", "None")
                        self.agents_state[name]["last_activity"] = agent.get("last_activity", time.time())
                
                for dept in data.get("departments", []):
                    name = dept.get("name")
                    if name in self.departments:
                        self.departments[name]["status"] = dept.get("status", "Idle")
                        self.departments[name]["current_task"] = dept.get("current_task", "None")
                        self.departments[name]["progress"] = dept.get("progress", 0)
                        self.departments[name]["last_update"] = dept.get("last_update", time.time())
        except Exception as e:
            logger.error(f"OfficeManager: Failed to load from Company Memory: {e}")

    def _initialize_agents(self) -> None:
        """Register all currently discovered agents with initial Idle state."""
        try:
            agent_names = registry.list_agents()
        except Exception:
            # Fallback if registry discovery fails during module load
            agent_names = ["neo", "atlas", "orion", "lumina", "echo", "developer", "reviewer", "qa", "bug_fixer", "performance"]

        for name in agent_names:
            if name not in self.agents_state:
                dept = self._get_department_for_agent(name)
                self.agents_state[name] = {
                    "name": name,
                    "department": dept,
                    "status": "Idle",
                    "current_task": "None",
                    "start_time": time.time(),
                    "last_activity": time.time(),
                    "memory_usage": 100.0  # logical default MB value
                }

    def _get_department_for_agent(self, agent_name: str) -> str:
        """Heuristically assign agents to their virtual office departments."""
        name_lower = agent_name.lower()
        if name_lower in ["neo", "atlas"]:
            return "CEO"
        elif name_lower in ["developer", "reviewer", "bug_fixer", "performance"]:
            return "Engineering"
        elif name_lower in ["qa"]:
            return "QA"
        elif name_lower in ["orion", "research", "sage"]:
            return "Research"
        else:
            return "Operations"

    def _setup_subscriptions(self) -> None:
        """Subscribe to event notifications to automatically update simulation state."""
        event_bus.subscribe("task_started", self.handle_task_started)
        event_bus.subscribe("TaskStarted", self.handle_task_started)
        
        event_bus.subscribe("task_completed", self.handle_task_completed)
        event_bus.subscribe("TaskCompleted", self.handle_task_completed)
        
        event_bus.subscribe("task_failed", self.handle_task_failed)
        event_bus.subscribe("TaskFailed", self.handle_task_failed)

        event_bus.subscribe("ExecutionStarted", self.handle_execution_event)
        event_bus.subscribe("ExecutionPaused", self.handle_execution_event)
        event_bus.subscribe("ExecutionResumed", self.handle_execution_event)
        event_bus.subscribe("ExecutionCompleted", self.handle_execution_event)
        event_bus.subscribe("ExecutionFailed", self.handle_execution_event)

    def handle_execution_event(self, event) -> None:
        """Expose live loop execution status to OfficeManager dashboard."""
        event_type = event.type
        if event_type in ["ExecutionStarted", "ExecutionResumed"]:
            self.company_status = "Running"
        elif event_type == "ExecutionPaused":
            self.company_status = "Paused"
        elif event_type == "ExecutionCompleted":
            self.company_status = "Completed"
        elif event_type == "ExecutionFailed":
            self.company_status = "Failed"
        self.persist_state()

    def persist_state(self) -> None:
        """Persist current dashboard state to Company Memory namespace."""
        from memory.memory_manager import memory_manager
        dashboard_data = self.get_dashboard_data()
        memory_manager.company.add({
            "type": "dashboard_state",
            "timestamp": time.time(),
            "data": dashboard_data
        })

    def handle_task_started(self, event) -> None:
        """Update simulation states when a TaskStarted event is captured."""
        sender = event.sender
        task = event.payload.get("task", "Executing task")
        project = event.payload.get("project", "Default Project")

        if project not in self.active_projects:
            self.active_projects.append(project)

        # Refresh agent list to capture dynamically registered custom agents
        self._initialize_agents()

        # Update Agent state
        if sender in self.agents_state:
            self.agents_state[sender]["status"] = "Working"
            self.agents_state[sender]["current_task"] = task
            self.agents_state[sender]["last_activity"] = time.time()
            self.agents_state[sender]["memory_usage"] = event.payload.get("memory_usage", 150.0)

        # Update Department state
        dept = self._get_department_for_agent(sender)
        if dept in self.departments:
            self.departments[dept]["status"] = "Busy"
            self.departments[dept]["current_task"] = task
            self.departments[dept]["progress"] = event.payload.get("progress", 10)
            self.departments[dept]["last_update"] = time.time()
        
        self.persist_state()

    def handle_task_completed(self, event) -> None:
        """Update simulation states when a TaskCompleted event is captured."""
        sender = event.sender
        self.completed_tasks += 1
        self._initialize_agents()

        # Update Agent state
        if sender in self.agents_state:
            self.agents_state[sender]["status"] = "Idle"
            self.agents_state[sender]["current_task"] = "None"
            self.agents_state[sender]["last_activity"] = time.time()
            self.agents_state[sender]["memory_usage"] = 50.0

        # Update Department state
        dept = self._get_department_for_agent(sender)
        if dept in self.departments:
            # Re-evaluate department status: if other agents in same department are working, keep Busy
            busy_agents = [name for name, state in self.agents_state.items()
                           if state["department"] == dept and state["status"] == "Working"]
            if not busy_agents:
                self.departments[dept]["status"] = "Idle"
                self.departments[dept]["current_task"] = "None"
                self.departments[dept]["progress"] = 100
            self.departments[dept]["last_update"] = time.time()
            
        self.persist_state()

    def handle_task_failed(self, event) -> None:
        """Update simulation states when a TaskFailed event is captured."""
        sender = event.sender
        self.failed_tasks += 1
        self._initialize_agents()

        # Update Agent state
        if sender in self.agents_state:
            self.agents_state[sender]["status"] = "Error"
            self.agents_state[sender]["current_task"] = "None"
            self.agents_state[sender]["last_activity"] = time.time()

        # Update Department state
        dept = self._get_department_for_agent(sender)
        if dept in self.departments:
            self.departments[dept]["status"] = "Error"
            self.departments[dept]["current_task"] = f"Error: {event.payload.get('error', 'Unknown failure')}"
            self.departments[dept]["progress"] = 0
            self.departments[dept]["last_update"] = time.time()
            
        self.persist_state()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Compile and return current snapshot of company status metrics."""
        self._initialize_agents()
        active_agents_count = sum(1 for state in self.agents_state.values() if state["status"] == "Working")
        uptime = time.time() - self.start_time

        departments_list = [
            {
                "name": name,
                "status": info["status"],
                "current_task": info["current_task"],
                "progress": info["progress"],
                "last_update": info["last_update"]
            }
            for name, info in self.departments.items()
        ]

        return {
            "company": "BharatAI",
            "status": self.company_status,
            "departments": departments_list,
            "agents": list(self.agents_state.values()),
            "statistics": {
                "completed_tasks": self.completed_tasks,
                "failed_tasks": self.failed_tasks,
                "active_agents": active_agents_count,
                "uptime": uptime
            }
        }

    def get_dashboard(self) -> Dict[str, Any]:
        """Alias for get_dashboard_data to match specific API requirements."""
        return self.get_dashboard_data()
