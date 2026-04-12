# Task 04: Agent Runtime 引擎

## Feature
实现核心 Agent 运行时引擎: Agent 执行、工具调用、会话管理、权限控制。

## 优先级
P0 - 核心功能

## 架构设计

```
┌─────────────────────────────────────────┐
│          Agent Runtime (Rust)           │
│  ┌─────────────────────────────────┐   │
│  │         Engine Core             │   │
│  │  ┌──────────┬──────────────┐   │   │
│  │  │ Session  │ Tool         │   │   │
│  │  │ Manager  │ Registry     │   │   │
│  │  └──────────┴──────────────┘   │   │
│  │  ┌──────────┬──────────────┐   │   │
│  │  │ Permission│ Provider    │   │   │
│  │  │ Evaluator │ Abstraction │   │   │
│  │  └──────────┴──────────────┘   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │         Harness Layer           │   │
│  │  Claude / OpenAI / Local / ...  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 验收标准
- [ ] Rust Agent 引擎核心 (参考 yakAgent Engine + Holaboss Harness)
- [ ] Provider 抽象: 支持 OpenAI / Anthropic / 本地模型 (Ollama)
- [ ] 工具注册表: 动态工具加载 + MCP 工具集成
- [ ] 权限系统: 4 层权限 (参考 yakAgent: global → agent → session → tool)
- [ ] 会话管理: 创建/恢复/销毁 Agent 会话
- [ ] 流式响应: Tauri Events 推送 AI token
- [ ] 子 Agent 生成: 递归深度保护 (参考 yakAgent)
- [ ] Doom loop 检测: 上下文溢出保护
- [ ] 错误恢复: 熔断器 + 自动恢复 (参考 ralph-claude-code)
- [ ] Tauri Plugin 封装: 作为 `tauri-plugin-agent-runtime`

## 关键数据结构

```rust
struct AgentEngine {
    providers: HashMap<String, Box<dyn Provider>>,
    tools: ToolRegistry,
    permissions: PermissionEvaluator,
    sessions: SessionManager,
    max_steps: usize,
    tool_timeout: Duration,
}

struct AgentSession {
    id: Uuid,
    agent_id: String,
    messages: Vec<Message>,
    permissions: Permissions,
    created_at: DateTime<Utc>,
}

enum Permission {
    Bash, ReadFile, WriteFile, Network, // ...
}
```

## 参考代码
- yakAgent: Engine + Permission + ToolRegistry — 简洁框架
- Holaboss: Harness Host + Harnesses — 可扩展 Agent 框架
- ralph-claude-code: 熔断器 + 退出检测 — 错误恢复
- Hermes: FTS5 会话搜索 — 会话管理

## 依赖
Task 01 (项目脚手架)

## 预估复杂度
非常高 — 核心引擎，需要精心设计
