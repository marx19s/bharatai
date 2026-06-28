"""
=================================================
BharatAI - Company Memory Engine Tests
=================================================
"""

import os
import tempfile
from pathlib import Path
import pytest

from memory.company_memory import CompanyMemoryNamespace, LessonsNamespace
from memory.memory_manager import MemoryManager


def test_company_memory_namespace_basic_crud():
    """Verify standard CRUD and search operations on a CompanyMemoryNamespace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test_namespace.json"
        ns = CompanyMemoryNamespace("test_ns", file_path=file_path)

        # 1. Test Add
        item_id = ns.add({"title": "Fix bug in Neo", "severity": "high", "tags": ["sprint-3", "neo"]})
        assert item_id is not None
        assert isinstance(item_id, str)
        assert len(item_id) > 0

        # 2. Test Get
        item = ns.get(item_id)
        assert item is not None
        assert item["title"] == "Fix bug in Neo"
        assert item["severity"] == "high"
        assert item["id"] == item_id

        # 3. Test Search
        results = ns.search("neo")
        assert len(results) == 1
        assert results[0]["id"] == item_id

        results_empty = ns.search("nonexistent")
        assert len(results_empty) == 0

        # 4. Test Update
        updated = ns.update(item_id, {"title": "Fix bug in Neo", "severity": "resolved", "tags": ["sprint-3", "neo"]})
        assert updated is True
        item_updated = ns.get(item_id)
        assert item_updated["severity"] == "resolved"

        # Test update invalid id
        assert ns.update("invalid_id", {"title": "Test"}) is False

        # 5. Test Delete
        deleted = ns.delete(item_id)
        assert deleted is True
        assert ns.get(item_id) is None

        # Test delete invalid id
        assert ns.delete("invalid_id") is False


def test_lessons_learned_api():
    """Verify lessons learned API functionality including similar search and verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test_lessons.json"
        lessons_ns = LessonsNamespace(file_path=file_path)

        # 1. Add Lessons
        lesson1_id = lessons_ns.add_lesson({
            "title": "Database connection pooling error",
            "solution": "Configure max connections to 50",
            "category": "database"
        })
        lesson2_id = lessons_ns.add_lesson({
            "title": "Thread deadlock in workflow scheduler",
            "solution": "Avoid synchronous nested locks",
            "category": "threading"
        })
        lesson3_id = lessons_ns.add_lesson({
            "title": "Ollama provider socket timeout",
            "solution": "Increase client timeout to 30 seconds for heavy model tasks",
            "category": "ollama"
        })

        assert lesson1_id is not None
        assert lesson2_id is not None
        assert lesson3_id is not None

        # Check default verification is False
        assert lessons_ns.get(lesson1_id)["verified"] is False

        # 2. Mark Verified
        success = lessons_ns.mark_verified(lesson1_id, True)
        assert success is True
        assert lessons_ns.get(lesson1_id)["verified"] is True

        # Test mark verified invalid id
        assert lessons_ns.mark_verified("invalid_id") is False

        # 3. Find Similar Lessons (overlap scoring)
        # Search for database lessons
        similar1 = lessons_ns.find_similar_lessons("database pooling error")
        assert len(similar1) > 0
        assert similar1[0]["id"] == lesson1_id  # Matches database, connection, pooling, error

        # Search for lock and thread issues
        similar2 = lessons_ns.find_similar_lessons("thread lock scheduler")
        assert len(similar2) > 0
        assert similar2[0]["id"] == lesson2_id  # Matches thread, lock, scheduler


def test_memory_manager_integration():
    """Verify MemoryManager instantiates namespaces, delegates lessons API, clears, and passes health checks."""
    manager = MemoryManager()

    # Verify all namespaces exist
    assert isinstance(manager.company, CompanyMemoryNamespace)
    assert isinstance(manager.ceo, CompanyMemoryNamespace)
    assert isinstance(manager.engineering, CompanyMemoryNamespace)
    assert isinstance(manager.qa, CompanyMemoryNamespace)
    assert isinstance(manager.research, CompanyMemoryNamespace)
    assert isinstance(manager.operations, CompanyMemoryNamespace)
    assert isinstance(manager.lessons, LessonsNamespace)
    assert isinstance(manager.projects, CompanyMemoryNamespace)

    # Clean state before testing
    manager.clear_all()

    # Verify lessons delegation
    lesson_id = manager.add_lesson({
        "title": "Memory leak in event bus subscriptions",
        "solution": "Always unsubscribe in final block"
    })
    assert lesson_id is not None

    similar = manager.find_similar_lessons("event bus memory leak")
    assert len(similar) > 0
    assert similar[0]["id"] == lesson_id
    assert similar[0]["verified"] is False

    success = manager.mark_verified(lesson_id, True)
    assert success is True
    assert manager.lessons.get(lesson_id)["verified"] is True

    # Test Health Check
    assert manager.health_check() is True

    # Test Clear All
    manager.clear_all()
    assert manager.lessons.get(lesson_id) is None
