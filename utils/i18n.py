"""
Internationalization (i18n)
============================
Simple dictionary-based translation system supporting EN and ID.
Language preference is stored in Streamlit session state.
"""

import json
import os

import streamlit as st

# ── Load translations ───────────────────────────────────────────────
_TRANSLATIONS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "translations.json"
)
_translations: dict | None = None

SUPPORTED_LANGUAGES = {"en": "English", "id": "Bahasa Indonesia"}
DEFAULT_LANGUAGE = "id"


def _load_translations() -> dict:
    """Load translations from JSON file (cached in module-level var)."""
    global _translations
    if _translations is None:
        with open(_TRANSLATIONS_FILE, "r", encoding="utf-8") as f:
            _translations = json.load(f)
    return _translations


# ── Public API ──────────────────────────────────────────────────────
def get_language() -> str:
    """Return the current language code from session state."""
    return st.session_state.get("language", DEFAULT_LANGUAGE)


def set_language(lang: str) -> None:
    """Set the language in session state."""
    if lang in SUPPORTED_LANGUAGES:
        st.session_state.language = lang


def t(key: str) -> str:
    """
    Translate a key to the current language.

    Falls back to English if the key is missing in the selected language,
    and returns the key itself if not found at all.
    """
    translations = _load_translations()
    lang = get_language()

    # Try current language
    if lang in translations and key in translations[lang]:
        return translations[lang][key]

    # Fallback to default language (Indonesian)
    if DEFAULT_LANGUAGE in translations and key in translations[DEFAULT_LANGUAGE]:
        return translations[DEFAULT_LANGUAGE][key]

    # Key not found — return key itself as fallback
    return key


def language_selector() -> None:
    """Render a language selector widget in the sidebar."""
    current = get_language()
    options = list(SUPPORTED_LANGUAGES.keys())
    labels = list(SUPPORTED_LANGUAGES.values())

    selected_label = st.selectbox(
        t("sidebar_language"),
        options=labels,
        index=options.index(current),
        key="language_selector",
    )

    # Map label back to code
    selected_code = options[labels.index(selected_label)]
    if selected_code != current:
        set_language(selected_code)
        st.rerun()
