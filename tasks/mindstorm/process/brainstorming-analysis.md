# Brainstorming Phase Analysis

> Task 2 of the Mindstorm Process — Analysis of mindmap tools, markdown conversion criteria, and workflow evaluation.

---

## 1. Top 5 Open-Source Mindmap Tools (Local File Saving)

### 1. Freeplane (Recommended)

- **License:** GPL v2+
- **Platform:** Windows / macOS / Linux
- **File Format:** `.mm` (XML-based, Freemind compatible)
- **Highlights:**
  - Actively maintained fork of FreeMind with significantly more features
  - Scripting support (Groovy), formula support, conditional styling
  - Export to Markdown, HTML, PDF, PNG, OPML
  - Local-first: all files saved on disk, no cloud dependency
  - Rich node formatting: icons, labels, links, notes
- **Why it fits:** Best balance of power and openness. The `.mm` format is widely supported and easy to parse for AI agent conversion. Has built-in Markdown export.

### 2. FreeMind

- **License:** GPL v2+
- **Platform:** Windows / macOS / Linux
- **File Format:** `.mm`
- **Highlights:**
  - The classic open-source mindmap tool, lightweight and fast
  - Simple, no-frills interface — good for quick brainstorming
  - Stable and mature (though less actively developed)
  - Local file save, XML-based format
- **Why it fits:** Minimal learning curve. If you want a simple tool that just works for capturing ideas without distractions, this is it. But consider Freeplane instead — it's a superset.

### 3. Draw.io (diagrams.net)

- **License:** Apache 2.0 (core)
- **Platform:** Web / Desktop (Electron)
- **File Format:** `.drawio` (XML), also supports `.mm` import
- **Highlights:**
  - General-purpose diagramming, not just mindmaps
  - Can save directly to local filesystem or GitHub
  - Desktop app works fully offline
  - Extensive shape libraries and templates
- **Why it fits:** If you also need flowcharts, architecture diagrams, etc., Draw.io handles them all in one tool. The trade-off is it's less specialized for mindmapping workflows.

### 4. Logseq (with mindmap plugin)

- **License:** AGPL v3
- **Platform:** Windows / macOS / Linux / Mobile
- **File Format:** `.md` (Markdown files on disk)
- **Highlights:**
  - Outliner + knowledge graph + mindmap (via plugin)
  - All data stored as plain Markdown files on disk
  - Bidirectional linking, daily journals, queries
  - Mindmap view is a plugin-rendered visualization of your existing notes
- **Why it fits:** This is the most interesting option for your workflow. Since Logseq stores everything as Markdown already, the "convert mindmap to markdown" step is essentially eliminated — the mindmap IS your markdown. However, the mindmap experience is less polished than dedicated tools.

### 5. Heimer

- **License:** GPL v3
- **Platform:** Linux / macOS (via Flatpak/brew)
- **File Format:** `.alz` (XML-based)
- **Highlights:**
  - Simple, focused mindmapping and thought diagramming
  - Designed specifically for brainstorming (not general diagramming)
  - Lightweight C++/Qt application, very fast
  - Local file save
- **Why it fits:** If you want a native desktop app that's focused purely on idea mapping without feature bloat.

### Comparison Table

| Tool | Local Save | Markdown Export | AI-Friendly Format | Active Dev | Ease of Use |
|------|-----------|----------------|-------------------|------------|-------------|
| **Freeplane** | Yes | Built-in | `.mm` XML (easy to parse) | Very active | Medium |
| **FreeMind** | Yes | Plugin | `.mm` XML | Low activity | Easy |
| **Draw.io** | Yes | Manual | `.drawio` XML | Active | Easy |
| **Logseq** | Yes | Native (`.md`) | Direct Markdown | Very active | Medium |
| **Heimer** | Yes | No (PNG/SVG only) | Less ideal | Moderate | Very Easy |

### Recommendation

**Primary choice: Freeplane** — most features, best export options, active community.  
**Alternative: Logseq** — if you want to skip the conversion step entirely and have your mindmap live as Markdown from the start.

---

## 2. Criteria for Converting Mindmap to Markdown Brainstorm Document

When asking an AI Agent to transform a mindmap into a structured Markdown brainstorm file, apply these criteria:

### 2.1 Structural Criteria

| Criterion | Description |
|-----------|-------------|
| **Hierarchical Preservation** | The markdown heading levels (H1→H2→H3...) must reflect the mindmap's node depth. Root = H1, first-level branches = H2, etc. |
| **Branch Ordering** | Related nodes should be grouped under the same parent heading. The order should follow the mindmap's visual layout (clockwise or logical flow). |
| **Orphan Node Handling** | Floating/unconnected nodes should be collected in an "Uncategorized Ideas" section at the end. |

### 2.2 Content Criteria

| Criterion | Description |
|-----------|-------------|
| **Node Text Fidelity** | Preserve the original text from each node. Do not paraphrase or summarize during conversion — the AI should transcribe, not interpret. |
| **Notes & Annotations** | Node notes (side content in mindmap) should become blockquotes (`>`) or indented paragraphs under the corresponding heading. |
| **Links & References** | Hyperlinks in nodes become Markdown links. Cross-node connections become `→ See also: [Section]` references. |
| **Labels & Icons** | Map icons/labels to emoji tags or text labels (e.g., `⚡ Priority`, `❓ Question`, `✅ Done`). |

### 2.3 Formatting Criteria

| Criterion | Description |
|-----------|-------------|
| **Metadata Header** | Include YAML frontmatter: date, source mindmap filename, topic, participant(s). |
| **One Idea Per Section** | Each terminal node (leaf) gets its own paragraph or bullet group, not merged with siblings. |
| **Visual Markers** | Use `---` horizontal rules to separate major branches. Use `**bold**` for key terms extracted from node labels. |
| **Actionability Marking** | If the brainstorm includes action items, mark them with `- [ ]` checkbox syntax. |

### 2.4 Quality Criteria

| Criterion | Description |
|-----------|-------------|
| **Completeness** | Every node in the mindmap must appear in the markdown. No dropped branches. |
| **Readability** | The document should be readable on its own, without needing to see the mindmap. Add transition sentences between major sections if needed. |
| **Losslessness** | The conversion should be reversible — a reader should be able to reconstruct the mindmap structure from the markdown alone. |
| **Conciseness** | No padding or filler content added by AI. The document captures what was brainstormed, nothing more. |

### 2.5 Example Output Structure

```markdown
---
date: 2026-04-11
source: my-brainstorm.mm
topic: Feature Planning for Capture Module
---

# Feature Planning for Capture Module

## Core Capture Features
> Notes from the central branch

### Quick Input
- Support TUI text input
- Support IM (Telegram/WeChat) input
- → See also: [IM Integration]

### Storage
- Local SQLite for offline-first
- Sync to cloud on demand

---

## IM Integration
- Telegram bot as input channel
- WeChat mini-program integration
- **Key concern:** message privacy

---

## Uncategorized Ideas
- Voice input support?
- Mobile app consideration
```

---

## 3. Workflow Evaluation: Is This Process Reasonable?

### The Proposed Flow

```
Idea Capture → Pick Ideas → Mindmap Brainstorm → AI Convert to Markdown → Review → AI Refine
```

### Assessment: Yes, This is a Sound Process

**Why it works:**

1. **Progressive structuring** — Ideas start loose (capture), get visual (mindmap), then get textual (markdown). Each step adds structure without losing the creative spark. This mirrors how human thinking actually works: scatter → cluster → organize.

2. **Low friction entry** — The mindmap is the right tool for brainstorming because it's non-linear. Traditional outlining (even in Markdown) forces sequential thinking too early. A mindmap lets you explore branches independently.

3. **AI as a bridge, not a creator** — Using AI to convert mindmap → markdown is a good use of AI because it's a mechanical transformation task, not a creative one. The human's ideas are preserved; AI just reformats them.

4. **Review + refine loop** — The human reviews the markdown, then asks AI to refine against criteria. This keeps the human in the loop for quality control while letting AI handle the tedious formatting work.

### Potential Pain Points and Mitigations

| Pain Point | Mitigation |
|-----------|------------|
| **Mindmap files are binary/XML** — not easy to version in git | Use Freeplane's `.mm` format (text XML) which git can diff. Or use Logseq where everything is Markdown. |
| **AI conversion may drop nodes** | Apply the "Completeness" criterion — always verify node count matches between mindmap and markdown. |
| **Context switching between tools** | Consider Logseq as an all-in-one option, or Freeplane + AI pipeline automation. |
| **Refinement can become circular** | Set a max of 2-3 refinement rounds. After that, the doc should be "good enough" and you move to next phase. |
| **Mindmap → Markdown loses visual relationships** | The "Losslessness" criterion addresses this. Add `→ See also` cross-references to preserve non-hierarchical connections. |

### Optimized Workflow Suggestion

```
1. Capture ideas (TUI / IM input)         → Raw idea pool
2. Select idea(s) for brainstorming        → Focused topic
3. Mindmap in Freeplane                    → Visual exploration
4. Save .mm file to project directory      → Version controlled
5. AI Agent: convert .mm → brainstorm.md   → Structured document
6. Human review: read, mark corrections    → Quality check
7. AI Agent: refine against criteria       → Polished document
8. (Repeat 6-7 if needed, max 3 rounds)   → Final output
9. Move brainstorm.md into project docs    → Actionable artifact
```

### Why This is User-Friendly

- **Step 1-2** are already built (capture module handles this)
- **Step 3** uses a visual tool (mindmaps are intuitive — no learning curve for basic use)
- **Step 4** is automatic (just save the file)
- **Step 5-7** are AI-assisted (minimal manual effort)
- **Step 8-9** are natural next steps

The total manual effort for the user is: **open mindmap tool → brainstorm → save file → review the generated doc**. Everything else is automated or AI-driven.

---

## Summary

| Question | Answer |
|----------|--------|
| **Best mindmap tool?** | **Freeplane** (most features, open source, local save, Markdown export). **Logseq** as alternative if you want native Markdown storage. |
| **Conversion criteria?** | 4 categories: Structural (hierarchy preserved), Content (fidelity to source), Formatting (consistent Markdown patterns), Quality (complete, readable, reversible). |
| **Is the process reasonable?** | Yes. Progressive structuring from loose ideas → visual map → structured doc is natural and low-friction. The main risk is tool-switching overhead, which can be mitigated by choosing the right tool combination. |

---

*Sources:*
- [6 Best Open Source Mind Mapping Tools - Wondershare](https://edrawmind.wondershare.com/drawing-tools/6-best-open-source-mind-mapping-tools.html)
- [Best Free and Open Source Mind Mapping Software - GoodFirms](https://www.goodfirms.co/mind-mapping-software/blog/best-free-and-open-source-mind-mapping-software)
- [23 Best Free Mind Mapping Software 2026 - The Digital Project Manager](https://thedigitalprojectmanager.com/tools/best-free-mind-mapping-software/)
- [Mind Map to Markdown Converter - Taskade](https://www.taskade.com/convert/mind-map/mind-map-to-markdown)
- [Markdown to Mind Map - MindMap AI](https://mindmapai.app/markdown-to-mindmap)
- [mindmap-mcp-server - Augment Code](https://www.augmentcode.com/mcp/mindmap-mcp-server)
