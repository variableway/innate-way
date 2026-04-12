# Task 01: Monorepo 项目脚手架

## Feature
初始化 Monorepo: pnpm workspaces + Turborepo，包含 Web 端 (Next.js) 和 Desktop 端 (Tauri) 及共享 packages。

## 优先级
P0 - 阻塞所有其他任务

## 技术栈
- pnpm workspaces + Turborepo (Monorepo)
- Next.js 16 + React 19 + TypeScript (Web 端)
- Tauri v2 + React 19 + Vite 8 + TypeScript (Desktop 端)
- Tailwind CSS v4 (OKLCH) + shadcn/ui (共享)
- Rust (Desktop 后端)
- pnpm (包管理)

## 验收标准

### Monorepo 基础
- [ ] pnpm workspaces 配置
- [ ] Turborepo 配置 (build/dev/lint pipelines)
- [ ] 共享 TypeScript 配置 (`packages/tsconfig/`)
- [ ] 共享 ESLint + Prettier/Biome 配置

### Web 端 (apps/web)
- [ ] Next.js 16 + App Router 初始化
- [ ] React 19 + TypeScript 配置
- [ ] Tailwind CSS v4 + shadcn/ui
- [ ] 基础页面路由: `/` `/ideas` `/tasks` `/settings`
- [ ] API Routes 基础结构
- [ ] `pnpm dev` 可启动 Web

### Desktop 端 (apps/desktop)
- [ ] Tauri v2 项目初始化
- [ ] React 19 + TypeScript + Vite 8 前端
- [ ] Tailwind CSS v4 + shadcn/ui (与 Web 共享配置)
- [ ] Rust 后端基础结构: 模块化组织
- [ ] SQLite 集成 (tauri-plugin-sql)
- [ ] Store 集成 (tauri-plugin-store)
- [ ] `pnpm tauri dev` 可启动桌面应用

### 共享 Packages
- [ ] `@innate/ui` — shadcn/ui 组件 (internal package, 不预编译)
- [ ] `@innate/core` — 业务逻辑 + Platform Bridge + 数据类型
- [ ] `@innate/views` — 共享页面/视图组件

### 基础设施
- [ ] Git 仓库初始化 + .gitignore (覆盖 Rust/Node/IDE)
- [ ] CI/CD 基础 (GitHub Actions: lint + type-check + build)
- [ ] README: Monorepo 结构说明 + 开发指南

## 项目结构

```
innate-app/
├── package.json              ← pnpm workspaces
├── turbo.json                ← Turborepo 配置
├── pnpm-workspace.yaml
├── apps/
│   ├── web/                  ← Next.js 16
│   │   ├── app/              ← App Router
│   │   ├── package.json
│   │   └── next.config.ts
│   └── desktop/              ← Tauri v2
│       ├── src/              ← React + Vite
│       ├── src-tauri/        ← Rust 后端
│       ├── package.json
│       └── tauri.conf.json
├── packages/
│   ├── ui/                   ← @innate/ui (shadcn)
│   │   ├── components/
│   │   └── package.json
│   ├── core/                 ← @innate/core
│   │   ├── platform/         ← Platform Bridge
│   │   ├── types/            ← 共享类型
│   │   └── package.json
│   └── views/                ← @innate/views
│       ├── ideas/
│       ├── tasks/
│       └── package.json
└── .github/
    └── workflows/
```

## 参考代码
- Multica: `innate-desktop-reference/multica/` — **Monorepo + 共享 Packages 最佳参考**
- GitButler: `innate-desktop-reference/gitbutler/` — Tauri v2 项目结构
- OpenYak: `innate-desktop-reference/openyak/` — Tauri v2 + AI 桌面
- Holaboss: `innate-desktop-reference/holaboss-ai/` — Electron + React + Shadcn

## 依赖
无

## 预估复杂度
中-高 — Monorepo 配置 + 双端初始化
