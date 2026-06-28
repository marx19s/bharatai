"""
=================================================
BharatAI - Quality Assurance Specialist (QAAgent)
=================================================
"""

import re
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from memory.memory_manager import memory_manager


class QAAgent(BaseAgent):
    """
    QAAgent is responsible for running unit and regression tests,
    parsing results, generating structured QA reports, and saving them to QA memory.
    """

    def __init__(self):
        super().__init__(
            name="qa",
            role="Quality Assurance Specialist. Runs tests, verifies regression, and generates reports."
        )

    def _parse_pytest(self, output: str) -> Dict[str, Any]:
        """Parse pytest stdout to extract total, passed, failed, execution time, and test names."""
        passed_tests = []
        failed_tests = []
        
        # Verbose line pattern: tests/test_file.py::test_name PASSED/FAILED/ERROR
        pattern = re.compile(r'([^\s]+::[^\s]+)\s+(PASSED|FAILED|ERROR)')
        for line in output.splitlines():
            match = pattern.search(line)
            if match:
                test_name = match.group(1)
                status = match.group(2)
                if status == "PASSED":
                    passed_tests.append(test_name)
                else:
                    failed_tests.append(test_name)

        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        error_match = re.search(r'(\d+)\s+error', output)
        time_match = re.search(r'in\s+([\d.]+)s', output)

        passed = int(passed_match.group(1)) if passed_match else len(passed_tests)
        failed = int(failed_match.group(1)) if failed_match else len(failed_tests)
        if error_match:
            failed += int(error_match.group(1))

        execution_time = float(time_match.group(1)) if time_match else 0.0
        total = passed + failed

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "execution_time": execution_time,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests
        }

    def _parse_regression(self, output: str) -> Dict[str, Any]:
        """Parse output of tests/full_test.py into a structured dictionary."""
        test_line_pattern = re.compile(r'^([a-zA-Z0-9:\s_-]+?)\s+(PASS|FAIL)\s*\((.*?)\)$')
        overall_pattern = re.compile(r'Overall:\s*(PASS|FAIL)')
        time_pattern = re.compile(r'Total execution time:\s*([\d.]+)s')

        results = []
        overall = "FAIL"
        total_time = 0.0

        for line in output.splitlines():
            line_str = line.strip()
            # Match test case line
            match = test_line_pattern.match(line_str)
            if match:
                results.append({
                    "test_name": match.group(1).strip(),
                    "status": match.group(2),
                    "details": match.group(3).strip()
                })
            # Match overall status
            overall_match = overall_pattern.search(line_str)
            if overall_match:
                overall = overall_match.group(1)
            # Match total execution time
            time_match = time_pattern.search(line_str)
            if time_match:
                total_time = float(time_match.group(1))

        passed_tests = [r["test_name"] for r in results if r["status"] == "PASS"]
        failed_tests = [r["test_name"] for r in results if r["status"] == "FAIL"]

        return {
            "results": results,
            "overall": overall,
            "total_time": total_time,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests
        }

    def run_unit_tests(self, test_path: Optional[str] = None) -> Dict[str, Any]:
        """Run pytest for a specific test file or all tests, returning summary metrics."""
        self.logger.info("QAAgent: Running unit tests...")
        cmd = ["pytest", "-v"]
        if test_path:
            cmd.append(test_path)

        memory_manager.qa.add({
            "action": "run_unit_tests_started",
            "test_path": test_path or "all",
            "timestamp": time.time()
        })

        start_time = time.time()
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        elapsed = time.time() - start_time

        parsed = self._parse_pytest(res.stdout + res.stderr)
        
        # If pytest failed to collect or run completely, fallback metrics
        if parsed["total"] == 0 and res.returncode != 0:
            parsed["failed"] = 1
            parsed["total"] = 1
            if parsed["execution_time"] == 0.0:
                parsed["execution_time"] = elapsed

        memory_manager.qa.add({
            "action": "run_unit_tests_completed",
            "metrics": parsed,
            "returncode": res.returncode,
            "timestamp": time.time()
        })

        return parsed

    def run_regression_tests(self) -> Dict[str, Any]:
        """Run the full regression test suite (tests/full_test.py)."""
        self.logger.info("QAAgent: Running regression tests...")
        cmd = ["python", "tests/full_test.py"]

        memory_manager.qa.add({
            "action": "run_regression_tests_started",
            "timestamp": time.time()
        })

        res = subprocess.run(cmd, capture_output=True, text=True, check=False)

        parsed = self._parse_regression(res.stdout + res.stderr)

        memory_manager.qa.add({
            "action": "run_regression_tests_completed",
            "overall": parsed.get("overall"),
            "timestamp": time.time()
        })

        return parsed

    def generate_report(self, run_results: Dict[str, Any]) -> Dict[str, Any]:
        """Produce a structured QA report based on test results dictionary."""
        self.logger.info("QAAgent: Generating QA report...")
        
        # Determine if it's regression results or unit test results
        is_regression = "results" in run_results
        
        if is_regression:
            overall = run_results.get("overall", "FAIL")
            passed_count = sum(1 for r in run_results.get("results", []) if r.get("status") == "PASS")
            failed_count = sum(1 for r in run_results.get("results", []) if r.get("status") == "FAIL")
            
            warnings = []
            if failed_count > 0:
                warnings.append(f"{failed_count} regression tests failed.")
            
            status = "APPROVED" if overall == "PASS" else "BLOCKED"
            recommendation = "All regression checks passed. Ready for deployment." if overall == "PASS" else "Fix regressions before deploying."
        else:
            passed_count = run_results.get("passed", 0)
            failed_count = run_results.get("failed", 0)
            total = run_results.get("total", 0)
            
            warnings = []
            if failed_count > 0:
                warnings.append(f"{failed_count} unit tests failed out of {total}.")
                status = "BLOCKED"
                recommendation = "Fix failing unit tests."
            elif total == 0:
                warnings.append("No unit tests were executed.")
                status = "WARNING"
                recommendation = "Add unit tests to cover new code."
            else:
                status = "APPROVED"
                recommendation = "All unit tests passed."

        report = {
            "status": status,
            "passed": passed_count,
            "failed": failed_count,
            "warnings": warnings,
            "recommendation": recommendation
        }

        memory_manager.qa.add({
            "action": "generate_report",
            "report": report,
            "timestamp": time.time()
        })
        return report

    def save_report(self, report: Dict[str, Any]) -> str:
        """Save a report dict to QA memory and return its generated memory ID."""
        self.logger.info("QAAgent: Saving report to QA Memory...")
        report_id = memory_manager.qa.add(report)
        return report_id

    def _analyze_test_history(self, current_failed: List[str], current_passed: List[str]) -> Dict[str, List[str]]:
        """Retrieve recent QA records to compute repeated regressions and flaky tests."""
        from memory.memory_manager import memory_manager
        
        try:
            entries = list(memory_manager.lessons._data.values())
            qa_lessons = [e for e in entries if e.get("category") == "qa"]
        except Exception:
            qa_lessons = []
            
        historical_failures = {}
        for lesson in qa_lessons:
            failed = lesson.get("failed_tests", [])
            for f in failed:
                historical_failures[f] = historical_failures.get(f, 0) + 1
                
        repeated_regressions = []
        flaky_tests = []
        
        for test in current_failed:
            if historical_failures.get(test, 0) > 0:
                repeated_regressions.append(test)
                
        for test in current_passed:
            if historical_failures.get(test, 0) > 0:
                flaky_tests.append(test)
                
        return {
            "repeated_regressions": list(set(repeated_regressions)),
            "flaky_tests": list(set(flaky_tests))
        }

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Route QA task actions."""
        from services.engineering_learning import EngineeringLearningService
        
        # Lessons Engine hook
        recs = EngineeringLearningService.query_lessons(task)
        if recs:
            if context is None:
                context = {}
            context["lessons_recommendations"] = recs
            self.logger.info(f"QAAgent: Recommended previous lessons: {recs}")

        self._current_context = context
        
        # Determine operation
        op = None
        test_path = None
        run_results = None
        report = None
        
        if context:
            op = context.get("operation")
            test_path = context.get("test_path")
            run_results = context.get("run_results")
            report = context.get("report")

        task_lower = task.lower()
        
        # Run execution
        if op == "run_unit_tests":
            results = self.run_unit_tests(test_path)
            return results
        elif op == "run_regression_tests":
            results = self.run_regression_tests()
            return results
        elif op == "generate_report" and run_results is not None:
            return self.generate_report(run_results)
        elif op == "save_report" and report is not None:
            return self.save_report(report)
            
        # Default behavior: run and report
        is_regression = "regression" in task_lower or "full" in task_lower
        if is_regression:
            results = self.run_regression_tests()
        else:
            results = self.run_unit_tests(test_path)
            
        report = self.generate_report(results)
        self.save_report(report)
        
        # Capture learning metrics
        failed_tests = results.get("failed_tests", [])
        passed_tests = results.get("passed_tests", [])
        
        history = self._analyze_test_history(failed_tests, passed_tests)
        
        EngineeringLearningService.capture_qa_result(
            task=task,
            failed_tests=failed_tests,
            flaky_tests=history["flaky_tests"],
            repeated_regressions=history["repeated_regressions"],
            passed_count=len(passed_tests),
            failed_count=len(failed_tests)
        )
        
        return report
