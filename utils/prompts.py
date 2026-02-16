import json
import os

TEMPLATE_FILE = "data/templates.json"


def get_templates():
    """Load prompt templates from the JSON file."""
    if not os.path.exists(TEMPLATE_FILE):
        return {}
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def add_template(name: str, template: str):
    """Add a new template to the JSON file."""
    templates = get_templates()
    templates[name] = template

    os.makedirs("data", exist_ok=True)
    with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
        json.dump(templates, f, indent=2)
