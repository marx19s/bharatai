"""
=================================================
BharatAI
User Memory (Persistent configuration and preferences)
=================================================
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from config.settings import DATA_DIR, LOG_FILE, LOG_LEVEL

logger = logging.getLogger("bharatai.memory.user")
if not logger.handlers:
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass


class UserMemory:
    """Persistent storage for user preferences and configurations, backed by local JSON file."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or (DATA_DIR / "user_memory.json")
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load user configurations from disk."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.info(f"User memory loaded from: {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load user memory: {e}")
                self._data = {}
        else:
            self._data = {}

    def save(self) -> None:
        """Save user configurations to disk."""
        try:
            # Ensure the directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            logger.debug(f"User memory saved to: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save user memory: {e}")

    def set(self, key: str, value: Any) -> None:
        """Set a user configuration parameter."""
        self._data[key] = value
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a user configuration parameter."""
        return self._data.get(key, default)

    def delete(self, key: str) -> None:
        """Delete a user configuration parameter."""
        if key in self._data:
            del self._data[key]
            self.save()

    def clear(self) -> None:
        """Reset user memory settings."""
        self._data.clear()
        self.save()
