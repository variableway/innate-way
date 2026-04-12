"""Markdown + Script template: produces README.md and setup.sh."""

from pathlib import Path
from typing import List

from capture_tui.tutorial.models import Tutorial
from capture_tui.tutorial.templates.base import TutorialTemplate


class MdScriptTemplate(TutorialTemplate):
    """Output: README.md + setup.sh"""

    @property
    def name(self) -> str:
        return "md_script"

    @property
    def output_files(self) -> List[str]:
        return ["README.md", "setup.sh"]

    def render(self, tutorial: Tutorial, output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []

        # Render README.md
        md_path = output_dir / "README.md"
        md_path.write_text(self._render_markdown(tutorial), encoding="utf-8")
        paths.append(md_path)

        # Render setup.sh
        if tutorial.scripts:
            sh_path = output_dir / "setup.sh"
            sh_path.write_text(tutorial.scripts[0].render(), encoding="utf-8")
            sh_path.chmod(0o755)
            paths.append(sh_path)

        return paths

    def _render_markdown(self, tutorial: Tutorial) -> str:
        lines = [f"# {tutorial.title}", ""]

        if tutorial.source_url:
            lines.append(f"> **Source**: [{tutorial.source_url}]({tutorial.source_url})")
            lines.append("")

        lines.append("---")
        lines.append("")

        for section in tutorial.prose_sections:
            prefix = "#" * section.level
            lines.append(f"{prefix} {section.title}")
            lines.append("")
            if section.content:
                lines.append(section.content)
                lines.append("")

        if tutorial.scripts:
            lines.append("## One-Stop Script")
            lines.append("")
            lines.append("```bash")
            lines.append("./setup.sh")
            lines.append("```")
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
