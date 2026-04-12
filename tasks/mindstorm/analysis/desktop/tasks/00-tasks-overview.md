# 任务总览

## 架构决策

**Monorepo (Next.js Web + Tauri Desktop + 共享 Packages)**
详见: [09-architecture-comparison.md](../09-architecture-comparison.md)

## 任务依赖图

```
Task 01: Monorepo 项目脚手架 (P0)
    │
    ├──▶ Task 02: 设计系统 + 共享 Packages (P0)
    │       │
    │       └──▶ Task 03: App Shell 布局 (P0)
    │               │
    │               ├──▶ Task 07: Ideas 管理 (P1)
    │               │       │
    │               │       └──▶ Task 08: 任务管理 (P1)
    │               │
    │               └──▶ Task 09: Terminal (P2)
    │
    ├──▶ Task 04: Agent Runtime (P0)
    │       │
    │       ├──▶ Task 05: 记忆系统 (P0)
    │       │
    │       └──▶ Task 06: MCP 工具集成 (P1)
    │               │
    │               └──▶ Task 11: 飞书集成 (P2)
    │
    ├──▶ Task 10: Skills 系统 (P2)
    ├──▶ Task 12: Sidecar/Plugin (P2)
    ├──▶ Task 13: Cloud 同步 (P3)
    ├──▶ Task 14: 自动更新 (P3)
    └──▶ Task 15: Web 端 (P2)
```

## 优先级分组

### Phase 1: 基础框架 (P0)
| Task | 名称 | 预估复杂度 | 说明 |
|------|------|------------|------|
| 01 | Monorepo 项目脚手架 | 中 | pnpm workspaces + Turborepo + apps/web + apps/desktop + packages/ |
| 02 | 设计系统 + 共享 Packages | 中 | @innate/ui + @innate/core + 主题 |
| 03 | App Shell 布局 | 高 | Toolbar + Sidebar + Content + AI Panel |
| 04 | Agent Runtime | 非常高 | Rust 引擎 + Provider 抽象 + 权限 |
| 05 | 记忆系统 | 高 | 三层记忆 + SQLite + 压缩边界 |

### Phase 2: 核心功能 (P1)
| Task | 名称 | 预估复杂度 | 说明 |
|------|------|------------|------|
| 06 | MCP 工具集成 | 中-高 | MCP Client + 内置工具 |
| 07 | Ideas 管理 | 中 | 收集箱 + AI 分析 |
| 08 | 任务管理 | 高 | 看板 + 子任务 + Agent 分配 |

### Phase 3: 扩展功能 (P2)
| Task | 名称 | 预估复杂度 | 说明 |
|------|------|------------|------|
| 09 | Terminal 集成 | 中 | xterm.js + tauri-plugin-pty |
| 10 | Skills 系统 | 中 | 可复用技能 + 市场 |
| 11 | 飞书集成 | 中 | MCP Server + 数据同步 |
| 12 | Sidecar/Plugin | 中 | 进程管理 + 插件架构 |
| 15 | Web 端 | 高 | Next.js 独立功能 + Platform Bridge |

### Phase 4: 上线准备 (P3)
| Task | 名称 | 预估复杂度 | 说明 |
|------|------|------------|------|
| 13 | Cloud 同步 | 中 | Turso + 本地优先 |
| 14 | 自动更新 | 中 | tauri-plugin-updater |

## 技术栈确认

```
Monorepo:     pnpm workspaces + Turborepo

Web 端 (apps/web):
  Next.js 16 + React 19 + TypeScript
  shadcn/ui + Tailwind CSS v4 (OKLCH)
  Next.js API Routes

Desktop 端 (apps/desktop):
  Tauri v2 + React 19 + Vite 8 + TypeScript
  shadcn/ui + Tailwind CSS v4 (OKLCH)
  Rust 后端 (Tauri commands + plugins)
  SQLite (tauri-plugin-sql)

共享 (packages/):
  @innate/ui      — 组件 + 主题
  @innate/core    — 业务逻辑 + Platform Bridge + 数据模型
  @innate/views   — 共享页面/视图

基础设施:
  State:     Zustand + TanStack Query
  Terminal:  xterm.js + tauri-plugin-pty (桌面)
  MCP:       Rust MCP Client (桌面)
  Update:    tauri-plugin-updater (桌面)
  Sidecar:   Go/Python (桌面按需)
```

## 功能差异化

| 功能 | Web 端 | 桌面端 |
|------|--------|--------|
| Ideas 管理 | ✅ | ✅ |
| 任务看板 | ✅ | ✅ |
| AI 聊天 | ✅ (HTTP API) | ✅ (本地 Rust) |
| 记忆系统 | ✅ (服务端) | ✅ (本地 SQLite) |
| 文件系统 | ❌ | ✅ |
| 终端 | ❌ | ✅ |
| 本地 Agent | ❌ | ✅ |
| Sidecar | ❌ | ✅ |
| 系统托盘 | ❌ | ✅ |
| 离线使用 | ❌ | ✅ |
| SEO/公开访问 | ✅ | ❌ |
| 移动端浏览器 | ✅ | ❌ |

## 目标用户
个人用户、小团队 (≤10人)

## 关键风险
| 风险 | 缓解 |
|------|------|
| Monorepo 复杂度 | Multica 已验证模式，有参考 |
| Rust 学习曲线 | 先用 sidecar 渐进，关键路径 Rust |
| MCP 生态早期 | 先内置核心工具，MCP 可选 |
| tauri-plugin-pty 早期 | 备选: sidecar node-pty |
| AI 流式需要 Event 模式 | 从 Day 1 规划 Event 架构 |
| Web/Desktop 功能差异 | Platform Bridge 从一开始设计 |
