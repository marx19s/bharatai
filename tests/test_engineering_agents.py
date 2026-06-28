"""
=================================================
BharatAI - Engineering Agents Unit Tests
=================================================
"""

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
import pytest

from core.registry import registry
from agents.engineering_dept import DeveloperAgent, ReviewerAgent
from memory.memory_manager import memory_manager


def test_agents_registered_automatically():
    """Verify that DeveloperAgent and ReviewerAgent are auto-discovered and registered."""
    agents = registry.list_agents()
    assert "developer" in agents
    assert "reviewer" in agents

    dev_instance = registry.get_agent("developer")
    assert isinstance(dev_instance, DeveloperAgent)

    rev_instance = registry.get_agent("reviewer")
    assert isinstance(rev_instance, ReviewerAgent)


def test_developer_agent_code_generation(monkeypatch):
    """Verify DeveloperAgent generate_code() invokes model and records in memory."""
    dev = DeveloperAgent()
    calls = []

    def mock_call_model(prompt, task=None, **kwargs):
        calls.append({"prompt": prompt, "task": task})
        return SimpleNamespace(content="def hello_world():\n    print('Hello')")

    monkeypatch.setattr(dev, "_call_model", mock_call_model)

    # Clean memory first
    memory_manager.clear_all()

    result = dev.generate_code("Write a hello world function in python.")

    assert result == "def hello_world():\n    print('Hello')"
    assert len(calls) == 1
    assert "hello world" in calls[0]["prompt"]
    assert calls[0]["task"] == "coding"

    # Verify action logged to memory
    dev_memory = memory_manager.developer.search("generate_code")
    assert len(dev_memory) > 0


def test_developer_agent_file_operations():
    """Verify DeveloperAgent create_file() and update_file() work on disk and memory."""
    dev = DeveloperAgent()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test_file.py")
        content = "print('Hello Bharat')"

        # Clean memory first
        memory_manager.clear_all()

        # 1. Test Create File
        success_create = dev.create_file(file_path, content)
        assert success_create is True
        assert os.path.exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == content

        # Verify in memory
        create_memory = memory_manager.developer.search("create_file")
        assert len(create_memory) > 0
        assert any(item.get("path") == file_path for item in create_memory)

        # 2. Test Update File
        new_content = "print('Hello Operating System')"
        success_update = dev.update_file(file_path, new_content)
        assert success_update is True
        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == new_content

        # Verify in memory
        update_memory = memory_manager.developer.search("update_file")
        assert len(update_memory) > 0
        assert any(item.get("path") == file_path for item in update_memory)


def test_developer_agent_explain_changes(monkeypatch):
    """Verify DeveloperAgent explain_changes() calls model and logs in memory."""
    dev = DeveloperAgent()
    calls = []

    def mock_call_model(prompt, task=None, **kwargs):
        calls.append({"prompt": prompt, "task": task})
        return SimpleNamespace(content="Changes explain: replaced Hello with Operating System.")

    monkeypatch.setattr(dev, "_call_model", mock_call_model)
    memory_manager.clear_all()

    explanation = dev.explain_changes("test.py", "print('Hello')", "print('Operating System')")

    assert "Changes explain" in explanation
    assert len(calls) == 1
    assert "test.py" in calls[0]["prompt"]
    assert calls[0]["task"] == "fast"

    # Verify memory log
    explain_memory = memory_manager.developer.search("explain_changes")
    assert len(explain_memory) > 0


def test_reviewer_agent_review_code(monkeypatch):
    """Verify ReviewerAgent review_code() retrieves lessons, calls model, and saves to memory."""
    rev = ReviewerAgent()
    calls = []

    # Inject a lessons learned to verify it's matched/retrieved
    memory_manager.clear_all()
    memory_manager.lessons.add_lesson({
        "title": "Unclosed database cursor smell",
        "solution": "Use try/finally or context manager to close",
        "category": "database"
    })

    def mock_call_model(prompt, task=None, **kwargs):
        calls.append({"prompt": prompt, "task": task})
        return SimpleNamespace(content="Code smell detected: unclosed db cursor.")

    monkeypatch.setattr(rev, "_call_model", mock_call_model)

    code_to_review = "db = connect()\ncursor = db.cursor()\ncursor.execute('SELECT 1')"
    report = rev.review_code(code_to_review)

    assert "Code smell detected" in report
    assert len(calls) == 1
    # Verify the lesson was loaded in the prompt
    assert "Unclosed database cursor smell" in calls[0]["prompt"]
    assert calls[0]["task"] == "fast"

    # Verify review findings saved in reviewer memory
    reviewer_memory = memory_manager.reviewer.search("review_code")
    assert len(reviewer_memory) > 0


def test_reviewer_agent_review_diff(monkeypatch):
    """Verify ReviewerAgent review_diff() calls model and saves to memory."""
    rev = ReviewerAgent()
    calls = []

    def mock_call_model(prompt, task=None, **kwargs):
        calls.append({"prompt": prompt, "task": task})
        return SimpleNamespace(content="Diff review: look good.")

    monkeypatch.setattr(rev, "_call_model", mock_call_model)
    memory_manager.clear_all()

    diff = "@@ -1,3 +1,3 @@\n-print('hello')\n+print('world')"
    report = rev.review_diff(diff)

    assert "Diff review" in report
    assert len(calls) == 1
    assert calls[0]["task"] == "fast"

    # Verify memory log
    diff_memory = memory_manager.reviewer.search("review_diff")
    assert len(diff_memory) > 0


def test_reviewer_agent_suggest_improvements(monkeypatch):
    """Verify ReviewerAgent suggest_improvements() calls model and saves to memory."""
    rev = ReviewerAgent()
    calls = []

    def mock_call_model(prompt, task=None, **kwargs):
        calls.append({"prompt": prompt, "task": task})
        return SimpleNamespace(content="Suggested improvement: use list comprehension.")

    monkeypatch.setattr(rev, "_call_model", mock_call_model)
    memory_manager.clear_all()

    code = "res = []\nfor x in items:\n    res.append(x * 2)"
    suggestions = rev.suggest_improvements(code)

    assert "Suggested improvement" in suggestions
    assert len(calls) == 1
    assert calls[0]["task"] == "fast"

    # Verify memory log
    improvements_memory = memory_manager.reviewer.search("suggest_improvements")
    assert len(improvements_memory) > 0
