"""
=================================================
BharatAI - Agent Scheduler (AgentScheduler)
=================================================
"""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional

from core.event_bus import event_bus
from memory.memory_manager import memory_manager

logger = logging.getLogger("bharatai.company.scheduler")


class AgentScheduler:
    """
    Manages job scheduling and work queues for BharatAI agents.
    Prioritizes tasks, respects dependencies, handles retries,
    detects stuck jobs, and persists queue state to Company Memory.
    """

    def __init__(self):
        self.queue: Dict[str, Dict[str, Any]] = {}
        self.load_from_memory()

    def load_from_memory(self) -> None:
        """Load the queue state from Company Memory."""
        try:
            entries = memory_manager.company.search("scheduler_state")
            if entries:
                # Sort by timestamp descending to get the newest snapshot
                entries.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
                self.queue = entries[0].get("queue", {})
                logger.info(f"AgentScheduler: Loaded {len(self.queue)} jobs from Company Memory.")
        except Exception as e:
            logger.error(f"AgentScheduler: Failed to load from Company Memory: {e}")
            self.queue = {}

    def persist_state(self) -> None:
        """Save the current queue state snapshot to Company Memory."""
        try:
            memory_manager.company.add({
                "type": "scheduler_state",
                "queue": self.queue,
                "timestamp": time.time()
            })
            logger.debug("AgentScheduler: State persisted to Company Memory.")
        except Exception as e:
            logger.error(f"AgentScheduler: Failed to persist state: {e}")

    def enqueue(self, project_id: str, task_id: str, assigned_agent: str, priority: str, job_id: Optional[str] = None) -> str:
        """Enqueue a new agent job."""
        j_id = job_id or uuid.uuid4().hex
        job = {
            "id": j_id,
            "project_id": project_id,
            "task_id": task_id,
            "assigned_agent": assigned_agent,
            "priority": priority,
            "status": "Queued",
            "retries": 0,
            "created_at": time.time(),
            "started_at": 0.0,
            "completed_at": 0.0
        }
        self.queue[j_id] = job
        self.persist_state()

        event_bus.publish("JobQueued", "scheduler", {
            "job_id": j_id,
            "project_id": project_id,
            "task_id": task_id,
            "assigned_agent": assigned_agent
        })
        return j_id

    def dequeue(self, job_id: str) -> bool:
        """Remove a job from the queue."""
        if job_id in self.queue:
            del self.queue[job_id]
            self.persist_state()
            return True
        return False

    def cancel_job(self, job_id: str) -> bool:
        """Mark a job status as Cancelled."""
        if job_id in self.queue:
            self.queue[job_id]["status"] = "Cancelled"
            self.persist_state()
            return True
        return False

    def assign_next_job(self, project_manager: Any) -> Optional[Dict[str, Any]]:
        """
        Select and assign the next eligible job from the queue based on priority
        and task dependency constraints. Marks it as Running and triggers ProjectManager.
        """
        queued_jobs = [j for j in self.queue.values() if j["status"] == "Queued"]
        if not queued_jobs:
            return None

        # Priority weights mapping
        priority_map = {"High": 3, "Medium": 2, "Low": 1}

        # Sort: priority weight descending, then oldest created_at first
        queued_jobs.sort(key=lambda j: (priority_map.get(j["priority"], 0), -j["created_at"]), reverse=True)

        for job in queued_jobs:
            project_id = job["project_id"]
            task_id = job["task_id"]
            
            project = project_manager.get_project_status(project_id)
            if not project:
                continue

            task = project.get("tasks", {}).get(task_id)
            if not task:
                continue

            # Verify that all dependencies are completed in ProjectManager
            dependencies_met = True
            for dep_id in task.get("dependencies", []):
                dep_task = project.get("tasks", {}).get(dep_id)
                if not dep_task or dep_task.get("status") != "Completed":
                    dependencies_met = False
                    break

            if dependencies_met:
                # Assign the job
                job["status"] = "Running"
                job["started_at"] = time.time()
                self.persist_state()

                event_bus.publish("JobStarted", "scheduler", {
                    "job_id": job["id"],
                    "project_id": project_id,
                    "task_id": task_id,
                    "assigned_agent": job["assigned_agent"]
                })

                # Trigger ProjectManager status start transition
                project_manager.start_task(project_id, task_id)
                return job

        return None

    def complete_job(self, job_id: str, project_manager: Any) -> bool:
        """Mark job as Completed and trigger ProjectManager task completion."""
        if job_id not in self.queue:
            return False
        
        job = self.queue[job_id]
        job["status"] = "Completed"
        job["completed_at"] = time.time()
        self.persist_state()

        event_bus.publish("JobCompleted", "scheduler", {
            "job_id": job_id,
            "project_id": job["project_id"],
            "task_id": job["task_id"]
        })

        project_manager.complete_task(job["project_id"], job["task_id"])
        return True

    def fail_job(self, job_id: str, error_msg: str, project_manager: Any) -> bool:
        """Mark job as Failed and trigger ProjectManager task failure."""
        if job_id not in self.queue:
            return False

        job = self.queue[job_id]
        job["status"] = "Failed"
        self.persist_state()

        event_bus.publish("JobFailed", "scheduler", {
            "job_id": job_id,
            "project_id": job["project_id"],
            "task_id": job["task_id"],
            "error": error_msg
        })

        project_manager.fail_task(job["project_id"], job["task_id"], error_msg)
        return True

    def retry_job(self, job_id: str, max_retries: int = 3) -> bool:
        """Increment retries for job; re-queues if under limit, else marks Failed."""
        if job_id not in self.queue:
            return False

        job = self.queue[job_id]
        job["retries"] += 1

        if job["retries"] < max_retries:
            job["status"] = "Queued"
            job["started_at"] = 0.0
            self.persist_state()
            
            event_bus.publish("JobQueued", "scheduler", {
                "job_id": job_id,
                "project_id": job["project_id"],
                "task_id": job["task_id"],
                "assigned_agent": job["assigned_agent"],
                "is_retry": True
            })
            return True
        else:
            job["status"] = "Failed"
            self.persist_state()
            
            event_bus.publish("JobFailed", "scheduler", {
                "job_id": job_id,
                "project_id": job["project_id"],
                "task_id": job["task_id"],
                "error": "Max retries exceeded"
            })
            return False

    def detect_stuck_jobs(self, timeout_seconds: float = 60.0) -> List[str]:
        """Detect and return job IDs currently Running exceeding specified timeout seconds."""
        stuck_ids = []
        now = time.time()
        for job_id, job in self.queue.items():
            if job["status"] == "Running":
                started = job.get("started_at", 0.0)
                if now - started > timeout_seconds:
                    stuck_ids.append(job_id)
        return stuck_ids

    def get_queue_status(self) -> List[Dict[str, Any]]:
        """Return list representing current state of all jobs in queue."""
        return list(self.queue.values())
