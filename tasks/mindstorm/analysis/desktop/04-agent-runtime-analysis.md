# Agent Runtime 引擎分析

> 覆盖仓库: hermes-agent, Archon, letta, yakAgent, agtx

## 1. 总体对比

| 维度 | Hermes | Archon | Letta | yakAgent | agtx |
|------|--------|--------|-------|----------|------|
| 语言 | Python | TypeScript | Python | Python | Rust |
| 核心 | 自我改进 Agent | 工作流引擎 | 记忆 Agent | 轻量框架 | 终端看板 |
| 存储 | SQLite+FTS5 | SQLite/PG | 自定义 | 会话内存 | 文件 |
| 特色 | 多平台网关 | DAG 工作流 | 高级记忆 | 权限系统 | TUI+tmux |

## 2. 各仓库详细分析

### 2.1 Hermes Agent

**概述**: Nous Research 的自我改进 AI Agent，内置学习循环，支持 $5 VPS 到 GPU 集群。

**运行时架构**:
- **核心循环**: `run_agent.py` 集中对话处理器 + 工具调用循环
- **状态管理**: SQLite + FTS5 全文搜索跨会话消息
- **记忆系统**: 多 Provider 架构 (BuiltinMemoryProvider + 一个外部插件)
- **会话管理**: 不可变会话 + parent_session_id 链用于压缩触发
- **工具系统**: 40+ 内置工具的模块化注册表

**可借鉴**:
- FTS5 虚拟表跨会话搜索
- Provider 模式记忆系统 + 故障转移
- 会话链 + 压缩触发器
- 多平台网关架构 (Telegram/Discord/Slack/WhatsApp/Signal)

### 2.2 Archon

**概述**: AI 编码 Agent 的工作流引擎，将开发流程定义为 YAML 工作流。

**运行时架构**:
- **编排器**: 中央消息路由器处理斜杠命令和 AI 对话
- **工作流引擎**: DAG 工作流执行，YAML 定义
- **隔离系统**: Git worktree 隔离 + 自动环境解析
- **平台适配器**: Web/CLI/Slack/Telegram/Discord/GitHub 统一接口

**关键模式**:
```typescript
// DAG 工作流定义
interface WorkflowDefinition {
  nodes: Array<{
    id: string;
    depends_on: string[];
    prompt?: string;
    bash?: string;
    loop?: { prompt: string; until: string; };
  }>;
}
```

**可借鉴**:
- Git worktree 隔离用于并行开发
- 不可变会话链 + 转换原因
- YAML 工作流定义 + 变量替换
- 平台适配器统一消息接口

### 2.3 Letta

**概述**: 具有高级记忆的 AI，可学习和自我改进。提供 CLI 和 API。

**运行时架构**:
- **BaseAgent 抽象类**: 定义 step() 接口
- **Agent 类**: 记忆块 + 工具执行 + 消息管理
- **记忆系统**: 上下文窗口 + 摘要 + 消息块管理
- **工具执行**: 沙箱化工具执行 + MCP 集成

**可借鉴**:
- 块记忆架构 (Block-based Memory)
- 流式刷新 CLI 界面
- 工具执行沙箱化
- MCP (Model Context Protocol) 集成
- 记忆摘要策略

### 2.4 yakAgent

**概述**: 轻量 Python Agent 框架，工具调用循环 + 权限 + 子 Agent + 流式。

**运行时架构**:
- **Engine**: 核心 Agent 循环 + 权限评估 + 子 Agent 生成
- **Agent Registry**: 管理多个 Agent 定义和切换
- **权限系统**: 4层层级 + 2D 匹配 (工具 × 资源模式)
- **工具注册表**: 内置 + 自定义 + MCP 工具自动发现

**关键模式**:
```python
class Engine:
    def __init__(self, provider, agents, tools, *,
                 global_permissions, max_steps, tool_timeout, hooks, store):
        self.provider = provider
        self.agents = AgentRegistry(agents)
        self.tools = ToolRegistry(tools)
        self.permissions = evaluate
```

**可借鉴**:
- 权限评估系统 + rulesets
- 子 Agent 生成 + 递归深度保护
- Doom loop 检测和上下文溢出处理
- 事件流式实时更新
- 简洁的 Provider 抽象

### 2.5 agtx

**概述**: 终端看板管理多个编码 Agent 会话，隔离 git worktree。支持协调器 Agent 自主管理。

**运行时架构**:
- **TUI 应用**: Ratatui 终端界面 + 看板可视化
- **任务工作流**: Backlog → Planning → Running → Review → Done
- **Worktree 隔离**: 每个任务独立 git worktree + tmux 窗口
- **插件系统**: Spec 驱动工作流 (GSD, Spec-kit, OpenSpec)
- **协调器**: AI Agent 通过 MCP 自主管理看板

**可借鉴**:
- tmux 集成的终端原生 UI
- 每任务 git worktree 隔离
- MCP Server 用于协调器通信
- TOML 配置的插件系统
- 看板状态管理

## 3. 共通模式总结

### 所有运行时共同具备
1. **持久化存储**: SQLite 或数据库保存对话历史
2. **工具注册表**: 可扩展工具系统，动态加载
3. **会话管理**: 对话状态 + 上下文管理
4. **Provider 抽象**: 支持多个 LLM Provider
5. **流式接口**: 实时响应处理
6. **错误恢复**: 优雅恢复和重试机制

### 推荐组合策略（个人 AI Agent Runtime）
1. **基础**: yakAgent 的简洁框架 + 权限系统
2. **工作流**: Archon 的 DAG 工作流 + YAML 定义
3. **记忆**: Hermes 的 FTS5 搜索 + Letta 的块记忆
4. **交互**: agtx 的终端 UI + 看板模式
5. **安全**: yakAgent 的 4 层权限 + 递归保护

## 4. 代码参考

- `innate-desktop-reference/hermes-agent/`
- `innate-desktop-reference/Archon/`
- `innate-desktop-reference/letta/`
- `innate-desktop-reference/yakAgent/`
- `innate-desktop-reference/agtx/`
