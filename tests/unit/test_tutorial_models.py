"""Unit tests for tutorial models."""

import pytest
from capture_tui.tutorial.models import (
    CodeBlock, ProseSection, ScriptDef, Tutorial, _slugify,
)


class TestSlugify:
    def test_basic(self):
        assert _slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert _slugify("How to: Run OpenClaw!") == "how-to-run-openclaw"

    def test_max_length(self):
        result = _slugify("a" * 100, max_len=10)
        assert len(result) <= 10

    def test_collapse_dashes(self):
        assert _slugify("foo---bar___baz") == "foo-bar-baz"


class TestCodeBlock:
    def test_to_dict_roundtrip(self):
        block = CodeBlock(language="bash", code="echo hello", is_executable=True)
        d = block.to_dict()
        restored = CodeBlock.from_dict(d)
        assert restored.language == "bash"
        assert restored.code == "echo hello"
        assert restored.is_executable is True


class TestScriptDef:
    def test_render_with_content(self):
        s = ScriptDef(filename="run.sh", content="#!/bin/bash\necho hi\n")
        assert s.render() == "#!/bin/bash\necho hi\n"

    def test_render_generated(self):
        s = ScriptDef(
            filename="setup.sh",
            commands=["echo hello", "echo world"],
            comments=["Setup script"],
            env_vars={"NAME": "test"},
        )
        rendered = s.render()
        assert "#!/usr/bin/env bash" in rendered
        assert "set -euo pipefail" in rendered
        assert "echo hello" in rendered
        assert 'NAME="test"' in rendered

    def test_to_dict_roundtrip(self):
        s = ScriptDef(filename="x.sh", language="bash")
        d = s.to_dict()
        restored = ScriptDef.from_dict(d)
        assert restored.filename == "x.sh"


class TestTutorial:
    def test_auto_slug(self):
        t = Tutorial(title="My Great Tutorial")
        assert t.slug == "my-great-tutorial"

    def test_auto_id(self):
        t = Tutorial(title="Test")
        assert t.id.startswith("tut-")

    def test_to_dict_roundtrip(self):
        t = Tutorial(
            title="Test Tutorial",
            code_blocks=[CodeBlock(language="bash", code="echo hi")],
            prose_sections=[ProseSection(title="Intro", content="Hello")],
            scripts=[ScriptDef(filename="run.sh")],
        )
        d = t.to_dict()
        restored = Tutorial.from_dict(d)
        assert restored.title == "Test Tutorial"
        assert len(restored.code_blocks) == 1
        assert len(restored.prose_sections) == 1
        assert len(restored.scripts) == 1

    def test_save(self, tmp_path):
        t = Tutorial(title="Save Test")
        meta = t.save(tmp_path / "output" / "test-tutorial")
        assert meta.exists()
        content = meta.read_text()
        assert "Save Test" in content
