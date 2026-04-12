# Task 06: MCP 工具集成

## Feature
实现 MCP Client，让 Agent Runtime 能发现和使用外部 MCP Server 的工具。

## 优先级
P1 - Agent 能力的核心扩展机制

## 架构设计

```
┌────────────────────────────────────────┐
│       Tauri App                        │
│  ┌──────────────────────────────────┐  │
│  │     MCP Client (Rust Plugin)     │  │
│  │  ┌────────┬────────┬─────────┐  │  │
│  │  │Discovery│Connect │Execute  │  │  │
│  │  └────────┴────────┴─────────┘  │  │
│  └──────────┬───────────────────────┘  │
│             │ stdio / SSE               │
│  ┌──────────▼───────────────────────┐  │
│  │     MCP Server Pool              │  │
│  │  ┌──────┐ ┌──────┐ ┌──────────┐ │  │
│  │  │ fs   │ │ db   │ │ feishu   │ │  │
│  │  │server│ │server│ │ MCP      │ │  │
│  │  └──────┘ └──────┘ └──────────┘ │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

## 验收标准
- [ ] Rust MCP Client 实现 (JSON-RPC 2.0 over stdio)
- [ ] MCP Server 发现: 扫描配置的 MCP Server 列表
- [ ] MCP Server 生命周期管理: 启动/停止/健康检查
- [ ] 工具调用桥接: MCP 工具 → Agent Runtime Tool Registry
- [ ] 配置文件: `mcp-servers.json` 定义 MCP Server 列表
- [ ] 内置 MCP Server: 文件系统 (tauri-plugin-fs 封装)
- [ ] 内置 MCP Server: Shell 执行 (tauri-plugin-shell 封装)
- [ ] 内置 MCP Server: SQLite 查询 (tauri-plugin-sql 封装)
- [ ] 工具权限: MCP 工具也受权限系统管控
- [ ] MCP Server 状态面板: 在 UI 显示运行状态
- [ ] 日志和错误追踪

## 配置格式

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@anthropic/mcp-filesystem", "--root", "/path"],
      "env": {}
    },
    "feishu": {
      "command": "feishu-mcp-server",
      "args": [],
      "env": {
        "FEISHU_APP_ID": "...",
        "FEISHU_APP_SECRET": "..."
      }
    }
  }
}
```

## 参考代码
- tauri-mcp: `innate-desktop-reference/` 外部 — Tauri MCP Server 模式
- yakAgent: MCP 工具自动发现 — 工具注册集成
- Holaboss: MCP SDK 集成 — Agent 工具集成

## 依赖
Task 04 (Agent Runtime)

## 预估复杂度
中-高 — MCP 协议实现 + 多进程管理
