"""
=================================================
BharatAI - UI Theme Configurator
=================================================
"""

import streamlit as st


def inject_custom_theme() -> None:
    """Inject custom HTML and CSS to create a premium dark glassmorphic style."""
    st.markdown(
        """
        <style>
        /* Custom dark theme colors & glassmorphism variables */
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-blue: #38bdf8;
            --accent-green: #4ade80;
            --accent-red: #f87171;
            --accent-yellow: #fbbf24;
        }

        /* Glassmorphic card styling class */
        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            color: var(--text-primary);
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }

        .glass-card h4 {
            margin-top: 0;
            margin-bottom: 0.5rem;
            color: var(--accent-blue);
            font-size: 1.1rem;
            font-weight: 600;
        }

        .metric-label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 0.2rem;
        }

        .metric-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        /* Status colors */
        .status-working { color: var(--accent-green); }
        .status-idle { color: var(--text-secondary); }
        .status-error { color: var(--accent-red); }
        .status-busy { color: var(--accent-yellow); }

        /* Hide Streamlit components */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Sidebar background styling */
        section[data-testid="stSidebar"] {
            background-color: #0b0f19 !important;
            border-right: 1px solid var(--card-border) !important;
        }

        /* Customize scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-color);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--card-border);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
