"""Fetch stage: retrieve content from URL, file, or raw text."""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from capture_tui.pipeline.context import PipelineContext
from capture_tui.pipeline.errors import FetchError
from capture_tui.pipeline.stages import Stage, StageResult, StageStatus


class FetchStage(Stage):
    """Fetch content from a source (URL, file path, or raw text)."""

    @property
    def name(self) -> str:
        return "fetch"

    def execute(self, context: PipelineContext) -> StageResult:
        source = context.source.strip()
        if not source:
            return StageResult(
                status=StageStatus.FAILED,
                stage_name=self.name,
                error=ValueError("Empty source"),
            )

        try:
            source_type = self._detect_type(source)
            context.source_type = source_type

            if source_type == "url":
                self._fetch_url(context)
            elif source_type == "file":
                self._fetch_file(context)
            else:
                self._fetch_text(context)

            return StageResult(status=StageStatus.SUCCESS, stage_name=self.name)

        except Exception as e:
            raise FetchError(str(e), cause=e) from e

    def _detect_type(self, source: str) -> str:
        """Detect source type: url, file, or text."""
        if source.startswith(("http://", "https://")):
            return "url"
        path = Path(source)
        if path.exists() and path.is_file():
            return "file"
        return "text"

    def _fetch_url(self, context: PipelineContext):
        """Fetch content from URL using httpx."""
        try:
            import httpx
        except ImportError:
            raise FetchError(
                "httpx not installed. Run: pip install httpx"
            )

        url = context.source
        timeout = self.config.get("timeout", 30)

        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            context.raw_content = resp.text
            context.metadata["source_url"] = url
            context.metadata["domain"] = urlparse(url).netloc
            context.metadata["content_type"] = resp.headers.get(
                "content-type", ""
            )

    def _fetch_file(self, context: PipelineContext):
        """Read content from local file."""
        path = Path(context.source)
        context.raw_content = path.read_text(encoding="utf-8")
        context.metadata["file_name"] = path.name
        context.metadata["file_suffix"] = path.suffix

    def _fetch_text(self, context: PipelineContext):
        """Use raw text content directly."""
        context.raw_content = context.source
