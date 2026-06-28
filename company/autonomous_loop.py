"""
=================================================
BharatAI - Autonomous Engineering Loop (AutonomousEngineeringLoop)
=================================================
"""

import time
import logging
from typing import Dict, Any, List, Optional

from core.event_bus import event_bus
from memory.memory_manager import memory_manager
from company.project_manager import ProjectManager
from company.agent_scheduler import AgentScheduler

# Import existing agents
from agents.engineering_dept import DeveloperAgent, ReviewerAgent
from agents.qa_agent import QAAgent
from agents.bug_fixer_agent import BugFixerAgent
from agents.performance_agent import PerformanceAgent

logger = logging.getLogger("bharatai.company.autonomous_loop")


class AutonomousEngineeringLoop:
    """
    Coordinates and drives the autonomous software engineering loop of BharatAI.
    Fetches tasks from the AgentScheduler, coordinates agent execution pipeline,
    manages pause/resume states, and handles fail/retry/performance flows.
    """

    def __init__(self, project_manager: ProjectManager, scheduler: AgentScheduler):
        self.project_manager = project_manager
        self.scheduler = scheduler
        self.active_project_id: Optional[str] = None
        self.status = "Stopped"  # Running, Paused, Stopped, Completed, Failed
        self.max_retries = 3

        # Instantiated agents
        self.developer = DeveloperAgent()
        self.reviewer = ReviewerAgent()
        self.qa = QAAgent()
        self.bug_fixer = BugFixerAgent()
        self.performance = PerformanceAgent()

        self.load_from_memory()

    def load_from_memory(self) -> None:
        """Restore active execution loop state from Company Memory."""
        try:
            entries = memory_manager.company.search("autonomous_loop_state")
            if entries:
                entries.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
                state = entries[0]
                self.active_project_id = state.get("active_project_id")
                self.status = state.get("status", "Stopped")
                logger.info(f"AutonomousLoop: Restored state: status={self.status}, project={self.active_project_id}")
        except Exception as e:
            logger.error(f"AutonomousLoop: Failed to restore state: {e}")
            self.status = "Stopped"

    def persist_state(self) -> None:
        """Save the current loop execution state to Company Memory."""
        try:
            memory_manager.company.add({
                "type": "autonomous_loop_state",
                "active_project_id": self.active_project_id,
                "status": self.status,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"AutonomousLoop: Failed to persist state: {e}")

    def execute_project(self, project_id: str) -> None:
        """Initialize project execution and start executing tasks in a loop."""
        self.active_project_id = project_id
        self.status = "Running"
        self.persist_state()

        event_bus.publish("ExecutionStarted", "autonomous_loop", {
            "project_id": project_id
        })

        # Enqueue all tasks of this project that are not yet Completed or Failed
        project = self.project_manager.get_project_status(project_id)
        if not project:
            self.status = "Failed"
            self.persist_state()
            event_bus.publish("ExecutionFailed", "autonomous_loop", {
                "project_id": project_id,
                "error": "Project not found"
            })
            return

        for task_id, task in project.get("tasks", {}).items():
            # Check if this task is already in the scheduler queue
            task_in_queue = any(
                j["project_id"] == project_id and j["task_id"] == task_id
                for j in self.scheduler.get_queue_status()
            )
            if not task_in_queue and task["status"] not in ["Completed", "Failed"]:
                self.scheduler.enqueue(
                    project_id=project_id,
                    task_id=task_id,
                    assigned_agent="developer",
                    priority=task["priority"]
                )

        # Main execution step-loop
        while self.status == "Running":
            run_result = self.execute_next_task()
            if not run_result:
                # No more jobs can be run
                break

        # Check if project completed successfully
        updated_project = self.project_manager.get_project_status(project_id)
        if updated_project and updated_project["status"] == "Completed":
            self.status = "Completed"
            self.persist_state()
            event_bus.publish("ExecutionCompleted", "autonomous_loop", {
                "project_id": project_id
            })
        elif self.status == "Running":
            # Running but loop broke because no jobs were runnable (e.g. dependency deadlock or queue empty)
            self.status = "Stopped"
            self.persist_state()

    def execute_next_task(self) -> bool:
        """
        Runs exactly one pipeline cycle: Scheduler Assign -> Developer -> Reviewer -> QA -> (Perf / BugFix).
        Returns True if a task was attempted, False if no tasks are available/runnable.
        """
        if self.status != "Running":
            return False

        # Assign next job from queue
        job = self.scheduler.assign_next_job(self.project_manager)
        if not job:
            return False

        project_id = job["project_id"]
        task_id = job["task_id"]
        job_id = job["id"]

        project = self.project_manager.get_project_status(project_id)
        task = project["tasks"][task_id] if project else None
        task_title = task["title"] if task else "Generic Task"
        task_desc = task["description"] if task else ""

        try:
            # 1. DeveloperAgent Execution
            logger.info(f"AutonomousLoop: Running DeveloperAgent on task: {task_title}")
            code = self.developer.generate_code(f"Develop software for task: {task_title}. Desc: {task_desc}")

            # 2. ReviewerAgent Review
            logger.info(f"AutonomousLoop: Running ReviewerAgent on code changes")
            review = self.reviewer.review_code(code)

            # 3. QAAgent Execution
            logger.info(f"AutonomousLoop: Running QAAgent tests")
            qa_res = self.qa.run_unit_tests()

            # Check test outcome
            tests_failed = qa_res.get("failed", 0)
            tests_passed = qa_res.get("passed", 0)

            if tests_failed == 0 and tests_passed > 0:
                # PASS
                logger.info(f"AutonomousLoop: QA PASS. Running PerformanceAgent")
                perf_report = self.performance.generate_performance_report()

                # Mark Complete
                self.scheduler.complete_job(job_id, self.project_manager)
                logger.info(f"AutonomousLoop: Job {job_id} successfully Completed.")
            else:
                # FAIL
                logger.warning(f"AutonomousLoop: QA FAIL. Running BugFixerAgent")
                bug_report = self.bug_fixer.create_bug_report()

                # Retry Job
                retry_success = self.scheduler.retry_job(job_id, max_retries=self.max_retries)
                if not retry_success:
                    logger.error(f"AutonomousLoop: Job {job_id} failed permanently (max retries reached).")
                    self.status = "Failed"
                    self.persist_state()
                    event_bus.publish("ExecutionFailed", "autonomous_loop", {
                        "project_id": project_id,
                        "error": f"Task failed: {task_title}"
                    })

        except Exception as e:
            logger.error(f"AutonomousLoop: Exception during execution cycle: {e}")
            self.scheduler.fail_job(job_id, str(e), self.project_manager)
            self.status = "Failed"
            self.persist_state()
            event_bus.publish("ExecutionFailed", "autonomous_loop", {
                "project_id": project_id,
                "error": str(e)
            })

        return True

    def pause_execution(self) -> None:
        """Pause active project execution loop."""
        if self.status == "Running":
            self.status = "Paused"
            self.persist_state()
            event_bus.publish("ExecutionPaused", "autonomous_loop", {
                "project_id": self.active_project_id
            })

    def resume_execution(self) -> None:
        """Resume paused project execution loop."""
        if self.status == "Paused":
            self.status = "Running"
            self.persist_state()
            event_bus.publish("ExecutionResumed", "autonomous_loop", {
                "project_id": self.active_project_id
            })
            # Restart loop execution
            if self.active_project_id:
                self.execute_project(self.active_project_id)

    def stop_execution(self) -> None:
        """Stop project execution loop."""
        self.status = "Stopped"
        self.persist_state()

    def execution_status(self) -> Dict[str, Any]:
        """Return the current loop state metadata."""
        return {
            "status": self.status,
            "active_project_id": self.active_project_id,
            "max_retries": self.max_retries
        }
