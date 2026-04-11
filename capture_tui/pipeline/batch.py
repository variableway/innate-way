"""Batch processor: parallel job execution."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List

from capture_tui.pipeline.context import PipelineContext
from capture_tui.pipeline.engine import PipelineConfig, PipelineEngine
from capture_tui.pipeline.queue import Job, JobQueue, JobStatus


@dataclass
class BatchResult:
    """Result of a batch processing run."""
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class BatchProcessor:
    """Process queued jobs in parallel."""

    def __init__(
        self,
        engine_factory,
        queue: JobQueue,
        max_workers: int = 4,
    ):
        self.engine_factory = engine_factory
        self.queue = queue
        self.max_workers = max_workers

    def process_pending(self) -> BatchResult:
        """Process all pending jobs."""
        jobs = self.queue.dequeue(limit=100)
        return self._process_jobs(jobs)

    def process_jobs(self, jobs: List[Job]) -> BatchResult:
        """Process specific jobs."""
        for job in jobs:
            self.queue.enqueue(job)
        return self._process_jobs(jobs)

    def _process_jobs(self, jobs: List[Job]) -> BatchResult:
        """Execute jobs in parallel."""
        result = BatchResult(total=len(jobs))

        if not jobs:
            return result

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for job in jobs:
                self.queue.update(job.id, JobStatus.RUNNING)
                future = executor.submit(self._run_job, job)
                futures[future] = job

            for future in as_completed(futures):
                job = futures[future]
                try:
                    output_dir = future.result()
                    self.queue.update(
                        job.id,
                        JobStatus.COMPLETED,
                        result_path=output_dir,
                    )
                    result.succeeded += 1
                except Exception as e:
                    self.queue.update(
                        job.id,
                        JobStatus.FAILED,
                        error=str(e),
                    )
                    result.failed += 1
                    result.errors.append(f"{job.id}: {e}")

        return result

    def _run_job(self, job: Job) -> str:
        """Run a single job. Returns output directory path."""
        engine = self.engine_factory()
        context = PipelineContext(
            source=job.input_ref,
            source_type=job.input_type,
            template_name=job.config_overrides.get("template", "md_script"),
            output_dir=job.config_overrides.get("output_dir"),
        )

        pipeline_result = engine.execute(context)

        if not pipeline_result.success:
            raise RuntimeError(
                pipeline_result.error or "Pipeline failed"
            )

        return context.output_dir or ""
