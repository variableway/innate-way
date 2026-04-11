"""Pipeline package: generic pipeline runtime for stage-based processing."""

from capture_tui.pipeline.errors import (
    PipelineError,
    StageError,
    FetchError,
    ParseError,
    ExtractionError,
    RenderError,
    RetryPolicy,
)

__all__ = [
    "PipelineError",
    "StageError",
    "FetchError",
    "ParseError",
    "ExtractionError",
    "RenderError",
    "RetryPolicy",
]
