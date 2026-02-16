"""
AI Engine — Cerebras Integration
==================================
Core AI module for prompt analysis (interviewer) and refinement (refiner).
Uses the Cerebras Cloud SDK. Models and templates loaded from data/ folder.
"""

import json
import os
from typing import Any

from cerebras.cloud.sdk import Cerebras

from utils.security import validate_and_sanitize_user_input

# ── Paths ───────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(_BASE_DIR, "data")
PROMPTS_DIR = os.path.join(_BASE_DIR, "prompts")

# ── Load config from data/ ──────────────────────────────────────────
def _load_json(filename: str) -> dict:
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


_models_config = _load_json("models.json")
AVAILABLE_MODELS: list[str] = [m["id"] for m in _models_config["available_models"]]
MODEL_TAGS: dict[str, dict] = {
    m["id"]: {"label": m["label"], "tag": m["tag"], "tag_color": m["tag_color"]}
    for m in _models_config["available_models"]
}
DEFAULT_MODEL: str = _models_config["default_model"]

_templates_config = _load_json("output_templates.json")
OUTPUT_TEMPLATES: dict[str, dict] = _templates_config
DEFAULT_TEMPLATE: str = list(_templates_config.keys())[0]  # First key

QUESTION_TYPES = ["General", "Detail", "Professional", "Technical", "Creative", "Academic"]
DEFAULT_QUESTION_TYPE = "General"

_QUESTION_TYPE_INSTRUCTIONS = {
    "General": "Ask broad, open-ended clarifying questions suitable for any audience.",
    "Detail": "Ask very specific, granular questions that drill deep into requirements, edge cases, and precise specifications.",
    "Professional": "Ask formal, business-oriented questions focusing on stakeholders, deliverables, KPIs, and organizational context.",
    "Technical": "Ask technically-focused questions about architecture, implementation details, tools, performance requirements, and technical constraints.",
    "Creative": "Ask imaginative, exploratory questions about style, tone, mood, audience engagement, and creative vision.",
    "Academic": "Ask scholarly questions about methodology, references, theoretical frameworks, evidence standards, and academic rigor.",
}

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
def analyze_prompt(
    raw_prompt: str,
    model: str = DEFAULT_MODEL,
    question_type: str = DEFAULT_QUESTION_TYPE,
) -> dict[str, Any]:
    """
    Send the user's raw prompt to the AI analyst.

    The AI returns clarifying questions as JSON:
        {"questions": ["q1", "q2", ...]}

    Raises:
        ValueError: If input fails validation or AI returns invalid JSON.
    """
    # Validate & sanitize
    sanitized, error = validate_and_sanitize_user_input(raw_prompt)
    if error:
        raise ValueError(error)

    system_instruction = _load_system_prompt("interviewer.txt")

    # Override question style in the system prompt based on selected type
    type_instruction = _QUESTION_TYPE_INSTRUCTIONS.get(question_type, _QUESTION_TYPE_INSTRUCTIONS[DEFAULT_QUESTION_TYPE])
    system_instruction += (
        f"\n\nIMPORTANT: Generate exactly 5 clarifying questions. "
        f"Question style: '{question_type}'. {type_instruction}"
    )

    client = get_cerebras_client()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": sanitized},
        ],
        temperature=0.7,
        max_tokens=800,
    )

    raw_text = response.choices[0].message.content.strip()

    # Parse JSON — handle possible markdown code fences
    cleaned = raw_text
    if cleaned.startswith("```"):
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

    return result


# ── Refiner ─────────────────────────────────────────────────────────
def refine_prompt(
    raw_prompt: str,
    answers: dict[str, str],
    model: str = DEFAULT_MODEL,
    output_template: str = DEFAULT_TEMPLATE,
) -> str:
    """
    Combine the raw prompt and user answers, then send to the AI refiner.

    Returns the refined prompt as a formatted string.

    Raises:
        ValueError: If the AI fails to generate a refined prompt.
    """
    system_instruction = _load_system_prompt("refiner.txt")

    # Inject the selected output template into the system prompt
    template_data = OUTPUT_TEMPLATES.get(output_template, OUTPUT_TEMPLATES[DEFAULT_TEMPLATE])
    template_structure = "\n".join(template_data["sections"])
    system_instruction += (
        f"\n\nIMPORTANT: You MUST format your refined prompt output using the "
        f"'{output_template}' framework. Structure the output EXACTLY as follows:\n"
        f"{template_structure}\n\n"
        f"Fill in each section with content derived from the user's original prompt and their answers."
    )

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
        model=model,
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
