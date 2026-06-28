"""
=================================================
BharatAI - PerformanceAgent Unit Tests
=================================================
"""

import os
import tempfile
import pytest

from core.registry import registry
from agents.performance_agent import PerformanceAgent
from memory.memory_manager import memory_manager


def test_performance_agent_registered_automatically():
    """Verify that PerformanceAgent is auto-discovered and registered."""
    agents = registry.list_agents()
    assert "performance" in agents

    performance_instance = registry.get_agent("performance")
    assert isinstance(performance_instance, PerformanceAgent)


def test_performance_agent_analyze_logs():
    """Verify PerformanceAgent analyze_logs() parses slow logs, duplicate calls, retries, and timeouts."""
    pa = PerformanceAgent()

    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_bharatai.log")
        
        mock_log_content = """
2026-06-28 16:00:00 - INFO - request_id=123 Attempting generation: Provider=ollama, Model=qwen2.5:1.5b
2026-06-28 16:00:01 - INFO - request_id=123 Attempting generation: Provider=ollama, Model=qwen2.5:1.5b
2026-06-28 16:00:02 - INFO - TIMING {"request_id":"123","stage":"workflow","elapsed_ms":6200.0}
2026-06-28 16:00:03 - WARNING - execution attempt 2/2 retrying...
2026-06-28 16:00:04 - ERROR - Connection timeout error occurred
2026-06-28 16:00:05 - ERROR - Exception: database connection failed
"""
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(mock_log_content)

        res = pa.analyze_logs(log_file)

        assert len(res["slow_requests"]) > 0
        assert len(res["duplicate_calls"]) > 0
        assert len(res["retry_loops"]) > 0
        assert len(res["timeouts"]) > 0
        assert len(res["exceptions"]) > 0


def test_performance_agent_analyze_metrics():
    """Verify PerformanceAgent analyze_metrics() computes statistics and detects bottlenecks."""
    pa = PerformanceAgent()

    mock_metrics = [
        {"agent": "neo", "latency": 1.5},
        {"agent": "atlas", "latency": 4.2},  # Bottleneck (>3.0)
        {"agent": "orion", "latency": 0.8}
    ]

    res = pa.analyze_metrics(mock_metrics)

    assert res["total_requests"] == 3
    assert abs(res["average_latency"] - 2.16) < 0.05
    assert res["slowest_operation"] == "atlas"
    assert len(res["bottlenecks"]) == 1
    assert "atlas" in res["bottlenecks"][0]


def test_performance_agent_generate_and_save_report():
    """Verify PerformanceAgent generate_performance_report() and save_report() behave correctly."""
    pa = PerformanceAgent()
    memory_manager.clear_all()

    # 1. Critical Case (Timeouts exist)
    log_res_crit = {
        "slow_requests": [],
        "duplicate_calls": [],
        "retry_loops": [],
        "timeouts": ["Timeout signature: connection timed out"],
        "exceptions": []
    }
    metrics_res_crit = {
        "average_latency": 1.2,
        "slowest_operation": "neo",
        "total_requests": 10,
        "bottlenecks": []
    }
    report_crit = pa.generate_performance_report(log_res_crit, metrics_res_crit)
    assert report_crit["health"] == "Critical"
    assert len(report_crit["timeouts"]) == 1
    assert any("timeout" in rec.lower() for rec in report_crit["recommendations"])

    # 2. Warning Case (Duplicates and slow requests exist)
    log_res_warn = {
        "slow_requests": ["Slow timing log"],
        "duplicate_calls": ["Duplicate model invocation detected"],
        "retry_loops": [],
        "timeouts": [],
        "exceptions": []
    }
    metrics_res_warn = {
        "average_latency": 4.5,
        "slowest_operation": "atlas",
        "total_requests": 15,
        "bottlenecks": ["Operation 'atlas' took 4.50s"]
    }
    report_warn = pa.generate_performance_report(log_res_warn, metrics_res_warn)
    assert report_warn["health"] == "Warning"
    assert len(report_warn["slow_operations"]) == 1
    assert len(report_warn["duplicate_calls"]) == 1

    # 3. Save Report
    report_id = pa.save_report(report_warn)
    assert report_id is not None
    saved = memory_manager.performance.get(report_id)
    assert saved is not None
    assert saved["health"] == "Warning"
