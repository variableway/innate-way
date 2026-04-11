"""Unit tests for tutorial pipeline stages."""

import pytest
from pathlib import Path

from capture_tui.pipeline.context import PipelineContext
from capture_tui.pipeline.stages import StageStatus
from capture_tui.tutorial.stages.fetch import FetchStage
from capture_tui.tutorial.stages.parse import ParseStage
from capture_tui.tutorial.stages.extract_code import CodeExtractionStage
from capture_tui.tutorial.stages.generate_script import GenerateScriptStage
from capture_tui.tutorial.stages.render import RenderStage


class TestFetchStage:
    def test_fetch_text(self):
        stage = FetchStage()
        ctx = PipelineContext(source="Hello World")
        result = stage.execute(ctx)
        assert result.status == StageStatus.SUCCESS
        assert ctx.source_type == "text"
        assert ctx.raw_content == "Hello World"

    def test_fetch_file(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Hello\n\nWorld")
        stage = FetchStage()
        ctx = PipelineContext(source=str(f))
        result = stage.execute(ctx)
        assert result.status == StageStatus.SUCCESS
        assert ctx.source_type == "file"
        assert "# Hello" in ctx.raw_content

    def test_fetch_empty_source(self):
        stage = FetchStage()
        ctx = PipelineContext(source="")
        result = stage.execute(ctx)
        assert result.status == StageStatus.FAILED


class TestParseStage:
    def test_parse_markdown(self):
        stage = ParseStage()
        ctx = PipelineContext(raw_content="# My Title\n\n## Section\n\nHello\n\n## Another\n\nWorld")
        result = stage.execute(ctx)
        assert result.status == StageStatus.SUCCESS
        assert ctx.title == "My Title"
        assert len(ctx.prose_sections) == 3  # h1 title + 2 sections

    def test_parse_empty(self):
        stage = ParseStage()
        ctx = PipelineContext(raw_content="")
        result = stage.execute(ctx)
        assert result.status == StageStatus.FAILED

    def test_parse_with_code_blocks(self):
        content = "# Tutorial\n\n```bash\necho hello\n```\n\nSome text."
        stage = ParseStage()
        ctx = PipelineContext(raw_content=content)
        result = stage.execute(ctx)
        assert result.status == StageStatus.SUCCESS
        assert ctx.title == "Tutorial"


class TestCodeExtractionStage:
    def test_extract_fenced_blocks(self):
        content = "# Title\n\n```bash\necho hello\n```\n\n```python\nprint('hi')\n```"
        stage = CodeExtractionStage()
        ctx = PipelineContext(parsed_content=content)
        result = stage.execute(ctx)
        assert result.status == StageStatus.SUCCESS
        assert len(ctx.code_blocks) == 2
        assert ctx.code_blocks[0].language == "bash"
        assert ctx.code_blocks[1].language == "python"

    def test_extract_empty(self):
        stage = CodeExtractionStage()
        ctx = PipelineContext(parsed_content="Just text, no code.")
        result = stage.execute(ctx)
        assert result.status == StageStatus.PARTIAL
        assert len(ctx.code_blocks) == 0

    def test_extract_inline_commands(self):
        content = "Run `npm install express` then `pip install flask`"
        stage = CodeExtractionStage()
        ctx = PipelineContext(parsed_content=content)
        result = stage.execute(ctx)
        assert len(ctx.code_blocks) >= 2


class TestGenerateScriptStage:
    def test_generate_from_blocks(self):
        from capture_tui.pipeline.context import CodeBlock
        stage = GenerateScriptStage()
        ctx = PipelineContext(
            title="Test Tutorial",
            code_blocks=[
                CodeBlock(language="bash", code="echo hello", is_executable=True),
                CodeBlock(language="bash", code="echo world", is_executable=True),
            ],
        )
        result = stage.execute(ctx)
        assert result.status == StageStatus.SUCCESS
        assert len(ctx.scripts) == 1
        assert "#!/usr/bin/env bash" in ctx.scripts[0].render()

    def test_no_executable_blocks(self):
        from capture_tui.pipeline.context import CodeBlock
        stage = GenerateScriptStage()
        ctx = PipelineContext(
            code_blocks=[CodeBlock(language="json", code='{"a": 1}', is_executable=False)],
        )
        result = stage.execute(ctx)
        assert result.status == StageStatus.PARTIAL


class TestRenderStage:
    def test_render_md_script(self, tmp_path):
        from capture_tui.pipeline.context import CodeBlock, ScriptDef
        stage = RenderStage(config={"output_base": str(tmp_path)})
        ctx = PipelineContext(
            title="Test Tutorial",
            template_name="md_script",
            code_blocks=[CodeBlock(language="bash", code="echo hi", is_executable=True)],
            scripts=[ScriptDef(filename="setup.sh", content="#!/bin/bash\necho hi\n")],
            metadata={"source_url": "https://example.com"},
        )
        result = stage.execute(ctx)
        assert result.status == StageStatus.SUCCESS
        assert ctx.output_dir
        assert (Path(ctx.output_dir) / "README.md").exists()
        assert (Path(ctx.output_dir) / "setup.sh").exists()
        assert (Path(ctx.output_dir) / "tutorial.json").exists()

    def test_render_md_only(self, tmp_path):
        stage = RenderStage(config={"output_base": str(tmp_path)})
        ctx = PipelineContext(
            title="MD Only Test",
            template_name="md_only",
        )
        result = stage.execute(ctx)
        assert result.status == StageStatus.SUCCESS
        assert (Path(ctx.output_dir) / "README.md").exists()
        assert not (Path(ctx.output_dir) / "setup.sh").exists()
