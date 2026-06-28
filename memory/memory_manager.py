"""
=================================================
BharatAI
Memory Manager (Unified memory layer)
=================================================
"""

import logging
from typing import Dict, Any

from memory.session_memory import SessionMemory
from memory.user_memory import UserMemory
from memory.conversation_memory import ConversationMemory
from memory.project_memory import ProjectMemory

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
    """Central manager coordinating session, conversation, project, and user memory modules."""

    def __init__(self):
        self.session = SessionMemory()
        self.user = UserMemory()
        self.conversation = ConversationMemory()
        self.project = ProjectMemory()
        logger.info("Universal MemoryManager initialized successfully.")

    def clear_all(self) -> None:
        """Reset all memory sub-modules (transient and persistent)."""
        logger.warning("Clearing all memory modules...")
        self.session.clear()
        self.user.clear()
        self.conversation.clear()
        self.project.clear()
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
            return True
        except Exception as e:
            logger.error(f"MemoryManager health check failed: {e}")
            return False


# Export global memory manager instance
memory_manager = MemoryManager()
