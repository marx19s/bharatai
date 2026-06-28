"""
=================================================
BharatAI - QAAgent Unit Tests
=================================================
"""

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest

from core.registry import registry
from agents.qa_agent import QAAgent
from memory.memory_manager import memory_manager


def test_qa_agent_registered_automatically():
    """Verify that QAAgent is auto-discovered and registered."""
    agents = registry.list_agents()
    assert "qa" in agents

    qa_instance = registry.get_agent("qa")
    assert isinstance(qa_instance, QAAgent)


def test_qa_agent_run_unit_tests(monkeypatch):
    """Verify QAAgent run_unit_tests() runs command, parses outputs, and logs in memory."""
    qa = QAAgent()
    cmd_run = []

    mock_stdout = """
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
collected 7 items

tests/test_example.py .......                                            [100%]
============================== 7 passed in 6.58s ==============================
"""

    def mock_subprocess_run(cmd, capture_output=True, text=True, check=False):
        cmd_run.append(cmd)
        return SimpleNamespace(returncode=0, stdout=mock_stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    memory_manager.clear_all()

    # 1. Run all unit tests
    res = qa.run_unit_tests()
    assert res["total"] == 7
    assert res["passed"] == 7
    assert res["failed"] == 0
    assert res["execution_time"] == 6.58
    assert cmd_run[0] == ["pytest"]

    # 2. Run specific test
    res_specific = qa.run_unit_tests("tests/test_example.py")
    assert res_specific["total"] == 7
    assert cmd_run[1] == ["pytest", "tests/test_example.py"]

    # Verify memory logging
    qa_memory = memory_manager.qa.search("run_unit_tests_completed")
    assert len(qa_memory) > 0


def test_qa_agent_run_regression_tests(monkeypatch):
    """Verify QAAgent run_regression_tests() runs command, parses regression output table, and logs in memory."""
    qa = QAAgent()
    cmd_run = []

    mock_stdout = """
==========================
Sprint 3 Verification
==========================

Startup                      PASS (Completed successfully in 14.27s)
Health                       PASS (Completed successfully in 3.20s)
Timeout Handling             FAIL (Test condition failed)
--------------------------
Total execution time: 82.94s
Overall: FAIL
"""

    def mock_subprocess_run(cmd, capture_output=True, text=True, check=False):
        cmd_run.append(cmd)
        return SimpleNamespace(returncode=1, stdout=mock_stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    memory_manager.clear_all()

    res = qa.run_regression_tests()
    assert res["overall"] == "FAIL"
    assert res["total_time"] == 82.94
    assert len(res["results"]) == 3
    assert res["results"][0]["test_name"] == "Startup"
    assert res["results"][0]["status"] == "PASS"
    assert res["results"][2]["test_name"] == "Timeout Handling"
    assert res["results"][2]["status"] == "FAIL"
    assert cmd_run[0] == ["python", "tests/full_test.py"]

    # Verify memory logging
    qa_memory = memory_manager.qa.search("run_regression_tests_completed")
    assert len(qa_memory) > 0


def test_qa_agent_generate_and_save_report():
    """Verify QAAgent generate_report() and save_report() behave correctly."""
    qa = QAAgent()
    memory_manager.clear_all()

    # 1. Generate report from successful unit tests
    unit_results = {"total": 5, "passed": 5, "failed": 0, "execution_time": 1.23}
    report1 = qa.generate_report(unit_results)
    assert report1["status"] == "APPROVED"
    assert report1["passed"] == 5
    assert report1["failed"] == 0
    assert len(report1["warnings"]) == 0
    assert "passed" in report1["recommendation"].lower()

    # 2. Generate report from failing unit tests
    unit_results_failing = {"total": 5, "passed": 3, "failed": 2, "execution_time": 1.5}
    report2 = qa.generate_report(unit_results_failing)
    assert report2["status"] == "BLOCKED"
    assert report2["passed"] == 3
    assert report2["failed"] == 2
    assert len(report2["warnings"]) == 1
    assert "failing" in report2["recommendation"].lower()

    # 3. Generate report from regression results
    regression_results = {
        "results": [
            {"test_name": "Startup", "status": "PASS", "details": ""},
            {"test_name": "Health", "status": "PASS", "details": ""}
        ],
        "overall": "PASS",
        "total_time": 15.0
    }
    report3 = qa.generate_report(regression_results)
    assert report3["status"] == "APPROVED"
    assert report3["passed"] == 2
    assert report3["failed"] == 0
    assert len(report3["warnings"]) == 0

    # 4. Save report to QA Memory
    report_id = qa.save_report(report3)
    assert report_id is not None
    saved = memory_manager.qa.get(report_id)
    assert saved is not None
    assert saved["status"] == "APPROVED"
