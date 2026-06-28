"""
=================================================
BharatAI - BugFixerAgent Unit Tests
=================================================
"""

import time
from types import SimpleNamespace
import pytest

from core.registry import registry
from agents.bug_fixer_agent import BugFixerAgent
from memory.memory_manager import memory_manager


def test_bug_fixer_registered_automatically():
    """Verify that BugFixerAgent is auto-discovered and registered."""
    agents = registry.list_agents()
    assert "bug_fixer" in agents

    bug_fixer_instance = registry.get_agent("bug_fixer")
    assert isinstance(bug_fixer_instance, BugFixerAgent)


def test_bug_fixer_analyze_error():
    """Verify BugFixerAgent analyze_error() detects error types correctly."""
    bf = BugFixerAgent()

    assert bf.analyze_error("SyntaxError: invalid syntax at line 5") == "SyntaxError"
    assert bf.analyze_error("IndentationError: unexpected indent") == "IndentationError"
    assert bf.analyze_error("ImportError: cannot import name x") == "ImportError"
    assert bf.analyze_error("ModuleNotFoundError: No module named pytest") == "ModuleNotFoundError"
    assert bf.analyze_error("TimeoutError: socket timeout occurred") == "TimeoutError"
    assert bf.analyze_error("AssertionError: assert False") == "AssertionError"
    assert bf.analyze_error("RuntimeError: dict changed size during iteration") == "RuntimeError"
    assert bf.analyze_error("SomeOtherError: message") == "UnknownError"


def test_bug_fixer_search_lessons():
    """Verify BugFixerAgent search_lessons() accesses Lessons Memory."""
    bf = BugFixerAgent()
    memory_manager.clear_all()

    # Add a mock lesson
    memory_manager.lessons.add_lesson({
        "title": "Config import error fixes",
        "solution": "Import from config.settings instead",
        "category": "import"
    })

    results = bf.search_lessons("import config error")
    assert len(results) > 0
    assert results[0]["title"] == "Config import error fixes"


def test_bug_fixer_suggest_fix(monkeypatch):
    """Verify BugFixerAgent suggest_fix() queries the model and parses cause, fix, and score."""
    bf = BugFixerAgent()
    calls = []

    mock_llm_response = """
PROBABLE_CAUSE: Misspelled import statement in app.py
RECOMMENDED_FIX: Change import config to import config.settings
CONFIDENCE_SCORE: 0.95
"""

    def mock_call_model(prompt, task=None, **kwargs):
        calls.append({"prompt": prompt, "task": task})
        return SimpleNamespace(content=mock_llm_response)

    monkeypatch.setattr(bf, "_call_model", mock_call_model)
    memory_manager.clear_all()

    res = bf.suggest_fix("ImportError: cannot import config")
    assert res["probable_cause"] == "Misspelled import statement in app.py"
    assert res["recommended_fix"] == "Change import config to import config.settings"
    assert res["confidence_score"] == 0.95
    assert len(calls) == 1
    assert calls[0]["task"] == "debugging"


def test_bug_fixer_create_bug_report(monkeypatch):
    """Verify BugFixerAgent create_bug_report() builds report and saves to Lessons Memory."""
    bf = BugFixerAgent()
    
    mock_llm_response = """
PROBABLE_CAUSE: Indentation mismatch in task_classifier.py
RECOMMENDED_FIX: Ensure all tabs are spaces
CONFIDENCE_SCORE: 0.88
"""

    def mock_call_model(prompt, task=None, **kwargs):
        return SimpleNamespace(content=mock_llm_response)

    monkeypatch.setattr(bf, "_call_model", mock_call_model)
    memory_manager.clear_all()

    error_text = "IndentationError: unexpected indent at line 42"
    report = bf.create_bug_report(error_text)

    assert report["error"] == "IndentationError"
    assert report["root_cause"] == "Indentation mismatch in task_classifier.py"
    assert report["suggested_fix"] == "Ensure all tabs are spaces"
    assert report["confidence"] == 0.88

    # Verify saved to Lessons Memory
    lessons = memory_manager.lessons.search("Bug Report - IndentationError")
    assert len(lessons) > 0
    assert lessons[0]["verified"] is True
    assert lessons[0]["report_data"]["confidence"] == 0.88
