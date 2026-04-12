"""Template base class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from capture_tui.tutorial.models import Tutorial


class TutorialTemplate(ABC):
    """Base class for output templates."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def output_files(self) -> List[str]:
        ...

    @abstractmethod
    def render(self, tutorial: Tutorial, output_dir: Path) -> List[Path]:
        ...
