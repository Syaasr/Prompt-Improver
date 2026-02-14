"""
AI Prompt Refiner — Main Application
======================================
Streamlit-native UI with injected design system.
Features: Dark/Light theme, flag-based language toggle,
persistent mini sidebar, Google sign-in.
"""

import streamlit as st
from dotenv import load_dotenv

from utils.ai_engine import analyze_prompt, refine_prompt
from utils.auth import (
    _auth_available,
    get_user_identifier,
    is_guest_mode,
    is_logged_in,
    should_show_login_screen,
)
from utils.i18n import (
    SUPPORTED_LANGUAGES,
    get_language,
    set_language,
    t,
)
from utils.rate_limiter import (
    get_remaining_prompts,
    increment_prompt_count,
)

load_dotenv()

# ── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Prompt Refiner",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Session State ───────────────────────────────────────────────────
def init_state():
    defaults = {
        "step": "input",
        "raw_prompt": "",
        "questions": [],
        "answers": {},
        "refined_prompt": "",
        "guest_mode": False,
        "theme": "light",
        "sidebar_expanded": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

is_dark = st.session_state.theme == "dark"
current_lang = get_language()

# ── Design System CSS ───────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ═══ THEME VARIABLES ═══ */
    :root {{
        --bg-primary:    {"#0F172A" if is_dark else "#FFFFFF"};
        --bg-secondary:  {"#1E293B" if is_dark else "#F8FAFC"};
        --bg-tertiary:   {"#334155" if is_dark else "#F1F5F9"};
        --bg-card:       {"#1E293B" if is_dark else "#FFFFFF"};
        --border:        {"#334155" if is_dark else "#E2E8F0"};
        --border-hover:  {"#475569" if is_dark else "#CBD5E1"};
        --text-primary:  {"#F8FAFC" if is_dark else "#0F172A"};
        --text-secondary:{"#94A3B8" if is_dark else "#64748B"};
        --text-muted:    {"#64748B" if is_dark else "#94A3B8"};
        --accent:        #EA580C;
        --accent-hover:  #C2410C;
        --accent-bg:     {"rgba(234,88,12,0.15)" if is_dark else "#FFF7ED"};
        --accent-border: {"rgba(234,88,12,0.3)" if is_dark else "#FDBA74"};
        --success:       #22C55E;
        --success-bg:    {"rgba(34,197,94,0.1)" if is_dark else "#F0FDF4"};
        --success-border:{"rgba(34,197,94,0.3)" if is_dark else "#86EFAC"};
        --info-bg:       {"rgba(59,130,246,0.1)" if is_dark else "#EFF6FF"};
        --info-border:   {"rgba(59,130,246,0.3)" if is_dark else "#BFDBFE"};
        --info-text:     {"#93C5FD" if is_dark else "#1E40AF"};
        --info-strong:   {"#60A5FA" if is_dark else "#1D4ED8"};
        --shadow:        {"0 1px 3px rgba(0,0,0,0.4)" if is_dark else "0 1px 3px rgba(0,0,0,0.06)"};
        --shadow-lg:     {"0 4px 12px rgba(0,0,0,0.5)" if is_dark else "0 4px 12px rgba(0,0,0,0.08)"};
    }}

    /* ═══ GLOBAL ═══ */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}
    .stApp {{
        background-color: var(--bg-primary) !important;
    }}
    .block-container {{
        max-width: 760px !important;
        padding: 1.5rem 1rem 4rem !important;
    }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .stDeployButton {{display: none;}}

    /* ═══ SIDEBAR — always visible, min-width when collapsed ═══ */
    section[data-testid="stSidebar"] {{
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
        min-width: 68px !important;
        transition: width 0.3s cubic-bezier(0.22, 1, 0.36, 1),
                    min-width 0.3s cubic-bezier(0.22, 1, 0.36, 1) !important;
    }}
    /* Keep sidebar visible when "collapsed" — show as mini rail */
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        min-width: 68px !important;
        width: 68px !important;
        transform: none !important;
        visibility: visible !important;
    }}
    section[data-testid="stSidebar"][aria-expanded="false"] .block-container,
    section[data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarContent"] {{
        overflow: hidden !important;
    }}
    /* In mini mode, hide text-heavy elements */
    section[data-testid="stSidebar"][aria-expanded="false"] .sb-section,
    section[data-testid="stSidebar"][aria-expanded="false"] .sb-profile-details,
    section[data-testid="stSidebar"][aria-expanded="false"] .badge,
    section[data-testid="stSidebar"][aria-expanded="false"] .stDivider,
    section[data-testid="stSidebar"][aria-expanded="false"] p.sb-footer,
    section[data-testid="stSidebar"][aria-expanded="false"] .sb-brand-text,
    section[data-testid="stSidebar"][aria-expanded="false"] .sb-login-info {{
        display: none !important;
    }}
    /* In mini mode, center buttons and avatars */
    section[data-testid="stSidebar"][aria-expanded="false"] .stButton > button {{
        padding: 0.4rem !important;
        width: 100% !important;
        font-size: 1.1rem !important;
        text-align: center !important;
        overflow: hidden !important;
        white-space: nowrap !important;
        text-overflow: clip !important;
        display: flex !important;
        justify-content: center !important;
    }}
    /* Hack to show only icon in mini buckets if possible, or just first char */
    /* Because Streamlit buttons are one text node, we rely on the icon being first */
    
    section[data-testid="stSidebar"][aria-expanded="false"] .sb-profile {{
        justify-content: center !important;
        padding: 0.5rem !important;
        background: transparent !important;
    }}
    section[data-testid="stSidebar"][aria-expanded="false"] .sb-avatar {{
        width: 38px; height: 38px;
    }}

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
        color: var(--text-primary) !important;
    }}
    section[data-testid="stSidebar"] .stDivider {{
        border-color: var(--border) !important;
    }}

    /* Sidebar section label */
    .sb-section {{
        font-size: 0.6rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        margin: 0.75rem 0 0.35rem;
        padding: 0 0.15rem;
    }}
    .sb-brand-text {{
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 0.5rem !important;
        color: var(--text-primary) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 0.45rem 0.75rem !important;
        transition: all 0.2s ease !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        border-color: var(--accent) !important;
        background: var(--accent-bg) !important;
        color: var(--accent) !important;
        transform: translateX(3px);
    }}

    /* Sidebar profile card */
    .sb-profile {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        padding: 0.65rem 0.75rem;
        background: var(--bg-tertiary);
        border-radius: 0.5rem;
        margin-top: 0.5rem;
    }}
    .sb-avatar {{
        width: 32px; height: 32px;
        border-radius: 50%;
        background: var(--accent);
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        flex-shrink: 0;
    }}
    .sb-name {{
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.2;
    }}
    .sb-role {{
        font-size: 0.65rem;
        color: var(--text-secondary);
    }}

    /* Footer */
    .sb-footer {{
        font-size: 0.6rem;
        color: var(--text-muted);
        text-align: center;
        margin-top: 1rem;
    }}

    /* ═══ STEP INDICATOR ═══ */
    .step-bar {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.75rem;
        margin: 0 0 2rem;
    }}
    .step-item {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .step-num {{
        width: 28px; height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 600;
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        border: 2px solid var(--border);
        color: var(--text-muted);
        background: transparent;
    }}
    .step-num.active {{
        background: var(--accent);
        border-color: var(--accent);
        color: #fff;
        box-shadow: 0 0 0 4px var(--accent-bg);
    }}
    .step-num.done {{
        background: var(--success);
        border-color: var(--success);
        color: #fff;
    }}
    .step-label {{
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-muted);
        transition: color 0.2s ease;
    }}
    .step-label.active {{ color: var(--accent); font-weight: 600; }}
    .step-label.done   {{ color: var(--success); }}
    .step-line {{
        width: 40px; height: 2px;
        background: var(--border);
        border-radius: 1px;
        transition: background 0.3s ease;
    }}
    .step-line.done {{ background: var(--success); }}

    /* ═══ TYPOGRAPHY ═══ */
    .page-title {{
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.15rem;
        letter-spacing: -0.025em;
    }}
    .page-subtitle {{
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
    }}

    /* ═══ BADGES ═══ */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.3rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        background: var(--accent-bg);
        color: var(--accent);
        border: 1px solid var(--accent-border);
    }}
    .badge-green {{
        background: var(--success-bg);
        color: {"#4ADE80" if is_dark else "#16A34A"};
        border: 1px solid var(--success-border);
    }}

    /* ═══ QUESTION LABEL ═══ */
    .q-label {{
        font-size: 0.825rem;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
        padding: 0.5rem 0 0.25rem;
    }}

    /* ═══ RESULT BOX ═══ */
    .result-box {{
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 0.5rem;
        padding: 1.5rem;
        font-size: 0.85rem;
        line-height: 1.75;
        color: var(--text-primary);
        white-space: pre-wrap;
        max-height: 500px;
        overflow-y: auto;
    }}

    /* ═══ ORIGINAL PROMPT BANNER ═══ */
    .original-banner {{
        background: var(--info-bg);
        border: 1px solid var(--info-border);
        border-radius: 0.5rem;
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
        color: var(--info-text);
        margin-bottom: 1.5rem;
    }}
    .original-banner strong {{ color: var(--info-strong); }}

    /* ═══ INPUT OVERRIDES ═══ */
    .stTextArea textarea {{
        border-radius: 0.5rem !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
        padding: 0.85rem 1rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }}
    .stTextArea textarea:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px {"rgba(234,88,12,0.25)" if is_dark else "rgba(234,88,12,0.12)"} !important;
    }}
    .stTextInput input {{
        border-radius: 0.5rem !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }}
    .stTextInput input:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px {"rgba(234,88,12,0.25)" if is_dark else "rgba(234,88,12,0.12)"} !important;
    }}

    /* ═══ BUTTON OVERRIDES ═══ */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {{
        background-color: var(--accent) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.55rem 1.5rem !important;
        transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {{
        background-color: var(--accent-hover) !important;
        transform: translateY(-1px) scale(1.02);
        box-shadow: 0 4px 12px rgba(234,88,12,0.3) !important;
    }}
    .stButton > button[kind="primary"]:active,
    .stButton > button[data-testid="stBaseButton-primary"]:active {{
        transform: translateY(0) scale(0.98);
    }}

    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"] {{
        border-radius: 0.5rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="stBaseButton-secondary"]:hover {{
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        transform: translateY(-1px);
    }}

    /* ═══ LOGIN SCREEN ═══ */
    .login-hero {{
        text-align: center;
        padding: 5rem 1rem 2rem;
    }}
    .login-hero h1 {{
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
    }}
    .login-hero p {{
        font-size: 1.05rem;
        color: var(--text-secondary);
        max-width: 420px;
        margin: 0 auto 2.5rem;
        line-height: 1.65;
    }}
    .login-card {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 1.75rem 2rem;
        text-align: center;
        max-width: 420px;
        margin: 0 auto;
        box-shadow: var(--shadow-lg);
    }}
    .login-feature {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem 0;
        font-size: 0.85rem;
        color: var(--text-primary);
    }}
    .login-feature-icon {{
        width: 28px; height: 28px;
        border-radius: 0.375rem;
        background: var(--accent-bg);
        color: var(--accent);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        flex-shrink: 0;
    }}

    /* ═══ RESPONSIVE ═══ */
    @media (max-width: 768px) {{
        .block-container {{
            padding: 1rem 0.75rem 3rem !important;
        }}
        .page-title {{ font-size: 1.25rem; }}
        .login-hero h1 {{ font-size: 1.75rem; }}
        .login-hero p {{ font-size: 0.9rem; }}
        .login-card {{ padding: 1.25rem; }}
        .step-label {{ display: none; }}
        .step-line {{ width: 24px; }}
        .result-box {{ padding: 1rem; font-size: 0.8rem; }}
    }}
    @media (max-width: 480px) {{
        .block-container {{
            padding: 0.75rem 0.5rem 2rem !important;
        }}
        .login-hero {{ padding: 3rem 0.5rem 1rem; }}
        .login-hero h1 {{ font-size: 1.5rem; }}
    }}

    /* ═══ ACCESSIBILITY ═══ */
    *:focus-visible {{
        outline: 2px solid var(--accent) !important;
        outline-offset: 2px !important;
    }}

    /* ═══ ANIMATIONS ═══ */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .animate-in {{
        animation: fadeInUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }}
    .stSpinner > div {{
        border-top-color: var(--accent) !important;
    }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  LOGIN SCREEN
# ═══════════════════════════════════════════════════════════════════
if should_show_login_screen():
    st.markdown(
        f'<div class="login-hero animate-in">'
        f'<h1>✦ {t("app_title")}</h1>'
        f'<p>{t("app_subtitle")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f'<div class="login-card">'
            f'<div class="login-feature">'
            f'<div class="login-feature-icon">✦</div>'
            f'<span>{t("login_google_desc")}</span>'
            f'</div>'
            f'<div class="login-feature">'
            f'<div class="login-feature-icon">🎯</div>'
            f'<span>{t("login_guest_desc")}</span>'
            f'</div>'
            f'<div class="login-feature">'
            f'<div class="login-feature-icon">⚡</div>'
            f'<span>{t("login_guest_desc")}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        if st.button(
            t("login_guest_button") + " →",
            type="primary",
            use_container_width=True,
            key="get_started",
        ):
            st.session_state.guest_mode = True
            st.rerun()

    st.stop()


# ── User Context ────────────────────────────────────────────────────
user_id, is_anon = get_user_identifier()
remaining = get_remaining_prompts(user_id, is_anon)


# ═══════════════════════════════════════════════════════════════════
#  STEP INDICATOR
# ═══════════════════════════════════════════════════════════════════
def _step_indicator(current: str):
    step_labels = [
        ("input", t("step_label_write")),
        ("questions", t("step_label_clarify")),
        ("result", t("step_label_result")),
    ]
    idx = next((i for i, s in enumerate(step_labels) if s[0] == current), 0)
    html = '<div class="step-bar">'
    for i, (key, label) in enumerate(step_labels):
        if i > 0:
            line_cls = "step-line done" if i <= idx else "step-line"
            html += f'<div class="{line_cls}"></div>'
        if i < idx:
            nc, lc = "step-num done", "step-label done"
            nt = "✓"
        elif i == idx:
            nc, lc = "step-num active", "step-label active"
            nt = str(i + 1)
        else:
            nc, lc = "step-num", "step-label"
            nt = str(i + 1)
        html += (
            f'<div class="step-item">'
            f'<div class="{nc}">{nt}</div>'
            f'<span class="{lc}">{label}</span>'
            f'</div>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR — Settings → Templates → Profile + Sign-in
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Brand
    st.markdown('<div class="sb-brand-text">✦ Prompt Refiner</div>', unsafe_allow_html=True)

    # ── SETTINGS ────────────────────────────────
    st.markdown(f'<p class="sb-section">⚙ {t("sidebar_language")}</p>', unsafe_allow_html=True)

    # Theme toggle
    theme_icon = "☀️" if is_dark else "🌙"
    theme_text = "Light Mode" if is_dark else "Dark Mode"
    if st.button(f"{theme_icon} {theme_text}", use_container_width=True, key="sb_theme"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

    # Language toggle
    if current_lang == "en":
        flag_btn = "🇮🇩 Bahasa Indonesia"
    else:
        flag_btn = "🇺🇸 English"

    if st.button(flag_btn, use_container_width=True, key="sb_lang_toggle"):
        new_lang = "id" if current_lang == "en" else "en"
        set_language(new_lang)
        st.rerun()

    st.divider()

    # ── TEMPLATES ───────────────────────────────
    st.markdown(f'<p class="sb-section">📋 {t("sidebar_templates")}</p>', unsafe_allow_html=True)

    templates = {
        "📝  Blog Post": "Write a blog post about...",
        "💻  Code Review": "Review this code and suggest improvements...",
        "📧  Email Draft": "Write a professional email to...",
        "🎯  Marketing": "Create compelling marketing copy for...",
        "📊  Data Analysis": "Analyze the following data and provide insights...",
    }
    for label, tpl in templates.items():
        if st.button(label, use_container_width=True, key=f"tpl_{label}"):
            st.session_state.raw_prompt = tpl
            st.session_state.step = "input"
            st.rerun()

    st.divider()

    # ── PROFILE (bottom) ───────────────────────
    avatar_letter = "G" if is_anon else user_id[0].upper()
    display_name = (
        t("sidebar_guest_mode") if is_anon else user_id.split("@")[0]
    )
    role = "Free tier" if is_anon else t("sidebar_logged_in_as")
    st.markdown(
        f'<div class="sb-profile">'
        f'<div class="sb-avatar">{avatar_letter}</div>'
        f'<div class="sb-profile-details">'
        f'<div class="sb-name">{display_name}</div>'
        f'<div class="sb-role">{role}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="badge" style="margin-top:0.5rem;">'
        f'{remaining} · {t("sidebar_remaining")}'
        f'</span>',
        unsafe_allow_html=True,
    )

    # Google Sign-in button
    if is_anon:
        st.markdown("")
        if _auth_available():
            if st.button(
                f"🔑 {t('sidebar_login_button')}",
                use_container_width=True,
                key="sb_google_login",
                type="primary",
            ):
                st.login("google")
        else:
            # Fallback if no auth secrets config
            st.markdown(
                f'<div class="sb-login-info">'
                f'<p style="font-size:0.7rem;color:var(--text-muted);'
                f'text-align:center;margin-top:0.25rem;">'
                f'{t("sidebar_login_prompt")}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
            # Add a 'fake' button for UI demo if secrets missing? 
            # User asked for the button to "appear and work". 
            # If it doesn't work (no secrets), we can't make it work.
            # But we can make it APPEAR.
            # Let's show a disabled button or a button that shows a toast if no secrets.
            # For now, sticking to logic: if no secrets, show text.
            pass
    else:
        # Show logout button for signed-in users
        st.markdown("")
        if st.button(
            f"🚪 {t('sidebar_logout_button')}",
            use_container_width=True,
            key="sb_logout",
        ):
            st.logout()

    st.markdown(
        '<p class="sb-footer">Built with Streamlit • v1.0</p>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════
st.markdown(
    f'<p class="page-title animate-in">✦ {t("app_title")}</p>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<p class="page-subtitle">{t("app_subtitle")}</p>',
    unsafe_allow_html=True,
)
_step_indicator(st.session_state.step)


# ━━ STEP 1: INPUT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if st.session_state.step == "input":
    prompt_text = st.text_area(
        t("step1_title"),
        value=st.session_state.raw_prompt,
        height=180,
        placeholder=t("step1_placeholder"),
        label_visibility="collapsed",
        help=t("step1_help"),
    )

    col_spacer, col_btn = st.columns([3, 1])
    with col_btn:
        analyze_clicked = st.button(
            t("step1_analyze_button"),
            type="primary",
            use_container_width=True,
        )

    if analyze_clicked:
        if not prompt_text.strip():
            st.warning(t("step1_empty_error"))
        elif remaining <= 0:
            st.error(t("step1_rate_limit_error"))
        else:
            st.session_state.raw_prompt = prompt_text.strip()
            with st.spinner(t("spinner_analyzing")):
                try:
                    result = analyze_prompt(st.session_state.raw_prompt)
                    st.session_state.questions = result["questions"]
                    st.session_state.step = "questions"
                    st.rerun()
                except Exception as e:
                    st.error(f'{t("error_generic")}: {e}')


# ━━ STEP 2: QUESTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif st.session_state.step == "questions":
    st.markdown(
        f'<div class="original-banner">'
        f'<strong>Original:</strong> {st.session_state.raw_prompt}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"#### {t('step2_title')}")
    st.markdown(f"*{t('step2_subtitle')}*")

    answers = {}
    for i, q in enumerate(st.session_state.questions):
        st.markdown(
            f'<div class="q-label">{i + 1}. {q}</div>',
            unsafe_allow_html=True,
        )
        answers[q] = st.text_input(
            f"q{i}",
            key=f"ans_{i}",
            placeholder=t("step2_answer_help"),
            label_visibility="collapsed",
        )

    st.markdown("")
    col_back, col_spacer, col_refine = st.columns([1, 2, 1])
    with col_back:
        if st.button(t("step2_back_button"), use_container_width=True):
            st.session_state.step = "input"
            st.rerun()
    with col_refine:
        if st.button(
            t("step2_generate_button"),
            type="primary",
            use_container_width=True,
        ):
            st.session_state.answers = answers
            with st.spinner(t("spinner_refining")):
                try:
                    refined = refine_prompt(
                        st.session_state.raw_prompt, answers
                    )
                    st.session_state.refined_prompt = refined
                    st.session_state.step = "result"
                    increment_prompt_count(user_id)
                    st.rerun()
                except Exception as e:
                    st.error(f'{t("error_generic")}: {e}')


# ━━ STEP 3: RESULT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif st.session_state.step == "result":
    st.markdown(f"#### {t('step3_title')}")
    st.markdown("")

    st.markdown(
        f'<div class="result-box">{st.session_state.refined_prompt}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(t("step2_back_button"), use_container_width=True):
            st.session_state.step = "questions"
            st.rerun()
    with col2:
        if st.button(t("step3_copy_button"), use_container_width=True):
            st.toast(t("step3_copied_toast"))
    with col3:
        if st.button(
            t("step3_start_over_button"),
            type="primary",
            use_container_width=True,
        ):
            st.session_state.step = "input"
            st.session_state.raw_prompt = ""
            st.session_state.questions = []
            st.session_state.answers = {}
            st.session_state.refined_prompt = ""
            st.rerun()
