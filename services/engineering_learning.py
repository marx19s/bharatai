"""
=================================================
BharatAI - Engineering Learning Service
=================================================
"""

from memory.lessons_engine import LessonsEngine
from typing import Dict, Any, List, Optional


class EngineeringLearningService:
    """
    Service layer providing unified interface for agents to record results
    and query previous lessons from the LessonsEngine.
    """

    @staticmethod
    def query_lessons(task_query: str) -> Optional[Dict[str, Any]]:
        """
        Query previous lessons matching the task description.
        """
        return LessonsEngine.get_recommendations(task_query)

    @staticmethod
    def capture_developer_result(
        task: str,
        task_type: str,
        success: bool,
        implementation_pattern: str,
        files_modified: List[str],
        has_recommendations: bool,
        lessons_applied_count: int,
        reused_fixes_count: int
    ) -> None:
        """
        Capture developer task completion results and store as a lesson asynchronously.
        """
        lesson = {
            "category": "developer",
            "task": task,
            "task_type": task_type,
            "success": success,
            "implementation_pattern": implementation_pattern,
            "files_modified": files_modified,
            "has_recommendations": has_recommendations,
            "lessons_applied_count": lessons_applied_count,
            "reused_fixes_count": reused_fixes_count
        }
        LessonsEngine.save_lesson_async(lesson)

    @staticmethod
    def capture_reviewer_result(
        task: str,
        review_comments: List[str],
        recurring_code_smells: List[str],
        architecture_issues: List[str]
    ) -> None:
        """
        Capture reviewer task completion results and store as a lesson asynchronously.
        """
        lesson = {
            "category": "reviewer",
            "task": task,
            "review_comments": review_comments,
            "recurring_code_smells": recurring_code_smells,
            "architecture_issues": architecture_issues
        }
        LessonsEngine.save_lesson_async(lesson)

    @staticmethod
    def capture_qa_result(
        task: str,
        failed_tests: List[str],
        flaky_tests: List[str],
        repeated_regressions: List[str],
        passed_count: int,
        failed_count: int
    ) -> None:
        """
        Capture QA test execution results and store as a lesson asynchronously.
        """
        lesson = {
            "category": "qa",
            "task": task,
            "failed_tests": failed_tests,
            "flaky_tests": flaky_tests,
            "repeated_regressions": repeated_regressions,
            "passed": passed_count,
            "failed": failed_count
        }
        LessonsEngine.save_lesson_async(lesson)

    @staticmethod
    def capture_bug_fix_result(
        error_type: str,
        probable_cause: str,
        recommended_fix: str
    ) -> None:
        """
        Capture BugFixer results and store as a reusable fix pattern lesson asynchronously.
        """
        reusable_fix_pattern = {
            "error_type": error_type,
            "trigger_regex": f".*{error_type}.*",
            "reusable_fix": recommended_fix
        }
        lesson = {
            "category": "debugging",
            "title": f"Bug Fix Pattern - {error_type}",
            "solution": f"Cause: {probable_cause}. Fix: {recommended_fix}",
            "reusable_fix_pattern": reusable_fix_pattern,
            "error_type": error_type,
            "reusable_fix": recommended_fix,
            "verified": True
        }
        LessonsEngine.save_lesson_async(lesson)

    @staticmethod
    def capture_performance_result(
        task: str,
        bottlenecks: List[str],
        optimization_suggestions: List[str],
        average_latency: float,
        slowest_operation: str,
        total_requests: int
    ) -> None:
        """
        Capture Performance task results and store as a lesson asynchronously.
        """
        lesson = {
            "category": "performance",
            "task": task,
            "bottlenecks": bottlenecks,
            "optimization_suggestions": optimization_suggestions,
            "execution_timings": {
                "average_latency": average_latency,
                "slowest_operation": slowest_operation,
                "total_requests": total_requests
            }
        }
        LessonsEngine.save_lesson_async(lesson)
