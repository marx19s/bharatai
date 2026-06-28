"""
=================================================
BharatAI
Company Memory Engine (Persistent Namespaces & Lessons Learned)
=================================================
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

from config.settings import DATA_DIR

logger = logging.getLogger("bharatai.memory.company")


class CompanyMemoryNamespace:
    """JSON-backed persistent namespace for company memory."""

    def __init__(self, namespace_name: str, file_path: Optional[Path] = None):
        self.namespace_name = namespace_name
        self.file_path = file_path or (DATA_DIR / f"company_memory_{namespace_name}.json")
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load data from JSON file on disk."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.info(f"Loaded namespace '{self.namespace_name}' from: {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load namespace '{self.namespace_name}' from {self.file_path}: {e}")
                self._data = {}
        else:
            self._data = {}

    def save(self) -> None:
        """Save data to JSON file on disk."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            logger.debug(f"Saved namespace '{self.namespace_name}' to: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save namespace '{self.namespace_name}' to {self.file_path}: {e}")

    def add(self, item: Dict[str, Any]) -> str:
        """Add a new item to the namespace. Generates an ID if not present."""
        item_id = item.get("id")
        if not item_id:
            item_id = uuid.uuid4().hex
        new_item = item.copy()
        new_item["id"] = item_id
        self._data[item_id] = new_item
        self.save()
        return item_id

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an item by its ID."""
        return self._data.get(id)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search items in the namespace where the query matches any field value."""
        query_lower = query.lower()
        results = []
        for item in self._data.values():
            if any(query_lower in str(v).lower() for v in item.values()):
                results.append(item)
        return results

    def update(self, id: str, item: Dict[str, Any]) -> bool:
        """Update an existing item by its ID."""
        if id in self._data:
            updated_item = item.copy()
            updated_item["id"] = id
            self._data[id] = updated_item
            self.save()
            return True
        return False

    def delete(self, id: str) -> bool:
        """Delete an item from the namespace by its ID."""
        if id in self._data:
            del self._data[id]
            self.save()
            return True
        return False

    def clear(self) -> None:
        """Clear all data in the namespace."""
        self._data.clear()
        self.save()


class LessonsNamespace(CompanyMemoryNamespace):
    """Specialized namespace for lessons learned containing specific API helper methods."""

    def __init__(self, file_path: Optional[Path] = None):
        super().__init__("lessons", file_path=file_path)

    def add_lesson(self, lesson: Dict[str, Any]) -> str:
        """Add a lesson learned. Defaults 'verified' to False."""
        lesson_data = lesson.copy()
        if "verified" not in lesson_data:
            lesson_data["verified"] = False
        return self.add(lesson_data)

    def find_similar_lessons(self, query: str) -> List[Dict[str, Any]]:
        """Find lessons containing matching words, ordered by relevance (number of overlapping words)."""
        query_words = set(query.lower().split())
        if not query_words:
            return []
        
        scored_lessons = []
        for item in self._data.values():
            # Join text values from lesson to check word overlap
            text_content = " ".join(str(v).lower() for v in item.values() if isinstance(v, (str, int, float)))
            item_words = set(text_content.split())
            overlap = len(query_words.intersection(item_words))
            if overlap > 0:
                scored_lessons.append((overlap, item))
                
        # Sort by overlap score descending
        scored_lessons.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_lessons]

    def mark_verified(self, id: str, verified: bool = True) -> bool:
        """Mark a lesson as verified."""
        item = self.get(id)
        if item is not None:
            item["verified"] = verified
            return self.update(id, item)
        return False
