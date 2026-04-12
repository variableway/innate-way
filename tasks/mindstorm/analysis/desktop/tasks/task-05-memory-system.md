# Task 05: 记忆系统

## Feature
实现三层记忆架构: 运行时记忆、会话记忆、持久记忆，支持跨会话 Agent 连续性。

## 优先级
P0 - Agent 持续工作的核心

## 架构设计

```
┌─────────────────────────────────────┐
│          Memory System              │
│                                     │
│  Layer 1: Runtime Memory            │
│  ┌───────────────────────────────┐ │
│  │ 当前执行上下文 (in-memory)     │ │
│  │ 活跃消息、工具调用状态         │ │
│  └───────────────────────────────┘ │
│           ↕ 压缩边界               │
│  Layer 2: Session Memory           │
│  ┌───────────────────────────────┐ │
│  │ SQLite: session_messages      │ │
│  │ 会话摘要、关键信息             │ │
│  │ 压缩边界快照                   │ │
│  └───────────────────────────────┘ │
│           ↕ 记忆演化               │
│  Layer 3: Durable Memory           │
│  ┌───────────────────────────────┐ │
│  │ 文件系统: Markdown 知识库      │ │
│  │ facts / procedures / refs     │ │
│  │ 用户偏好、工作空间知识         │ │
│  │ sqlite-vec 向量搜索 (可选)     │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 验收标准
- [ ] SQLite 存储层: sessions, messages, memory_entries 表
- [ ] 运行时记忆: 当前会话的活跃上下文 (内存)
- [ ] 会话记忆: 会话历史 + 摘要压缩 (SQLite)
- [ ] 持久记忆: Markdown 文件 + 元数据目录
- [ ] 记忆类型分类: facts, procedures, blockers, references, preferences
- [ ] 记忆演化: Agent 自动提取持久记忆
- [ ] 压缩边界: 会话恢复时的高效状态还原
- [ ] 记忆召回: 上下文相关的记忆检索
- [ ] 向量搜索 (可选): sqlite-vec 语义搜索
- [ ] FTS5 全文搜索 (参考 Hermes)
- [ ] 跨会话连续性: Agent 能引用之前的对话和知识
- [ ] 记忆管理 UI: 查看/编辑/删除记忆

## 关键数据结构

```sql
-- 会话记忆
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    workspace_id TEXT,
    agent_id TEXT,
    parent_session_id TEXT,  -- 压缩链
    summary TEXT,
    created_at DATETIME,
    ended_at DATETIME
);

CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    role TEXT,  -- user/assistant/tool/system
    content TEXT,
    tool_calls JSON,
    created_at DATETIME
);

-- 持久记忆
CREATE TABLE memory_entries (
    id TEXT PRIMARY KEY,
    workspace_id TEXT,
    type TEXT,  -- fact/procedure/blocker/reference/preference
    content TEXT,
    source_session_id TEXT,
    embedding BLOB,  -- 可选
    created_at DATETIME,
    updated_at DATETIME
);

-- 压缩边界
CREATE TABLE compaction_boundaries (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    boundary_type TEXT,
    state_snapshot JSON,
    created_at DATETIME
);
```

## 参考代码
- Holaboss: 三层记忆架构 — 最佳参考
- Letta: 块记忆架构 + 摘要策略
- Hermes: FTS5 全文搜索 + Provider 模式

## 依赖
Task 04 (Agent Runtime)

## 预估复杂度
高 — 记忆演化逻辑需要仔细设计
