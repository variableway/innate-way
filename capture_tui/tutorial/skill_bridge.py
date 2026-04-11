"""Skill bridge: adapter between pipeline stages and Claude Code skills.

When running inside Claude Code, stages emit prompts that Claude handles.
When running standalone, stages use regex/heuristic fallbacks.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from capture_tui.pipeline.context import PipelineContext, CodeBlock, ScriptDef


@dataclass
class SkillPrompt:
    """A prompt emitted for Claude to handle."""
    stage: str
    instruction: str
    input_data: Dict[str, Any]
    output_schema: Dict[str, Any]


class SkillBridge:
    """Bridge between pipeline stages and Claude Code."""

    def __init__(self, claude_enabled: bool = True):
        self.claude_enabled = claude_enabled

    def create_prompt(self, stage: str, context: PipelineContext) -> Optional[SkillPrompt]:
        """Create a skill prompt for the given stage."""
        if not self.claude_enabled:
            return None

        builders = {
            "extract_code": self._build_extract_prompt,
            "generate_script": self._build_script_prompt,
        }
        builder = builders.get(stage)
        return builder(context) if builder else None

    def _build_extract_prompt(self, context: PipelineContext) -> SkillPrompt:
        """Build prompt for intelligent code extraction."""
        return SkillPrompt(
            stage="extract_code",
            instruction=(
                "Analyze the following article content and extract all code blocks. "
                "For each block: identify language, whether executable, and dependencies. "
                "Also find inline code that should be extracted as executable steps."
            ),
            input_data={
                "content": context.parsed_content[:8000],  # truncate for prompt limits
                "existing_blocks": [b.to_dict() for b in context.code_blocks],
            },
            output_schema={
                "code_blocks": [{"language": str, "code": str, "executable": bool}],
                "prose_sections": [{"title": str, "content": str}],
            },
        )

    def _build_script_prompt(self, context: PipelineContext) -> SkillPrompt:
        """Build prompt for script generation."""
        return SkillPrompt(
            stage="generate_script",
            instruction=(
                "Generate a single executable bash script from these code blocks. "
                "Add shebang, error handling (set -euo pipefail), progress messages, "
                "comments, and organize commands in logical order. "
                "Include prerequisite checks and a verification step at the end."
            ),
            input_data={
                "code_blocks": [
                    {"language": b.language, "code": b.code, "executable": b.is_executable}
                    for b in context.code_blocks
                ],
                "title": context.title,
                "source_url": context.metadata.get("source_url", ""),
            },
            output_schema={
                "scripts": [{
                    "filename": str,
                    "language": str,
                    "content": str,
                }],
            },
        )

    def parse_script_response(self, response: str) -> List[ScriptDef]:
        """Parse Claude's script generation response into ScriptDef objects."""
        scripts = []

        # Try to extract bash script blocks from the response
        import re
        pattern = re.compile(r"```(?:bash|sh|shell)\s*\n(.*?)```", re.DOTALL)
        for i, match in enumerate(pattern.finditer(response)):
            scripts.append(ScriptDef(
                filename="setup.sh" if i == 0 else f"step{i + 1}.sh",
                language="bash",
                content=match.group(1).strip(),
            ))

        # If no fenced blocks found, treat entire response as script
        if not scripts and response.strip().startswith("#!/"):
            scripts.append(ScriptDef(
                filename="setup.sh",
                language="bash",
                content=response.strip(),
            ))

        return scripts

    def parse_extraction_response(self, response: str) -> List[CodeBlock]:
        """Parse Claude's extraction response into CodeBlock objects."""
        import re
        import json

        blocks = []

        # Try JSON response first
        try:
            data = json.loads(response)
            for b in data.get("code_blocks", []):
                blocks.append(CodeBlock(
                    language=b.get("language", "text"),
                    code=b.get("code", ""),
                    is_executable=b.get("executable", False),
                ))
            return blocks
        except (json.JSONDecodeError, TypeError):
            pass

        # Fall back to extracting fenced code blocks from response
        pattern = re.compile(r"```(\w*)\s*\n(.*?)```", re.DOTALL)
        for match in pattern.finditer(response):
            blocks.append(CodeBlock(
                language=match.group(1) or "text",
                code=match.group(2).strip(),
                is_executable=True,
            ))

        return blocks
