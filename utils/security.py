import re
from typing import Optional, Tuple


def validate_input_length(input_text: str, max_length: int = 4000) -> bool:
    """Return True if the input text is within the allowed length."""
    return len(input_text) <= max_length


def sanitize_input(input_text: str) -> str:
    """Remove potentially dangerous characters and normalize unicode."""
    # Remove null bytes
    sanitized = input_text.replace("\x00", "")

    # Normalize unicode
    try:
        sanitized = sanitized.encode("utf-8", "ignore").decode("utf-8")
    except Exception:
        pass

    return sanitized.strip()


def detect_prompt_injection(input_text: str) -> Tuple[bool, Optional[str]]:
    """
    Detect potential prompt injection attempts.

    Returns:
        (is_injection, reason)
    """
    injection_patterns = [
        r"ignore (all )?(previous|above|prior) (instructions|prompts)",
        r"disregard (all )?(previous|above|prior) (instructions|prompts)",
        r"(new|updated) instructions:",
        r"act as (a )?(hacker|attacker|malicious)",
        r"system prompt:",
        r"pretend (you are|to be)",
        r"let's play a game",
        r"in this scenario",
        r"override",
        r"bypass",
    ]

    for pattern in injection_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return True, f"Detected potential injection pattern: {pattern}"

    # Check for excessive special characters (potential encoding attacks)
    special_char_count = sum(1 for c in input_text if ord(c) > 127)
    if special_char_count > len(input_text) * 0.5:
        return True, "Too many special characters detected"

    return False, None


def validate_and_sanitize_user_input(
    input_text: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Comprehensive input validation pipeline.

    Returns:
        (sanitized_text, error_message) — one of them is always None.
    """
    # Check length
    if not validate_input_length(input_text):
        return None, "Input is too long (max 4000 characters)"

    # Detect injection
    is_injection, reason = detect_prompt_injection(input_text)
    if is_injection:
        return None, f"Security alert: {reason}"

    # Sanitize
    sanitized = sanitize_input(input_text)

    # Final empty check
    if not sanitized:
        return None, "Input cannot be empty"

    return sanitized, None
