# 总体分析: Desktop App + Agent Runtime

> 基于 16 个参考仓库的综合分析

## 1. 技术栈对比: Tauri vs Electron

### 1.1 Tauri 的优势

| 维度 | 说明 |
|------|------|
| **安装包体积** | ~10-20MB vs Electron ~100MB+ |
| **内存占用** | 原生 shell，使用系统 WebView，无内嵌 Chromium |
| **安全性** | Rust 内存安全 + Tauri 细粒度权限模型 |
| **性能** | Rust 后端直接系统调用，无 Node.js 中间层 |
| **原生体验** | 更接近原生应用的外观和性能 |
| **跨平台** | macOS/Windows/Linux 全支持 |

**已验证的 Tauri 生产级案例**:
- **GitButler**: 50+ Rust crate 的复杂应用，证明 Tauri 可支撑大型项目
- **OpenYak**: Tauri v2 + AI Agent 的直接参考

### 1.2 Electron 迁移到 Tauri 的可行性

#### 可以完全满足的部分
- 所有 UI 渲染（WebView 已足够成熟）
- IPC 通信（Tauri Commands 等价于 Electron IPC）
- 系统集成（托盘、菜单、通知、文件对话框）
- 自动更新
- 原生模块（通过 Rust sidecar 或 Tauri 插件）

#### 难度和挑战

| 挑战 | 难度 | 解决方案 |
|------|------|----------|
| Node.js 原生模块 | ★★★★ | 需用 Rust 重写或 sidecar 进程 |
| npm 生态依赖 | ★★★ | 纯前端库无影响，Node 库需替代 |
| Better SQLite3 等 | ★★ | Tauri 有 Rust SQLite 插件 |
| 团队 Rust 经验 | ★★★★ | 学习曲线较陡，但长期收益大 |
| WebView 兼容性 | ★★ | 现代系统 WebView 已足够成熟 |

#### 代码迁移成本估算

| 组件 | 成本 | 说明 |
|------|------|------|
| 前端 UI (React/Svelte) | **低** | 几乎不变，仅 IPC 调用方式调整 |
| IPC 通信 | **中** | 需要重写为 Tauri Commands/Events |
| 状态管理 | **低** | 前端状态管理不变 |
| 后端逻辑 | **高** | Node.js → Rust 需要重写 |
| 原生功能 | **中** | 用 Tauri 插件替代 Electron API |
| 打包/分发 | **低** | Tauri 内置 CI/CD 支持 |

### 1.3 替代方案

| 方案 | 描述 | 适用场景 |
|------|------|----------|
| **Tauri v2 + React** | 推荐方案 | 平衡性能和生态 |
| **Tauri v2 + Svelte** | GitButler 方案 | 更轻量，编译更快 |
| **Wails (Go)** | Go 后端 + WebView | 如果偏好 Go 后端 |
| **Electron + Rust Sidecar** | 混合方案 | 渐进迁移路径 |
| **Neutralinojs** | 极轻量方案 | 简单应用 |
| **PWA + Tauri** | Web 优先 + 桌面壳 | 最大化 Web 复用 |

## 2. 推荐技术方案

### 2.1 推荐架构: Tauri v2 + Next.js/React + Rust

```
┌──────────────────────────────────────────────────┐
│                Tauri v2 Shell                     │
│  ┌───────────────────────────────────────────┐   │
│  │        Next.js / React Frontend           │   │
│  │  ┌─────────────────────────────────────┐  │   │
│  │  │  @innate/ui (shadcn + Tailwind)     │  │   │
│  │  │  Platform Bridge (Web ↔ Desktop)    │  │   │
│  │  └─────────────────────────────────────┘  │   │
│  └────────────────┬──────────────────────────┘   │
│                   │ Tauri IPC                     │
│  ┌────────────────▼──────────────────────────┐   │
│  │           Rust Backend                     │   │
│  │  ┌──────────┬──────────┬───────────────┐  │   │
│  │  │ Agent    │ Memory   │ Task          │  │   │
│  │  │ Runtime  │ Store    │ Manager       │  │   │
│  │  └──────────┴──────────┴───────────────┘  │   │
│  │  ┌──────────┬──────────┬───────────────┐  │   │
│  │  │ Tool     │ Workspace│ Integration   │  │   │
│  │  │ Registry │ Manager  │ Layer         │  │   │
│  │  └──────────┴──────────┴───────────────┘  │   │
│  └──────────────────────────────────────────┘   │
│                  SQLite (sqlite-vec)              │
└──────────────────────────────────────────────────┘
```

### 2.2 技术选型理由

| 选择 | 理由 | 参考来源 |
|------|------|----------|
| Tauri v2 | 体积小、性能好、安全、Rust 后端 | GitButler, OpenYak |
| React 19 | 生态最大、组件最多、人才多 | Multica, ClawX, Aperant |
| Zustand | 简洁、性能好 | Multica, ClawX |
| TanStack Query | 服务端状态管理标准 | Multica |
| SQLite + sqlite-vec | 本地优先、向量搜索 | Holaboss, Hermes |
| Tailwind + shadcn | 现代 UI 工具链 | 多个项目 |
| Rust 后端 | 性能 + 安全 + Agent Runtime | GitButler |

### 2.3 备选方案: 如果 Rust 学习成本太高

如果团队 Rust 经验不足，可采用 **Tauri v2 + Node.js Sidecar** 混合方案：
- Tauri 壳负责窗口管理和系统集成
- Node.js sidecar 进程处理 Agent Runtime 逻辑
- 前端不变
- 渐进式将性能关键部分迁移到 Rust

## 3. Desktop App 核心功能参考矩阵

| 功能 | 最佳参考 | 次优参考 |
|------|----------|----------|
| 三栏布局 | Holaboss (文件+浏览器+聊天) | — |
| 任务看板 | Multica (Agent 看板) | agtx (终端看板) |
| Agent 编排 | Aperant (多 Agent) | Archon (DAG 工作流) |
| 记忆系统 | Holaboss (三层记忆) | Hermes (FTS5) |
| 权限系统 | yakAgent (4 层权限) | GitButler (Agent 权限) |
| 技能市场 | rivonclaw (技能市场) | Multica (技能积累) |
| 热重载 | ClawX (技能热重载) | rivonclaw (配置热重载) |
| 自动更新 | GitButler (Tauri updater) | — |
| 多窗口 | GitButler (多项目) | — |
| 系统托盘 | rivonclaw (Tray-only) | — |

## 4. Ideas 收集与分析集成

### 4.1 Ideas 收集模块

参考多个项目的输入模式，设计 Ideas 收集系统：

```
输入源                    处理                      输出
┌──────────┐     ┌─────────────────┐     ┌──────────────┐
│ 手动输入  │────▶│                 │────▶│              │
│ 聊天捕获  │────▶│  Ideas Inbox    │────▶│  分类/标签    │
│ 网页剪藏  │────▶│  (Holaboss式    │────▶│  优先级评估   │
│ 文件导入  │────▶│   任务提议)     │────▶│  关联分析     │
│ API 接入  │────▶│                 │────▶│              │
└──────────┘     └─────────────────┘     └──────────────┘
```

### 4.2 分析引擎

```
Ideas ──▶ AI 分析 Agent ──▶ 分析报告
              │
              ├── 可行性评估
              ├── 技术方案建议
              ├── 工作量估算
              └── 依赖关系分析
```

### 4.3 任务拆解

```
分析报告 ──▶ 任务拆解 Agent ──▶ 子任务列表
                │
                ├── 自动拆解 (Archon DAG 模式)
                ├── 依赖排序
                ├── 分配到看板
                └── 进度追踪
```

### 4.4 集成策略

| 模块 | 数据结构 | 存储 | 触发方式 |
|------|----------|------|----------|
| Ideas Inbox | `idea{title, content, source, tags, priority}` | SQLite | 手动 + Agent 自动 |
| 分析结果 | `analysis{idea_id, feasibility, suggestion, estimate}` | SQLite | Agent 处理 |
| 任务拆解 | `task{parent_id, title, status, assignee, deps[]}` | SQLite | 手动 + 自动 |
| 执行追踪 | `execution{task_id, agent_id, status, progress}` | SQLite + WebSocket | Agent 运行时 |

## 5. 飞书 CLI 集成方案

### 5.1 集成架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  飞书 CLI     │────▶│  Integration │────▶│  Agent       │
│  (开放平台)   │◀────│  Layer       │◀────│  Runtime     │
└──────────────┘     └──────────────┘     └──────────────┘
      │                     │
      ▼                     ▼
┌──────────────┐     ┌──────────────┐
│  飞书多维表格 │     │  本地 SQLite  │
│  飞书文档     │     │  文件系统     │
│  飞书日历     │     │              │
│  飞书消息     │     │              │
└──────────────┘     └──────────────┘
```

### 5.2 集成功能

| 飞书功能 | 集成方式 | 产品场景 |
|----------|----------|----------|
| 多维表格 | CLI → API → 本地同步 | Ideas 管理、任务看板 |
| 文档 | CLI → Markdown 同步 | 分析报告、知识库 |
| 日历 | CLI → 本地日历 | 任务排期、提醒 |
| 消息/机器人 | Webhook → Agent 通知 | Agent 进度通知 |
| 审批流 | CLI → Agent 触发 | 任务审批、代码审查 |

### 5.3 实现路径
1. **Phase 1**: 飞书 CLI 封装为 Agent Tool（通过 MCP）
2. **Phase 2**: 飞书多维表格作为 Ideas/任务的云端同步
3. **Phase 3**: 飞书机器人作为 Agent 通知通道
4. **Phase 4**: 飞书工作流触发 Agent 任务执行

## 6. 项目路线图建议

### Phase 1: 基础框架 (2-3 周)
- [ ] Tauri v2 + Next.js 项目初始化
- [ ] 基础三栏布局
- [ ] SQLite 数据层
- [ ] 基础 IPC 通信

### Phase 2: Agent Runtime 核心 (3-4 周)
- [ ] Agent 执行引擎 (参考 yakAgent + Holaboss Harness)
- [ ] 记忆系统 (参考 Holaboss 三层记忆)
- [ ] 工具注册表 (MCP 集成)
- [ ] 权限系统

### Phase 3: 任务管理 (2-3 周)
- [ ] Ideas Inbox
- [ ] 看板系统 (参考 Multica)
- [ ] 任务拆解 Agent
- [ ] 进度追踪

### Phase 4: 集成与优化 (2-3 周)
- [ ] 飞书 CLI 集成
- [ ] 自动更新
- [ ] 系统托盘
- [ ] 打包分发

## 7. 核心结论

1. **推荐 Tauri v2**: 体积小、性能好、安全性高，GitButler 已证明可行性
2. **Electron 迁移成本**: 前端低，后端高，建议新项目直接用 Tauri
3. **Agent Runtime**: Holaboss 的 Harness 模式 + yakAgent 的权限系统
4. **记忆系统**: Holaboss 三层记忆是最佳参考
5. **任务管理**: Multica 的看板 + 技能积累模式
6. **飞书集成**: 通过 MCP Tool 封装 CLI，渐进式集成
