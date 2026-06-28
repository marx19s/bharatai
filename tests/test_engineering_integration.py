"""
=================================================
BharatAI - Engineering Department Integration Tests
=================================================
"""

import time
from types import SimpleNamespace
import pytest

from core.registry import registry
from agents.engineering_dept import EngineeringDepartmentOrchestrator
from memory.memory_manager import memory_manager


def test_engineering_integration_workflow_qa_pass(monkeypatch):
    """Verify integration workflow when QA tests pass successfully."""
    # Ensure all agents are loaded
    dev = registry.get_agent("developer")
    rev = registry.get_agent("reviewer")
    qa = registry.get_agent("qa")
    perf = registry.get_agent("performance")

    # Mock dev agent model call
    def mock_dev_call(prompt, task=None, **kwargs):
        return SimpleNamespace(content="def sum_two(a, b):\n    return a + b")
    monkeypatch.setattr(dev, "_call_model", mock_dev_call)

    # Mock reviewer agent model call
    def mock_rev_call(prompt, task=None, **kwargs):
        return SimpleNamespace(content="Code review: looks perfect, no issues.")
    monkeypatch.setattr(rev, "_call_model", mock_rev_call)

    # Mock qa agent unit test run to return 0 failures (PASS)
    def mock_qa_run_tests(test_path=None):
        return {
            "total": 3,
            "passed": 3,
            "failed": 0,
            "execution_time": 0.5
        }
    monkeypatch.setattr(qa, "run_unit_tests", mock_qa_run_tests)

    # Mock performance agent model call
    def mock_perf_call(prompt, task=None, **kwargs):
        return SimpleNamespace(content="Performance report: health is Good.")
    monkeypatch.setattr(perf, "_call_model", mock_perf_call)

    orchestrator = EngineeringDepartmentOrchestrator()
    memory_manager.clear_all()

    try:
        report = orchestrator.run_workflow(
            "Write a function to sum two numbers.",
            context={
                "metrics": [{"agent": "developer", "latency": 1.2}],
                "log_path": "logs/bharatai.log"
            }
        )

        assert report["developer"] == "PASS"
        assert report["review"] == "PASS"
        assert report["qa"] == "PASS"
        assert report["bug_analysis"] == "PASS"
        assert report["performance"] == "PASS"
        assert report["overall"] == "SUCCESS"
        
    finally:
        # Cleanup subscriptions to prevent test leakage
        orchestrator.cleanup()


def test_engineering_integration_workflow_qa_fail(monkeypatch):
    """Verify integration workflow when QA tests fail and BugFixer is invoked."""
    dev = registry.get_agent("developer")
    rev = registry.get_agent("reviewer")
    qa = registry.get_agent("qa")
    bf = registry.get_agent("bug_fixer")
    perf = registry.get_agent("performance")

    # Mock dev agent model call
    monkeypatch.setattr(dev, "_call_model", lambda prompt, task=None, **kwargs: SimpleNamespace(content="def bad_code(): pass"))

    # Mock reviewer agent model call
    monkeypatch.setattr(rev, "_call_model", lambda prompt, task=None, **kwargs: SimpleNamespace(content="Code review completed."))

    # Mock qa agent unit test run to return 1 failure (FAIL)
    monkeypatch.setattr(qa, "run_unit_tests", lambda test_path=None: {
        "total": 3,
        "passed": 2,
        "failed": 1,
        "execution_time": 0.5
    })

    # Mock bug fixer agent model call
    mock_bf_response = """
PROBABLE_CAUSE: Typo in bad_code definition
RECOMMENDED_FIX: Correct return value
CONFIDENCE_SCORE: 0.90
"""
    monkeypatch.setattr(bf, "_call_model", lambda prompt, task=None, **kwargs: SimpleNamespace(content=mock_bf_response))

    # Mock performance agent model call
    monkeypatch.setattr(perf, "_call_model", lambda prompt, task=None, **kwargs: SimpleNamespace(content="Performance is OK."))

    orchestrator = EngineeringDepartmentOrchestrator()
    memory_manager.clear_all()

    try:
        report = orchestrator.run_workflow(
            "Write a function to sum two numbers.",
            context={
                "metrics": [{"agent": "developer", "latency": 1.2}],
                "log_path": "logs/bharatai.log"
            }
        )

        assert report["developer"] == "PASS"
        assert report["review"] == "PASS"
        assert report["qa"] == "FAIL"
        assert report["bug_analysis"] == "PASS"
        assert report["performance"] == "PASS"
        assert report["overall"] == "SUCCESS"
        
    finally:
        orchestrator.cleanup()
