"""
=================================================
BharatAI - Kanban Board UI Component
=================================================
"""

import streamlit as st
from typing import Dict, Any, List

from ui.base_component import BaseComponent
from ui.state import UIStateManager
from ui.layout import DashboardLayoutManager


class KanbanComponent(BaseComponent):
    """
    Renders Project tasks partitioned into columns: Todo, In Progress, Review, and Done.
    """

    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        projects = data.get("projects", [])
        if not projects:
            st.info("No active projects found to render Kanban board.")
            return

        st.subheader("📋 Project Kanban Board")

        # Project Selector Dropdown to filter Kanban tasks
        proj_names = [p["name"] for p in projects]
        selected_name = st.selectbox(
            "Select Project",
            proj_names,
            index=0 if state.selected_project is None or state.selected_project not in proj_names else proj_names.index(state.selected_project)
        )
        state.selected_project = selected_name

        # Get tasks for selected project
        project = next(p for p in projects if p["name"] == selected_name)
        tasks = project.get("tasks", {})

        # Categorize tasks into Kanban states
        todo_tasks: List[Dict[str, Any]] = []
        progress_tasks: List[Dict[str, Any]] = []
        review_tasks: List[Dict[str, Any]] = []
        done_tasks: List[Dict[str, Any]] = []

        for task in tasks.values():
            status = task.get("status", "Pending")
            if status == "Pending":
                todo_tasks.append(task)
            elif status == "InProgress":
                progress_tasks.append(task)
            elif status in ["Review", "Reviewing"]:
                review_tasks.append(task)
            elif status in ["Completed", "Failed"]:
                done_tasks.append(task)

        # Draw Columns
        cols = DashboardLayoutManager.create_kanban_grid(4)

        columns_data = [
            ("📝 Todo", todo_tasks, "#38bdf8"),
            ("🏃 In Progress", progress_tasks, "#fbbf24"),
            ("👀 Review", review_tasks, "#a855f7"),
            ("✅ Done", done_tasks, "#4ade80")
        ]

        for idx, (title, task_list, color) in enumerate(columns_data):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div style='background-color: rgba(30, 41, 59, 0.4); border-top: 3px solid {color}; border-radius: 8px; padding: 0.8rem; min-height: 250px;'>
                        <h5 style='color: white; margin-top: 0; margin-bottom: 0.8rem;'>{title} ({len(task_list)})</h5>
                    """,
                    unsafe_allow_html=True
                )

                if not task_list:
                    st.markdown("<p style='color: #64748b; font-size: 0.85rem; text-align: center; padding-top: 2rem;'>Empty</p>", unsafe_allow_html=True)
                else:
                    for task in task_list:
                        assigned = task.get("assigned_agent", "None")
                        priority = task.get("priority", "Medium")
                        p_color = "#f87171" if priority == "High" else ("#fbbf24" if priority == "Medium" else "#38bdf8")
                        
                        task_status = task.get("status", "Pending")
                        status_bullet = "●"
                        if task_status == "Failed":
                            status_bullet = "🔴"
                        elif task_status == "Completed":
                            status_bullet = "🟢"

                        st.markdown(
                            f"""
                            <div style='background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 0.6rem; margin-bottom: 0.5rem;'>
                                <div style='font-size: 0.85rem; font-weight: bold; color: #f8fafc; margin-bottom: 0.2rem;'>
                                    {status_bullet} {task.get('title', 'Task')}
                                </div>
                                <div style='font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.4rem;'>
                                    {task.get('description', '')[:60]}...
                                </div>
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <span style='background-color: rgba(255,255,255,0.05); border-radius: 4px; padding: 1px 4px; font-size: 0.7rem; color: #38bdf8;'>
                                        👤 {assigned}
                                    </span>
                                    <span style='color: {p_color}; font-size: 0.7rem; font-weight: bold;'>
                                        ▲ {priority}
                                    </span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown("</div>", unsafe_allow_html=True)
