"""
=================================================
BharatAI - Live Activity Feed Component
=================================================
"""

import time
import threading
from collections import deque
from typing import Dict, Any, List, Optional
import streamlit as st

from ui.base_component import BaseComponent
from ui.state import UIStateManager


# ---------------------------------------------------------------------------
# ActivityFeedStore  (in-process ring-buffer, no backend modification)
# ---------------------------------------------------------------------------

class ActivityFeedStore:
    """
    Thread-safe ring-buffer holding the last MAX_EVENTS activity records.
    Populated by subscribing to the global EventBus; persisted to Company
    Memory via OfficeAPI helpers so the feed survives across refreshes.
    """

    MAX_EVENTS = 100

    # Event type → (emoji, label, status)
    EVENT_META: Dict[str, tuple] = {
        "ProjectCreated":     ("📁", "Project Created",      "info"),
        "TaskAssigned":       ("📋", "Task Assigned",        "info"),
        "JobStarted":         ("▶️",  "Job Started",          "running"),
        "JobCompleted":       ("✅", "Job Completed",        "success"),
        "JobFailed":          ("❌", "Job Failed",           "error"),
        "ExecutionStarted":   ("🚀", "Execution Started",    "running"),
        "ExecutionCompleted": ("🏁", "Execution Completed",  "success"),
        "TelegramSent":       ("✈️",  "Telegram Sent",        "info"),
        "Error":              ("🔴", "Error",                "error"),
        # Internal aliases emitted by agents
        "TaskStarted":        ("▶️",  "Task Started",         "running"),
        "TaskCompleted":      ("✅", "Task Completed",       "success"),
        "TaskFailed":         ("❌", "Task Failed",          "error"),
        "ExecutionFailed":    ("❌", "Execution Failed",     "error"),
        "ExecutionPaused":    ("⏸️",  "Execution Paused",     "warning"),
        "ExecutionResumed":   ("▶️",  "Execution Resumed",    "running"),
    }

    def __init__(self):
        self._lock = threading.Lock()
        self._events: deque = deque(maxlen=self.MAX_EVENTS)

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_event(self, event_type: str, sender: str,
                     payload: Optional[Dict[str, Any]] = None) -> None:
        """Add a new activity record derived from an EventBus event."""
        payload = payload or {}
        meta = self.EVENT_META.get(event_type, ("⚪", event_type, "info"))

        record = {
            "timestamp":  time.time(),
            "event_type": event_type,
            "emoji":      meta[0],
            "label":      meta[1],
            "status":     meta[2],
            "agent":      sender,
            "department": payload.get("department", _infer_dept(sender)),
            "task":       payload.get("task", payload.get("description", "—")),
            "duration":   payload.get("duration", payload.get("elapsed", None)),
            "error":      payload.get("error", None),
        }

        with self._lock:
            self._events.appendleft(record)   # newest first

    def ingest_raw(self, record: Dict[str, Any]) -> None:
        """Ingest a pre-built record dict (used when loading from memory)."""
        with self._lock:
            self._events.appendleft(record)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._events)[:limit]

    def count(self) -> int:
        with self._lock:
            return len(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

_DEPT_MAP = {
    "neo":          "CEO",
    "atlas":        "CEO",
    "developer":    "Engineering",
    "reviewer":     "Engineering",
    "bug_fixer":    "Engineering",
    "performance":  "Engineering",
    "qa":           "QA",
    "orion":        "Research",
    "research":     "Research",
    "sage":         "Research",
    "lumina":       "Operations",
    "echo":         "Operations",
}


def _infer_dept(agent_name: str) -> str:
    return _DEPT_MAP.get(agent_name.lower(), "Operations")


# ---------------------------------------------------------------------------
# ActivityFeedComponent  (Streamlit UI)
# ---------------------------------------------------------------------------

class ActivityFeedComponent(BaseComponent):
    """
    Renders the chronological live activity feed.
    Reads from the data dict key 'activity_feed' (a list of activity records)
    that is injected by dashboard.py from OfficeAPI.get_activity_feed().
    """

    # Status → colour palette
    _STATUS_STYLE: Dict[str, Dict[str, str]] = {
        "success": {"bg": "rgba(74, 222, 128, 0.08)",  "border": "rgba(74, 222, 128, 0.35)",  "badge": "#4ade80"},
        "running": {"bg": "rgba(56, 189, 248, 0.08)",  "border": "rgba(56, 189, 248, 0.35)",  "badge": "#38bdf8"},
        "error":   {"bg": "rgba(248, 113, 113, 0.08)", "border": "rgba(248, 113, 113, 0.35)", "badge": "#f87171"},
        "warning": {"bg": "rgba(251, 191, 36, 0.08)",  "border": "rgba(251, 191, 36, 0.35)",  "badge": "#fbbf24"},
        "info":    {"bg": "rgba(139, 92, 246, 0.08)",  "border": "rgba(139, 92, 246, 0.35)",  "badge": "#8b5cf6"},
    }

    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        st.subheader("📡 Live Activity Feed")

        events: List[Dict[str, Any]] = data.get("activity_feed", [])

        if not events:
            st.info("No recent activity.")
            return

        # Optional filter controls
        with st.expander("🔍 Filter", expanded=False):
            col_status, col_dept, col_agent = st.columns(3)

            all_statuses = sorted({e.get("status", "info") for e in events})
            all_depts    = sorted({e.get("department", "—") for e in events})
            all_agents   = sorted({e.get("agent", "—") for e in events})

            sel_status = col_status.multiselect("Status", all_statuses, key="af_status")
            sel_dept   = col_dept.multiselect("Department", all_depts,   key="af_dept")
            sel_agent  = col_agent.multiselect("Agent", all_agents,      key="af_agent")

        # Apply filters
        filtered = events
        if sel_status:
            filtered = [e for e in filtered if e.get("status") in sel_status]
        if sel_dept:
            filtered = [e for e in filtered if e.get("department") in sel_dept]
        if sel_agent:
            filtered = [e for e in filtered if e.get("agent") in sel_agent]

        if not filtered:
            st.warning("No events match the current filters.")
            return

        st.caption(f"Showing {len(filtered)} event(s) · newest first")

        for event in filtered:
            self._render_event_card(event)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _render_event_card(self, event: Dict[str, Any]) -> None:
        status = event.get("status", "info")
        style  = self._STATUS_STYLE.get(status, self._STATUS_STYLE["info"])

        emoji      = event.get("emoji", "⚪")
        label      = event.get("label", event.get("event_type", "Event"))
        agent      = event.get("agent", "—")
        department = event.get("department", "—")
        task       = event.get("task", "—")
        duration   = event.get("duration")
        error      = event.get("error")
        ts         = event.get("timestamp", 0.0)

        # Human-readable time-ago
        try:
            ago = max(0, int(time.time() - float(ts)))
            time_str = _format_ago(ago)
        except Exception:
            time_str = "N/A"

        # Duration badge
        dur_html = ""
        if duration is not None:
            try:
                dur_html = (
                    f"<span style='background:{style['badge']}22; color:{style['badge']}; "
                    f"border:1px solid {style['badge']}55; border-radius:4px; "
                    f"padding:1px 6px; font-size:0.70rem; margin-left:0.5rem;'>"
                    f"{float(duration):.2f}s</span>"
                )
            except Exception:
                pass

        # Error snippet
        error_html = ""
        if error:
            error_html = (
                f"<div style='margin-top:0.3rem; color:#f87171; font-size:0.73rem;'>"
                f"⚠ {str(error)[:120]}</div>"
            )

        st.markdown(
            f"""
            <div style='
                background: {style["bg"]};
                border: 1px solid {style["border"]};
                border-left: 3px solid {style["badge"]};
                border-radius: 6px;
                padding: 0.55rem 0.75rem;
                margin-bottom: 0.35rem;
            '>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div style='font-size:0.84rem; color:#f8fafc; font-weight:600;'>
                        {emoji} {label}{dur_html}
                    </div>
                    <small style='color:#64748b; font-size:0.72rem; white-space:nowrap;'>
                        {time_str}
                    </small>
                </div>
                <div style='margin-top:0.25rem; font-size:0.78rem; color:#94a3b8; display:flex; gap:1.2rem;'>
                    <span>🏢 <b style='color:#cbd5e1;'>{department}</b></span>
                    <span>🤖 <b style='color:#cbd5e1;'>{agent}</b></span>
                    <span>📌 <b style='color:#cbd5e1;'>{str(task)[:60]}</b></span>
                </div>
                {error_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _format_ago(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s ago"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s ago"
    else:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h {m}m ago"
