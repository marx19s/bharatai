"""
=================================================
BharatAI - Agent Control Center UI Component
=================================================
"""

import time
import streamlit as st
from typing import Dict, Any

from ui.base_component import BaseComponent
from ui.state import UIStateManager
from company.control_center import ControlCenter


class AgentControlCenterComponent(BaseComponent):
    """
    Modular control dashboard for pausing, resuming, stopping, and restarting
    agents, adjusting scheduler queues, and viewing agent details and memory.
    """

    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        st.subheader("🛠️ Agent Control Center")

        # Instantiate mutation controller
        controller = ControlCenter()

        # Retrieve agents list from dashboard data
        agents = data.get("agents", [])
        if not agents:
            st.warning("No active agents found.")
            return

        agent_names = [a.get("name") for a in agents]

        # ----------------------------------------------------
        # 1. Agent Selection & Details Panel
        # ----------------------------------------------------
        col_agent_select, col_agent_details = st.columns([1, 2])

        with col_agent_select:
            selected_agent_name = st.selectbox(
                "Select Agent to Monitor/Control",
                options=agent_names,
                key="control_center_agent_select"
            )

        # Retrieve detailed stats using OfficeAPI (read-only query)
        from company.office_api import OfficeAPI
        api = OfficeAPI()
        agent_stats = api.get_agent_stats(selected_agent_name)

        selected_agent = next((a for a in agents if a.get("name") == selected_agent_name), {})
        status = selected_agent.get("status", "Idle")
        current_task = selected_agent.get("current_task", "None")
        dept = selected_agent.get("department", "Operations")

        # Map status to colors
        status_lower = status.lower()
        if status_lower in ["working", "busy"]:
            status_color = "green"
        elif status_lower == "paused":
            status_color = "orange"
        elif status_lower == "stopped":
            status_color = "gray"
        elif status_lower == "error":
            status_color = "red"
        else:
            status_color = "blue"

        with col_agent_details:
            st.markdown(
                f"""
                <div class='glass-card' style='padding: 1.2rem; margin-bottom: 1rem;'>
                    <h3 style='margin-top:0;'>🤖 Agent: {selected_agent_name.capitalize()}</h3>
                    <p style='margin: 0.2rem 0;'><b>Department:</b> {dept} | <b>Status:</b> <span style='color:{status_color}; font-weight:bold;'>● {status}</span></p>
                    <p style='margin: 0.2rem 0;'><b>Current Task:</b> {current_task}</p>
                    <div style='display: flex; gap: 1rem; margin-top: 0.8rem;'>
                        <div style='flex: 1; text-align: center; background: rgba(255,255,255,0.03); padding: 0.5rem; border-radius: 4px;'>
                            <small style='color:#94a3b8;'>QUEUE</small>
                            <h4 style='margin:0; color:#38bdf8;'>{agent_stats["queue_length"]}</h4>
                        </div>
                        <div style='flex: 1; text-align: center; background: rgba(255,255,255,0.03); padding: 0.5rem; border-radius: 4px;'>
                            <small style='color:#94a3b8;'>COMPLETED</small>
                            <h4 style='margin:0; color:#38bdf8;'>{agent_stats["tasks_completed"]}</h4>
                        </div>
                        <div style='flex: 1; text-align: center; background: rgba(255,255,255,0.03); padding: 0.5rem; border-radius: 4px;'>
                            <small style='color:#94a3b8;'>SUCCESS</small>
                            <h4 style='margin:0; color:#38bdf8;'>{agent_stats["success_rate"]}</h4>
                        </div>
                        <div style='flex: 1; text-align: center; background: rgba(255,255,255,0.03); padding: 0.5rem; border-radius: 4px;'>
                            <small style='color:#94a3b8;'>AVG TIME</small>
                            <h4 style='margin:0; color:#38bdf8;'>{agent_stats["avg_execution_time"]}</h4>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ----------------------------------------------------
        # 2. Agent Controls
        # ----------------------------------------------------
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown("##### Agent Workload Controls")
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("⏸️ Pause Agent", key=f"btn_pause_{selected_agent_name}", use_container_width=True):
                    controller.pause_agent(selected_agent_name)
                    st.success(f"Agent {selected_agent_name} paused.")
                    time.sleep(0.5)
                    st.rerun()

            with btn_col2:
                if st.button("▶️ Resume Agent", key=f"btn_resume_{selected_agent_name}", use_container_width=True):
                    controller.resume_agent(selected_agent_name)
                    st.success(f"Agent {selected_agent_name} resumed.")
                    time.sleep(0.5)
                    st.rerun()

            btn_col3, btn_col4 = st.columns(2)
            with btn_col3:
                # Requires confirmation before destructive actions
                confirm_stop = st.checkbox("Confirm Stop", key=f"confirm_stop_{selected_agent_name}", value=False)
                if st.button("🛑 Stop Agent", key=f"btn_stop_{selected_agent_name}", use_container_width=True, disabled=not confirm_stop):
                    controller.stop_agent(selected_agent_name)
                    st.success(f"Agent {selected_agent_name} stopped.")
                    time.sleep(0.5)
                    st.rerun()

            with btn_col4:
                if st.button("🔄 Restart Agent", key=f"btn_restart_{selected_agent_name}", use_container_width=True):
                    controller.restart_agent(selected_agent_name)
                    st.success(f"Agent {selected_agent_name} restarted.")
                    time.sleep(0.5)
                    st.rerun()

        # ----------------------------------------------------
        # 3. Scheduler Controls
        # ----------------------------------------------------
        with col_c2:
            st.markdown("##### Scheduler Queue Mutator")
            queue = data.get("scheduler_queue", [])
            if not queue:
                st.info("No active tasks in scheduler queue.")
            else:
                job_ids = [j.get("id") for j in queue]
                selected_job_id = st.selectbox("Select Task Job", options=job_ids, key="control_center_job_select")
                selected_job = next((j for j in queue if j.get("id") == selected_job_id), {})

                st.markdown(
                    f"**Task ID:** `{selected_job.get('task_id')}` | **Agent:** `{selected_job.get('assigned_agent')}` | **Status:** `{selected_job.get('status')}`"
                )

                op_col1, op_col2 = st.columns(2)
                with op_col1:
                    new_priority = st.selectbox(
                        "Change Priority",
                        options=["Low", "Medium", "High"],
                        index=["Low", "Medium", "High"].index(selected_job.get("priority", "Medium")),
                        key="control_center_priority_select"
                    )
                    if st.button("Apply Priority", key="btn_apply_priority", use_container_width=True):
                        controller.change_priority(selected_job_id, new_priority)
                        st.success("Priority updated.")
                        time.sleep(0.5)
                        st.rerun()

                with op_col2:
                    new_agent = st.selectbox("Reassign Agent", options=agent_names, key="control_center_reassign_agent")
                    if st.button("Move Task", key="btn_move_task", use_container_width=True):
                        controller.move_task(selected_job_id, new_agent)
                        st.success("Task reassigned.")
                        time.sleep(0.5)
                        st.rerun()

                sched_col1, sched_col2 = st.columns(2)
                with sched_col1:
                    is_failed = selected_job.get("status") == "Failed"
                    if st.button("🔄 Retry Task", key="btn_retry_task", use_container_width=True, disabled=not is_failed):
                        controller.retry_task(selected_job_id)
                        st.success("Task re-queued.")
                        time.sleep(0.5)
                        st.rerun()

                with sched_col2:
                    confirm_cancel = st.checkbox("Confirm Cancel", key=f"confirm_cancel_{selected_job_id}", value=False)
                    if st.button("❌ Cancel Task", key="btn_cancel_task", use_container_width=True, disabled=not confirm_cancel):
                        controller.cancel_task(selected_job_id)
                        st.success("Task cancelled.")
                        time.sleep(0.5)
                        st.rerun()

        st.write("---")

        # ----------------------------------------------------
        # 4. Memory & Actions Timeline Panels
        # ----------------------------------------------------
        col_memory, col_timeline = st.columns([3, 2])

        with col_memory:
            st.markdown("##### 🧠 Agent Memory View")
            memory_data = data.get("agent_memory", {})
            tab_lessons, tab_bugs, tab_reviews, tab_fixes = st.tabs(
                ["📚 Recent Lessons", "🐛 Previous Bugs", "🔍 Recent Reviews", "♻️ Previous Fixes"]
            )

            with tab_lessons:
                lessons = memory_data.get("recent_lessons", [])
                if not lessons:
                    st.write("No recent lessons found.")
                for l in lessons:
                    st.markdown(f"**{l['title']}**\n*{l['details']}*")

            with tab_bugs:
                bugs = memory_data.get("previous_bugs", [])
                if not bugs:
                    st.write("No previous bug reports found.")
                for b in bugs:
                    st.markdown(f"**{b['title']}**\n*{b['details']}*")

            with tab_reviews:
                reviews = memory_data.get("recent_reviews", [])
                if not reviews:
                    st.write("No recent reviews found.")
                for r in reviews:
                    st.markdown(f"**{r['title']}**\n*{r['details']}*")

            with tab_fixes:
                fixes = memory_data.get("previous_fixes", [])
                if not fixes:
                    st.write("No previous reusable fixes found.")
                for f in fixes:
                    st.markdown(f"**{f['title']}**\n*{f['details']}*")

        with col_timeline:
            st.markdown("##### 🕒 Recent Actions Timeline")
            timeline = data.get("timeline", [])
            if not timeline:
                st.write("No actions recorded in timeline.")
            else:
                for action in timeline[:20]:
                    timestamp = action.get("timestamp", 0.0)
                    time_str = time.strftime('%H:%M:%S', time.localtime(timestamp))
                    emoji = action.get("emoji", "⚙️")
                    label = action.get("label", "Action")
                    agent = action.get("agent", "System")
                    task_info = action.get("task", "")
                    
                    st.markdown(
                        f"""
                        <div style='background: rgba(255,255,255,0.02); padding: 0.5rem; margin-bottom: 0.4rem; border-radius: 4px; border-left: 3px solid #38bdf8;'>
                            <small style='color: #64748b;'>{time_str}</small> | <b>{emoji} {label}</b> by <i>{agent}</i>
                            <div style='font-size: 0.85rem; color: #94a3b8; margin-top: 0.2rem;'>{task_info}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
