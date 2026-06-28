"""
=================================================
BharatAI - AutonomousEngineeringLoop Unit Tests
=================================================
"""

import time
import pytest
from unittest.mock import MagicMock

from core.event_bus import event_bus
from memory.memory_manager import memory_manager
from company.office_manager import OfficeManager
from company.project_manager import ProjectManager
from company.agent_scheduler import AgentScheduler
from company.autonomous_loop import AutonomousEngineeringLoop


def test_autonomous_loop_pipeline_pass(monkeypatch):
    """Verify the full pipeline: Developer -> Reviewer -> QA PASS -> Performance -> Complete."""
    memory_manager.clear_all()
    pm = ProjectManager()
    scheduler = AgentScheduler()
    om = OfficeManager()

    loop = AutonomousEngineeringLoop(pm, scheduler)

    # Mock agent endpoints for success path
    monkeypatch.setattr(loop.developer, "generate_code", lambda p: "def hello(): pass")
    monkeypatch.setattr(loop.reviewer, "review_code", lambda c: "Clean code")
    monkeypatch.setattr(loop.qa, "run_unit_tests", lambda: {"passed": 3, "failed": 0})
    monkeypatch.setattr(loop.performance, "generate_performance_report", lambda: {"status": "Excellent"})

    # Setup project and task
    p_id = pm.create_project("Loop Project", "Desc", "High", "ceo", "2026-12-31")
    t_id = pm.create_task(p_id, "Write code", "Implement hello", "High")

    # Enqueue
    job_id = scheduler.enqueue(p_id, t_id, "developer", "High")

    # Execute step
    loop.status = "Running"
    loop.active_project_id = p_id
    success = loop.execute_next_task()

    assert success is True
    # Verify task was completed in PM and scheduler
    assert pm.get_project_status(p_id)["progress"] == 100.0
    assert scheduler.queue[job_id]["status"] == "Completed"


def test_autonomous_loop_retry_and_failure(monkeypatch):
    """Verify retry handling: QA FAIL -> BugFixer -> Retry -> Max Retries -> ExecutionFailed."""
    memory_manager.clear_all()
    pm = ProjectManager()
    scheduler = AgentScheduler()
    om = OfficeManager()

    loop = AutonomousEngineeringLoop(pm, scheduler)
    loop.max_retries = 2

    # Mock agent endpoints for failure path
    monkeypatch.setattr(loop.developer, "generate_code", lambda p: "broken code")
    monkeypatch.setattr(loop.reviewer, "review_code", lambda c: "Issues found")
    # Always fail
    monkeypatch.setattr(loop.qa, "run_unit_tests", lambda: {"passed": 0, "failed": 1})
    monkeypatch.setattr(loop.bug_fixer, "create_bug_report", lambda: {"error": "syntax error"})

    # Setup project and task
    p_id = pm.create_project("Retry Project", "Desc", "High", "ceo", "2026-12-31")
    t_id = pm.create_task(p_id, "Fix bug", "Debug it", "High")
    job_id = scheduler.enqueue(p_id, t_id, "developer", "High")

    loop.status = "Running"
    loop.active_project_id = p_id

    # 1. First attempt fails, retries enqueued (status back to Queued)
    attempt1 = loop.execute_next_task()
    assert attempt1 is True
    assert scheduler.queue[job_id]["status"] == "Queued"
    assert scheduler.queue[job_id]["retries"] == 1
    assert loop.status == "Running"

    # 2. Second attempt fails, exceeds max_retries=2, permanent failure
    attempt2 = loop.execute_next_task()
    assert attempt2 is True
    assert scheduler.queue[job_id]["status"] == "Failed"
    assert scheduler.queue[job_id]["retries"] == 2
    assert loop.status == "Failed"


def test_autonomous_loop_pause_resume():
    """Verify pause, resume, and stop loop states."""
    memory_manager.clear_all()
    pm = ProjectManager()
    scheduler = AgentScheduler()
    loop = AutonomousEngineeringLoop(pm, scheduler)

    loop.status = "Running"
    loop.pause_execution()
    assert loop.status == "Paused"

    loop.stop_execution()
    assert loop.status == "Stopped"


def test_autonomous_loop_persistence():
    """Verify loop state saves to Company Memory and recovers."""
    memory_manager.clear_all()
    pm = ProjectManager()
    scheduler = AgentScheduler()

    loop1 = AutonomousEngineeringLoop(pm, scheduler)
    loop1.active_project_id = "test_proj_123"
    loop1.status = "Paused"
    loop1.persist_state()

    # Re-instantiate
    loop2 = AutonomousEngineeringLoop(pm, scheduler)
    assert loop2.active_project_id == "test_proj_123"
    assert loop2.status == "Paused"


def test_autonomous_loop_event_publishing(monkeypatch):
    """Verify event publishing for autonomous execution lifecycle."""
    memory_manager.clear_all()
    pm = ProjectManager()
    scheduler = AgentScheduler()
    loop = AutonomousEngineeringLoop(pm, scheduler)

    # Mock success path
    monkeypatch.setattr(loop.developer, "generate_code", lambda p: "def hello(): pass")
    monkeypatch.setattr(loop.reviewer, "review_code", lambda c: "Clean code")
    monkeypatch.setattr(loop.qa, "run_unit_tests", lambda: {"passed": 3, "failed": 0})
    monkeypatch.setattr(loop.performance, "generate_performance_report", lambda: {"status": "Excellent"})

    events = []

    def capture_events(event):
        events.append(event)

    event_bus.subscribe("*", capture_events)

    try:
        p_id = pm.create_project("Event Project", "Desc", "High", "ceo", "2026-12-31")
        t_id = pm.create_task(p_id, "Event Task", "Desc", "High")

        loop.execute_project(p_id)

        event_types = [e.type for e in events]
        assert "ExecutionStarted" in event_types
        assert "ExecutionCompleted" in event_types

    finally:
        event_bus.unsubscribe("*", capture_events)
