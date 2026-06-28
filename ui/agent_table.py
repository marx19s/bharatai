"""
=================================================
BharatAI - Agent Monitor UI Component
=================================================
"""

import streamlit as st
from typing import Dict, Any

from ui.base_component import BaseComponent
from ui.state import UIStateManager


class AgentTableComponent(BaseComponent):
    """
    Renders a live table monitoring agent status, current workload,
    and task progress.
    """

    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        agents = data.get("agents", [])
        if not agents:
            st.info("No agents currently registered.")
            return

        st.subheader("🤖 Agent Monitor")

        # HTML Table styling for a premium dark slate look
        table_html = """
        <table style='width: 100%; border-collapse: collapse; background: rgba(30, 41, 59, 0.4); border-radius: 8px; overflow: hidden;'>
            <thead>
                <tr style='background: rgba(15, 23, 42, 0.6); border-bottom: 1px solid rgba(255,255,255,0.08); text-align: left;'>
                    <th style='padding: 0.8rem; font-size: 0.85rem; color: #94a3b8;'>AGENT NAME</th>
                    <th style='padding: 0.8rem; font-size: 0.85rem; color: #94a3b8;'>DEPARTMENT</th>
                    <th style='padding: 0.8rem; font-size: 0.85rem; color: #94a3b8;'>STATUS</th>
                    <th style='padding: 0.8rem; font-size: 0.85rem; color: #94a3b8;'>CURRENT TASK</th>
                    <th style='padding: 0.8rem; font-size: 0.85rem; color: #94a3b8;'>MEMORY</th>
                </tr>
            </thead>
            <tbody>
        """

        for agent in agents:
            name = agent.get("name", "Unknown")
            dept = agent.get("department", "Operations")
            status = agent.get("status", "Idle")
            task = agent.get("current_task", "None")
            mem = agent.get("memory_usage", 100.0)

            # Determine status label color
            status_lower = status.lower()
            if status_lower == "working":
                bg = "rgba(74, 222, 128, 0.1)"
                fg = "#4ade80"
            elif status_lower == "error":
                bg = "rgba(248, 113, 113, 0.1)"
                fg = "#f87171"
            else:
                bg = "rgba(148, 163, 184, 0.1)"
                fg = "#94a3b8"

            table_html += f"""
            <tr style='border-bottom: 1px solid rgba(255,255,255,0.04);'>
                <td style='padding: 0.8rem; font-size: 0.85rem; font-weight: bold; color: #f8fafc;'>👤 {name}</td>
                <td style='padding: 0.8rem; font-size: 0.85rem; color: #e2e8f0;'>{dept}</td>
                <td style='padding: 0.8rem; font-size: 0.85rem;'>
                    <span style='background: {bg}; color: {fg}; border-radius: 4px; padding: 2px 6px; font-weight: bold;'>
                        {status}
                    </span>
                </td>
                <td style='padding: 0.8rem; font-size: 0.85rem; color: #94a3b8; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>
                    {task}
                </td>
                <td style='padding: 0.8rem; font-size: 0.85rem; color: #38bdf8; font-weight: bold;'>{mem:.1f} MB</td>
            </tr>
            """

        table_html += "</tbody></table>"

        st.markdown(table_html, unsafe_allow_html=True)
