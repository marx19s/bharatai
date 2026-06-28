"""
=================================================
BharatAI
Memory Manager (Unified memory layer)
=================================================
"""

import logging
from typing import Dict, Any, List

from memory.session_memory import SessionMemory
from memory.user_memory import UserMemory
from memory.conversation_memory import ConversationMemory
from memory.project_memory import ProjectMemory
from memory.company_memory import CompanyMemoryNamespace, LessonsNamespace

from config.settings import LOG_FILE, LOG_LEVEL

logger = logging.getLogger("bharatai.memory")
if not logger.handlers:
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass


class MemoryManager:
    """Central manager coordinating session, conversation, project, user, and company memory modules."""

    def __init__(self):
        self.session = SessionMemory()
        self.user = UserMemory()
        self.conversation = ConversationMemory()
        self.project = ProjectMemory()
        
        # New company memory namespaces
        self.company = CompanyMemoryNamespace("company")
        self.ceo = CompanyMemoryNamespace("ceo")
        self.engineering = CompanyMemoryNamespace("engineering")
        self.qa = CompanyMemoryNamespace("qa")
        self.research = CompanyMemoryNamespace("research")
        self.operations = CompanyMemoryNamespace("operations")
        self.lessons = LessonsNamespace()
        self.projects = CompanyMemoryNamespace("projects")
        self.developer = CompanyMemoryNamespace("developer")
        self.reviewer = CompanyMemoryNamespace("reviewer")
        self.performance = CompanyMemoryNamespace("performance")
        
        logger.info("Universal MemoryManager initialized successfully.")

    def clear_all(self) -> None:
        """Reset all memory sub-modules (transient and persistent)."""
        logger.warning("Clearing all memory modules...")
        self.session.clear()
        self.user.clear()
        self.conversation.clear()
        self.project.clear()
        
        # Clear company memory namespaces
        self.company.clear()
        self.ceo.clear()
        self.engineering.clear()
        self.qa.clear()
        self.research.clear()
        self.operations.clear()
        self.lessons.clear()
        self.projects.clear()
        self.developer.clear()
        self.reviewer.clear()
        self.performance.clear()
        
        logger.info("All memory modules cleared.")

    def health_check(self) -> bool:
        """Ensure all persistent storage targets are writable."""
        try:
            # Simple self-write check
            self.session.set("_health_check", True)
            assert self.session.get("_health_check") is True
            self.session.delete("_health_check")
            
            # Persistent checks
            self.user.load()
            self.conversation.load()
            self.project.load()
            
            # Company memory checks
            self.company.load()
            self.ceo.load()
            self.engineering.load()
            self.qa.load()
            self.research.load()
            self.operations.load()
            self.lessons.load()
            self.projects.load()
            self.developer.load()
            self.reviewer.load()
            self.performance.load()
            return True
        except Exception as e:
            logger.error(f"MemoryManager health check failed: {e}")
            return False

    def add_lesson(self, lesson: Dict[str, Any]) -> str:
        """Add a lesson learned to the lessons namespace."""
        return self.lessons.add_lesson(lesson)

    def find_similar_lessons(self, query: str) -> List[Dict[str, Any]]:
        """Find lessons matching the given query."""
        return self.lessons.find_similar_lessons(query)

    def mark_verified(self, id: str, verified: bool = True) -> bool:
        """Mark a lesson as verified."""
        return self.lessons.mark_verified(id, verified)


# Export global memory manager instance
memory_manager = MemoryManager()
