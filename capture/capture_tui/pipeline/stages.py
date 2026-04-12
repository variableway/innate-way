"""Pipeline stage base class and result types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .context import PipelineContext


class StageStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result from a single stage execution."""
    status: StageStatus
    stage_name: str
    duration_ms: float = 0.0
    warnings: List[str] = field(default_factory=list)
    error: Optional[Exception] = None


class Stage(ABC):
    """Base class for all pipeline stages."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def execute(self, context: PipelineContext) -> StageResult:
        ...

    def should_run(self, context: PipelineContext) -> bool:
        return True
