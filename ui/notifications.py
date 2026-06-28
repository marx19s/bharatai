"""
=================================================
BharatAI - Notifications UI Component
=================================================
"""

import time
import streamlit as st
from typing import Dict, Any

from ui.base_component import BaseComponent
from ui.state import UIStateManager


class NotificationComponent(BaseComponent):
    """
    Renders a live event stream of completed jobs, warnings, and failures.
    """

    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        notifications = data.get("notifications", [])
        
        st.subheader("🔔 Activity Stream")

        if not notifications:
            st.info("No recent notifications recorded.")
            return

        for note in notifications:
            category = note.get("type", "info")
            msg = note.get("message", "")
            timestamp = note.get("timestamp", 0.0)

            # Format ago
            try:
                ago = max(0, int(time.time() - timestamp))
                time_str = f"{ago}s ago" if ago < 60 else f"{ago//60}m ago"
            except Exception:
                time_str = "N/A"

            # Style by category
            if category == "completed":
                bg = "rgba(74, 222, 128, 0.08)"
                border_color = "rgba(74, 222, 128, 0.3)"
                bullet = "🟢"
            elif category == "failure":
                bg = "rgba(248, 113, 113, 0.08)"
                border_color = "rgba(248, 113, 113, 0.3)"
                bullet = "🔴"
            elif category == "telegram":
                bg = "rgba(56, 189, 248, 0.08)"
                border_color = "rgba(56, 189, 248, 0.3)"
                bullet = "✈️"
            else:
                bg = "rgba(251, 191, 36, 0.08)"
                border_color = "rgba(251, 191, 36, 0.3)"
                bullet = "⚠️"

            st.markdown(
                f"""
                <div style='background: {bg}; border: 1px solid {border_color}; border-radius: 6px; padding: 0.6rem; margin-bottom: 0.4rem; display: flex; justify-content: space-between; align-items: center;'>
                    <div style='font-size: 0.82rem; color: #f8fafc; font-weight: 500;'>
                        <span style='margin-right: 0.4rem;'>{bullet}</span> {msg}
                    </div>
                    <small style='color: #64748b; font-size: 0.72rem; white-space: nowrap; margin-left: 0.8rem;'>{time_str}</small>
                </div>
                """,
                unsafe_allow_html=True
            )
