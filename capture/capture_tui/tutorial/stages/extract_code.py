"""Code extraction stage: extract code blocks from parsed content."""

import re
from typing import List

from capture_tui.pipeline.context import PipelineContext, CodeBlock
from capture_tui.pipeline.errors import ExtractionError
from capture_tui.pipeline.stages import Stage, StageResult, StageStatus


class CodeExtractionStage(Stage):
    """Extract code blocks from parsed content using regex."""

    @property
    def name(self) -> str:
        return "extract_code"

    def execute(self, context: PipelineContext) -> StageResult:
        try:
            content = context.parsed_content
            if not content:
                return StageResult(
                    status=StageStatus.FAILED,
                    stage_name=self.name,
                    error=ValueError("No parsed content"),
                )

            blocks = self._extract_fenced_blocks(content)

            # Also try inline code patterns that look executable
            inline = self._extract_inline_commands(content)
            blocks.extend(inline)

            context.code_blocks = blocks

            if not blocks:
                return StageResult(
                    status=StageStatus.PARTIAL,
                    stage_name=self.name,
                    warnings=["No code blocks found"],
                )

            return StageResult(status=StageStatus.SUCCESS, stage_name=self.name)

        except Exception as e:
            raise ExtractionError(str(e), cause=e) from e

    def _extract_fenced_blocks(self, content: str) -> List[CodeBlock]:
        """Extract fenced code blocks (```lang ... ```)."""
        blocks = []
        pattern = re.compile(
            r"```(\w*)\s*\n(.*?)```",
            re.DOTALL,
        )

        for i, match in enumerate(pattern.finditer(content)):
            lang = match.group(1) or "text"
            code = match.group(2).strip()
            start_line = content[:match.start()].count("\n") + 1
            end_line = start_line + code.count("\n")

            # Find section title above the code block
            section_title = self._find_section_title(content, match.start())

            # Heuristic: determine if executable
            is_exec = self._is_executable(lang, code)

            blocks.append(CodeBlock(
                language=lang,
                code=code,
                section_title=section_title,
                line_range=(start_line, end_line),
                is_executable=is_exec,
            ))

        return blocks

    def _extract_inline_commands(self, content: str) -> List[CodeBlock]:
        """Extract inline code that looks like shell commands."""
        blocks = []
        # Match patterns like `command args` that contain common shell commands
        shell_patterns = [
            r"npm install", r"pip install", r"brew install",
            r"apt-get", r"yum install", r"cargo install",
            r"git clone", r"docker run", r"kubectl",
            r"curl ", r"wget ", r"chmod ", r"mkdir ",
            r"export ", r"source ", r"eval ",
            r"go mod", r"go run", r"go build",
            r"python ", r"node ", r"ruby ",
            r"make ", r"cmake ", r"./",
        ]

        pattern = re.compile(r"`([^`]+)`")
        for match in pattern.finditer(content):
            code = match.group(1).strip()
            if any(re.search(p, code) for p in shell_patterns):
                blocks.append(CodeBlock(
                    language="bash",
                    code=code,
                    is_executable=True,
                ))

        return blocks

    def _find_section_title(self, content: str, pos: int) -> str:
        """Find the nearest heading above a position."""
        before = content[:pos]
        lines = before.split("\n")
        for line in reversed(lines):
            m = re.match(r"^#{1,6}\s+(.+)$", line)
            if m:
                return m.group(1).strip()
        return ""

    def _is_executable(self, lang: str, code: str) -> bool:
        """Heuristic: is this code block executable?"""
        exec_langs = {"bash", "sh", "zsh", "shell", "python", "python3", "ruby", "node", "js"}
        if lang.lower() in exec_langs:
            return True
        # Check for shebang
        if code.startswith("#!/"):
            return True
        # Check for common command patterns
        if lang.lower() in ("", "text") and re.match(r"^\$?\s*\w+", code):
            return True
        return False
