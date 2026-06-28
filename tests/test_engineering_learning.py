"""
=================================================
BharatAI - Engineering Intelligence & Learning Unit Tests
=================================================
"""

import time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

from memory.memory_manager import memory_manager
from memory.lessons_engine import LessonsEngine
from services.engineering_learning import EngineeringLearningService
from company.office_api import OfficeAPI

from agents.engineering_dept import DeveloperAgent, ReviewerAgent
from agents.qa_agent import QAAgent
from agents.bug_fixer_agent import BugFixerAgent
from agents.performance_agent import PerformanceAgent


@pytest.fixture(autouse=True)
def clean_memory():
    """Clear memory manager before every test to ensure isolation."""
    memory_manager.clear_all()
    yield
    memory_manager.clear_all()


def test_lessons_engine_recommendations():
    """Verify LessonsEngine retrieves similar lessons and builds correct recommendations mapping."""
    # 1. Populate mock database
    memory_manager.lessons.add_lesson({
        "category": "debugging",
        "reusable_fix": "Use close() in finally block",
        "solution": "Old solution",
        "title": "Database connection error"
    })
    memory_manager.lessons.add_lesson({
        "category": "developer",
        "implementation_pattern": "Factory Pattern",
        "solution": "Old dev solution",
        "title": "Object Creation task"
    })
    memory_manager.lessons.add_lesson({
        "category": "reviewer",
        "review_comments": ["Avoid duplicate code", "Add docstrings"],
        "title": "Code Review suggestion"
    })

    # 2. Get recommendations based on query overlap words
    recs = LessonsEngine.get_recommendations("database object creation code review suggestion block")
    
    assert recs is not None
    assert recs["previous_fix"] == "Use close() in finally block"
    assert recs["previous_implementation"] == "Factory Pattern"
    assert recs["previous_review"] == "Avoid duplicate code; Add docstrings"


def test_lessons_engine_save_async():
    """Verify LessonsEngine saves lessons asynchronously in a background thread."""
    lesson = {
        "category": "developer",
        "task": "Test task",
        "success": True
    }
    
    LessonsEngine.save_lesson_async(lesson)
    
    # Sleep a tiny bit to allow background thread to execute
    time.sleep(0.1)
    
    all_lessons = list(memory_manager.lessons._data.values())
    assert len(all_lessons) == 1
    assert all_lessons[0]["task"] == "Test task"
    assert all_lessons[0]["success"] is True


def test_engineering_learning_service_query():
    """Verify service interface queries recommendations correctly."""
    memory_manager.lessons.add_lesson({
        "category": "debugging",
        "reusable_fix": "Fix pattern details",
        "title": "Database error"
    })
    
    recs = EngineeringLearningService.query_lessons("Database error")
    assert recs is not None
    assert recs["previous_fix"] == "Fix pattern details"


def test_developer_agent_learning_and_lessons_injection():
    """Verify DeveloperAgent executes task, queries recommendations, injects into prompt, and stores stats."""
    dev = DeveloperAgent()
    
    # 1. Add matching lesson to database
    memory_manager.lessons.add_lesson({
        "category": "debugging",
        "reusable_fix": "Avoid double negative conditions",
        "title": "conditional logic"
    })
    
    prompts_called = []
    
    def mock_call_model(prompt, task=None, **kwargs):
        prompts_called.append(prompt)
        return SimpleNamespace(content="def fix_logic():\n    pass")
        
    dev._call_model = mock_call_model
    
    # Run DeveloperAgent execute
    res = dev.execute("Implement conditional logic", {"task_type": "coding"})
    
    assert "def fix_logic" in res
    assert len(prompts_called) == 1
    # Check that recommendations were injected into model prompt
    assert "Avoid double negative conditions" in prompts_called[0]
    
    # Sleep a tiny bit for async save
    time.sleep(0.1)
    
    # Verify developer task details captured in lessons
    all_lessons = list(memory_manager.lessons._data.values())
    dev_lessons = [l for l in all_lessons if l.get("category") == "developer"]
    
    assert len(dev_lessons) == 1
    assert dev_lessons[0]["success"] is True
    assert dev_lessons[0]["task_type"] == "coding"
    assert dev_lessons[0]["lessons_applied_count"] == 0
    assert dev_lessons[0]["reused_fixes_count"] == 1


def test_reviewer_agent_learning():
    """Verify ReviewerAgent queries recommendations and captures review details."""
    rev = ReviewerAgent()
    
    def mock_call_model(prompt, task=None, **kwargs):
        return SimpleNamespace(content="- Code smell: long parameter list\n- Suggestion: group parameters into object\n- Design issue: high coupling")
        
    rev._call_model = mock_call_model
    
    rev.execute("Review this code block")
    
    time.sleep(0.1)
    
    # Verify reviewer task details captured
    all_lessons = list(memory_manager.lessons._data.values())
    rev_lessons = [l for l in all_lessons if l.get("category") == "reviewer"]
    
    assert len(rev_lessons) == 1
    assert "long parameter list" in rev_lessons[0]["recurring_code_smells"][0]
    assert "high coupling" in rev_lessons[0]["architecture_issues"][0]
    assert "group parameters into object" in rev_lessons[0]["review_comments"][0]


def test_qa_agent_learning_and_history():
    """Verify QAAgent parses verbose pytest, queries history for regressions, and captures lessons."""
    qa = QAAgent()
    
    # 1. Prime memory with prior failure to trigger repeated regression detection
    memory_manager.lessons.add_lesson({
        "category": "qa",
        "failed_tests": ["tests/test_demo.py::test_failing"],
        "passed": 0,
        "failed": 1
    })
    
    # 2. Mock pytest subprocess output
    pytest_stdout = """
============================= test session starts =============================
collected 2 items

tests/test_demo.py::test_passing PASSED                                  [ 50%]
tests/test_demo.py::test_failing FAILED                                  [100%]

================================== FAILURES ===================================
    """
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = SimpleNamespace(returncode=1, stdout=pytest_stdout, stderr="")
        
        qa.execute("Run unit tests")
        
    time.sleep(0.1)
    
    # Verify QA lesson captured
    all_lessons = list(memory_manager.lessons._data.values())
    # The first lesson is the primed failure, the second is our run
    qa_lessons = [l for l in all_lessons if l.get("category") == "qa" and l.get("task") == "Run unit tests"]
    
    assert len(qa_lessons) == 1
    assert "tests/test_demo.py::test_failing" in qa_lessons[0]["failed_tests"]
    assert "tests/test_demo.py::test_passing" not in qa_lessons[0]["failed_tests"]
    # Check repeated regressions detection works
    assert "tests/test_demo.py::test_failing" in qa_lessons[0]["repeated_regressions"]


def test_bug_fixer_agent_learning():
    """Verify BugFixerAgent captures reusable fix pattern."""
    bf = BugFixerAgent()
    
    def mock_call_model(prompt, task=None, **kwargs):
        return SimpleNamespace(content="PROBABLE_CAUSE: Module not installed\nRECOMMENDED_FIX: run pip install request\nCONFIDENCE_SCORE: 0.95")
        
    bf._call_model = mock_call_model
    
    bf.execute("ModuleNotFoundError: No module named 'request'")
    
    time.sleep(0.1)
    
    # Verify bug fix lesson captured
    all_lessons = list(memory_manager.lessons._data.values())
    bf_lessons = [l for l in all_lessons if l.get("category") == "debugging"]
    
    assert len(bf_lessons) == 1
    assert bf_lessons[0]["error_type"] == "ModuleNotFoundError"
    assert bf_lessons[0]["reusable_fix"] == "run pip install request"
    assert bf_lessons[0]["reusable_fix_pattern"]["trigger_regex"] == ".*ModuleNotFoundError.*"


def test_performance_agent_learning():
    """Verify PerformanceAgent captures performance metrics."""
    perf = PerformanceAgent()
    
    def mock_call_model(prompt, task=None, **kwargs):
        return SimpleNamespace(content="[]")
        
    perf._call_model = mock_call_model
    
    # Execute with logs log-analysis mock data
    context = {
        "operation": "execute",
        "metrics": [{"agent": "developer", "elapsed_ms": 3200.0}],
        "log_path": "dummy_path.log"
    }
    
    # Mock log analysis returns
    perf.analyze_logs = MagicMock(return_value={"timeouts": [], "slow_requests": ["Slow execution: developer"], "duplicate_calls": []})
    
    perf.execute("Performance optimization task", context)
    
    time.sleep(0.1)
    
    # Verify performance lesson captured
    all_lessons = list(memory_manager.lessons._data.values())
    perf_lessons = [l for l in all_lessons if l.get("category") == "performance"]
    
    assert len(perf_lessons) == 1
    assert len(perf_lessons[0]["bottlenecks"]) > 0
    assert perf_lessons[0]["execution_timings"]["average_latency"] == 3.2


def test_office_api_get_engineering_insights():
    """Verify OfficeAPI correctly aggregates insights metrics from lessons database."""
    api = OfficeAPI()
    
    # 1. Prime lessons with various categories
    # Successful dev task with recommendations used -> Bugs prevented / lessons applied / reused fix
    memory_manager.lessons.add_lesson({
        "category": "developer",
        "success": True,
        "lessons_applied_count": 1,
        "reused_fixes_count": 1,
        "has_recommendations": True
    })
    # Review lesson -> Clean (100% review quality)
    memory_manager.lessons.add_lesson({
        "category": "reviewer",
        "recurring_code_smells": ["None detected."],
        "architecture_issues": ["None detected."]
    })
    # QA lesson -> 4 passed, 1 flaky (stability = 3 / 4 = 75%)
    memory_manager.lessons.add_lesson({
        "category": "qa",
        "passed": 4,
        "failed": 0,
        "flaky_tests": ["tests/test_flaky.py::test_flaky"]
    })
    
    insights = api.get_engineering_insights()
    
    assert insights["bugs_prevented"] == 1
    assert insights["reused_fixes"] == 1
    assert insights["lessons_applied"] == 1
    assert insights["review_quality"] == "100%"
    assert insights["test_stability"] == "75%"
