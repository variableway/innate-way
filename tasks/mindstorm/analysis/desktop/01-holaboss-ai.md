# Holaboss-AI 分析

> 优先级: ★★★ 重点参考

## 1. 项目概述

Holaboss 是一个 AI Workspace 桌面应用，支持构建、运行和打包具有长周期 Agent 能力的 AI 工作空间。系统超越简单的单次任务执行，支持角色持久化的 AI Agent，能在多个会话间保持状态、记忆和持续工作。

### 核心功能
- **AI 工作空间管理**: 创建和管理多个 AI 工作空间，配置不同 Agent、技能和能力
- **长周期 Agent**: 通过记忆、状态持久化和工作空间组织，Agent 跨会话保持连续性
- **多层记忆系统**: 会话连续性、工作空间知识、用户偏好
- **任务管理**: 基于工作空间上下文主动提议任务
- **桌面界面**: 三栏布局 - 文件浏览器、浏览器面板、AI 聊天
- **应用生态**: 通过市场安装应用和工作空间模板
- **技能框架**: 可复用的工作空间级技能扩展 Agent 能力

## 2. 技术栈

### 桌面应用
| 层面 | 技术 |
|------|------|
| 框架 | Electron |
| UI | React 19 + TypeScript |
| 构建 | Vite |
| 样式 | Tailwind CSS + Shadcn UI |
| 认证 | Better Auth (Electron 支持) |
| 数据库 | Better SQLite3 |
| 图标 | Lucide React |

### 运行时引擎
| 层面 | 技术 |
|------|------|
| 运行时 | Node.js 22+ |
| Web 框架 | Fastify |
| 数据库 | SQLite + sqlite-vec (向量搜索) |
| Agent 框架 | PI Agent Framework (Mario Zechner) |
| 工具集成 | MCP (Model Context Protocol) |

## 3. 架构分析

### 系统架构图
```
┌─────────────────────────────────────────────┐
│                Desktop App                   │
│  ┌──────────┬──────────┬──────────────────┐  │
│  │ File     │ Browser  │ Chat/AI          │  │
│  │ Explorer │ Pane     │ Interface        │  │
│  └──────────┴──────────┴──────────────────┘  │
│           │ Preload Bridge (IPC)              │
├───────────┼───────────────────────────────────┤
│           ▼                                   │
│  ┌──────────────────────────────────────┐    │
│  │         Runtime Engine               │    │
│  │  ┌────────────┬─────────────────┐    │    │
│  │  │ API Server │  State Store    │    │    │
│  │  │ (Fastify)  │  (SQLite+vec)  │    │    │
│  │  └────────────┴─────────────────┘    │    │
│  │  ┌────────────┬─────────────────┐    │    │
│  │  │ Harness    │  Harnesses      │    │    │
│  │  │ Host       │  (PI, etc.)     │    │    │
│  │  └────────────┴─────────────────┘    │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### 核心模块

| 模块 | 路径 | 功能 |
|------|------|------|
| API Server | `runtime/api-server/` | REST API、会话管理、执行编排 |
| State Store | `runtime/state-store/` | SQLite 数据访问层，向量搜索 |
| Harness Host | `runtime/harness-host/` | Agent 执行环境，PI 框架集成 |
| Harnesses | `runtime/harnesses/` | 可扩展的 Agent 框架适配 |
| SDK Bridge | `sdk/` | 集成代理和工作空间输出辅助 |

### 关键数据结构

```sql
-- 核心实体
workspaces        -- 工作空间定义
agent_sessions    -- Agent 会话管理
session_inputs    -- 用户请求和任务执行
turn_results      -- 执行结果和 token 使用
memory_entries    -- 持久记忆目录
compaction_boundaries -- 会话连续性产物
task_proposals    -- 主动任务建议
apps              -- 已安装工作空间应用
skills            -- 可复用工作空间技能
integrations      -- 外部服务连接
```

### Agent 执行流程
1. **会话初始化** → 用户输入创建带工作空间上下文的会话
2. **工作空间编译** → 编译 workspace.yaml 和 AGENTS.md
3. **能力投影** → 确定本次运行可用的工具和技能
4. **Prompt 组装** → 从记忆、会话状态和工作空间知识构建上下文
5. **Agent 执行** → PI Agent Framework 执行
6. **结果处理** → 捕获输出、token 使用和执行产物
7. **记忆演化** → 提取持久记忆并更新知识库
8. **连续性管理** → 创建压缩边界用于未来会话恢复

## 4. Agent 运行时引擎

### 记忆架构 (三层)
- **运行时连续性**: `.holaboss/` 目录中的会话特定状态
- **会话记忆**: 有界连续性快照，快速恢复
- **持久记忆**: Markdown 文件 + 元数据目录的工作空间知识
- **记忆类型**: facts, procedures, blockers, references

### 任务管理
- **主动系统**: 远程分析师生成任务建议
- **本地执行**: 建议在本地运行时执行
- **生命周期**: Created → Accepted → Executed → Completed

## 5. 可借鉴的功能

### 高度可借鉴
1. **工作空间中心设计** - 每个工作空间自包含，有自己的状态、记忆和配置
2. **长周期 Agent 架构** - 会话压缩边界实现高效状态恢复
3. **多层记忆系统** - 运行时/会话/持久三层记忆
4. **模块化运行时设计** - API Server / State Store / Harness Host 清晰分离
5. **Harness 模式** - 可扩展的 Agent 框架适配，支持多种后端

### 部分可借鉴
1. Electron 打包和分发模式
2. 三栏 UI 布局
3. OAuth 集成架构
4. 市场和应用生态系统

## 6. 对当前项目的适用性

| 方面 | 适用度 | 说明 |
|------|--------|------|
| 工作空间概念 | ★★★★★ | 直接可用于个人项目管理 |
| 记忆系统 | ★★★★★ | 个人 Agent 跨会话记忆核心需求 |
| Agent 运行时 | ★★★★ | Harness 模式可参考但需简化 |
| 桌面 UI | ★★★ | 可参考布局，但技术栈可能不同 |
| 技能框架 | ★★★★ | 可复用技能机制 |

## 7. 代码参考

源码位置: `innate-desktop-reference/holaboss-ai/`
