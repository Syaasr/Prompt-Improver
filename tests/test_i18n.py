"""
Tests for utils/i18n.py
=========================
Validates translation loading and key lookups for EN and ID.
"""

import json
import os
from unittest.mock import patch

import pytest


# ── Translation data tests ──────────────────────────────────────────
class TestTranslationData:
    """Test the translations.json file directly."""

    @pytest.fixture
    def translations(self):
        filepath = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "translations.json",
        )
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_has_en_and_id(self, translations):
        assert "en" in translations
        assert "id" in translations

    def test_keys_match(self, translations):
        en_keys = set(translations["en"].keys())
        id_keys = set(translations["id"].keys())
        missing_in_id = en_keys - id_keys
        extra_in_id = id_keys - en_keys

        assert missing_in_id == set(), f"Missing in ID: {missing_in_id}"
        assert extra_in_id == set(), f"Extra in ID: {extra_in_id}"

    def test_no_empty_values(self, translations):
        for lang in ["en", "id"]:
            for key, value in translations[lang].items():
                assert value.strip(), f"Empty value for {lang}.{key}"

    def test_minimum_key_count(self, translations):
        """Ensure we have a reasonable number of translations."""
        assert len(translations["en"]) >= 40
        assert len(translations["id"]) >= 40


# ── i18n module tests ───────────────────────────────────────────────
class TestI18nModule:
    """Test the i18n.py translation functions (requires mocked session_state)."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock Streamlit's session_state for i18n tests."""
        # Streamlit's session_state supports both dict and attribute access
        class SessionDict(dict):
            def __getattr__(self, key):
                try:
                    return self[key]
                except KeyError:
                    raise AttributeError(key)
            def __setattr__(self, key, value):
                self[key] = value
            def __delattr__(self, key):
                del self[key]

        mock_state = SessionDict()

        with patch("utils.i18n.st") as mock_st:
            mock_st.session_state = mock_state
            # Reset cached translations
            import utils.i18n
            utils.i18n._translations = None
            yield mock_st, mock_state

    def test_get_language_default(self, mock_streamlit):
        from utils.i18n import get_language
        assert get_language() == "en"

    def test_set_language(self, mock_streamlit):
        _, mock_state = mock_streamlit
        from utils.i18n import get_language, set_language
        set_language("id")
        assert get_language() == "id"

    def test_set_invalid_language(self, mock_streamlit):
        _, mock_state = mock_streamlit
        from utils.i18n import get_language, set_language
        set_language("fr")  # Not supported
        assert get_language() == "en"  # Should stay default

    def test_translate_en(self, mock_streamlit):
        from utils.i18n import t
        result = t("app_title")
        assert result == "AI Prompt Refiner"

    def test_translate_id(self, mock_streamlit):
        _, mock_state = mock_streamlit
        from utils.i18n import set_language, t
        set_language("id")
        result = t("app_subtitle")
        assert "Ubah" in result  # Indonesian text

    def test_fallback_to_en(self, mock_streamlit):
        from utils.i18n import t
        # Should return the key itself if not found anywhere
        result = t("nonexistent_key_12345")
        assert result == "nonexistent_key_12345"

    def test_supported_languages(self):
        from utils.i18n import SUPPORTED_LANGUAGES
        assert "en" in SUPPORTED_LANGUAGES
        assert "id" in SUPPORTED_LANGUAGES
        assert SUPPORTED_LANGUAGES["en"] == "English"
        assert SUPPORTED_LANGUAGES["id"] == "Bahasa Indonesia"
