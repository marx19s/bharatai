"""
=================================================
BharatAI - Performance Specialist (PerformanceAgent)
=================================================
"""

import re
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from memory.memory_manager import memory_manager
from config.settings import LOG_FILE


class PerformanceAgent(BaseAgent):
    """
    PerformanceAgent is responsible for read-only analysis of performance logs and metrics,
    detecting duplicate model calls, retries, bottlenecks, and generating performance reports.
    """

    def __init__(self):
        super().__init__(
            name="performance",
            role="Performance Specialist. Monitors execution profiles, counts duplicate calls, and suggests optimizations."
        )

    def analyze_logs(self, log_path: Optional[str] = None) -> Dict[str, Any]:
        """Scan log file to detect slow requests, duplicate model calls, retries, and exceptions."""
        self.logger.info("PerformanceAgent: Analyzing log file...")
        target_path = Path(log_path or LOG_FILE)
        
        slow_requests = []
        duplicate_calls = []
        retry_loops = []
        timeouts = []
        exceptions = []

        if not target_path.exists():
            self.logger.warning(f"PerformanceAgent: Log file does not exist: {target_path}")
            return {
                "slow_requests": slow_requests,
                "duplicate_calls": duplicate_calls,
                "retry_loops": retry_loops,
                "timeouts": timeouts,
                "exceptions": exceptions
            }

        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            # Sub-heuristics
            # Track model requests per request ID to identify duplicates
            model_calls_by_req = {}
            
            for line in lines[-1000:]: # Look at the last 1000 lines
                line_str = line.strip()
                
                # 1. Slow requests
                # e.g., "completed in 12.34s" or "elapsed_ms=5356.2" or "TIMING {...}"
                if "elapsed_ms" in line_str:
                    try:
                        ms_match = re.search(r'elapsed_ms[^\d]+?([\d.]+)', line_str)
                        if ms_match:
                            ms = float(ms_match.group(1))
                            if ms > 5000.0:
                                slow_requests.append(f"Slow timing log: {line_str[:120]}...")
                    except Exception:
                        pass
                elif "completed in" in line_str or "succeeded in" in line_str:
                    time_match = re.search(r'(completed|succeeded)\s+in\s+([\d.]+)s', line_str)
                    if time_match:
                        seconds = float(time_match.group(2))
                        if seconds > 5.0:
                            slow_requests.append(f"Slow execution: {line_str[:120]}...")

                # 2. Duplicate model calls
                if "request_id=" in line_str and ("Attempting generation" in line_str or "Ollama generation requested" in line_str):
                    req_match = re.search(r'request_id=([a-f0-9]+)', line_str)
                    if req_match:
                        req_id = req_match.group(1)
                        model_calls_by_req[req_id] = model_calls_by_req.get(req_id, 0) + 1
                        if model_calls_by_req[req_id] > 1:
                            duplicate_calls.append(f"Duplicate model invocation detected for request_id: {req_id}")

                # 3. Retry loops
                if "attempt" in line_str.lower() and ("retry" in line_str.lower() or "attempt 2" in line_str.lower()):
                    retry_loops.append(f"Retry attempt: {line_str[:120]}...")

                # 4. Timeout events
                if "timeout" in line_str.lower():
                    timeouts.append(f"Timeout signature: {line_str[:120]}...")

                # 5. Repeated exceptions
                if "exception" in line_str.lower() or "traceback" in line_str.lower() or "error" in line_str.lower():
                    if "timing" not in line_str.lower() and "level" not in line_str.lower():
                        exceptions.append(f"Error signature: {line_str[:100]}...")

        except Exception as e:
            self.logger.error(f"PerformanceAgent: Failed to read logs: {e}")

        # Unique lists to prevent spamming report
        return {
            "slow_requests": list(set(slow_requests))[:5],
            "duplicate_calls": list(set(duplicate_calls))[:5],
            "retry_loops": list(set(retry_loops))[:5],
            "timeouts": list(set(timeouts))[:5],
            "exceptions": list(set(exceptions))[:5]
        }

    def analyze_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute metrics summary including average latency, slowest operations, and bottlenecks."""
        self.logger.info("PerformanceAgent: Analyzing metrics list...")
        
        if not metrics:
            return {
                "average_latency": 0.0,
                "slowest_operation": "N/A",
                "total_requests": 0,
                "bottlenecks": []
            }

        total_latency = 0.0
        slowest_op = "N/A"
        max_latency = -1.0
        bottlenecks = []
        total_requests = len(metrics)

        for item in metrics:
            latency = item.get("latency", item.get("elapsed_ms", 0.0))
            # Normalise millisecond values to seconds if appropriate
            if "elapsed_ms" in item:
                latency = latency / 1000.0
            
            total_latency += latency
            op_name = item.get("agent", item.get("operation", item.get("type", "unknown")))
            
            if latency > max_latency:
                max_latency = latency
                slowest_op = op_name
                
            if latency > 3.0: # 3 seconds threshold for bottleneck
                bottlenecks.append(f"Operation '{op_name}' took {latency:.2f}s")

        avg_latency = total_latency / total_requests if total_requests > 0 else 0.0

        return {
            "average_latency": avg_latency,
            "slowest_operation": slowest_op,
            "total_requests": total_requests,
            "bottlenecks": list(set(bottlenecks))
        }

    def generate_performance_report(self, log_analysis: Dict[str, Any], metrics_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create structured performance report dict."""
        self.logger.info("PerformanceAgent: Constructing report...")
        
        timeouts = log_analysis.get("timeouts", [])
        slow_reqs = log_analysis.get("slow_requests", [])
        dup_calls = log_analysis.get("duplicate_calls", [])
        avg_latency = metrics_analysis.get("average_latency", 0.0)

        # Health rule determination
        if len(timeouts) > 0 or avg_latency > 10.0:
            health = "Critical"
        elif len(slow_reqs) > 0 or len(dup_calls) > 0 or avg_latency > 3.0:
            health = "Warning"
        else:
            health = "Good"

        # Recommendations derivation
        recommendations = []
        if len(timeouts) > 0:
            recommendations.append("Increase connection/socket timeout configurations on OllamaProvider.")
        if len(dup_calls) > 0:
            recommendations.append("Ensure task classifiers cache classification results to avoid duplicate model invocations.")
        if avg_latency > 3.0:
            recommendations.append(f"Slowest operation '{metrics_analysis.get('slowest_operation')}' is causing bottleneck. Review its logic.")
        if not recommendations:
            recommendations.append("No actions needed. Performance is optimal.")

        report = {
            "health": health,
            "slow_operations": metrics_analysis.get("bottlenecks", []),
            "duplicate_calls": dup_calls,
            "timeouts": timeouts,
            "recommendations": recommendations
        }

        memory_manager.performance.add({
            "action": "generate_performance_report",
            "report": report,
            "timestamp": time.time()
        })
        
        return report

    def save_report(self, report: Dict[str, Any]) -> str:
        """Save a report to Performance memory."""
        self.logger.info("PerformanceAgent: Saving report to Performance Memory...")
        return memory_manager.performance.add(report)

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Route performance tasks."""
        from services.engineering_learning import EngineeringLearningService
        
        # Lessons Engine hook
        recs = EngineeringLearningService.query_lessons(task)
        if recs:
            if context is None:
                context = {}
            context["lessons_recommendations"] = recs
            self.logger.info(f"PerformanceAgent: Recommended previous lessons: {recs}")

        self._current_context = context
        metrics = []
        if context and "metrics" in context:
            metrics = context["metrics"]

        log_path = None
        if context and "log_path" in context:
            log_path = context["log_path"]

        op = context.get("operation") if context else None
        
        if op == "analyze_logs":
            return self.analyze_logs(log_path)
        elif op == "analyze_metrics":
            return self.analyze_metrics(metrics)
        elif op == "generate_performance_report":
            log_res = context.get("log_res", {})
            metrics_res = context.get("metrics_res", {})
            return self.generate_performance_report(log_res, metrics_res)
        elif op == "save_report":
            report = context.get("report", {})
            return self.save_report(report)

        # Default action: run full analysis and save report
        log_res = self.analyze_logs(log_path)
        metrics_res = self.analyze_metrics(metrics)
        report = self.generate_performance_report(log_res, metrics_res)
        self.save_report(report)
        
        # Capture learning result
        EngineeringLearningService.capture_performance_result(
            task=task,
            bottlenecks=report.get("slow_operations", []),
            optimization_suggestions=report.get("recommendations", []),
            average_latency=metrics_res.get("average_latency", 0.0),
            slowest_operation=metrics_res.get("slowest_operation", "N/A"),
            total_requests=metrics_res.get("total_requests", 0)
        )
        
        return report
