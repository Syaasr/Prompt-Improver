import streamlit as st
import streamlit_antd_components as sac
from dotenv import load_dotenv

from utils.ai_engine import (
    analyze_prompt,
    refine_prompt,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    OUTPUT_TEMPLATES,
    DEFAULT_TEMPLATE,
    QUESTION_TYPES,
    DEFAULT_QUESTION_TYPE,
)
from utils.auth import (
    _auth_available,
    get_user_identifier,
    is_guest_mode,
    is_logged_in,
    should_show_login_screen,
)
from utils.i18n import (
    get_language,
    set_language,
    t,
)
from utils.rate_limiter import (
    get_remaining_prompts,
)
from utils.ui_config import inject_custom_css

load_dotenv()

# ── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prompt Refiner",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
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
        "theme": "dark",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Inject Design System (dark theme only) ────────────────────────
inject_custom_css(theme="dark")

# ── Login Logic (DISABLED) ──────────────────────────────────────────
if should_show_login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>✦ Prompt Refiner</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #94A3B8; margin-bottom: 3rem;'>{t('app_subtitle')}</p>", unsafe_allow_html=True)
        
        if st.button(t("login_guest_button") + " →", use_container_width=True, type="primary"):
            st.session_state.guest_mode = True
            st.rerun()
            
        if _auth_available():
             if st.button(t("sidebar_login_button"), use_container_width=True):
                st.login("google")
    st.stop()

# ── User Context ────────────────────────────────────────────────────
user_id, is_anon = get_user_identifier()
remaining = get_remaining_prompts(user_id, is_anon)

# ── Load sidebar templates from data/ ───────────────────────────────
import json, os
_templates_file = os.path.join(os.path.dirname(__file__), "data", "templates.json")
with open(_templates_file, "r", encoding="utf-8") as f:
    _sidebar_templates = json.load(f)

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    # ── Settings: Language Selection ───────────────────────────────
    st.markdown(f"<div class='settings-header'>{t('settings_title')}</div>", unsafe_allow_html=True)

    current_lang = get_language()
    
    # Language options using flag emojis
    lang_labels = {"en": "🇬🇧 English", "id": "🇮🇩 Indonesia"}
    
    # Get current selection label
    default_label = lang_labels.get(current_lang, "🇬🇧 English")
    
    selected_label = st.segmented_control(
        label=t("settings_language"),
        options=list(lang_labels.values()),
        default=default_label,
        selection_mode="single",
        label_visibility="collapsed",
        key="lang_select"
    )

    if selected_label:
        # Find code from label
        new_lang = next((k for k, v in lang_labels.items() if v == selected_label), current_lang)
        if new_lang != current_lang:
            set_language(new_lang)
            st.rerun()

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # ── Templates with icons (bilingual) ────────────────────────────
    lang = get_language()
    template_menu_items = []
    for name, data in _sidebar_templates.items():
        icon = data.get("icon", "file-text")
        template_menu_items.append(sac.MenuItem(name, icon=icon))

    selected_item = sac.menu([
        sac.MenuItem('Refine', icon='stars', description=t('app_subtitle')),
        sac.MenuItem(t('sidebar_templates'), icon='card-text', children=template_menu_items),
    ], size='lg', color='yellow', open_all=True)

    # Handle Sidebar Actions
    if selected_item and selected_item in _sidebar_templates:
        if st.session_state.get("last_selected_template") != selected_item:
            # Load template in current language
            template_data = _sidebar_templates[selected_item]
            template_text = template_data.get(lang, template_data.get("en", ""))
            st.session_state.raw_prompt = template_text
            st.session_state.input_prompt = template_text
            st.session_state.step = "input"
            st.session_state.last_selected_template = selected_item
            st.rerun()


# ── Main Content Layout ─────────────────────────────────────────────
left_col, main_col, right_col = st.columns([1, 6, 1])

with main_col:
    # Header
    st.markdown("<h2 style='margin-bottom: 0.5rem;'>Prompt <span style='color:#FACC15'>Refiner</span></h2>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom: 0.75rem; color: #64748B;'>✦ Unlimited prompts — no login required.</div>", unsafe_allow_html=True)

    # Options Row: Model | Output Format | Question Type
    col_model, col_template, col_questions = st.columns(3)
    with col_model:
        selected_model = st.selectbox(
            "AI Model",
            options=AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(DEFAULT_MODEL),
            key="selected_model",
        )
    with col_template:
        template_names = list(OUTPUT_TEMPLATES.keys())
        selected_template = st.selectbox(
            "Output Format",
            options=template_names,
            index=template_names.index(DEFAULT_TEMPLATE),
            key="selected_template",
        )
    with col_questions:
        selected_q_type = st.selectbox(
            "Question Type",
            options=QUESTION_TYPES,
            index=QUESTION_TYPES.index(DEFAULT_QUESTION_TYPE),
            key="selected_q_type",
        )
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # ━━ STEP 1: INPUT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if st.session_state.step == "input":
        st.text_area(
            "Input Prompt", 
            value=st.session_state.raw_prompt,
            height=200,
            key="input_prompt",
            placeholder=t("step1_placeholder"),
            label_visibility="collapsed"
        )
        
        col_actions = st.columns([4, 1])
        with col_actions[1]:
            if st.button(t("step1_analyze_button") + "  →", type="primary", use_container_width=True):
                raw = st.session_state.input_prompt.strip()
                if not raw:
                    st.warning(t("step1_empty_error"))
                else:
                    st.session_state.raw_prompt = raw
                    with st.spinner(t("spinner_analyzing")):
                        try:
                            result = analyze_prompt(
                                raw,
                                model=selected_model,
                                question_type=selected_q_type,
                            )
                            st.session_state.questions = result["questions"]
                            st.session_state.step = "questions"
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # ━━ STEP 2: QUESTIONS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif st.session_state.step == "questions":
        st.markdown(f"<div style='padding:1rem; border:1px solid var(--border-color); border-radius:0.5rem; margin-bottom:2rem; background:var(--bg-surface); color:var(--text-secondary);'><em>{st.session_state.raw_prompt}</em></div>", unsafe_allow_html=True)
        
        with st.form("questions_form"):
            st.markdown(f"### {t('step2_title')}")
            answers = {}
            for i, q in enumerate(st.session_state.questions):
                st.markdown(f"**{i+1}. {q}**")
                answers[q] = st.text_input(f"answer_{i}", label_visibility="collapsed", placeholder=t("step2_answer_help"))
            
            st.markdown("---")
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.form_submit_button(f"← {t('step2_back_button')}"):
                    st.session_state.step = "input"
                    st.rerun()
            with c2:
                if st.form_submit_button(f"{t('step2_generate_button')} →", type="primary"):
                    st.session_state.answers = answers
                    with st.spinner(t("spinner_refining")):
                        try:
                            refined = refine_prompt(
                                st.session_state.raw_prompt,
                                answers,
                                model=st.session_state.get('selected_model', DEFAULT_MODEL),
                                output_template=st.session_state.get('selected_template', DEFAULT_TEMPLATE),
                            )
                            st.session_state.refined_prompt = refined
                            st.session_state.step = "result"
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    # ━━ STEP 3: RESULT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    elif st.session_state.step == "result":
        st.success(t("step3_success") if t("step3_success") != "step3_success" else "Prompt Refined Successfully!")
        st.markdown(f"### {t('step3_title') if t('step3_title') != 'step3_title' else 'Final Prompt'}")
        st.code(st.session_state.refined_prompt, language="markdown")
        
        if st.button(t("step3_restart") if t("step3_restart") != "step3_restart" else "Start Over"):
            st.session_state.step = "input"
            st.session_state.raw_prompt = ""
            st.rerun()
