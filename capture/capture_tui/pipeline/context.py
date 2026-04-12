"""Pipeline context: typed data bag passed between stages."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class CodeBlock:
    """Extracted code block."""
    language: str
    code: str
    filename_hint: Optional[str] = None
    section_title: Optional[str] = None
    line_range: Optional[Tuple[int, int]] = None
    is_executable: bool = False
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ProseSection:
    """Extracted prose section."""
    title: str
    content: str
    level: int = 2
    position: int = 0


@dataclass
class ScriptDef:
    """Generated executable script."""
    filename: str
    language: str = "bash"
    shebang: str = "#!/usr/bin/env bash"
    commands: List[str] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[str] = None
    content: str = ""

    def render(self) -> str:
        """Render the script to a string."""
        if self.content:
            return self.content

        lines = [self.shebang, ""]
        if self.comments:
            for c in self.comments:
                lines.append(f"# {c}")
            lines.append("")
        if self.env_vars:
            for k, v in self.env_vars.items():
                lines.append(f'{k}="{v}"')
            lines.append("")
        lines.append("set -euo pipefail")
        lines.append("")
        for cmd in self.commands:
            lines.append(cmd)
        return "\n".join(lines) + "\n"


@dataclass
class PipelineContext:
    """Data bag passed between pipeline stages."""
    # Input
    source: str = ""
    source_type: str = ""  # "url", "file", "text"

    # Stage outputs
    raw_content: str = ""
    parsed_content: str = ""
    title: str = "Untitled"
    code_blocks: List[CodeBlock] = field(default_factory=list)
    prose_sections: List[ProseSection] = field(default_factory=list)
    scripts: List[ScriptDef] = field(default_factory=list)
    tutorial_markdown: str = ""

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    # Output config
    template_name: str = "md_script"
    output_dir: Optional[str] = None

    def add_warning(self, msg: str):
        self.warnings.append(msg)
