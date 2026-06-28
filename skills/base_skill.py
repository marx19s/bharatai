"""
=================================================
BharatAI
Base Skill Interface
=================================================
"""

from abc import ABC, abstractmethod
from typing import Any

class BaseSkill(ABC):
    """Abstract Base Class for all reusable agent skills in BharatAI."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the skill (e.g. 'web_search')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief summary detailing what the skill accomplishes."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Primary execution block containing skill logic."""
        pass
