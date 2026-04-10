# Innate Way - 项目路线图

> 更新日期：2026-04-10

## 项目愿景

构建一个**个人 AI IDE**——从灵感捕获、任务编排到 AI 自动执行的完整工作流系统。让 AI 成为个人的超级助手，减少认知负担和决策疲劳。

---

## 已完成的工作

| 项目 | 状态 | 说明 |
|------|------|------|
| **innate-capture** (CLI) | ✅ 完成 | Python + Go 双实现，80 测试通过，跨平台构建 |
| **innate-capture** (Go TUI) | ✅ 完成 | Bubble Tea 看板、任务流管理 |
| **innate-chaos** | ✅ 基本完成 | HyperTrace 交易信号仪表盘 |
| **innate-next-mono** | ✅ 基础完成 | 50+ 共享 UI 组件库 |
| **spark-cli / spark-skills** | ✅ 已有基础 | CLI 工具 + AI Agent 技能集 |

---

## 接下来的工作（按优先级）

### P0 — 基础设施

#### 1. 搭建 Desktop/Web 应用架构

- 扩展 `innate-next-mono` 为 monorepo
- `apps/desktop/`（Tauri 2.x）+ `apps/web/`（Next.js）
- 共享 `packages/`（capture-core 等）
- 技术栈：Next.js 16+, React 19, TypeScript, Tailwind, shadcn/ui

#### 2. 分类管理 UI 功能

- 读取 TUI 分类文件夹结构
- 设置页配置分类路径
- CRUD 操作（最多 10 个分类）

### P0 — Agent 系统

#### 3. 本地任务编排 Daemon (Go)

- SQLite 任务队列轮询
- 分发到多个 AI Agent（Claude, Codex, Kimi, OpenClaw）
- 执行监控、日志捕获、状态更新
- 飞书通知集成

#### 4. 多 Agent 统一接口

- 会话管理和上下文保持
- 错误恢复和重试机制
- 进度追踪

### P1 — AI 增强

#### 5. 内容分析与总结

- AI 摘要生成、趋势分析
- 任务优先级决策支持
- 对话记录集成

### P2 — 高级功能

#### 6. 导出与集成

- 多格式导出（CSV, JSON, Markdown）
- 飞书多维表格
- TODO Dashboard

#### 7. 知识管理

- 本地研究 Wiki + RAG
- 跨项目知识共享

---

## 建议切入点

**Desktop/Web 应用架构搭建**（P0 #1），理由：

- 所有后续 UI 功能的基础
- 可复用 `innate-next-mono` 已有的 50+ 组件
- 与 capture-core 共享逻辑，连接已有 CLI 工具
- Tauri 2.x 提供成熟的跨平台桌面能力
