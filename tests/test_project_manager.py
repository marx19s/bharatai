"""
=================================================
BharatAI - ProjectManager Unit Tests
=================================================
"""

import json
import time
import pytest

from core.event_bus import event_bus
from company.office_manager import OfficeManager
from company.project_manager import ProjectManager
from memory.memory_manager import memory_manager


def test_project_manager_project_creation_and_deletion():
    """Verify that ProjectManager creates, archives, and deletes projects correctly."""
    pm = ProjectManager()
    memory_manager.clear_all()

    # Create project
    p_id = pm.create_project(
        name="Apollo Launch",
        description="Launch Apollo spacecraft to outer space",
        priority="High",
        owner="ceo",
        deadline="2026-12-31"
    )

    assert p_id is not None
    proj = pm.get_project_status(p_id)
    assert proj["name"] == "Apollo Launch"
    assert proj["status"] == "Active"

    # Archive project
    assert pm.archive_project(p_id) is True
    assert pm.get_project_status(p_id)["status"] == "Archived"

    # Delete project
    assert pm.delete_project(p_id) is True
    assert pm.get_project_status(p_id) is None


def test_project_manager_task_lifecycle_and_progress():
    """Verify task creation, assignment, progress calculation, and completion."""
    pm = ProjectManager()
    memory_manager.clear_all()

    p_id = pm.create_project("Project Alpha", "Description", "Medium", "ceo", "2026-08-30")

    # Create 2 tasks
    t1 = pm.create_task(p_id, "Design Database", "Schema draft", "High")
    t2 = pm.create_task(p_id, "Write APIs", "Flask endpoints", "High")

    assert t1 is not None
    assert t2 is not None

    proj = pm.get_project_status(p_id)
    assert len(proj["tasks"]) == 2
    assert proj["progress"] == 0.0

    # Assign and start first task
    assert pm.assign_task(p_id, t1, "developer") is True
    assert pm.start_task(p_id, t1) is True
    assert proj["tasks"][t1]["status"] == "InProgress"
    assert proj["tasks"][t1]["department"] == "Engineering"

    # Complete first task (progress should become 50.0%)
    assert pm.complete_task(p_id, t1) is True
    assert proj["tasks"][t1]["status"] == "Completed"
    assert proj["progress"] == 50.0

    # Complete second task (progress should become 100.0% and project status should become Completed)
    assert pm.assign_task(p_id, t2, "developer") is True
    assert pm.complete_task(p_id, t2) is True
    assert proj["progress"] == 100.0
    assert proj["status"] == "Completed"


def test_project_manager_event_publishing():
    """Verify ProjectManager publishes correct event notifications to EventBus."""
    pm = ProjectManager()
    memory_manager.clear_all()

    events_published = []

    def capture_events(event):
        events_published.append(event)

    event_bus.subscribe("*", capture_events)

    try:
        p_id = pm.create_project("Project Beta", "Description", "Low", "ceo", "2026-09-01")
        t_id = pm.create_task(p_id, "Analyze metrics", "Scan files", "Low")
        pm.assign_task(p_id, t_id, "performance")
        pm.start_task(p_id, t_id)
        pm.fail_task(p_id, t_id, "Out of memory error")

        # Expect: ProjectCreated, TaskAssigned, TaskStarted, TaskFailed
        event_types = [e.type for e in events_published]
        assert "ProjectCreated" in event_types
        assert "TaskAssigned" in event_types
        assert "TaskStarted" in event_types
        assert "TaskFailed" in event_types

    finally:
        event_bus.unsubscribe("*", capture_events)


def test_project_manager_persistence():
    """Verify that ProjectManager persists state to Company Memory and retrieves it."""
    # 1. Create a project and persist
    pm1 = ProjectManager()
    memory_manager.clear_all()

    p_id = pm1.create_project("Apollo Spacecraft", "Goal", "High", "ceo", "2027-01-01")
    pm1.create_task(p_id, "Test thrusters", "Run ignition test", "High")

    # 2. Instantiate new ProjectManager to simulate reload/restart
    pm2 = ProjectManager()
    proj = pm2.get_project_status(p_id)

    assert proj is not None
    assert proj["name"] == "Apollo Spacecraft"
    assert len(proj["tasks"]) == 1


def test_office_manager_integration():
    """Verify ProjectManager task state events update OfficeManager dashboard statistics."""
    om = OfficeManager()
    pm = ProjectManager()
    memory_manager.clear_all()

    p_id = pm.create_project("Virtual Office Integrator", "Integrate systems", "High", "ceo", "2026-12-31")
    t1 = pm.create_task(p_id, "Align department models", "Mapping updates", "High")
    t2 = pm.create_task(p_id, "Setup logging levels", "Verify logger output", "High")

    # 1. Test Task Assignment and Startup updates OfficeManager Agent active count
    pm.assign_task(p_id, t1, "developer")
    pm.start_task(p_id, t1)

    dashboard = om.get_dashboard()
    assert dashboard["statistics"]["active_agents"] == 1
    assert om.departments["Engineering"]["status"] == "Busy"

    # 2. Test Task Completion updates OfficeManager Completed count
    pm.complete_task(p_id, t1)
    dashboard = om.get_dashboard()
    assert dashboard["statistics"]["completed_tasks"] == 1
    assert dashboard["statistics"]["active_agents"] == 0

    # 3. Test Task Failure updates OfficeManager Failed count
    pm.assign_task(p_id, t2, "qa")
    pm.start_task(p_id, t2)
    pm.fail_task(p_id, t2, "pytest run failure")

    dashboard = om.get_dashboard()
    assert dashboard["statistics"]["failed_tasks"] == 1
    assert om.departments["QA"]["status"] == "Error"
