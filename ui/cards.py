"""
=================================================
BharatAI - Department Cards UI Component
=================================================
"""

import time
import streamlit as st
from typing import Dict, Any

from ui.base_component import BaseComponent
from ui.state import UIStateManager
from ui.layout import DashboardLayoutManager


class DepartmentCardsComponent(BaseComponent):
    """
    Renders live department status cards dynamically based on API payloads.
    """

    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        departments = data.get("departments", [])
        if not departments:
            st.warning("No departments registered.")
            return

        st.subheader("🏢 Department status cards")

        # Dynamically generate grid columns based on department count
        cols = DashboardLayoutManager.create_department_grid(len(departments))

        for idx, dept in enumerate(departments):
            name = dept.get("name", "Unknown")
            status = dept.get("status", "Idle")
            task = dept.get("current_task", "None")
            progress = dept.get("progress", 0)
            last_update = dept.get("last_update", 0.0)

            # Map status strings to color classes
            status_lower = status.lower()
            if status_lower in ["working", "busy"]:
                color_class = "status-working"
            elif status_lower == "error":
                color_class = "status-error"
            else:
                color_class = "status-idle"

            # Parse last update timestamp
            try:
                ago = max(0, int(time.time() - last_update))
                time_str = f"{ago}s ago" if ago < 60 else f"{ago//60}m ago"
            except Exception:
                time_str = "N/A"

            # Render styled card using HTML glassmorphism
            with cols[idx]:
                st.markdown(
                    f"""
                    <div class='glass-card'>
                        <h4>{name}</h4>
                        <div class='metric-label'>STATUS</div>
                        <div style='margin-bottom: 0.5rem;'>
                            <span class='{color_class}' style='font-weight: bold;'>● {status}</span>
                        </div>
                        <div class='metric-label'>CURRENT TASK</div>
                        <div style='font-size: 0.9rem; font-weight: 500; height: 38px; overflow: hidden; text-overflow: ellipsis; white-space: normal; line-height: 1.1;'>
                            {task}
                        </div>
                        <div style='margin-top: 0.5rem;'>
                            <div class='metric-label'>PROGRESS ({progress}%)</div>
                            <div style='background-color: rgba(255,255,255,0.05); border-radius: 4px; height: 6px;'>
                                <div style='background-color: #38bdf8; width: {progress}%; height: 6px; border-radius: 4px;'></div>
                            </div>
                        </div>
                        <div style='margin-top: 0.5rem; text-align: right;'>
                            <small style='color: #64748b; font-size: 0.75rem;'>Updated: {time_str}</small>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
