"""
AI Engine — Cerebras Integration
==================================
Core AI module for prompt analysis (interviewer) and refinement (refiner).
Uses the Cerebras Cloud SDK with the llama-3.3-70b model.
"""

import json
import os
from typing import Any

from cerebras.cloud.sdk import Cerebras

from utils.security import validate_and_sanitize_user_input

# ── Constants ───────────────────────────────────────────────────────
MODEL = "llama-3.3-70b"
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

# ── Client singleton ───────────────────────────────────────────────
_client: Cerebras | None = None


def get_cerebras_client() -> Cerebras:
    """Return a cached Cerebras client instance."""
    global _client
    if _client is None:
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            raise ValueError(
                "CEREBRAS_API_KEY not found. "
                "Please set it in your .env file."
            )
        _client = Cerebras(api_key=api_key)
    return _client


def _load_system_prompt(filename: str) -> str:
    """Load a system instruction from the prompts/ directory."""
    filepath = os.path.join(PROMPTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()


# ── Interviewer ─────────────────────────────────────────────────────
def analyze_prompt(raw_prompt: str) -> dict[str, Any]:
    """
    Send the user's raw prompt to the AI analyst.

    The AI returns 3-5 clarifying questions as JSON:
        {"questions": ["q1", "q2", "q3"]}

    Raises:
        ValueError: If input fails validation or AI returns invalid JSON.
    """
    # Validate & sanitize
    sanitized, error = validate_and_sanitize_user_input(raw_prompt)
    if error:
        raise ValueError(error)

    system_instruction = _load_system_prompt("interviewer.txt")
    client = get_cerebras_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": sanitized},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    raw_text = response.choices[0].message.content.strip()

    # Parse JSON — handle possible markdown code fences
    cleaned = raw_text
    if cleaned.startswith("```"):
        # Remove ```json ... ``` wrapper
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError(
            "The AI returned an invalid response. Please try again."
        )

    # Validate structure
    if "questions" not in result or not isinstance(result["questions"], list):
        raise ValueError(
            "The AI returned an unexpected format. Please try again."
        )

    if not (3 <= len(result["questions"]) <= 5):
        raise ValueError(
            "The AI returned an unexpected number of questions. Please try again."
        )

    return result


# ── Refiner ─────────────────────────────────────────────────────────
def refine_prompt(raw_prompt: str, answers: dict[str, str]) -> str:
    """
    Combine the raw prompt and user answers, then send to the AI refiner.

    Returns the refined prompt as a formatted string.

    Raises:
        ValueError: If the AI fails to generate a refined prompt.
    """
    system_instruction = _load_system_prompt("refiner.txt")
    client = get_cerebras_client()

    # Build the user message with context
    answers_text = "\n".join(
        f"Q: {question}\nA: {answer}"
        for question, answer in answers.items()
    )

    user_message = (
        f"ORIGINAL PROMPT:\n{raw_prompt}\n\n"
        f"ADDITIONAL CONTEXT FROM USER:\n{answers_text}"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=1500,
    )

    refined = response.choices[0].message.content.strip()

    if not refined:
        raise ValueError(
            "The AI returned an empty response. Please try again."
        )

    return refined
