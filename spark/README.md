# Spark

Personal AI Assistant — Ideas, Tasks, Agents, all in one workspace.

## Architecture

Monorepo with shared packages:

```
spark/
├── apps/web/          Next.js 16 — Web app (SSR/SEO/API)
├── apps/desktop/      Tauri v2 — Desktop app (Rust + React)
├── packages/ui/       @spark/ui — Shared UI components (shadcn)
├── packages/core/     @spark/core — Business logic + Platform Bridge
├── packages/views/    @spark/views — Shared page views
└── packages/tsconfig/ @spark/tsconfig — Shared TypeScript configs
```

## Quick Start

```bash
# Install dependencies
pnpm install

# Web development
pnpm dev:web

# Desktop development
pnpm dev:desktop

# Build all
pnpm build
```

## Tech Stack

| Layer | Web | Desktop |
|-------|-----|---------|
| Framework | Next.js 16 | Tauri v2 + Vite |
| UI | React 19 + shadcn/ui | React 19 + shadcn/ui |
| Backend | Next.js API Routes | Rust (Tauri) |
| Database | PostgreSQL / Turso | SQLite |

## Target Users

Individuals and small teams (≤10 people).

## License

Private
