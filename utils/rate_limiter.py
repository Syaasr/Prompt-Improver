"""
Rate Limiter
=============
Tracks per-user daily prompt usage with two tiers:
  • Anonymous (session-based): 1 prompt / day
  • Logged-in (Google OAuth):  5 prompts / day
"""

import json
import os
import uuid
from datetime import date

import streamlit as st

RATE_LIMIT_FILE = "data/rate_limits.json"
LOGGED_IN_DAILY_LIMIT = 5
ANONYMOUS_DAILY_LIMIT = 1


# ── Persistence ─────────────────────────────────────────────────────
def load_rate_limits() -> dict:
    """Load rate limit data from the JSON file."""
    if not os.path.exists(RATE_LIMIT_FILE):
        return {}
    with open(RATE_LIMIT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_rate_limits(limits: dict) -> None:
    """Persist rate limit data to the JSON file."""
    os.makedirs("data", exist_ok=True)
    with open(RATE_LIMIT_FILE, "w", encoding="utf-8") as f:
        json.dump(limits, f, indent=2)


# ── Anonymous session tracking ──────────────────────────────────────
def get_or_create_session_id() -> str:
    """
    Return a stable anonymous session identifier.

    Generated once per browser session and stored in session_state.
    """
    if "anonymous_session_id" not in st.session_state:
        st.session_state.anonymous_session_id = f"anon_{uuid.uuid4().hex[:12]}"
    return st.session_state.anonymous_session_id


# ── Core logic ──────────────────────────────────────────────────────
def _get_daily_limit(is_anonymous: bool) -> int:
    """Return the correct daily limit for the user type."""
    return ANONYMOUS_DAILY_LIMIT if is_anonymous else LOGGED_IN_DAILY_LIMIT


def check_rate_limit(user_id: str, is_anonymous: bool = False) -> bool:
    """Return True if the user is still under the daily limit."""
    # DISABLED: Rate limiting bypassed — always allow
    return True
    # today = date.today().isoformat()
    # limits = load_rate_limits()
    # daily_limit = _get_daily_limit(is_anonymous)
    #
    # if user_id not in limits:
    #     return True
    # if today not in limits[user_id]:
    #     return True
    #
    # return limits[user_id][today] < daily_limit


def increment_prompt_count(user_id: str) -> None:
    """Increment the daily prompt counter for the given user."""
    today = date.today().isoformat()
    limits = load_rate_limits()

    if user_id not in limits:
        limits[user_id] = {}
    if today not in limits[user_id]:
        limits[user_id][today] = 0

    limits[user_id][today] += 1
    save_rate_limits(limits)


def get_remaining_prompts(user_id: str, is_anonymous: bool = False) -> int:
    """Return the number of remaining prompts for today."""
    # DISABLED: Rate limiting bypassed — return unlimited
    return 9999
    # today = date.today().isoformat()
    # limits = load_rate_limits()
    # daily_limit = _get_daily_limit(is_anonymous)
    #
    # if user_id not in limits:
    #     return daily_limit
    # if today not in limits[user_id]:
    #     return daily_limit
    #
    # return max(0, daily_limit - limits[user_id][today])


def get_daily_limit(is_anonymous: bool = False) -> int:
    """Public accessor for the daily limit constant."""
    return _get_daily_limit(is_anonymous)
