"""Script-only template: produces run.sh with embedded comments."""

from pathlib import Path
from typing import List

from capture_tui.tutorial.models import Tutorial
from capture_tui.tutorial.templates.base import TutorialTemplate


class ScriptOnlyTemplate(TutorialTemplate):
    """Output: run.sh only"""

    @property
    def name(self) -> str:
        return "script_only"

    @property
    def output_files(self) -> List[str]:
        return ["run.sh"]

    def render(self, tutorial: Tutorial, output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        sh_path = output_dir / "run.sh"
        sh_path.write_text(self._render(tutorial), encoding="utf-8")
        sh_path.chmod(0o755)
        return [sh_path]

    def _render(self, tutorial: Tutorial) -> str:
        lines = ["#!/usr/bin/env bash", ""]
        lines.append(f"# {tutorial.title}")
        if tutorial.source_url:
            lines.append(f"# Source: {tutorial.source_url}")
        lines.append("set -euo pipefail")
        lines.append("")

        for section in tutorial.prose_sections:
            lines.append(f"# --- {section.title} ---")
            if section.content:
                for para in section.content.split("\n\n"):
                    for text_line in para.strip().split("\n"):
                        lines.append(f"# {text_line}")
                lines.append("")

        for block in tutorial.code_blocks:
            if block.section_title:
                lines.append(f"# --- {block.section_title} ---")
                lines.append("")
            if block.is_executable and block.language in ("bash", "sh", "shell", ""):
                lines.append(block.code)
            else:
                for code_line in block.code.split("\n"):
                    lines.append(f"# {code_line}")
            lines.append("")

        return "\n".join(lines) + "\n"
