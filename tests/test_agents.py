"""
=================================================
BharatAI - Sprint 2 Unit Tests
=================================================
"""

import json
import pytest
from core.registry import registry
from core.event_bus import event_bus, Event
from core.context import ExecutionContext
from memory.memory_manager import memory_manager
from skills.skill_manager import skill_manager
from agents.neo import NEOAgent
from agents.atlas import ATLASAgent
from agents.orion import ORIONAgent

# -------------------------------------------------------
# SHARED MEMORY TESTS
# -------------------------------------------------------
def test_shared_memory_systems():
    """Verify Session, User, Conversation, and Project memories read/write correctly."""
    # Test Session Memory
    memory_manager.session.set("temp_key", "temp_value")
    assert memory_manager.session.get("temp_key") == "temp_value"
    memory_manager.session.delete("temp_key")
    assert memory_manager.session.get("temp_key") is None

    # Test User Memory
    memory_manager.user.set("theme", "dark")
    assert memory_manager.user.get("theme") == "dark"

    # Test Conversation Memory
    memory_manager.conversation.clear()
    memory_manager.conversation.add_message("user", "Hello BharatAI", sender="user")
    messages = memory_manager.conversation.get_messages()
    assert len(messages) == 1
    assert messages[0]["content"] == "Hello BharatAI"

    # Test Project Memory
    memory_manager.project.clear()
    memory_manager.project.add_fact("System convention: local-first")
    facts = memory_manager.project.get_facts()
    assert "System convention: local-first" in facts

    # Test Manager Health Check
    assert memory_manager.health_check() is True

# -------------------------------------------------------
# CONTEXT MANAGER TESTS
# -------------------------------------------------------
def test_execution_context():
    """Verify ExecutionContext logs steps, holds variables, and registers subtasks."""
    context = ExecutionContext("Analyze project setup")
    context.set_variable("convention", "SOLID")
    assert context.get_variable("convention") == "SOLID"

    idx = context.add_subtask("Research standard layouts", "orion")
    assert idx == 0
    subtasks = context.get_subtasks()
    assert subtasks[idx]["agent"] == "orion"
    assert subtasks[idx]["status"] == "pending"

    context.update_subtask(idx, status="completed", result="Codebase clean")
    assert context.get_subtasks()[idx]["status"] == "completed"
    assert context.get_subtasks()[idx]["result"] == "Codebase clean"

    context.log_step("Context validation completed")
    assert "Context validation completed" in context.get_logs()

# -------------------------------------------------------
# EVENT BUS TESTS
# -------------------------------------------------------
def test_event_bus():
    """Verify publishing and subscribing through the EventBus."""
    received_events = []

    def callback(event: Event):
        received_events.append(event)

    event_bus.subscribe("AgentAlert", callback)
    event_bus.publish("AgentAlert", "neo", {"message": "System active"})

    assert len(received_events) == 1
    assert received_events[0].type == "AgentAlert"
    assert received_events[0].sender == "neo"
    assert received_events[0].payload["message"] == "System active"

    # Unsubscribe check
    event_bus.unsubscribe("AgentAlert", callback)
    event_bus.publish("AgentAlert", "neo", {"message": "System check"})
    assert len(received_events) == 1  # count should remain 1

# -------------------------------------------------------
# SKILL MANAGER TESTS
# -------------------------------------------------------
def test_skill_manager_and_skills():
    """Verify dynamic loading and execution of registered skills."""
    skills = skill_manager.list_skills()
    skill_names = [s["name"] for s in skills]
    
    assert "web_search" in skill_names
    assert "git_ops" in skill_names
    assert "python_exec" in skill_names

    # Test execution
    math_res = skill_manager.execute_skill("python_exec", expression="abs(-42)")
    assert "42" in str(math_res)

    web_res = skill_manager.execute_skill("web_search", query="standard conventions")
    assert "convention" in web_res.lower()

    git_res = skill_manager.execute_skill("git_ops", action="status")
    assert "branch" in git_res.lower()

# -------------------------------------------------------
# AGENT DEPLOYMENT TESTS
# -------------------------------------------------------
def test_agent_registry_discovery():
    """Verify registry auto-discovers newly implemented agents."""
    agents = registry.list_agents()
    assert "atlas" in agents
    assert "orion" in agents
    assert "neo" in agents

    atlas = registry.get_agent("atlas")
    assert isinstance(atlas, ATLASAgent)

    orion = registry.get_agent("orion")
    assert isinstance(orion, ORIONAgent)

def test_atlas_planner():
    """Verify that ATLAS can generate prioritized DAG subtasks."""
    atlas = registry.get_agent("atlas")
    plan_str = atlas.execute("Research log rotation and create a Git summary")
    
    plan = json.loads(plan_str)
    assert len(plan) > 0
    assert "id" in plan[0]
    assert "assigned_agent" in plan[0]
    assert "dependencies" in plan[0]
