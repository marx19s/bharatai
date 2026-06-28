"""
=================================================
BharatAI
Session Memory (Transient in-memory storage)
=================================================
"""

from typing import Dict, Any

class SessionMemory:
    """Transient, thread-safe in-memory storage for active session data."""
    def __init__(self):
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]

    def clear(self) -> None:
        self._data.clear()
