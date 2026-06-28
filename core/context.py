"""
=================================================
BharatAI
Centralized Execution Context
=================================================
"""

import threading
import logging
from typing import Dict, Any, List, Optional

from config.settings import LOG_FILE, LOG_LEVEL

logger = logging.getLogger("bharatai.core.context")
if not logger.handlers:
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass


class ExecutionContext:
    """Centralized, thread-safe execution context for tracking active system goals and parameters."""

    def __init__(self, goal: str):
        self.goal = goal
        self.variables: Dict[str, Any] = {}
        self.subtasks: List[Dict[str, Any]] = []
        self.active_agent: Optional[str] = None
        self.logs: List[str] = []
        self._lock = threading.Lock()
        logger.info(f"ExecutionContext created for goal: '{self.goal[:50]}...'")

    def set_variable(self, key: str, value: Any) -> None:
        """Store a shared variable within the workspace context."""
        with self._lock:
            self.variables[key] = value
            logger.info(f"Context variable set: '{key}'")

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Retrieve a shared variable from the workspace context."""
        with self._lock:
            return self.variables.get(key, default)

    def add_subtask(self, subtask: str, agent: str, status: str = "pending") -> int:
        """Register a subtask to be executed, returning its index."""
        with self._lock:
            idx = len(self.subtasks)
            self.subtasks.append({
                "index": idx,
                "subtask": subtask,
                "agent": agent,
                "status": status,
                "result": None
            })
            logger.info(f"Registered subtask {idx} for agent '{agent}': '{subtask[:50]}'")
            return idx

    def update_subtask(self, idx: int, status: str, result: Any = None) -> None:
        """Update status and output of a registered subtask."""
        with self._lock:
            if 0 <= idx < len(self.subtasks):
                self.subtasks[idx]["status"] = status
                if result is not None:
                    self.subtasks[idx]["result"] = result
                logger.info(f"Subtask {idx} updated to status '{status}'")
            else:
                logger.warning(f"Attempted to update subtask with out-of-bounds index: {idx}")

    def log_step(self, message: str) -> None:
        """Log a high-level orchestration step message inside this execution run."""
        with self._lock:
            self.logs.append(message)
            logger.info(f"[Execution Log] {message}")

    def get_subtasks(self) -> List[Dict[str, Any]]:
        """Retrieve full details of all execution subtasks."""
        with self._lock:
            return list(self.subtasks)

    def get_logs(self) -> List[str]:
        """Retrieve full execution log trace."""
        with self._lock:
            return list(self.logs)
