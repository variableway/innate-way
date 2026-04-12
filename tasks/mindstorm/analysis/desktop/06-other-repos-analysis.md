# 其他仓库分析

> 覆盖仓库: openase, openyak, pi-mono

## 1. OpenASE — 票据驱动自动化软件工程

**概述**: 将 GitHub Issue 和 JIRA 票据转为可工作代码的平台。AI Agent 自动领取票据、执行工作流、交付结果。

**技术栈**: Go 1.26 + SvelteKit (嵌入式前端) + PostgreSQL + Echo

**架构亮点**:
- 单 Go 二进制 + 嵌入式 Web UI（运行时无 Node.js）
- 票据驱动的编排模型
- 多 Agent 支持 (Claude Code, Codex, Gemini CLI)
- 工作流引擎 + Harness 文档 + Skills
- SSE 实时活动流

**可借鉴**:
- 票据管理 + 看板系统
- 单二进制部署模式
- SSH/本地机器管理 + 健康探测
- SSE 实时流

## 2. OpenYak — 本地 AI 助手

**概述**: 完全在桌面运行的本地 AI Agent，连接 100+ 模型/20+ Provider，管理文件、自动化工作流。

**技术栈**: **Tauri v2 (Rust)** + Next.js 15 + FastAPI + SQLite + Cloudflare Tunnel

**架构亮点**:
- Monorepo: 前端/后端/桌面分离
- Local-first 架构 + 文件系统访问
- QR 码远程访问 (Cloudflare Tunnel)
- Provider 无关 LLM 集成
- 工具执行环境 + 文件操作

**可借鉴**:
- **Tauri v2 桌面应用模式** — 直接参考
- 本地文件系统 API 访问
- Provider 无关 LLM 抽象层
- 桌面自动化工具执行框架
- SQLite 本地存储方案

## 3. Pi Mono — AI Agent 工具集

**概述**: 提供 AI Agent 构建工具和 LLM 部署管理的 Monorepo。包含编码 Agent、多 Provider LLM API、Agent Runtime、UI 组件。

**技术栈**: TypeScript/Node.js + Svelte (TUI) + WebSocket

**架构亮点**:
- Monorepo 包架构，关注点分离
- 终端 UI 差分渲染
- Web 组件聊天界面
- CLI Agent 执行

**可借鉴**:
- 多 Provider LLM API 抽象
- Agent Runtime + 工具调用 + 状态管理
- 终端 UI 框架差分渲染
- 包式架构的模块化 AI 工具

## 4. 三个项目的综合价值

| 项目 | 最佳贡献 | 对个人 Agent 桌面应用的价值 |
|------|----------|----------------------------|
| OpenASE | 工作流编排 + 单二进制部署 | ★★★★ |
| OpenYak | **Tauri v2 桌面模式** | ★★★★★ |
| Pi Mono | Agent Runtime + 多 Provider | ★★★★ |

**特别说明**: OpenYak 是 Tauri v2 在 AI 桌面应用中的直接参考，与当前项目的技术选型高度相关。

## 5. 代码参考

- `innate-desktop-reference/openase/`
- `innate-desktop-reference/openyak/`
- `innate-desktop-reference/pi-mono/`
