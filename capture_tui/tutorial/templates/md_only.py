"""Markdown-only template: produces README.md with inline code."""

from pathlib import Path
from typing import List

from capture_tui.tutorial.models import Tutorial
from capture_tui.tutorial.templates.base import TutorialTemplate


class MdOnlyTemplate(TutorialTemplate):
    """Output: README.md only"""

    @property
    def name(self) -> str:
        return "md_only"

    @property
    def output_files(self) -> List[str]:
        return ["README.md"]

    def render(self, tutorial: Tutorial, output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)

        md_path = output_dir / "README.md"
        md_path.write_text(self._render(tutorial), encoding="utf-8")
        return [md_path]

    def _render(self, tutorial: Tutorial) -> str:
        lines = [f"# {tutorial.title}", ""]

        if tutorial.source_url:
            lines.append(f"> **Source**: [{tutorial.source_url}]({tutorial.source_url})")
            lines.append("")

        for section in tutorial.prose_sections:
            prefix = "#" * section.level
            lines.append(f"{prefix} {section.title}")
            lines.append("")
            if section.content:
                lines.append(section.content)
                lines.append("")

        for block in tutorial.code_blocks:
            if block.section_title:
                lines.append(f"### {block.section_title}")
                lines.append("")
            lines.append(f"```{block.language}")
            lines.append(block.code)
            lines.append("```")
            lines.append("")

        return "\n".join(lines)
