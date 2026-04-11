"""TutorialGenerator: high-level facade for generating executable tutorials."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from capture_tui.config import TutorialConfig
from capture_tui.pipeline.context import PipelineContext
from capture_tui.pipeline.engine import PipelineConfig, PipelineEngine
from capture_tui.pipeline.errors import RetryPolicy
from capture_tui.pipeline.batch import BatchProcessor
from capture_tui.pipeline.queue import Job, JobQueue
from capture_tui.tutorial.models import Tutorial
from capture_tui.tutorial.stages.fetch import FetchStage
from capture_tui.tutorial.stages.parse import ParseStage
from capture_tui.tutorial.stages.extract_code import CodeExtractionStage
from capture_tui.tutorial.stages.generate_script import GenerateScriptStage
from capture_tui.tutorial.stages.render import RenderStage
from capture_tui.tutorial.stages.review import ReviewStage


class TutorialGenerator:
    """High-level API for generating executable tutorials."""

    def __init__(self, config: Optional[TutorialConfig] = None):
        self.config = config or TutorialConfig()

    def generate(
        self,
        source: str,
        template: str = "md_script",
        output_dir: Optional[str] = None,
        review: bool = False,
        claude_enabled: bool = True,
    ) -> Tutorial:
        """Generate a single executable tutorial."""
        context = PipelineContext(
            source=source,
            template_name=template,
            output_dir=output_dir,
        )

        engine = self._build_engine(review=review, claude_enabled=claude_enabled)
        result = engine.execute(context)

        if not result.success:
            raise RuntimeError(
                f"Pipeline failed: {result.error}"
            )

        # Build Tutorial model from context for return
        tutorial = Tutorial(
            title=context.title,
            source_url=context.metadata.get("source_url"),
            source_type=context.source_type,
            code_blocks=context.code_blocks,
            prose_sections=context.prose_sections,
            scripts=context.scripts,
            metadata=context.metadata,
        )

        return tutorial

    def generate_batch(
        self,
        sources: List,
        template: str = "md_script",
        output_dir: Optional[str] = None,
        max_workers: int = 4,
    ) -> "BatchResult":
        """Generate tutorials in batch from a list of sources."""
        from capture_tui.pipeline.batch import BatchResult

        queue_dir = self.config.queue_dir or f"{self.config.output_dir}/.tutorial"
        queue = JobQueue(queue_dir)

        # Normalize sources to Job objects
        jobs = []
        for i, source in enumerate(sources):
            if isinstance(source, str):
                source_ref = source
                overrides = {"template": template}
            elif isinstance(source, dict):
                source_ref = source.get("source", source.get("url", ""))
                overrides = {
                    "template": source.get("template", template),
                    "tags": source.get("tags", []),
                }
            else:
                continue

            now = datetime.now()
            job = Job(
                id=f"tut-{now.strftime('%Y%m%d')}-{i:04d}",
                input_ref=source_ref,
                config_overrides=overrides,
            )
            jobs.append(job)

        processor = BatchProcessor(
            engine_factory=lambda: self._build_engine(),
            queue=queue,
            max_workers=max_workers,
        )

        return processor.process_jobs(jobs)

    def _build_engine(
        self,
        review: bool = False,
        claude_enabled: bool = True,
    ) -> PipelineEngine:
        """Build a configured pipeline engine."""
        stages = [
            FetchStage(config={"timeout": self.config.fetch_timeout}),
            ParseStage(),
            CodeExtractionStage(),
            GenerateScriptStage(),
            RenderStage(config={"output_base": self.config.output_dir}),
        ]

        if review or self.config.review_enabled:
            stages.append(ReviewStage(config={"review_enabled": True}))

        config = PipelineConfig(
            stages=stages,
            retry_policy=RetryPolicy(
                max_retries=self.config.retry_max,
                backoff_base=self.config.retry_backoff,
            ),
        )

        return PipelineEngine(config)
