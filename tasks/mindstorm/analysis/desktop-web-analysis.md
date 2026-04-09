# Desktop & Web Application Analysis

## Source
Mindstorm file: `tasks/mindstorm/capture/Desktop-Web.md`
GitHub Issue: #3

## Overview

The goal is to build both a **Desktop application** (via Tauri) and a **Web application** that share the same UI components and frontend tech stack. The application will provide a GUI for the existing Capture TUI functionality, starting with category management.

## Key Requirements

### 1. Dual Application Types
- **Desktop App**: Built with Tauri 2.x + Next.js for native cross-platform support
- **Web App**: Same Next.js codebase running as a standard web application
- Both apps share identical UI components

### 2. Monorepo Structure
- Follow the `innate-next-mono` pattern: `apps/` + `packages/` with pnpm workspaces
- Shared packages: `ui/` (components), `utils/` (utilities), `tsconfig/` (TS configs)

### 3. Tech Stack (Shared)
| Technology | Purpose |
|------------|---------|
| Next.js 16+ | React framework (App Router) |
| TypeScript 5+ | Type safety |
| Tailwind CSS 4 | Styling |
| shadcn/ui | Component library |
| pnpm workspaces | Monorepo management |
| Tauri 2.x | Desktop packaging (desktop app only) |

### 4. Category Feature (Phase 1)
- Read the TUI category folder structure into the desktop app
- Settings page to configure which folder is the category folder
- Default category folder matches the CLI default path
- Max 10 categories (matching TUI constraint)

## Architecture Decision

### Monorepo Layout
```
innate-way/                          # Current project (planning docs, CLI tools)
innate-next-mono/                    # Existing monorepo (reference pattern)
  apps/
    desktop/                         # Tauri + Next.js desktop app
    web/                             # Next.js web app (same UI, no Tauri)
  packages/
    ui/                              # Shared shadcn/ui components
    utils/                           # Shared utilities
    tsconfig/                        # Shared TS configs
    capture-core/                    # Shared business logic (category management)
```

**Decision**: Place the new desktop/web apps in the existing `innate-next-mono` monorepo, extending it with new apps rather than creating a separate monorepo. This follows the user's instruction to use "mono-repo style like ../innate-next-mono structure."

### Shared vs App-Specific Code
- **Shared (packages/)**: UI components, utilities, TypeScript configs, capture business logic
- **Desktop-specific (apps/desktop/src-tauri/)**: Rust commands, Tauri IPC, native file system access
- **Web-specific (apps/web/)**: Web-optimized config (no Tauri, different build target)

### Category Data Flow
```
[TUI Category Folders] → [Rust/Tauri IPC or Web API] → [React UI]
```
- Desktop: Rust reads filesystem directly via Tauri commands
- Web: API endpoint reads filesystem (or uses browser storage as fallback)

## Dependencies on Existing Code

### From Capture TUI (Python)
- `capture_tui/models/category.py` — Category data model (name, display_name, count, description)
- `capture_tui/core/category_manager.py` — CRUD operations, max 10 categories constraint

### From Capture TUI (Go)
- `capture-tui-go/internal/models/category.go` — Category model

These will be reimplemented in TypeScript in a shared `capture-core` package.

## Risks & Considerations

1. **File system access**: Web app cannot directly access local filesystem — need API layer or browser storage fallback
2. **Tauri 2.x compatibility**: Must use `@tauri-apps/api` v2 patterns
3. **Next.js static export**: Tauri requires `output: 'export'` in next.config
4. **CSP security**: Development uses `csp: null`, production needs proper CSP
