"""Tutorial generator data models."""

import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _slugify(text: str, max_len: int = 60) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:max_len].strip('-')


def _generate_id() -> str:
    """Generate a tutorial ID."""
    now = datetime.now()
    short_uuid = uuid.uuid4().hex[:6]
    return f"tut-{now.strftime('%Y%m%d-%H%M%S')}-{short_uuid}"


@dataclass
class CodeBlock:
    """Extracted code block from source content."""
    language: str
    code: str
    filename_hint: Optional[str] = None
    section_title: Optional[str] = None
    line_range: Optional[Tuple[int, int]] = None
    is_executable: bool = False
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CodeBlock":
        return cls(**data)


@dataclass
class ProseSection:
    """Section of explanatory text."""
    title: str
    content: str
    level: int = 2
    position: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ProseSection":
        return cls(**data)


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

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ScriptDef":
        return cls(**data)

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
class Tutorial:
    """Complete executable tutorial."""
    id: str = field(default_factory=_generate_id)
    title: str = "Untitled"
    slug: str = ""
    source_url: Optional[str] = None
    source_type: str = ""  # "url", "file", "text"
    source_fetched_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    code_blocks: List[CodeBlock] = field(default_factory=list)
    prose_sections: List[ProseSection] = field(default_factory=list)
    scripts: List[ScriptDef] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.slug:
            self.slug = _slugify(self.title)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Tutorial":
        data["code_blocks"] = [
            CodeBlock.from_dict(b) for b in data.get("code_blocks", [])
        ]
        data["prose_sections"] = [
            ProseSection.from_dict(s) for s in data.get("prose_sections", [])
        ]
        data["scripts"] = [
            ScriptDef.from_dict(s) for s in data.get("scripts", [])
        ]
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def save(self, output_dir: Path):
        """Save tutorial metadata to output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        meta_path = output_dir / "tutorial.json"
        meta_path.write_text(self.to_json(), encoding="utf-8")
        return meta_path
