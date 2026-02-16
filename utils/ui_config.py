import streamlit as st


def inject_custom_css(theme: str = "dark"):
    """
    Injects global CSS to enforce the design system.
    Supports both 'dark' and 'light' themes.
    Includes styling for custom toggle switches.
    """

    # Theme-specific variables
    if theme == "light":
        theme_vars = """
            --bg-primary: #F8FAFC;
            --bg-secondary: #F1F5F9;
            --bg-surface: #FFFFFF;
            --text-primary: #0F172A;
            --text-secondary: #475569;
            --text-muted: #64748B;
            --border-color: #E2E8F0;
            --border-hover: #CBD5E1;
            --input-bg: #FFFFFF;
            --input-border: #CBD5E1;
            --input-text: #0F172A;
            --scrollbar-track: #F1F5F9;
            --scrollbar-thumb: #CBD5E1;
            --scrollbar-hover: #94A3B8;
            --code-bg: #F1F5F9;
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.08);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
        """
    else:
        theme_vars = """
            --bg-primary: #0F172A;
            --bg-secondary: #1E293B;
            --bg-surface: #1E293B;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --border-color: #334155;
            --border-hover: #475569;
            --input-bg: #1E293B;
            --input-border: #334155;
            --input-text: #F8FAFC;
            --scrollbar-track: #0F172A;
            --scrollbar-thumb: #334155;
            --scrollbar-hover: #475569;
            --code-bg: #1E293B;
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        """

    st.markdown(f"""
        <style>
        /* Import Roboto Font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        /* Theme Variables */
        :root {{
            --primary-orange: #FACC15;
            --primary-orange-hover: #EAB308;
            {theme_vars}
        }}

        /* Global Font & Theme */
        html, body, [class*="css"] {{
            font-family: 'Roboto', sans-serif !important;
        }}

        /* Button Styling */
        .stButton > button {{
            border-radius: 0.5rem !important;
            background-color: var(--primary-orange) !important;
            color: #0F172A !important;
            border: none !important;
            font-weight: 500 !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: var(--shadow-sm);
        }}

        .stButton > button:hover {{
            background-color: var(--primary-orange-hover) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(250, 204, 21, 0.3);
        }}

        .stButton > button:active {{
            transform: translateY(0);
        }}

        /* Input Styling */
        .stTextArea textarea, .stTextInput input {{
            border-radius: 0.5rem !important;
            border: 1px solid var(--input-border) !important;
            background-color: var(--input-bg) !important;
            color: var(--input-text) !important;
            transition: all 0.2s ease;
        }}

        .stTextArea textarea:focus, .stTextInput input:focus {{
            border-color: var(--primary-orange) !important;
            box-shadow: 0 0 0 1px var(--primary-orange) !important;
        }}

        /* Remove default top padding */
        .block-container {{
            padding-top: 2rem !important;
        }}

        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: var(--scrollbar-track);
        }}
        ::-webkit-scrollbar-thumb {{
            background: var(--scrollbar-thumb);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--scrollbar-hover);
        }}

        /* ── Toggle Switch Styling ──────────────────────────── */
        .toggle-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.5rem 0.75rem;
            margin-bottom: 0.25rem;
            border-radius: 0.5rem;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
        }}
        .toggle-row .toggle-label {{
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .toggle-row .toggle-label .toggle-icon {{
            font-size: 1rem;
        }}

        /* Streamlit toggle override for sidebar */
        [data-testid="stSidebar"] .stToggle > div {{
            flex-direction: row-reverse;
            gap: 0.5rem;
        }}

        /* Sidebar divider */
        .sidebar-divider {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 0.75rem 0;
        }}

        /* Settings section header */
        .settings-header {{
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            color: var(--text-muted) !important;
            padding: 0.5rem 0.25rem !important;
            margin-bottom: 0.5rem !important;
            margin-top: 0.5rem !important;
        }}

        /* Clean up Select/Segmented Control containers */
        div[data-baseweb="select"] {{
            background-color: var(--input-bg) !important;
            border-radius: 0.5rem !important;
            border: 1px solid var(--border-color) !important;
        }}

        /* ── Model Tag Badge ────────────────────────────── */
        .model-tag {{
            display: inline-block;
            font-size: 0.65rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 0.15rem 0.5rem;
            border: 1.5px solid;
            border-radius: 999px;
            line-height: 1;
            margin-top: -0.25rem;
        }}

        </style>
    """, unsafe_allow_html=True)
