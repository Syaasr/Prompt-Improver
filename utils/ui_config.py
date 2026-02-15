import streamlit as st

def inject_custom_css():
    """
    Injects global CSS to enforce the 'Intentional Minimalism' design system.
    Focuses on:
    - Roboto font enforcement
    - Orange accent colors (#F97316)
    - 0.5rem border radius for buttons and inputs
    - Removal of default Streamlit padding for a cleaner look
    """
    st.markdown("""
        <style>
        /* Import Roboto Font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

        /* Global Font Enforcement */
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif !important;
        }

        /* Accent Color Variables */
        :root {
            --primary-orange: #F97316;
            --primary-orange-hover: #EA580C;
            --surface-dark: #1E293B;
            --bg-dark: #0F172A;
        }

        /* Button Styling - The "Trigger" */
        .stButton > button {
            border-radius: 0.5rem !important;
            background-color: var(--primary-orange) !important;
            color: white !important;
            border: none !important;
            font-weight: 500 !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }

        .stButton > button:hover {
            background-color: var(--primary-orange-hover) !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.3);
        }

        .stButton > button:active {
            transform: translateY(0);
        }

        /* Input Styling - The "Terminal" */
        .stTextArea textarea, .stTextInput input {
            border-radius: 0.5rem !important;
            border: 1px solid #334155 !important;
            background-color: #1E293B !important;
            color: #F8FAFC !important;
            transition: all 0.2s ease;
        }

        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: var(--primary-orange) !important;
            box-shadow: 0 0 0 1px var(--primary-orange) !important;
        }
        
        /* Remove default top padding */
        .block-container {
            padding-top: 2rem !important;
        }

        /* Custom Scrollbar for Webkit */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0F172A; 
        }
        ::-webkit-scrollbar-thumb {
            background: #334155; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #475569; 
        }

        </style>
    """, unsafe_allow_html=True)
