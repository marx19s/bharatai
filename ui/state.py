"""
=================================================
BharatAI - UI State Manager
=================================================
"""

import streamlit as st
from typing import Dict, Any, Optional


class UIStateManager:
    """
    Manages session-persisted UI state parameters for the BharatAI dashboard.
    """

    def __init__(self):
        # Initialize default session values if not present
        if "selected_project" not in st.session_state:
            st.session_state["selected_project"] = None
        if "selected_department" not in st.session_state:
            st.session_state["selected_department"] = None
        if "selected_agent" not in st.session_state:
            st.session_state["selected_agent"] = None
        if "refresh_interval" not in st.session_state:
            st.session_state["refresh_interval"] = 5
        if "theme" not in st.session_state:
            st.session_state["theme"] = "dark"
        if "filters" not in st.session_state:
            st.session_state["filters"] = {}

    @property
    def selected_project(self) -> Optional[str]:
        return st.session_state["selected_project"]

    @selected_project.setter
    def selected_project(self, val: Optional[str]) -> None:
        st.session_state["selected_project"] = val

    @property
    def selected_department(self) -> Optional[str]:
        return st.session_state["selected_department"]

    @selected_department.setter
    def selected_department(self, val: Optional[str]) -> None:
        st.session_state["selected_department"] = val

    @property
    def selected_agent(self) -> Optional[str]:
        return st.session_state["selected_agent"]

    @selected_agent.setter
    def selected_agent(self, val: Optional[str]) -> None:
        st.session_state["selected_agent"] = val

    @property
    def refresh_interval(self) -> int:
        return st.session_state["refresh_interval"]

    @refresh_interval.setter
    def refresh_interval(self, val: int) -> None:
        st.session_state["refresh_interval"] = val

    @property
    def theme(self) -> str:
        return st.session_state["theme"]

    @theme.setter
    def theme(self, val: str) -> None:
        st.session_state["theme"] = val

    @property
    def filters(self) -> Dict[str, Any]:
        return st.session_state["filters"]

    @filters.setter
    def filters(self, val: Dict[str, Any]) -> None:
        st.session_state["filters"] = val
