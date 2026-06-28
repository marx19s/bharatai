"""
=================================================
BharatAI
Conversation Memory (Persistent chat history)
=================================================
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from config.settings import DATA_DIR, LOG_FILE, LOG_LEVEL

logger = logging.getLogger("bharatai.memory.conversation")
if not logger.handlers:
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass


class ConversationMemory:
    """Persistent chat transaction log storage, backed by local JSON file."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or (DATA_DIR / "conversation_memory.json")
        self._history: List[Dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Load conversation log history from disk."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
                logger.info(f"Conversation memory loaded from: {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load conversation memory: {e}")
                self._history = []
        else:
            self._history = []

    def save(self) -> None:
        """Save conversation log history to disk."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=4, ensure_ascii=False)
            logger.debug(f"Conversation memory saved to: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save conversation memory: {e}")

    def add_message(self, role: str, content: str, sender: Optional[str] = None) -> None:
        """Append a message to the history and save it."""
        self._history.append({
            "role": role,
            "content": content,
            "sender": sender or role
        })
        self.save()

    def get_messages(self) -> List[Dict[str, Any]]:
        """Retrieve full conversation logs."""
        return self._history

    def clear(self) -> None:
        """Reset conversation logs."""
        self._history.clear()
        self.save()
