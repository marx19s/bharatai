"""
=================================================
BharatAI - Engineering Insights Component
=================================================
"""

import streamlit as st
from typing import Dict, Any

from ui.base_component import BaseComponent
from ui.state import UIStateManager


class EngineeringInsightsComponent(BaseComponent):
    """
    Renders live engineering insights metrics based on the lessons namespace.
    """

    def render(self, data: Dict[str, Any], state: UIStateManager) -> None:
        insights = data.get("engineering_insights", {})
        if not insights:
            insights = {
                "bugs_prevented": 0,
                "reused_fixes": 0,
                "lessons_applied": 0,
                "review_quality": "100%",
                "test_stability": "100%"
            }

        st.subheader("💡 Engineering Insights")
        cols = st.columns(5)

        metrics = [
            ("🛡️ Bugs Prevented", insights.get("bugs_prevented", 0)),
            ("♻️ Reused Fixes", insights.get("reused_fixes", 0)),
            ("📚 Lessons Applied", insights.get("lessons_applied", 0)),
            ("🔍 Review Quality", insights.get("review_quality", "100%")),
            ("🧪 Test Stability", insights.get("test_stability", "100%"))
        ]

        for idx, (label, val) in enumerate(metrics):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div class='glass-card' style='text-align: center; padding: 1.2rem;'>
                        <div style='font-size: 0.8rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>{label}</div>
                        <div style='font-size: 1.8rem; font-weight: bold; margin-top: 0.5rem; color: #38bdf8;'>{val}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
