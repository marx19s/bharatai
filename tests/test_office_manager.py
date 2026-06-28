"""
=================================================
BharatAI - OfficeManager Unit Tests
=================================================
"""

import time
import pytest

from core.event_bus import event_bus
from company.office_manager import OfficeManager


def test_office_manager_initialization():
    """Verify that OfficeManager starts with clean Idle states."""
    om = OfficeManager()
    data = om.get_dashboard_data()

    assert data["company"] == "BharatAI"
    assert data["status"] == "Working"
    assert len(data["departments"]) == 5
    assert len(data["agents"]) > 0

    # Ensure statistics are zeroed
    assert data["statistics"]["completed_tasks"] == 0
    assert data["statistics"]["failed_tasks"] == 0
    assert data["statistics"]["active_agents"] == 0


def test_office_manager_task_started_event():
    """Verify department and agent updates on a task_started event."""
    om = OfficeManager()

    # Publish start event from developer (Engineering)
    event_bus.publish("task_started", "developer", {
        "task": "Implement UI components",
        "project": "HQ Dashboard",
        "progress": 25,
        "memory_usage": 180.0
    })

    # Verify agent state
    agent_state = om.agents_state["developer"]
    assert agent_state["status"] == "Working"
    assert agent_state["current_task"] == "Implement UI components"
    assert agent_state["memory_usage"] == 180.0

    # Verify department state
    eng_dept = om.departments["Engineering"]
    assert eng_dept["status"] == "Busy"
    assert eng_dept["current_task"] == "Implement UI components"
    assert eng_dept["progress"] == 25

    # Verify dashboard statistics
    data = om.get_dashboard_data()
    assert data["statistics"]["active_agents"] == 1
    assert "HQ Dashboard" in om.active_projects


def test_office_manager_task_completed_event():
    """Verify state transitions and statistics increment on task_completed."""
    om = OfficeManager()

    # Start task
    event_bus.publish("task_started", "qa", {
        "task": "Run tests",
        "project": "HQ Dashboard",
        "progress": 50
    })

    # Complete task
    event_bus.publish("task_completed", "qa", {})

    # Verify agent is Idle again
    assert om.agents_state["qa"]["status"] == "Idle"
    assert om.agents_state["qa"]["current_task"] == "None"

    # Verify department returns to Idle (if no other agent is working)
    assert om.departments["QA"]["status"] == "Idle"

    # Verify statistics
    data = om.get_dashboard_data()
    assert data["statistics"]["completed_tasks"] == 1
    assert data["statistics"]["active_agents"] == 0


def test_office_manager_task_failed_event():
    """Verify status is set to Error and error details are reported on task_failed."""
    om = OfficeManager()

    # Start task
    event_bus.publish("task_started", "reviewer", {
        "task": "Review code",
        "project": "HQ Dashboard",
        "progress": 80
    })

    # Fail task
    event_bus.publish("task_failed", "reviewer", {
        "error": "Syntax error at line 12"
    })

    # Verify agent status
    assert om.agents_state["reviewer"]["status"] == "Error"

    # Verify department status
    assert om.departments["Engineering"]["status"] == "Error"
    assert "Syntax error" in om.departments["Engineering"]["current_task"]

    # Verify statistics
    data = om.get_dashboard_data()
    assert data["statistics"]["failed_tasks"] == 1


def test_office_manager_get_dashboard_and_memory_persistence():
    """Verify get_dashboard() and dashboard persistence in Company Memory."""
    from memory.memory_manager import memory_manager
    om = OfficeManager()
    memory_manager.clear_all()

    # Get dashboard
    data = om.get_dashboard()
    assert data["company"] == "BharatAI"

    # Trigger event
    event_bus.publish("task_started", "developer", {
        "task": "Develop new features",
        "project": "BharatAI",
        "progress": 10
    })

    # Verify state was persisted to Company Memory
    stored_states = memory_manager.company.search("dashboard_state")
    assert len(stored_states) > 0
    assert stored_states[0]["data"]["company"] == "BharatAI"

