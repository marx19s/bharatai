"""
=================================================
BharatAI - Office Simulation API (OfficeAPI)
=================================================
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional

from core.event_bus import event_bus
from memory.memory_manager import memory_manager
from company.office_manager import OfficeManager
from company.project_manager import ProjectManager
from company.agent_scheduler import AgentScheduler

logger = logging.getLogger("bharatai.company.api")

# Activity event types captured by the feed
_ACTIVITY_EVENTS = [
    "ProjectCreated",
    "TaskAssigned",
    "JobStarted",
    "JobCompleted",
    "JobFailed",
    "ExecutionStarted",
    "ExecutionCompleted",
    "TelegramSent",
    "Error",
    # Internal aliases
    "TaskStarted",
    "TaskCompleted",
    "TaskFailed",
    "ExecutionFailed",
    "ExecutionPaused",
    "ExecutionResumed",
]


class OfficeAPI:
    """
    Exposes a unified read-only querying interface aggregating states from
    OfficeManager, ProjectManager, AgentScheduler, and Company Memory namespaces.
    """

    def __init__(self, office_manager: Optional[OfficeManager] = None,
                 project_manager: Optional[ProjectManager] = None,
                 scheduler: Optional[AgentScheduler] = None):
        self.office_manager = office_manager or OfficeManager()
        self.project_manager = project_manager or ProjectManager()
        self.scheduler = scheduler or AgentScheduler()
        
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self) -> None:
        """Subscribe internal logging hooks to populate notification history in Company Memory."""
        event_bus.subscribe("JobCompleted", self._on_job_completed)
        event_bus.subscribe("TaskCompleted", self._on_job_completed)
        
        event_bus.subscribe("JobFailed", self._on_job_failed)
        event_bus.subscribe("TaskFailed", self._on_job_failed)
        event_bus.subscribe("ExecutionFailed", self._on_job_failed)

        # Activity feed — subscribe to all tracked event types
        for event_type in _ACTIVITY_EVENTS:
            event_bus.subscribe(event_type, self._on_activity_event)

    def _on_job_completed(self, event) -> None:
        payload = event.payload
        msg = f"Task successfully completed: {payload.get('task', 'Unknown Task')}"
        self._add_notification_to_memory(category="completed", message=msg)

    def _on_job_failed(self, event) -> None:
        payload = event.payload
        msg = f"Task failed: {payload.get('task', 'Unknown Task')} - Error: {payload.get('error', 'Unknown Error')}"
        self._add_notification_to_memory(category="failure", message=msg)

    def _on_activity_event(self, event) -> None:
        """Capture any tracked EventBus event and persist it as an activity record."""
        from ui.activity_feed import ActivityFeedStore, _infer_dept  # local import avoids circular
        _EVENT_META = ActivityFeedStore.EVENT_META
        meta = _EVENT_META.get(event.type, ("⚪", event.type, "info"))
        payload = event.payload or {}
        record = {
            "type":       "activity",
            "event_type": event.type,
            "emoji":      meta[0],
            "label":      meta[1],
            "status":     meta[2],
            "agent":      event.sender,
            "department": payload.get("department", _infer_dept(event.sender)),
            "task":       payload.get("task", payload.get("description", "—")),
            "duration":   payload.get("duration", payload.get("elapsed", None)),
            "error":      payload.get("error", None),
            "timestamp":  event.timestamp,
        }
        self._add_activity_to_memory(record)

    def _add_activity_to_memory(self, record: Dict[str, Any]) -> None:
        """Persist an activity record to Company Memory, capping at 100 entries."""
        try:
            memory_manager.company.add(record)
            # Prune: keep only the newest 100 activity records
            all_activities = [
                v for v in memory_manager.company._data.values()
                if v.get("type") == "activity"
            ]
            if len(all_activities) > 100:
                # Sort oldest first, delete excess
                all_activities.sort(key=lambda x: x.get("timestamp", 0))
                for old in all_activities[:-100]:
                    memory_manager.company.delete(old["id"])
        except Exception as e:
            logger.error(f"OfficeAPI: Failed to persist activity record: {e}")

    def _add_notification_to_memory(self, category: str, message: str) -> None:
        """Persist a notification state item to the Company Memory namespace."""
        try:
            memory_manager.company.add({
                "type": "notification",
                "category": category,
                "message": message,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.error(f"OfficeAPI: Failed to log notification to Company Memory: {e}")

    def get_company_dashboard(self) -> Dict[str, Any]:
        """Compile and return the complete aggregated HQ status snapshot."""
        om_data = self.office_manager.get_dashboard()
        
        # Pull projects from ProjectManager
        projects_list = list(self.project_manager.projects.values())

        return {
            "company": om_data["company"],
            "status": om_data["status"],
            "uptime": str(om_data["statistics"].get("uptime", 0.0)),
            "projects": projects_list,
            "departments": om_data["departments"],
            "agents": om_data["agents"],
            "notifications": self.get_notifications(limit=10),
            "activity_feed": self.get_activity_feed(limit=100),
            "engineering_insights": self.get_engineering_insights(),
            "scheduler_queue": self.scheduler.get_queue_status(),
            "agent_memory": self.get_agent_memory(),
            "timeline": self.get_timeline(limit=20)
        }

    def get_departments_status(self) -> List[Dict[str, Any]]:
        """Return the live status snapshot of all HQ departments."""
        return [
            {
                "name": name,
                "status": info["status"],
                "current_task": info["current_task"],
                "progress": info["progress"],
                "last_update": info["last_update"]
            }
            for name, info in self.office_manager.departments.items()
        ]

    def get_agents_status(self) -> List[Dict[str, Any]]:
        """Return the live workload allocation state of all agents."""
        agents = []
        for state in self.office_manager.agents_state.values():
            agents.append({
                "name": state["name"],
                "department": state["department"],
                "status": state["status"],
                "current_task": state["current_task"],
                "progress": self._get_agent_progress(state["name"]),
                "last_activity": state["last_activity"]
            })
        return agents

    def _get_agent_progress(self, agent_name: str) -> int:
        """Helper to resolve current progress for an active agent."""
        for proj in self.project_manager.projects.values():
            for task in proj.get("tasks", {}).values():
                if task.get("assigned_agent") == agent_name and task.get("status") == "InProgress":
                    return int(proj.get("progress", 0))
        return 0

    def get_projects_status(self) -> List[Dict[str, Any]]:
        """Return compilation of project metrics including active and failed tasks."""
        results = []
        for proj in self.project_manager.projects.values():
            tasks = list(proj.get("tasks", {}).values())
            completed = sum(1 for t in tasks if t["status"] == "Completed")
            failed = sum(1 for t in tasks if t["status"] == "Failed")
            active = sum(1 for t in tasks if t["status"] == "InProgress")
            results.append({
                "project_id": proj["id"],
                "name": proj["name"],
                "status": proj["status"],
                "progress": proj["progress"],
                "completed_tasks": completed,
                "failed_tasks": failed,
                "active_tasks": active
            })
        return results

    def get_activity_feed(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Return the most recent activity records from Company Memory.
        Records are produced by _on_activity_event() for each tracked EventBus event.
        """
        try:
            entries = list(memory_manager.company._data.values())
            activities = [e for e in entries if e.get("type") == "activity"]
            activities.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
            return activities[:limit]
        except Exception as e:
            logger.error(f"OfficeAPI: Error loading activity feed from memory: {e}")
            return []

    def get_notifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Query latest notification logs from Company Memory, appending Telegram status."""
        results = []
        
        # Query memory
        try:
            entries = memory_manager.company.search("notification")
            notifications = [e for e in entries if e.get("type") == "notification"]
            notifications.sort(key=lambda x: x.get("timestamp", 0.0), reverse=True)
            
            for n in notifications[:limit]:
                results.append({
                    "type": n.get("category", "info"),
                    "message": n.get("message", ""),
                    "timestamp": n.get("timestamp", 0.0)
                })
        except Exception as e:
            logger.error(f"OfficeAPI: Error loading notifications from memory: {e}")

        # Inject Telegram connection status
        tg_enabled = os.environ.get("ENABLE_TELEGRAM", "false").lower() == "true"
        results.insert(0, {
            "type": "telegram",
            "message": f"Telegram notifications status is {'Enabled' if tg_enabled else 'Disabled'}",
            "timestamp": time.time()
        })
        
        return results[:limit]

    def get_engineering_insights(self) -> Dict[str, Any]:
        """Aggregate insights dynamically from stored lessons in Company Memory."""
        try:
            entries = list(memory_manager.lessons._data.values())
        except Exception:
            entries = []

        # 1. Bugs prevented
        # Count tasks with success=True and where lessons were retrieved
        bugs_prevented = sum(
            1 for l in entries
            if l.get("category") == "developer" and l.get("success") is True and l.get("lessons_applied_count", 0) > 0
        )

        # 2. Reused fixes
        # Count times a reusable fix was recommended
        reused_fixes = sum(
            1 for l in entries
            if l.get("category") == "developer" and l.get("reused_fixes_count", 0) > 0
        )

        # 3. Lessons applied
        # Count total times lessons were looked up/recommended
        lessons_applied = sum(
            l.get("lessons_applied_count", 0) for l in entries
            if l.get("category") == "developer"
        )
        if lessons_applied == 0:
            lessons_applied = sum(
                1 for l in entries
                if l.get("category") == "developer" and l.get("has_recommendations") is True
            )

        # 4. Review quality
        # Count reviewer lessons
        rev_lessons = [l for l in entries if l.get("category") == "reviewer"]
        if not rev_lessons:
            review_quality = "100%"
        else:
            clean_reviews = 0
            for r in rev_lessons:
                smells = r.get("recurring_code_smells", [])
                arch = r.get("architecture_issues", [])
                is_clean = True
                for s in smells:
                    if s.strip().lower() not in ("", "none", "none detected.", "none detected"):
                        is_clean = False
                for a in arch:
                    if a.strip().lower() not in ("", "none", "none detected.", "none detected"):
                        is_clean = False
                if is_clean:
                    clean_reviews += 1
            review_quality = f"{int((clean_reviews / len(rev_lessons)) * 100)}%"

        # 5. Test stability
        qa_lessons = [l for l in entries if l.get("category") == "qa"]
        if not qa_lessons:
            test_stability = "100%"
        else:
            total_passed = sum(l.get("passed", 0) for l in qa_lessons)
            total_failed = sum(l.get("failed", 0) for l in qa_lessons)
            total_tests = total_passed + total_failed
            total_flaky = sum(len(l.get("flaky_tests", [])) for l in qa_lessons)
            
            if total_tests == 0:
                test_stability = "100%"
            else:
                stability = max(0, int(((total_passed - total_flaky) / total_tests) * 100))
                test_stability = f"{stability}%"

        return {
            "bugs_prevented": bugs_prevented,
            "reused_fixes": reused_fixes,
            "lessons_applied": lessons_applied,
            "review_quality": review_quality,
            "test_stability": test_stability
        }

    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Compute live execution statistics for an agent from history and memory."""
        try:
            entries = list(memory_manager.lessons._data.values())
        except Exception:
            entries = []

        category_map = {
            "developer": "developer",
            "reviewer": "reviewer",
            "qa": "qa",
            "bug_fixer": "debugging",
            "performance": "performance"
        }
        category = category_map.get(agent_name.lower())

        completed = 0
        total = 0
        total_time = 0.0
        time_count = 0

        for l in entries:
            if category and l.get("category") == category:
                total += 1
                if l.get("success") is not False:
                    completed += 1
                if "execution_timings" in l:
                    total_time += l["execution_timings"].get("average_latency", 0.0)
                    time_count += 1
                elif "execution_time" in l:
                    total_time += l.get("execution_time", 0.0)
                    time_count += 1
                elif "metrics" in l and isinstance(l["metrics"], dict) and "execution_time" in l["metrics"]:
                    total_time += l["metrics"].get("execution_time", 0.0)
                    time_count += 1

        success_rate = "100%" if total == 0 else f"{int((completed / total) * 100)}%"
        avg_time = f"{total_time / time_count:.2f}s" if time_count > 0 else "N/A"

        queue_len = sum(
            1 for job in self.scheduler.get_queue_status()
            if job.get("assigned_agent") == agent_name and job.get("status") in ("Queued", "Running")
        )

        return {
            "queue_length": queue_len,
            "tasks_completed": completed,
            "success_rate": success_rate,
            "avg_execution_time": avg_time
        }

    def get_agent_memory(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve recent lessons, bugs, reviews, and fixes from Company Memory."""
        try:
            entries = list(memory_manager.lessons._data.values())
        except Exception:
            entries = []

        recent_lessons = []
        previous_bugs = []
        recent_reviews = []
        previous_fixes = []

        for l in reversed(entries):
            category = l.get("category", "")
            if category == "developer" and len(recent_lessons) < 5:
                recent_lessons.append({
                    "title": l.get("title", f"Dev Task - {l.get('task_type', 'coding')}") or f"Dev Task - {l.get('task_type', 'coding')}",
                    "details": f"Pattern: {l.get('implementation_pattern', 'N/A')}. Success: {l.get('success')}"
                })
            elif category == "debugging" and len(previous_fixes) < 5:
                previous_fixes.append({
                    "title": l.get("title", "Bug Fix"),
                    "details": l.get("solution", "")
                })
                previous_bugs.append({
                    "title": l.get("title", "Bug Type"),
                    "details": f"Error: {l.get('error_type', 'Unknown')}. Fix: {l.get('reusable_fix', '')}"
                })
            elif category == "reviewer" and len(recent_reviews) < 5:
                comments = l.get("review_comments", [])
                comments_str = "; ".join(comments) if isinstance(comments, list) else str(comments)
                recent_reviews.append({
                    "title": l.get("title", "Code Review"),
                    "details": comments_str[:120] + "..." if len(comments_str) > 120 else comments_str
                })

        return {
            "recent_lessons": recent_lessons,
            "previous_bugs": previous_bugs,
            "recent_reviews": recent_reviews,
            "previous_fixes": previous_fixes
        }

    def get_timeline(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return the last 20 actions from the activity feed timeline."""
        return self.get_activity_feed(limit=limit)

    def shutdown(self) -> None:
        """Unsubscribe hooks cleanly from global EventBus to prevent leaks."""
        try:
            event_bus.unsubscribe("JobCompleted", self._on_job_completed)
            event_bus.unsubscribe("TaskCompleted", self._on_job_completed)
            event_bus.unsubscribe("JobFailed", self._on_job_failed)
            event_bus.unsubscribe("TaskFailed", self._on_job_failed)
            event_bus.unsubscribe("ExecutionFailed", self._on_job_failed)
            # Unsubscribe activity feed hooks
            for event_type in _ACTIVITY_EVENTS:
                event_bus.unsubscribe(event_type, self._on_activity_event)
        except Exception as e:
            logger.debug(f"OfficeAPI: EventBus unsubscribe failed: {e}")
