"""
=================================================
BharatAI - Agent Control Center Unit Tests
=================================================
"""

import time
import pytest
from unittest.mock import MagicMock

from core.registry import registry
from memory.memory_manager import memory_manager
from company.agent_scheduler import AgentScheduler
from company.control_center import ControlCenter
from company.office_api import OfficeAPI
from company.office_manager import OfficeManager


@pytest.fixture(autouse=True)
def clean_all_states():
    """Clear memory and reset registry before every test."""
    memory_manager.clear_all()
    # Reset registry activations
    for name in registry.list_agents():
        registry.activate_agent(name)
    yield
    memory_manager.clear_all()
    for name in registry.list_agents():
        registry.activate_agent(name)


def test_control_center_pause_resume():
    """Verify ControlCenter correctly pauses and resumes agents, updating memory and registry."""
    controller = ControlCenter()
    
    # Pause agent
    success_pause = controller.pause_agent("developer")
    assert success_pause is True
    assert registry.get_agent("developer").is_active is False
    
    om = OfficeManager()
    assert om.agents_state["developer"]["status"] == "Paused"
    
    # Resume agent
    success_resume = controller.resume_agent("developer")
    assert success_resume is True
    assert registry.get_agent("developer").is_active is True
    
    om = OfficeManager()
    assert om.agents_state["developer"]["status"] == "Idle"


def test_control_center_stop_restart():
    """Verify ControlCenter correctly stops and restarts agents."""
    controller = ControlCenter()
    
    # Stop agent
    success_stop = controller.stop_agent("reviewer")
    assert success_stop is True
    assert registry.get_agent("reviewer").is_active is False
    
    om = OfficeManager()
    assert om.agents_state["reviewer"]["status"] == "Stopped"
    assert om.agents_state["reviewer"]["current_task"] == "None"
    
    # Restart agent
    success_restart = controller.restart_agent("reviewer")
    assert success_restart is True
    assert registry.get_agent("reviewer").is_active is True
    
    om = OfficeManager()
    assert om.agents_state["reviewer"]["status"] == "Idle"
    assert om.agents_state["reviewer"]["current_task"] == "None"


def test_control_center_scheduler_mutations():
    """Verify ControlCenter queue modifications change scheduler states."""
    scheduler = AgentScheduler()
    controller = ControlCenter(scheduler=scheduler)
    
    # Enqueue a dummy task
    job_id = scheduler.enqueue(
        project_id="proj_123",
        task_id="task_abc",
        assigned_agent="developer",
        priority="Medium"
    )
    
    assert scheduler.queue[job_id]["priority"] == "Medium"
    
    # 1. Change priority
    success_priority = controller.change_priority(job_id, "High")
    assert success_priority is True
    assert scheduler.queue[job_id]["priority"] == "High"
    
    # 2. Reassign task
    success_reassign = controller.move_task(job_id, "reviewer")
    assert success_reassign is True
    assert scheduler.queue[job_id]["assigned_agent"] == "reviewer"
    
    # 3. Cancel task
    success_cancel = controller.cancel_task(job_id)
    assert success_cancel is True
    assert scheduler.queue[job_id]["status"] == "Cancelled"
    
    # 4. Retry task
    success_retry = controller.retry_task(job_id)
    assert success_retry is True
    assert scheduler.queue[job_id]["status"] == "Queued"


def test_office_api_stats_and_memory():
    """Verify read-only OfficeAPI correctly aggregates agent statistics and memory."""
    api = OfficeAPI()
    
    # Prime memory with lesson results
    memory_manager.lessons.add_lesson({
        "category": "developer",
        "success": True,
        "execution_time": 4.5,
        "title": "Build UI Component"
    })
    memory_manager.lessons.add_lesson({
        "category": "developer",
        "success": False,
        "execution_time": 2.5,
        "title": "Buggy Script"
    })
    
    # Query stats via OfficeAPI
    stats = api.get_agent_stats("developer")
    
    assert stats["tasks_completed"] == 1 # 1 success
    assert stats["success_rate"] == "50%"
    assert stats["avg_execution_time"] == "3.50s" # (4.5 + 2.5) / 2 = 3.5s
    
    # Query memory via OfficeAPI
    memory = api.get_agent_memory()
    
    assert len(memory["recent_lessons"]) == 2
    assert memory["recent_lessons"][0]["title"] == "Buggy Script"
    assert memory["recent_lessons"][1]["title"] == "Build UI Component"


def test_office_api_timeline():
    """Verify OfficeAPI retrieves last 20 actions timeline correctly."""
    api = OfficeAPI()
    
    # Add dummy activity records to company memory
    for i in range(25):
        memory_manager.company.add({
            "type": "activity",
            "event_type": "JobCompleted",
            "emoji": "✅",
            "label": "Job Completed",
            "agent": "developer",
            "task": f"Task {i}",
            "timestamp": float(i)
        })
        
    timeline = api.get_timeline(limit=20)
    
    assert len(timeline) == 20
    # Should be sorted newest first (timestamp 24 first)
    assert timeline[0]["task"] == "Task 24"
    assert timeline[19]["task"] == "Task 5"
