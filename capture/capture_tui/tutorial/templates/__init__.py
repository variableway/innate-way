"""Tutorial output templates."""

from capture_tui.tutorial.templates.base import TutorialTemplate
from capture_tui.tutorial.templates.md_script import MdScriptTemplate
from capture_tui.tutorial.templates.md_only import MdOnlyTemplate
from capture_tui.tutorial.templates.script_only import ScriptOnlyTemplate

TEMPLATES = {
    "md_script": MdScriptTemplate,
    "md_only": MdOnlyTemplate,
    "script_only": ScriptOnlyTemplate,
}


def get_template(name: str) -> TutorialTemplate:
    """Get a template by name."""
    cls = TEMPLATES.get(name)
    if cls:
        return cls()
    raise ValueError(f"Unknown template: {name}. Available: {list(TEMPLATES.keys())}")
