"""Pipeline error types and retry policy."""

from dataclasses import dataclass
from typing import Tuple, Type, Optional


@dataclass
class RetryPolicy:
    """Retry configuration for pipeline stages."""
    max_retries: int = 3
    backoff_base: float = 2.0
    max_backoff: float = 60.0
    retryable_exceptions: Tuple[Type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )


class PipelineError(Exception):
    """Base error for pipeline operations."""


class StageError(PipelineError):
    """Error from a specific pipeline stage."""

    def __init__(self, stage_name: str, message: str, cause: Optional[Exception] = None):
        self.stage_name = stage_name
        self.cause = cause
        super().__init__(f"[{stage_name}] {message}")


class FetchError(StageError):
    """Error during content fetching."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__("fetch", message, cause)


class ParseError(StageError):
    """Error during content parsing."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__("parse", message, cause)


class ExtractionError(StageError):
    """Error during code extraction."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__("extract_code", message, cause)


class RenderError(StageError):
    """Error during template rendering."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__("render", message, cause)
