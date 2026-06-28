"""
=================================================
BharatAI
Project Memory (Workspace context and metadata)
=================================================
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from config.settings import DATA_DIR, LOG_FILE, LOG_LEVEL

logger = logging.getLogger("bharatai.memory.project")
if not logger.handlers:
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass


class ProjectMemory:
    """Persistent storage for project workspace context details, facts, and settings."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or (DATA_DIR / "project_memory.json")
        self._data: Dict[str, Any] = {
            "facts": [],
            "metadata": {}
        }
        self.load()

    def load(self) -> None:
        """Load project facts and metadata from disk."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                # Safeguard schema properties
                if "facts" not in self._data:
                    self._data["facts"] = []
                if "metadata" not in self._data:
                    self._data["metadata"] = {}
                logger.info(f"Project memory loaded from: {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load project memory: {e}")
                self._data = {"facts": [], "metadata": {}}
        else:
            self._data = {"facts": [], "metadata": {}}

    def save(self) -> None:
        """Save project facts and metadata to disk."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            logger.debug(f"Project memory saved to: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save project memory: {e}")

    def add_fact(self, fact: str) -> None:
        """Add a factual context statement about the project workspace."""
        if fact not in self._data["facts"]:
            self._data["facts"].append(fact)
            self.save()
            logger.info(f"Added new fact to project memory: '{fact}'")

    def get_facts(self) -> List[str]:
        """Retrieve all registered facts."""
        return self._data.get("facts", [])

    def set_metadata(self, key: str, value: Any) -> None:
        """Store metadata key-value parameters."""
        self._data["metadata"][key] = value
        self.save()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Retrieve metadata parameter."""
        return self._data.get("metadata", {}).get(key, default)

    def clear(self) -> None:
        """Reset project workspace memory."""
        self._data = {"facts": [], "metadata": {}}
        self.save()
