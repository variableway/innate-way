"""Render stage: produce output files using templates."""

from pathlib import Path
from typing import List

from capture_tui.pipeline.context import PipelineContext
from capture_tui.pipeline.errors import RenderError
from capture_tui.pipeline.stages import Stage, StageResult, StageStatus
from capture_tui.tutorial.models import Tutorial
from capture_tui.tutorial.templates import get_template


class RenderStage(Stage):
    """Render tutorial output using a template."""

    @property
    def name(self) -> str:
        return "render"

    def execute(self, context: PipelineContext) -> StageResult:
        try:
            template_name = context.template_name or "md_script"
            template = get_template(template_name)

            # Build Tutorial model from context
            tutorial = Tutorial(
                title=context.title,
                source_url=context.metadata.get("source_url"),
                source_type=context.source_type,
                code_blocks=context.code_blocks,
                prose_sections=context.prose_sections,
                scripts=context.scripts,
                metadata=context.metadata,
            )

            # Determine output directory
            output_dir = self._resolve_output_dir(context)
            context.output_dir = str(output_dir)

            # Render
            paths = template.render(tutorial, output_dir)

            # Save metadata
            meta_path = tutorial.save(output_dir)

            return StageResult(
                status=StageStatus.SUCCESS,
                stage_name=self.name,
                warnings=[f"Output: {[str(p) for p in paths]}"],
            )

        except Exception as e:
            raise RenderError(str(e), cause=e) from e

    def _resolve_output_dir(self, context: PipelineContext) -> Path:
        """Resolve output directory path."""
        if context.output_dir:
            return Path(context.output_dir)

        base = Path(self.config.get("output_base", "./output/tutorials"))
        slug = _slugify(context.title)
        return base / slug


def _slugify(text: str, max_len: int = 60) -> str:
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:max_len].strip('-')
