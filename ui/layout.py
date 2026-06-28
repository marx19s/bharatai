"""
=================================================
BharatAI - Dashboard Layout Manager
=================================================
"""

import streamlit as st
from typing import Tuple, List, Any


class DashboardLayoutManager:
    """
    Manages grid structures, responsive sizing, and container allocation
    for all dashboard UI modules.
    """

    @staticmethod
    def create_department_grid(count: int) -> List[Any]:
        """Generate dynamic columns to display department status cards."""
        return st.columns(max(1, count))

    @staticmethod
    def create_kanban_grid(count: int = 4) -> List[Any]:
        """Generate columns to display the Kanban board."""
        return st.columns(count)

    @staticmethod
    def create_lower_grid() -> Tuple[Any, Any]:
        """
        Split the lower section into two columns:
        Left for Agent Table, Right for Notifications.
        """
        col_agent, col_notification = st.columns([3, 2])
        return col_agent, col_notification
