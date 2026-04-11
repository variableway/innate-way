"""Unit tests for pipeline engine and stages."""

import pytest
from capture_tui.pipeline.context import PipelineContext
from capture_tui.pipeline.engine import PipelineConfig, PipelineEngine, PipelineResult
from capture_tui.pipeline.errors import RetryPolicy
from capture_tui.pipeline.stages import Stage, StageResult, StageStatus


class FakeStage(Stage):
    """Stage that always succeeds."""
    @property
    def name(self) -> str:
        return "fake"

    def execute(self, context: PipelineContext) -> StageResult:
        context.metadata["ran"] = True
        return StageResult(status=StageStatus.SUCCESS, stage_name=self.name)


class FailingStage(Stage):
    """Stage that always fails."""
    @property
    def name(self) -> str:
        return "fail"

    def execute(self, context: PipelineContext) -> StageResult:
        return StageResult(
            status=StageStatus.FAILED,
            stage_name=self.name,
            error=RuntimeError("boom"),
        )


class SkipStage(Stage):
    """Stage that should be skipped."""
    @property
    def name(self) -> str:
        return "skip"

    def should_run(self, context: PipelineContext) -> bool:
        return False

    def execute(self, context: PipelineContext) -> StageResult:
        raise AssertionError("Should not be called")


class TestPipelineEngine:
    def test_success_flow(self):
        engine = PipelineEngine(PipelineConfig(stages=[FakeStage()]))
        ctx = PipelineContext()
        result = engine.execute(ctx)
        assert result.success
        assert ctx.metadata["ran"] is True

    def test_failure_stops_pipeline(self):
        engine = PipelineEngine(PipelineConfig(
            stages=[FailingStage(), FakeStage()],
            on_failure="stop",
        ))
        result = engine.execute(PipelineContext())
        assert not result.success
        assert len(result.stage_results) == 1

    def test_skip_stage(self):
        engine = PipelineEngine(PipelineConfig(stages=[SkipStage()]))
        result = engine.execute(PipelineContext())
        assert result.success
        assert result.stage_results[0].status == StageStatus.SKIPPED

    def test_continue_on_failure(self):
        engine = PipelineEngine(PipelineConfig(
            stages=[FailingStage(), FakeStage()],
            on_failure="continue",
        ))
        result = engine.execute(PipelineContext())
        assert result.success  # pipeline completes even with failures in "continue" mode
        assert len(result.stage_results) == 2


class TestRetryPolicy:
    def test_retry_on_retryable_error(self):
        call_count = 0

        class FlakeyStage(Stage):
            @property
            def name(self) -> str:
                return "flakey"

            def execute(self, context: PipelineContext) -> StageResult:
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise ConnectionError("timeout")
                return StageResult(status=StageStatus.SUCCESS, stage_name=self.name)

        engine = PipelineEngine(PipelineConfig(
            stages=[FlakeyStage()],
            retry_policy=RetryPolicy(max_retries=3, backoff_base=0.01),
        ))
        result = engine.execute(PipelineContext())
        assert result.success
        assert call_count == 3
