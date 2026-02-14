"""
Authentication Helpers
=======================
Google OAuth via Streamlit's native auth, with an optional
"Continue without login" path for anonymous users.

Gracefully handles the case where OAuth is not configured
(missing secrets.toml) — falls back to guest-only mode.
"""

import streamlit as st

from utils.rate_limiter import get_or_create_session_id


def _auth_available() -> bool:
    """Check if Streamlit's native auth is configured."""
    try:
        # Directly access st.user.is_logged_in — if OAuth is not
        # configured in secrets.toml, this will raise AttributeError.
        # We use a bare access + catch instead of hasattr() because
        # Streamlit's custom __getattr__ may not work with hasattr().
        _ = st.user.is_logged_in  # noqa: F841
        return True
    except (AttributeError, Exception):
        return False


def is_logged_in() -> bool:
    """Check whether the current user is authenticated via Google OAuth."""
    if not _auth_available():
        return False
    try:
        return st.user.is_logged_in
    except Exception:
        return False


def get_user_identifier() -> tuple[str, bool]:
    """
    Return (identifier, is_anonymous).

    • Logged-in  → (email, False)
    • Anonymous  → (session_uuid, True)
    """
    if is_logged_in():
        return st.user.email, False
    return get_or_create_session_id(), True


def get_user_email() -> str | None:
    """Return the logged-in user's email, or None."""
    if is_logged_in():
        return st.user.email
    return None


def login_screen() -> bool:
    """
    Render the login / welcome screen.

    Returns True if the user chose "Continue without login",
    allowing the main app to proceed in anonymous mode.
    """
    st.markdown("# 🚀 AI Prompt Refiner")
    st.markdown(
        "*Transform your basic prompts into powerful, "
        "well-structured instructions.*"
    )

    st.divider()

    auth_ok = _auth_available()

    if auth_ok:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🔑 Log in with Google")
            st.markdown(
                "Get **5 free prompt refinements** per day."
            )
            st.button(
                "Log in with Google",
                on_click=st.login,
                type="primary",
                use_container_width=True,
            )

        with col2:
            st.markdown("#### 👤 Try without login")
            st.markdown(
                "Get **1 free try** per day — no account needed."
            )
            if st.button(
                "Continue as Guest",
                use_container_width=True,
            ):
                st.session_state.guest_mode = True
                st.rerun()
    else:
        # OAuth not configured — only guest mode available
        st.markdown("#### 👤 Welcome!")
        st.markdown(
            "Get **1 free prompt refinement** per day. "
            "Sign in with Google for **5 per day** *(coming soon)*."
        )
        if st.button(
            "🚀 Get Started",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.guest_mode = True
            st.rerun()

    return False


def is_guest_mode() -> bool:
    """Check if the user has opted for guest / anonymous mode."""
    return st.session_state.get("guest_mode", False)


def should_show_login_screen() -> bool:
    """
    Determine if we need to show the login screen.

    Returns False (skip login screen) when:
      1. User is already logged in via Google, OR
      2. User has chosen guest mode in this session
    """
    return not is_logged_in() and not is_guest_mode()
