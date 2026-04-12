"""Parse stage: normalize HTML/markdown/text content."""

import re
from typing import List, Optional

from capture_tui.pipeline.context import PipelineContext, ProseSection
from capture_tui.pipeline.errors import ParseError
from capture_tui.pipeline.stages import Stage, StageResult, StageStatus


class ParseStage(Stage):
    """Parse and normalize fetched content."""

    @property
    def name(self) -> str:
        return "parse"

    def execute(self, context: PipelineContext) -> StageResult:
        try:
            content = context.raw_content
            if not content:
                return StageResult(
                    status=StageStatus.FAILED,
                    stage_name=self.name,
                    error=ValueError("No content to parse"),
                )

            content_type = context.metadata.get("content_type", "")
            file_suffix = context.metadata.get("file_suffix", "")

            # Determine format
            if "html" in content_type or "<html" in content[:500].lower():
                content = self._html_to_markdown(content)
            elif file_suffix in (".md", ".markdown") or self._looks_like_markdown(content):
                content = self._normalize_markdown(content)
            else:
                content = self._normalize_text(content)

            # Extract title
            title = self._extract_title(content)
            if title:
                context.title = title

            # Extract prose sections
            context.prose_sections = self._extract_sections(content)
            context.parsed_content = content

            return StageResult(status=StageStatus.SUCCESS, stage_name=self.name)

        except Exception as e:
            raise ParseError(str(e), cause=e) from e

    def _looks_like_markdown(self, text: str) -> bool:
        """Check if content looks like markdown."""
        indicators = ["# ", "## ", "```", "---\n", "- [", "* ["]
        return any(ind in text[:2000] for ind in indicators)

    def _html_to_markdown(self, html: str) -> str:
        """Convert HTML to simplified markdown."""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # Fallback: strip tags
            text = re.sub(r"<[^>]+>", "", html)
            return self._normalize_text(text)

        soup = BeautifulSoup(html, "html.parser")

        # Remove script/style
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        lines = []
        for el in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            level = int(el.name[1])
            lines.append(f"{'#' * level} {el.get_text(strip=True)}")
            lines.append("")

        for el in soup.find_all("p"):
            text = el.get_text(strip=True)
            if text:
                lines.append(text)
                lines.append("")

        for el in soup.find_all("pre"):
            code = el.get_text()
            code_tag = el.find("code")
            lang = ""
            if code_tag and code_tag.get("class"):
                for cls in code_tag["class"]:
                    if cls.startswith(("language-", "lang-")):
                        lang = cls.split("-", 1)[1]
                        break
            lines.append(f"```{lang}")
            lines.append(code.rstrip())
            lines.append("```")
            lines.append("")

        # Lists
        for el in soup.find_all("li"):
            lines.append(f"- {el.get_text(strip=True)}")
        lines.append("")

        return "\n".join(lines)

    def _normalize_markdown(self, text: str) -> str:
        """Normalize markdown content."""
        # Remove frontmatter
        text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
        # Normalize line endings
        text = text.replace("\r\n", "\n")
        # Collapse excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _normalize_text(self, text: str) -> str:
        """Normalize plain text content."""
        text = text.replace("\r\n", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _extract_title(self, content: str) -> Optional[str]:
        """Extract title from content."""
        m = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
        if m:
            return m.group(1).strip()
        return None

    def _extract_sections(self, content: str) -> List[ProseSection]:
        """Extract prose sections from markdown."""
        sections = []
        pos = 0
        lines = content.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                level = len(heading.group(1))
                title = heading.group(2).strip()

                # Collect content until next heading
                content_lines = []
                j = i + 1
                while j < len(lines) and not re.match(r"^#{1,6}\s+", lines[j]):
                    content_lines.append(lines[j])
                    j += 1

                sections.append(ProseSection(
                    title=title,
                    content="\n".join(content_lines).strip(),
                    level=level,
                    position=pos,
                ))
                pos += 1
                i = j
            else:
                i += 1

        return sections
