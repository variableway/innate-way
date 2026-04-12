# 架构方案对比与决策: Web + Desktop

> 确认方案: A - Monorepo (Next.js Web + Tauri Desktop + 共享 Packages)

## 1. 三方案对比

### 方案 A: Monorepo (已选择 ★)

```
monorepo/
├── apps/
│   ├── web/          ← Next.js 完整 Web (SSR/API Routes/SEO)
│   └── desktop/      ← Tauri v2 + React (Vite)
├── packages/
│   ├── ui/           ← 共享 shadcn/ui 组件
│   ├── core/         ← 共享业务逻辑 (平台无关)
│   └── views/        ← 共享页面/视图
├── sidecars/         ← 外部进程 (Go/Python MCP 等)
└── rust-backend/     ← 共享 Rust 逻辑 (可选)
```

**优势**:
- 代码复用最大化: UI/业务逻辑/数据模型写一次，Web 和 Desktop 共用
- 各端最优化: Web 端 Next.js 完整能力，桌面端 Tauri 原生性能
- 差异化自然实现: Web 去掉本地功能，桌面加上，通过 Platform Bridge 隔离
- 独立部署: Web 和 Desktop 各自发布互不影响
- 已有成功案例: Multica 就是这个模式

**劣势**:
- Monorepo 复杂度 (pnpm workspaces + Turbo)
- 两个 app 维护
- 包边界需提前设计

### 方案 B: Next.js 统一 (未选择)

```
nextjs-app/
├── app/              ← Next.js App Router
├── Web 部署:         完整 Next.js
└── Desktop:          next export → Tauri (失去 SSR/API)
```

- 桌面端能力受限: 静态导出失去服务端能力
- 本地能力难集成: PTY/Sidecar 需复杂桥接
- 功能差异化困难: 共用路由，本地功能需条件渲染

### 方案 C: Vite 优先 (未选择)

```
tauri-app/
├── src/              ← React + Vite
├── src-tauri/        ← Rust backend
└── Web 部署:         后续单独处理
```

- Web 版需要额外搭建
- 无法 SSR (公开网站 SEO 受限)
- 两套独立项目可能代码重复

## 2. 对比矩阵

| 维度 | A: Monorepo | B: Next.js 统一 | C: Vite 优先 |
|------|-------------|-----------------|--------------|
| 代码复用 | ★★★★★ | ★★★★ | ★★ |
| 桌面端能力 | ★★★★★ | ★★★ | ★★★★★ |
| Web 端能力 | ★★★★★ | ★★★★★ | ★★★ |
| 本地能力集成 | ★★★★★ | ★★ | ★★★★★ |
| 功能差异化 | ★★★★★ | ★★ | ★★★ |
| SEO/公开网站 | ★★★★★ | ★★★★★ | ★★ |
| 自托管部署 | ★★★★★ | ★★★★★ | ★★★★ |
| 移动端适配 | ★★★★ | ★★★★★ | ★★★ |
| 维护成本 | ★★★ | ★★★★ | ★★★★★ |
| 初期复杂度 | ★★ | ★★★★★ | ★★★★★ |
| 长期扩展性 | ★★★★★ | ★★★ | ★★★ |

## 3. 功能差异化矩阵

### 桌面端独有 (Tauri 本地能力)
| 功能 | 实现方式 |
|------|----------|
| 本地文件系统 | tauri-plugin-fs |
| 终端/PTY | tauri-plugin-pty + xterm.js |
| Agent 本地执行 | Rust Agent Runtime |
| Sidecar 进程 | tauri-plugin-shell sidecar |
| MCP Server 管理 | 本地进程管理 |
| 系统托盘 | tauri-plugin-tray |
| 全局快捷键 | tauri-plugin-global-shortcut |
| 本地 AI (Ollama) | Rust HTTP 客户端 (绕过 CORS) |
| 自动更新 | tauri-plugin-updater |
| 离线使用 | SQLite 本地优先 |

### Web 端独有
| 功能 | 实现方式 |
|------|----------|
| SEO 优化 | Next.js SSR/SSG |
| 公开访问 | Next.js 部署 |
| 多用户认证 | Next.js API Routes |
| 移动端浏览器 | 响应式设计 |
| 无需安装 | 浏览器直接访问 |

### 共享功能 (通过 packages/)
| 功能 | 所在包 |
|------|--------|
| UI 组件 | `@innate/ui` |
| Ideas 管理 | `@innate/core` |
| 任务看板 | `@innate/views` |
| AI 聊天界面 | `@innate/views` |
| 技能系统 | `@innate/core` |
| 设计系统/主题 | `@innate/ui` |
| 数据类型定义 | `@innate/core` |
| API 客户端 | `@innate/core` |

## 4. Platform Bridge 设计

```typescript
// packages/core/platform/index.ts
export interface PlatformAdapter {
  // 存储
  storage: StorageAdapter;

  // 文件系统 (仅桌面)
  fs?: FileSystemAdapter;

  // 终端 (仅桌面)
  terminal?: TerminalAdapter;

  // Agent Runtime (桌面=Rust, Web=HTTP API)
  agent: AgentAdapter;

  // 通知
  notification: NotificationAdapter;

  // 更新检查 (仅桌面)
  updater?: UpdaterAdapter;

  // 能力查询
  capabilities: Set<PlatformCapability>;
}

export type PlatformCapability =
  | 'fs'           // 文件系统
  | 'terminal'     // 终端
  | 'local-agent'  // 本地 Agent
  | 'sidecar'      // 外部进程
  | 'tray'         // 系统托盘
  | 'hotkey'       // 全局快捷键
  | 'offline'      // 离线使用
  | 'auto-update'; // 自动更新
```

```typescript
// apps/desktop/src/platform.ts — 桌面端实现
export const desktopPlatform: PlatformAdapter = {
  storage: new SqliteStorage(),
  fs: new TauriFsAdapter(),
  terminal: new TauriPtyAdapter(),
  agent: new RustAgentRuntime(),
  notification: new TauriNotificationAdapter(),
  updater: new TauriUpdaterAdapter(),
  capabilities: new Set(['fs', 'terminal', 'local-agent', 'sidecar', 'tray', 'hotkey', 'offline', 'auto-update']),
};
```

```typescript
// apps/web/src/platform.ts — Web 端实现
export const webPlatform: PlatformAdapter = {
  storage: new IndexedDbStorage(),
  fs: undefined,           // Web 无文件系统
  terminal: undefined,     // Web 无终端
  agent: new HttpAgentRuntime('/api/agent'),
  notification: new WebNotificationAdapter(),
  updater: undefined,
  capabilities: new Set([]), // Web 无本地能力
};
```

## 5. 技术栈更新 (Monorepo)

```
Monorepo:     pnpm workspaces + Turborepo
Web:          Next.js 16 (App Router) + React 19 + TypeScript
Desktop:      Tauri v2 + React 19 + Vite 8 + TypeScript
UI:           shadcn/ui + Tailwind CSS v4 (OKLCH)
共享:         packages/ui + packages/core + packages/views
后端(桌面):   Rust (Tauri commands + plugins)
后端(Web):    Next.js API Routes (Node.js)
数据库(桌面): SQLite (tauri-plugin-sql)
数据库(Web):  PostgreSQL / Turso
状态管理:     Zustand (client) + TanStack Query (server)
```

## 6. 选择理由总结

1. Web 三场景全覆盖: Next.js 公开网站有 SSR/SEO，自托管 Docker 部署，移动端响应式
2. 功能差异化天然支持: Platform Bridge 让本地能力自然降级
3. 桌面端不受限: Tauri + Vite 完整本地能力
4. Multica 已验证: 内部包模式 + Platform Bridge 是成熟模式
5. 长期扩展性: 后续可加 Mobile (React Native) 复用 packages
