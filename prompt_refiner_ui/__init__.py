import os
import streamlit.components.v1 as components

# For local development/fallback on Windows, we serve the frontend via python http.server
# and point the component to that URL.
# This bypasses Streamlit's internal static file serving which is failing.
_RELEASE = True

# We ignore _RELEASE for the component source in this workaround
# Always use the URL of the local server handling dist/ or dev
COMPONENT_URL = "http://localhost:5173"

_component_func = components.declare_component(
    "prompt_refiner_component",
    url=COMPONENT_URL,
)

def prompt_refiner_ui(
    step: str = "input",
    raw_prompt: str = "",
    questions: list[str] | None = None,
    answers: dict[str, str] | None = None,
    refined_prompt: str = "",
    theme: str = "light",
    user: dict | None = None,
    key: str | None = None,
):
    """
    Create a new instance of "prompt_refiner_ui".
    """
    component_value = _component_func(
        step=step,
        raw_prompt=raw_prompt,
        questions=questions,
        answers=answers,
        refined_prompt=refined_prompt,
        theme=theme,
        user=user,
        key=key,
        default=None,
    )

    return component_value
