"""
=================================================
BharatAI - Sidebar UI Component
=================================================
"""

import streamlit as st
from typing import Dict, Any

from ui.base_component import BaseComponent
from ui.state import UIStateManager


class SidebarComponent(BaseComponent):
    """
    Renders left sidebar metadata including Company Logo, Status, Uptime,
    and summary metrics.
    """

    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        stats = data.get("statistics", {})
        
        # 1. Company Logo & Branding
        st.sidebar.markdown(
            """
            <div style='text-align: center; padding-bottom: 1.5rem;'>
                <h2 style='color: #38bdf8; margin-bottom: 0.2rem;'>⚡ BHARAT AI</h2>
                <small style='color: #64748b;'>Command Center v1.1</small>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.sidebar.write("---")

        # 2. Company Status Metric
        status = data.get("status", "Working")
        status_color = "#4ade80" if status.lower() == "working" else "#f87171"
        st.sidebar.markdown(
            f"""
            <div class='glass-card' style='padding: 0.8rem; text-align: center;'>
                <div class='metric-label'>COMPANY STATUS</div>
                <div style='font-size: 1.25rem; font-weight: bold; color: {status_color};'>{status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 3. Uptime
        uptime_val = stats.get("uptime", 0.0)
        # Format uptime nicely: Hh Mm Ss
        try:
            uptime_seconds = int(float(uptime_val))
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            uptime_str = f"{hours}h {minutes}m {seconds}s"
        except Exception:
            uptime_str = f"{uptime_val}s"

        st.sidebar.markdown(
            f"""
            <div class='glass-card' style='padding: 0.8rem;'>
                <div class='metric-label'>SYSTEM UPTIME</div>
                <div class='metric-value'>{uptime_str}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 4. Summary metrics: Active Projects, Active Agents
        projects = data.get("projects", [])
        active_projects_count = sum(1 for p in projects if p.get("status") == "Active")
        active_agents = stats.get("active_agents", 0)

        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class='glass-card' style='padding: 0.8rem; text-align: center;'>
                    <div class='metric-label'>ACTIVE PROJS</div>
                    <div class='metric-value' style='color: #38bdf8;'>{active_projects_count}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class='glass-card' style='padding: 0.8rem; text-align: center;'>
                    <div class='metric-label'>ACTIVE AGENTS</div>
                    <div class='metric-value' style='color: #fbbf24;'>{active_agents}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        st.sidebar.write("---")
        
        # User interactive config options (refresh interval)
        refresh = st.sidebar.slider("Refresh rate (sec)", min_value=2, max_value=30, value=state.refresh_interval)
        if refresh != state.refresh_interval:
            state.refresh_interval = refresh
