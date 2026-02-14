"""
Tests for utils/rate_limiter.py
=================================
Validates rate limiting for both anonymous and logged-in users.
Uses a temporary file to avoid corrupting production data.
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from utils.rate_limiter import (
    ANONYMOUS_DAILY_LIMIT,
    LOGGED_IN_DAILY_LIMIT,
    check_rate_limit,
    get_daily_limit,
    get_remaining_prompts,
    increment_prompt_count,
    load_rate_limits,
    save_rate_limits,
)


@pytest.fixture(autouse=True)
def temp_rate_file(tmp_path):
    """Redirect rate limit storage to a temporary file for each test."""
    temp_file = str(tmp_path / "rate_limits.json")
    with patch("utils.rate_limiter.RATE_LIMIT_FILE", temp_file):
        yield temp_file


# ── Constants ───────────────────────────────────────────────────────
class TestConstants:
    def test_logged_in_limit(self):
        assert LOGGED_IN_DAILY_LIMIT == 5

    def test_anonymous_limit(self):
        assert ANONYMOUS_DAILY_LIMIT == 1


# ── Daily limit helper ──────────────────────────────────────────────
class TestGetDailyLimit:
    def test_anonymous(self):
        assert get_daily_limit(is_anonymous=True) == 1

    def test_logged_in(self):
        assert get_daily_limit(is_anonymous=False) == 5


# ── Logged-in user rate limiting ────────────────────────────────────
class TestLoggedInRateLimiting:
    def test_fresh_user_allowed(self):
        assert check_rate_limit("user@example.com", is_anonymous=False) is True

    def test_allows_up_to_limit(self):
        email = "user@example.com"
        for _ in range(LOGGED_IN_DAILY_LIMIT):
            assert check_rate_limit(email, is_anonymous=False) is True
            increment_prompt_count(email)

    def test_blocks_after_limit(self):
        email = "user@example.com"
        for _ in range(LOGGED_IN_DAILY_LIMIT):
            increment_prompt_count(email)
        assert check_rate_limit(email, is_anonymous=False) is False

    def test_remaining_prompts(self):
        email = "user@example.com"
        assert get_remaining_prompts(email, is_anonymous=False) == 5
        increment_prompt_count(email)
        assert get_remaining_prompts(email, is_anonymous=False) == 4
        increment_prompt_count(email)
        assert get_remaining_prompts(email, is_anonymous=False) == 3


# ── Anonymous user rate limiting ────────────────────────────────────
class TestAnonymousRateLimiting:
    def test_fresh_anonymous_allowed(self):
        assert check_rate_limit("anon_abc123", is_anonymous=True) is True

    def test_blocks_after_one(self):
        session_id = "anon_abc123"
        increment_prompt_count(session_id)
        assert check_rate_limit(session_id, is_anonymous=True) is False

    def test_remaining_prompts_anonymous(self):
        session_id = "anon_xyz789"
        assert get_remaining_prompts(session_id, is_anonymous=True) == 1
        increment_prompt_count(session_id)
        assert get_remaining_prompts(session_id, is_anonymous=True) == 0


# ── Persistence ─────────────────────────────────────────────────────
class TestPersistence:
    def test_save_and_load(self, tmp_path):
        temp_file = str(tmp_path / "persist_test.json")
        with patch("utils.rate_limiter.RATE_LIMIT_FILE", temp_file):
            data = {"user@test.com": {"2026-01-01": 3}}
            save_rate_limits(data)
            loaded = load_rate_limits()
            assert loaded == data

    def test_load_missing_file(self, tmp_path):
        temp_file = str(tmp_path / "nonexistent.json")
        with patch("utils.rate_limiter.RATE_LIMIT_FILE", temp_file):
            assert load_rate_limits() == {}


# ── Multiple users ──────────────────────────────────────────────────
class TestMultipleUsers:
    def test_independent_limits(self):
        user_a = "alice@example.com"
        user_b = "bob@example.com"

        for _ in range(LOGGED_IN_DAILY_LIMIT):
            increment_prompt_count(user_a)

        # User A is blocked
        assert check_rate_limit(user_a, is_anonymous=False) is False

        # User B is still allowed
        assert check_rate_limit(user_b, is_anonymous=False) is True
