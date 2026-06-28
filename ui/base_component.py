"""
=================================================
BharatAI - Base Component Lifecycle Class
=================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from ui.state import UIStateManager


class BaseComponent(ABC):
    """
    Abstract Base class for all dashboard UI components.
    Ensures consistent rendering lifecycle across all modular UI blocks.
    """

    @abstractmethod
    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        """
        Renders the component using the provided single-refresh data snapshot
        and state manager interface.
        """
        pass
