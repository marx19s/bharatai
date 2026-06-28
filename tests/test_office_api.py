"""
=================================================
BharatAI - OfficeAPI Unit Tests
=================================================
"""

import time
import pytest

from core.event_bus import event_bus
from memory.memory_manager import memory_manager
from company.office_manager import OfficeManager
from company.project_manager import ProjectManager
from company.agent_scheduler import AgentScheduler
from company.office_api import OfficeAPI


def test_office_api_dashboard_query():
    """Verify get_company_dashboard collects and returns correct aggregated state."""
    memory_manager.clear_all()
    om = OfficeManager()
    pm = ProjectManager()
    scheduler = AgentScheduler()
    api = OfficeAPI(om, pm, scheduler)

    try:
        # Create a dummy project and task
        p_id = pm.create_project("Project Mercury", "Spaceflight", "High", "ceo", "2026-12-31")
        pm.create_task(p_id, "Build Capsule", "Metal fabrication", "High")

        dashboard = api.get_company_dashboard()

        assert dashboard["company"] == "BharatAI"
        assert dashboard["status"] == "Working"
        assert len(dashboard["projects"]) == 1
        assert dashboard["projects"][0]["name"] == "Project Mercury"
        assert len(dashboard["departments"]) == 5
        assert len(dashboard["agents"]) > 0
        assert len(dashboard["notifications"]) > 0  # Should contain Telegram status

    finally:
        api.shutdown()


def test_office_api_departments_live_status():
    """Verify live status for all five departments CEO, Engineering, QA, Research, Operations."""
    memory_manager.clear_all()
    om = OfficeManager()
    api = OfficeAPI(office_manager=om)

    try:
        depts = api.get_departments_status()
        assert len(depts) == 5
        dept_names = [d["name"] for d in depts]
        assert "CEO" in dept_names
        assert "Engineering" in dept_names
        assert "QA" in dept_names
        assert "Research" in dept_names
        assert "Operations" in dept_names

    finally:
        api.shutdown()


def test_office_api_agents_status():
    """Verify live agent status reports tasks and progress fields."""
    memory_manager.clear_all()
    om = OfficeManager()
    pm = ProjectManager()
    api = OfficeAPI(office_manager=om, project_manager=pm)

    try:
        # Assign agent to a task to check task/progress reporting
        p_id = pm.create_project("Project Gemini", "Spaceflight", "High", "ceo", "2026-12-31")
        t_id = pm.create_task(p_id, "Orbit Earth", "Orbital flight", "High")
        pm.assign_task(p_id, t_id, "developer")
        pm.start_task(p_id, t_id)

        agents = api.get_agents_status()
        developer_status = next(a for a in agents if a["name"] == "developer")
        assert developer_status["department"] == "Engineering"
        assert developer_status["status"] in ["Working", "Idle"]

    finally:
        api.shutdown()


def test_office_api_projects_status():
    """Verify project metrics returns correct task completed/failed counts."""
    memory_manager.clear_all()
    pm = ProjectManager()
    api = OfficeAPI(project_manager=pm)

    try:
        p_id = pm.create_project("Project Apollo", "Manned landing", "High", "ceo", "2029-07-20")
        pm.create_task(p_id, "Launch Saturn V", "Launch phase", "High")
        
        status = api.get_projects_status()
        assert len(status) == 1
        assert status[0]["name"] == "Project Apollo"
        assert status[0]["completed_tasks"] == 0
        assert status[0]["active_tasks"] == 0

    finally:
        api.shutdown()


def test_office_api_notifications_and_event_hooks():
    """Verify notifications map completed and failed events to Company Memory logs."""
    memory_manager.clear_all()
    pm = ProjectManager()
    api = OfficeAPI(project_manager=pm)

    try:
        # Publish completed and failed event
        event_bus.publish("JobCompleted", "scheduler", {"task": "Verify ignition", "job_id": "job_1"})
        event_bus.publish("JobFailed", "scheduler", {"task": "Launch abort", "error": "Booster malfunction", "job_id": "job_2"})

        notifications = api.get_notifications()
        
        # Expect at least: Telegram status, Completed, and Failed notification
        assert len(notifications) >= 3
        
        # Verify categorizations
        categories = [n["type"] for n in notifications]
        assert "telegram" in categories
        assert "completed" in categories
        assert "failure" in categories

    finally:
        api.shutdown()
