"""Script generation stage: create executable scripts from code blocks."""

from capture_tui.pipeline.context import PipelineContext, ScriptDef
from capture_tui.pipeline.stages import Stage, StageResult, StageStatus


class GenerateScriptStage(Stage):
    """Generate executable scripts from extracted code blocks."""

    @property
    def name(self) -> str:
        return "generate_script"

    def execute(self, context: PipelineContext) -> StageResult:
        exec_blocks = [b for b in context.code_blocks if b.is_executable]

        if not exec_blocks:
            return StageResult(
                status=StageStatus.PARTIAL,
                stage_name=self.name,
                warnings=["No executable code blocks to generate script from"],
            )

        script = self._build_script(context.title, exec_blocks)
        context.scripts = [script]

        return StageResult(status=StageStatus.SUCCESS, stage_name=self.name)

    def _build_script(self, title: str, blocks) -> ScriptDef:
        """Build a ScriptDef from executable code blocks."""
        lines = ["#!/usr/bin/env bash", ""]
        lines.append(f"# {title}")
        lines.append("# Auto-generated executable tutorial script")
        lines.append("")
        lines.append("set -euo pipefail")
        lines.append("")

        # Colors
        lines.append("""RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }
""")

        total = len(blocks)
        for i, block in enumerate(blocks, 1):
            section = block.section_title or f"Step {i}"
            lines.append(f"# --- {section} ({i}/{total}) ---")
            lines.append(f'info "Step {i}/{total}: {section}"')
            lines.append("")

            code = block.code
            # Strip leading $ prompts
            code_lines = []
            for line in code.split("\n"):
                stripped = line.lstrip()
                if stripped.startswith("$ "):
                    code_lines.append(stripped[2:])
                else:
                    code_lines.append(line)
            lines.append("\n".join(code_lines))
            lines.append("")

        lines.append('info "All steps completed successfully!"')

        return ScriptDef(
            filename="setup.sh",
            language="bash",
            content="\n".join(lines) + "\n",
        )
