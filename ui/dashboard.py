"""
=================================================
BharatAI - Dashboard Main Coordinator
=================================================
"""

import streamlit as st
import streamlit.components.v1 as components

from company.office_api import OfficeAPI
from ui.state import UIStateManager
from ui.theme import inject_custom_theme
from ui.layout import DashboardLayoutManager

from ui.sidebar import SidebarComponent
from ui.cards import DepartmentCardsComponent
from ui.engineering_insights import EngineeringInsightsComponent
from ui.agent_control_center import AgentControlCenterComponent
from ui.kanban import KanbanComponent
from ui.agent_table import AgentTableComponent
from ui.notifications import NotificationComponent
from ui.activity_feed import ActivityFeedComponent


def render_dashboard() -> None:
    """Main rendering execution entrypoint for BharatAI Streamlit Headquarters dashboard."""
    # 1. State & API initialization
    state = UIStateManager()
    api = OfficeAPI()

    # 2. Retrieve dashboard data EXACTLY ONCE per rerun cycle
    dashboard_data = api.get_company_dashboard()

    # 3. Inject premium dark glassmorphism stylesheet
    inject_custom_theme()

    # 4. Render Sidebar
    sidebar_comp = SidebarComponent()
    sidebar_comp.render(dashboard_data, state)

    # 5. Render dynamic Department Status Cards
    cards_comp = DepartmentCardsComponent()
    cards_comp.render(dashboard_data, state)

    # 5.5 Render Engineering Insights
    insights_comp = EngineeringInsightsComponent()
    insights_comp.render(dashboard_data, state)

    # 5.6 Render Agent Control Center Panel
    control_center_comp = AgentControlCenterComponent()
    control_center_comp.render(dashboard_data, state)

    st.write("---")

    # 6. Render Kanban Board
    kanban_comp = KanbanComponent()
    kanban_comp.render(dashboard_data, state)

    st.write("---")

    # 7. Layout lower columns grid
    col_agent, col_notification = DashboardLayoutManager.create_lower_grid()

    with col_agent:
        agent_table_comp = AgentTableComponent()
        agent_table_comp.render(dashboard_data, state)

    with col_notification:
        notif_comp = NotificationComponent()
        notif_comp.render(dashboard_data, state)

    st.write("---")

    # 8. Activity Feed (full width)
    activity_feed_comp = ActivityFeedComponent()
    activity_feed_comp.render(dashboard_data, state)

    # 9. Clean up event hooks to prevent memory leaks
    api.shutdown()

    # 9. Client-side browser-driven 5-second auto-refresh trigger (Non-blocking)
    # We display a Refresh button in the sidebar (hidden or visual refresh button)
    st.sidebar.markdown(
        "<div style='display:none;'>",
        unsafe_allow_html=True
    )
    if st.sidebar.button("Refresh", key="refresh_trigger_btn"):
        st.rerun()
    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    interval_ms = state.refresh_interval * 1000
    js_code = """
        <script>
        const parentDoc = window.parent.document;
        setTimeout(function() {
            const buttons = parentDoc.querySelectorAll("button");
            for (let i = 0; i < buttons.length; i++) {
                if (buttons[i].textContent.trim() === "Refresh") {
                    buttons[i].click();
                    break;
                }
            }
        }, {interval_ms});
        </script>
        """.replace("{interval_ms}", str(interval_ms))
    components.html(js_code, height=0)
