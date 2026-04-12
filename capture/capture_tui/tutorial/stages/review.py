"""Review stage: optional human review gate."""

import subprocess
import sys
from pathlib import Path

from capture_tui.pipeline.context import PipelineContext
from capture_tui.pipeline.stages import Stage, StageResult, StageStatus


class ReviewStage(Stage):
    """Present output for human review before finalizing."""

    @property
    def name(self) -> str:
        return "review"

    def should_run(self, context: PipelineContext) -> bool:
        return self.config.get("review_enabled", False)

    def execute(self, context: PipelineContext) -> StageResult:
        output_dir = context.output_dir
        if not output_dir:
            return StageResult(
                status=StageStatus.SKIPPED,
                stage_name=self.name,
                warnings=["No output directory to review"],
            )

        md_path = Path(output_dir) / "README.md"
        if md_path.exists():
            self._show_file(str(md_path))

        # Ask for approval
        response = input("\nApprove output? [Y/e(dit)/r(eject)]: ").strip().lower()

        if response in ("", "y", "yes"):
            return StageResult(status=StageStatus.SUCCESS, stage_name=self.name)
        elif response in ("e", "edit"):
            self._open_editor(str(md_path))
            return StageResult(status=StageStatus.SUCCESS, stage_name=self.name)
        else:
            return StageResult(
                status=StageStatus.FAILED,
                stage_name=self.name,
                error=ValueError("Review rejected"),
            )

    def _show_file(self, path: str):
        """Display file content using pager or print."""
        try:
            pager = self.config.get("pager") or "less"
            subprocess.run([pager, path], check=False)
        except Exception:
            Path(path).read_text(encoding="utf-8")

    def _open_editor(self, path: str):
        """Open file in editor."""
        editor = self.config.get("editor") or "vim"
        subprocess.run([editor, path], check=False)
