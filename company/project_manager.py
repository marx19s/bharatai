"""
=================================================
BharatAI - Project Management System (ProjectManager)
=================================================
"""

import json
import uuid
import time
import logging
from typing import Dict, Any, List, Optional

from core.event_bus import event_bus
from memory.memory_manager import memory_manager

logger = logging.getLogger("bharatai.company.project")


class ProjectManager:
    """
    Manages BharatAI project structures, task lifecycle, allocations,
    and publishes project coordination events to EventBus while persisting to Company Memory.
    """

    def __init__(self):
        self.projects: Dict[str, Dict[str, Any]] = {}
        self.load_from_memory()

    def load_from_memory(self) -> None:
        """Load project states from Company Memory if they exist."""
        try:
            entries = memory_manager.company.search("project_manager_state")
            if entries:
                # Sort by timestamp descending to get the newest snapshot
                entries.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
                self.projects = entries[0].get("projects", {})
                logger.info(f"ProjectManager: Loaded {len(self.projects)} projects from Company Memory.")
        except Exception as e:
            logger.error(f"ProjectManager: Failed to load from Company Memory: {e}")
            self.projects = {}

    def persist_state(self) -> None:
        """Save the current projects state snapshot to Company Memory."""
        try:
            memory_manager.company.add({
                "type": "project_manager_state",
                "projects": self.projects,
                "timestamp": time.time()
            })
            logger.debug("ProjectManager: State persisted to Company Memory.")
        except Exception as e:
            logger.error(f"ProjectManager: Failed to persist state: {e}")

    def create_project(self, name: str, description: str, priority: str, owner: str, deadline: str, project_id: Optional[str] = None) -> str:
        """Create a new project entry and publish ProjectCreated event."""
        p_id = project_id or uuid.uuid4().hex
        project = {
            "id": p_id,
            "name": name,
            "description": description,
            "status": "Active",
            "priority": priority,
            "owner": owner,
            "deadline": deadline,
            "progress": 0.0,
            "tasks": {}
        }
        self.projects[p_id] = project
        self.persist_state()

        event_bus.publish("ProjectCreated", "project_manager", {
            "project_id": p_id,
            "name": name,
            "owner": owner
        })
        return p_id

    def delete_project(self, project_id: str) -> bool:
        """Delete a project by its ID."""
        if project_id in self.projects:
            del self.projects[project_id]
            self.persist_state()
            return True
        return False

    def archive_project(self, project_id: str) -> bool:
        """Set project status to Archived."""
        if project_id in self.projects:
            self.projects[project_id]["status"] = "Archived"
            self.persist_state()
            return True
        return False

    def create_task(self, project_id: str, title: str, description: str, priority: str, task_id: Optional[str] = None, dependencies: Optional[List[str]] = None) -> Optional[str]:
        """Create a new task under a project."""
        if project_id not in self.projects:
            return None

        t_id = task_id or uuid.uuid4().hex
        now = time.time()
        task = {
            "id": t_id,
            "title": title,
            "description": description,
            "assigned_agent": "None",
            "department": "None",
            "status": "Pending",
            "priority": priority,
            "dependencies": dependencies or [],
            "created_at": now,
            "updated_at": now
        }
        self.projects[project_id]["tasks"][t_id] = task
        self._recalculate_progress(project_id)
        self.persist_state()
        return t_id

    def assign_task(self, project_id: str, task_id: str, agent_name: str) -> bool:
        """Assign a task to an agent, automatically mapping the department."""
        if project_id not in self.projects or task_id not in self.projects[project_id]["tasks"]:
            return False

        # Simple department resolver
        name_lower = agent_name.lower()
        if name_lower in ["neo", "atlas"]:
            dept = "CEO"
        elif name_lower in ["developer", "reviewer", "bug_fixer", "performance"]:
            dept = "Engineering"
        elif name_lower in ["qa"]:
            dept = "QA"
        elif name_lower in ["orion", "research", "sage"]:
            dept = "Research"
        else:
            dept = "Operations"

        task = self.projects[project_id]["tasks"][task_id]
        task["assigned_agent"] = agent_name
        task["department"] = dept
        task["updated_at"] = time.time()
        self.persist_state()

        event_bus.publish("TaskAssigned", "project_manager", {
            "project_id": project_id,
            "task_id": task_id,
            "assigned_agent": agent_name,
            "department": dept
        })
        return True

    def start_task(self, project_id: str, task_id: str) -> bool:
        """Mark task as InProgress and publish TaskStarted event to notify OfficeManager."""
        if project_id not in self.projects or task_id not in self.projects[project_id]["tasks"]:
            return False

        task = self.projects[project_id]["tasks"][task_id]
        task["status"] = "InProgress"
        task["updated_at"] = time.time()
        
        self._recalculate_progress(project_id)
        self.persist_state()

        # Publish TaskStarted event which triggers OfficeManager updates
        event_bus.publish("TaskStarted", task["assigned_agent"], {
            "task": task["title"],
            "project": self.projects[project_id]["name"],
            "progress": self.projects[project_id]["progress"]
        })
        return True

    def complete_task(self, project_id: str, task_id: str) -> bool:
        """Mark task as Completed, update progress, and check for project completion."""
        if project_id not in self.projects or task_id not in self.projects[project_id]["tasks"]:
            return False

        task = self.projects[project_id]["tasks"][task_id]
        task["status"] = "Completed"
        task["updated_at"] = time.time()
        
        self._recalculate_progress(project_id)
        self.persist_state()

        event_bus.publish("TaskCompleted", task["assigned_agent"], {
            "task": task["title"],
            "project": self.projects[project_id]["name"]
        })

        # Check if all tasks in the project are completed
        all_tasks = self.projects[project_id]["tasks"].values()
        if all_tasks and all(t["status"] == "Completed" for t in all_tasks):
            self.projects[project_id]["status"] = "Completed"
            self.persist_state()
            event_bus.publish("ProjectCompleted", "project_manager", {
                "project_id": project_id,
                "name": self.projects[project_id]["name"]
            })

        return True

    def fail_task(self, project_id: str, task_id: str, error_msg: str) -> bool:
        """Mark task as Failed and publish TaskFailed event."""
        if project_id not in self.projects or task_id not in self.projects[project_id]["tasks"]:
            return False

        task = self.projects[project_id]["tasks"][task_id]
        task["status"] = "Failed"
        task["updated_at"] = time.time()
        
        self._recalculate_progress(project_id)
        self.persist_state()

        event_bus.publish("TaskFailed", task["assigned_agent"], {
            "task": task["title"],
            "project": self.projects[project_id]["name"],
            "error": error_msg
        })
        return True

    def _recalculate_progress(self, project_id: str) -> None:
        """Calculate project progress percentage based on task completion status."""
        project = self.projects[project_id]
        tasks = project["tasks"].values()
        if not tasks:
            project["progress"] = 0.0
            return

        completed = sum(1 for t in tasks if t["status"] == "Completed")
        project["progress"] = (completed / len(tasks)) * 100.0

    def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Return status dictionary of the given project."""
        return self.projects.get(project_id)

    def export_project_json(self, project_id: str) -> Optional[str]:
        """Return JSON string of the given project's structure."""
        project = self.projects.get(project_id)
        if project:
            return json.dumps(project, indent=4)
        return None
