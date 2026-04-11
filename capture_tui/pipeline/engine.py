"""Pipeline engine: orchestrates stage execution."""

import time
from dataclasses import dataclass, field
from typing import List, Optional

from .context import PipelineContext
from .errors import RetryPolicy, StageError
from .stages import Stage, StageResult, StageStatus


@dataclass
class PipelineResult:
    """Result of a full pipeline run."""
    success: bool
    stage_results: List[StageResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    error: Optional[Exception] = None


@dataclass
class PipelineConfig:
    """Pipeline configuration."""
    stages: List[Stage]
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    on_failure: str = "stop"  # "stop" | "skip" | "continue"


class PipelineEngine:
    """Orchestrates sequential stage execution."""

    def __init__(self, config: PipelineConfig):
        self.config = config

    def execute(self, context: PipelineContext) -> PipelineResult:
        """Run all stages in order."""
        start = time.monotonic()
        results: List[StageResult] = []

        for stage in self.config.stages:
            if not stage.should_run(context):
                results.append(StageResult(
                    status=StageStatus.SKIPPED,
                    stage_name=stage.name,
                ))
                continue

            result = self._execute_with_retry(stage, context)
            results.append(result)

            if result.status == StageStatus.FAILED:
                if self.config.on_failure == "stop":
                    return PipelineResult(
                        success=False,
                        stage_results=results,
                        total_duration_ms=(time.monotonic() - start) * 1000,
                        error=result.error,
                    )
                # "skip" or "continue" - move on

        return PipelineResult(
            success=True,
            stage_results=results,
            total_duration_ms=(time.monotonic() - start) * 1000,
        )

    def _execute_with_retry(self, stage: Stage, context: PipelineContext) -> StageResult:
        """Execute a stage with retry logic."""
        policy = self.config.retry_policy
        last_error: Optional[Exception] = None

        for attempt in range(policy.max_retries + 1):
            stage_start = time.monotonic()
            try:
                result = stage.execute(context)
                result.duration_ms = (time.monotonic() - stage_start) * 1000
                return result
            except tuple(policy.retryable_exceptions) as e:
                last_error = e
                if attempt < policy.max_retries:
                    backoff = min(
                        policy.backoff_base ** attempt,
                        policy.max_backoff,
                    )
                    time.sleep(backoff)
            except StageError as e:
                return StageResult(
                    status=StageStatus.FAILED,
                    stage_name=stage.name,
                    duration_ms=(time.monotonic() - stage_start) * 1000,
                    error=e,
                )
            except Exception as e:
                return StageResult(
                    status=StageStatus.FAILED,
                    stage_name=stage.name,
                    duration_ms=(time.monotonic() - stage_start) * 1000,
                    error=e,
                )

        return StageResult(
            status=StageStatus.FAILED,
            stage_name=stage.name,
            error=last_error,
        )
