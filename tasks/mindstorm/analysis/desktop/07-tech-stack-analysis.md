# Tech Stack 深度分析与确认

> 架构决策详见: [09-architecture-comparison.md](09-architecture-comparison.md)

## 1. 核心技术栈决策

### 确认方案: Monorepo (Next.js Web + Tauri v2 Desktop + 共享 Packages)

**整体架构**:
```
monorepo/  (pnpm workspaces + Turborepo)
├── apps/web/         ← Next.js 16 (SSR/SEO/API Routes) — Web 端
├── apps/desktop/     ← Tauri v2 + React 19 + Vite 8 — 桌面端
├── packages/ui/      ← 共享 shadcn/ui 组件
├── packages/core/    ← 共享业务逻辑 (平台无关)
└── packages/views/   ← 共享页面/视图
```

| 层面 | Web 端 | 桌面端 | 共享 |
|------|--------|--------|------|
| **框架** | Next.js 16 (App Router) | Tauri v2 + Vite 8 | React 19 + TypeScript |
| **UI** | shadcn/ui + Tailwind v4 | shadcn/ui + Tailwind v4 | `packages/ui` |
| **后端** | Next.js API Routes | Rust (Tauri commands) | `packages/core` |
| **数据库** | PostgreSQL / Turso | SQLite (tauri-plugin-sql) | 共享数据模型 |
| **状态** | Zustand + TanStack Query | Zustand + TanStack Query | 共享 store 逻辑 |
| **部署** | Vercel / Docker | 安装包 (.dmg/.exe/.AppImage) | — |

### 为什么桌面不用 Next.js

Next.js 在 Tauri 中只能用 `output: 'export'` 静态导出，**失去所有核心优势**：
- ❌ Server Components / Server Actions
- ❌ next/image 优化
- ❌ API Routes / Middleware
- ❌ SSR / ISR

> Tauri 维护者 FabianLars: "Next.js SSR-first 的本性和 Tauri 不匹配，直接用 Vite + React 更好"

**解决方案**: Monorepo 让 Web 端用 Next.js 完整能力，桌面端用 Vite + React，共享 packages 避免代码重复。通过 Platform Bridge 隔离本地能力差异。

## 2. Sidecar 模式分析

### 官方支持
Sidecar 是 Tauri v2 一等公民功能，通过 `tauri.conf.json` 的 `"externalBin"` 配置。

### 三种 Sidecar 模式对比

| 模式 | 适用场景 | 通信方式 | 推荐度 |
|------|----------|----------|--------|
| **Direct Spawn** | Go 二进制 | stdout/stdin + Tauri Events | ★★★★★ |
| **HTTP Server** | Python (FastAPI/Flask) | HTTP localhost | ★★★★ |
| **RPC Plugin** | Bun/Node/Deno | 类型安全 RPC (kkrpc) | ★★★ |

### 各语言 Sidecar 推荐

| 语言 | 方案 | 说明 |
|------|------|------|
| **Go** | Direct spawn | 编译为单二进制，直接 sidecar |
| **Python** | PyInstaller 打包 + sidecar | 或 FastAPI localhost server |
| **Bun/TS** | kkrpc 插件 | 类型安全 RPC，类似 Electron IPC |
| **Rust** | 直接集成到 Tauri 后端 | 最佳方案，无需 sidecar |

### 权限配置
Sidecar 需要在 `capabilities/default.json` 中显式授权：
```json
{
  "permissions": ["shell:allow-execute", "shell:allow-spawn"]
}
```

## 3. CLI/MCP 集成方案

### MCP 集成架构

```
┌─────────────────────────────────────┐
│          Tauri Desktop App          │
│  ┌─────────────────────────────┐   │
│  │    MCP Client (Rust)        │   │
│  │  ┌───────┬───────┬───────┐  │   │
│  │  │ fs    │ db    │ feishu│  │   │
│  │  │ tools │ tools │ tools │  │   │
│  │  └───────┴───────┴───────┘  │   │
│  └─────────────────────────────┘   │
│         │ stdio / SSE               │
│  ┌──────▼──────────────────────┐   │
│  │    MCP Servers (外部进程)    │   │
│  │  飞书CLI / 自定义工具 / ...  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 实现路径
1. **Phase 1**: Rust 实现 MCP Client，通过 stdio 连接外部 MCP Server
2. **Phase 2**: 内置常用 MCP Server (文件系统、数据库)
3. **Phase 3**: 飞书 CLI 封装为 MCP Server
4. **Phase 4**: 支持用户自定义 MCP Server

### 状态评估
| 组件 | 成熟度 | 风险 |
|------|--------|------|
| MCP Client (Rust) | 实验性 | 中-高 |
| MCP Server 管理 | 早期 | 中 |
| 飞书 CLI → MCP | 自定义开发 | 中 |

## 4. Plugin 模式

### Tauri v2 插件架构

**30+ 官方插件可用**: autostart, clipboard, dialog, fs, http, log, notification, sql, store, updater, websocket, window-state 等。

### 插件开发流程
```bash
# 创建自定义插件
npx @tauri-apps/cli plugin init my-plugin
```

### 推荐插件组合

| 插件 | 用途 |
|------|------|
| `tauri-plugin-sql` | SQLite 数据库 |
| `tauri-plugin-fs` | 文件系统访问 |
| `tauri-plugin-shell` | Shell/Sidecar 执行 |
| `tauri-plugin-store` | 键值对持久化 |
| `tauri-plugin-updater` | 自动更新 |
| `tauri-plugin-clipboard` | 剪贴板 |
| `tauri-plugin-notification` | 系统通知 |
| `tauri-plugin-pty` | 终端集成 |
| `tauri-plugin-dialog` | 原生对话框 |
| `tauri-plugin-autostart` | 开机启动 |
| `tauri-plugin-global-shortcut` | 全局快捷键 |

### 自定义插件建议
- Agent Runtime 作为 Tauri Plugin 封装
- 记忆系统作为 Tauri Plugin
- MCP Client 作为 Tauri Plugin

## 5. Terminal 集成方案

### 技术方案: tauri-plugin-pty + xterm.js

```
Rust: tauri_plugin_pty → portable-pty → 系统终端
         ↕ Tauri Events
JS:   xterm.js ↔ tauri-pty (spawn + onData/write)
```

### 成熟度
- **Electron**: node-pty + xterm.js，非常成熟 (VS Code 使用)
- **Tauri**: tauri-plugin-pty + xterm.js，功能可用但社区较小

### 注意事项
- 依赖大小: 18-64MB (portable-pty)
- Resize 事件需手动转发
- 早期阶段，欢迎贡献

### 推荐路径
1. **Phase 1**: 基础终端集成 (xterm.js + tauri-plugin-pty)
2. **Phase 2**: Agent 会话终端 (PTY 内运行 Agent CLI)
3. **Phase 3**: 多终端 Tab 管理

## 6. Cloud 端集成方案

### 推荐: SQLite + 可选云同步

```
┌──────────────┐         ┌──────────────┐
│  本地 SQLite  │◀─同步──▶│   云端       │
│  (tauri-     │         │  Turso /     │
│  plugin-sql) │         │  自建服务    │
└──────────────┘         └──────────────┘
```

### 方案对比

| 方案 | 适用场景 | 复杂度 | 推荐 |
|------|----------|--------|------|
| **SQLite + Turso** | 小团队同步 | 中 | ★★★★★ |
| **SQLite + 自建 API** | 完全控制 | 高 | ★★★★ |
| **CRDT (Yjs)** | 实时协作 | 高 | ★★★ |
| **纯本地** | 仅个人 | 低 | ★★★★★(个人) |

### 个人用户推荐: 纯本地 + 可选云备份
- 10 人以内不需要实时协作
- 本地 SQLite 足够
- 云端仅做备份和跨设备同步

## 7. CORS 和网络注意事项

### Tauri WebView CORS 限制
- 生产环境 origin 是 `tauri://localhost`
- WebView 强制 CORS
- **必须**: 通过 Rust 代理命令转发 localhost 请求 (Ollama, 本地 API 等)

### 解决方案
```typescript
// 不要直接 fetch
fetch('http://localhost:11434/api/generate') // ❌ CORS 阻止

// 通过 Rust 代理
import { invoke } from '@tauri-apps/api/core';
await invoke('proxy_request', { url: 'http://localhost:11434/api/generate' }) // ✅
```

## 8. AI 流式响应方案

Tauri command 默认缓冲响应，**AI 聊天流式输出必须用 Event 系统**：

```rust
#[tauri::command]
async fn start_chat(prompt: String, app: AppHandle) {
    // 通过事件逐 token 推送
    for token in ai_stream(&prompt).await {
        app.emit("chat-token", token).unwrap();
    }
}
```

```typescript
// 前端监听
import { listen } from '@tauri-apps/api/event';
await listen('chat-token', (event) => {
    appendToChat(event.payload);
});
```

## 9. 技术风险总结

| 技术领域 | 风险等级 | 缓解措施 |
|----------|----------|----------|
| Tauri + React | 🟢 低 | 成熟方案，大量模板 |
| Sidecar | 🟢 低 | 官方一等支持 |
| Plugin 系统 | 🟢 低 | 30+ 官方插件 |
| shadcn/ui | 🟢 低 | 桌面端良好适配 |
| Terminal/PTY | 🟡 中 | 早期但可用，备选 sidecar node-pty |
| MCP 集成 | 🟡 中-高 | 生态系统早期，需自定义开发 |
| Cloud 同步 | 🟢 低 | SQLite + Turso 成熟方案 |
| Auto-update | 🟢 低 | 官方插件，全平台支持 |

## 10. 最终技术栈确认 (Monorepo)

```
Monorepo:     pnpm workspaces + Turborepo

Web 端 (apps/web):
  Next.js 16 (App Router) + React 19 + TypeScript
  Tailwind CSS v4 (OKLCH) + shadcn/ui
  Next.js API Routes (后端)
  PostgreSQL / Turso (数据库)

Desktop 端 (apps/desktop):
  Tauri v2 (Rust shell + WebView)
  React 19 + TypeScript + Vite 8
  Tailwind CSS v4 (OKLCH) + shadcn/ui
  Rust 后端 (Tauri commands + plugins)
  SQLite (tauri-plugin-sql) + sqlite-vec

共享 (packages/):
  @innate/ui      — shadcn/ui 组件 + 主题
  @innate/core    — 业务逻辑 + Platform Bridge + 数据模型
  @innate/views   — 共享页面/视图组件

基础设施:
  State:     Zustand (client) + TanStack Query (server)
  Terminal:  xterm.js + tauri-plugin-pty (桌面端)
  MCP:       Rust MCP Client (桌面端)
  Cloud:     可选 Turso / 自建 API
  Update:    tauri-plugin-updater (桌面端)
  Sidecar:   Go/Python (桌面端按需)
```
