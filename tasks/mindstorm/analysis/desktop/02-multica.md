# Multica 分析

> 优先级: ★★★ 重点参考

## 1. 项目概述

Multica 是一个开源托管 Agent 平台，将 AI 编码 Agent 转变为真正的团队成员。本质上是一个任务管理系统（类似 Linear/Jira），但 AI Agent 是一等公民。

### 核心功能
- **Agent 即队友**: Agent 有档案、看板展示、发布评论、创建 Issue、报告阻塞
- **自主执行**: 完整的任务生命周期管理，WebSocket 实时进度流
- **可复用技能**: 每个解决方案成为全团队可复用的技能
- **统一运行时**: 一个 Dashboard 管理所有计算环境（本地守护进程和云运行时）
- **多工作空间**: 工作空间级隔离
- **多 Agent 支持**: Claude Code, Codex, OpenClaw, OpenCode

## 2. 技术栈

### 前端
| 层面 | 技术 |
|------|------|
| 框架 | Next.js 16 (App Router) + React 19 |
| 桌面 | Electron (electron-vite) |
| 样式 | Tailwind CSS v4 (OKLCh) + shadcn/ui |
| 状态管理 | Zustand (客户端) + TanStack Query (服务端) |
| 图标 | Lucide React |

### 后端
| 层面 | 技术 |
|------|------|
| 语言 | Go 1.26.1 |
| 路由 | Chi |
| 数据库 | PostgreSQL 17 + pgvector |
| 实时通信 | Gorilla WebSocket |
| 认证 | JWT |
| 基础设施 | Docker, AWS S3/Secrets Manager |

## 3. 架构分析

### 项目结构
```
multica/
├── server/                    # Go 后端
│   ├── cmd/                  # CLI 命令 (server, daemon, CLI)
│   ├── internal/             # 内部包
│   │   ├── handler/          # HTTP 处理器
│   │   ├── daemon/           # Agent 守护进程逻辑
│   │   └── middleware/       # 认证、CORS 等
│   └── pkg/agent/            # Agent 执行接口
├── apps/
│   ├── web/                  # Next.js Web 应用
│   └── desktop/              # Electron 桌面应用
└── packages/                 # 共享 React 包
    ├── core/                 # 业务逻辑（平台无关）
    ├── ui/                   # 原子 UI 组件
    ├── views/                # 共享业务页面/组件
    └── tsconfig/             # 共享 TypeScript 配置
```

### 关键架构决策

#### 1. 内部包模式 (Internal Packages)
- 所有共享包导出原始 `.ts/.tsx` 文件
- 消费应用的 bundler 直接编译
- 零配置 HMR，即时 go-to-definition

#### 2. 平台桥接 (Platform Bridge)
```typescript
// 平台无关核心 → 平台特定实现
interface PlatformAdapter {
  navigate(path: string): void;
  openExternal(url: string): void;
}
```

#### 3. 严格状态边界
- **TanStack Query**: 管理所有服务端状态
- **Zustand**: 管理所有客户端状态
- **React Context**: 仅用于跨切面平台管道

### 关键数据结构

```typescript
// Agent 定义
interface Agent {
  id: string;
  workspace_id: string;
  name: string;
  instructions: string;
  skills: Skill[];
  status: "idle" | "working" | "blocked" | "error" | "offline";
}

// 任务生命周期
type TaskStatus = "queued" | "dispatched" | "running" | "completed" | "failed" | "cancelled";

// 运行时设备
interface RuntimeDevice {
  id: string;
  provider: string;
  status: "online" | "offline";
}
```

### Agent 执行架构

```go
// 统一 Agent 接口
type Backend interface {
    Execute(ctx context.Context, prompt string, opts ExecOptions) (*Session, error)
}

// Daemon 模式
daemon.pollLoop() → daemon.handleTask() → backend.Execute()
```

**执行流程**:
1. Daemon 后台运行 → 检测可用 Agent CLI
2. 注册为运行时 → 轮询任务
3. 隔离工作目录 → 注入运行时配置
4. WebSocket 实时流 → 任务消息转发

## 4. Agent 运行时引擎

### 守护进程模式
- 后台进程轮询工作
- 检测 PATH 上可用的 Agent CLI
- 每个任务创建隔离工作目录
- 保留工作目录供未来任务复用

### 实时通信
```go
type TaskMessage struct {
    Type    string // "text", "thinking", "tool_use", "tool_result"
    Content string
    Tool    string
}
```

### 技能系统
- 技能存储在工作空间中
- 执行时注入到 Agent 环境
- 随时间积累（组织记忆）

## 5. 可借鉴的功能

### 高度可借鉴
1. **Daemon 模式** - 后台守护进程轮询 + 隔离执行环境，非常适合个人 Agent
2. **跨平台 UI 架构** - Internal Packages + Platform Bridge，一套代码 Web+Desktop
3. **实时任务管理** - WebSocket + 乐观更新
4. **技能/模板系统** - 解决方案积累为可复用技能
5. **状态管理架构** - Query(服务端) + Zustand(客户端) 严格分离
6. **工作空间隔离** - 多租户架构模式

### 关键设计模式
| 模式 | 说明 | 适用性 |
|------|------|--------|
| Daemon Worker | 后台进程轮询任务 | ★★★★★ |
| Platform Bridge | 平台无关核心 | ★★★★★ |
| Internal Packages | 共享包零编译 | ★★★★ |
| Skill Compound | 技能随时间积累 | ★★★★ |
| Workspace Isolation | 工作空间级隔离 | ★★★★ |

## 6. 对当前项目的适用性

| 方面 | 适用度 | 说明 |
|------|--------|------|
| Daemon Agent 执行 | ★★★★★ | 个人 Agent 核心运行模式 |
| 任务看板系统 | ★★★★★ | 个人任务管理的完美参考 |
| 跨平台 UI | ★★★★★ | Web+Desktop 一套代码 |
| 技能系统 | ★★★★ | 个人工作流积累 |
| 多 Agent 支持 | ★★★ | 个人使用简化即可 |
| Go 后端 | ★★★ | 可参考设计，不一定要用 Go |

## 7. 代码参考

源码位置: `innate-desktop-reference/multica/`
