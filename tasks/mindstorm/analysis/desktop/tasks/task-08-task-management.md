# Task 08: 任务管理与看板

## Feature
实现任务看板系统: 多视图(看板/列表)、任务生命周期、子任务拆解、Agent 分配。

## 优先级
P1 - 核心功能

## 验收标准
- [ ] 看板视图: Backlog → Planning → Running → Review → Done (参考 agtx + Multica)
- [ ] 列表视图: 可排序列表，支持过滤和分组
- [ ] 任务 CRUD: 创建、编辑、删除、归档
- [ ] 子任务: 树形任务拆解 (AI 辅助拆解)
- [ ] Agent 分配: 将任务分配给 AI Agent 执行
- [ ] 任务状态机: queued → dispatched → running → review → completed/failed
- [ ] 拖拽排序: 看板列间拖拽 + 列内排序
- [ ] 进度追踪: 实时进度更新 (WebSocket/Event)
- [ ] 任务详情: 描述、子任务、关联 Idea、执行日志、Agent 输出
- [ ] 工作空间隔离: 每个工作空间独立任务集
- [ ] 快捷操作: 快速创建 (Cmd+N)、快速分配
- [ ] 统计: 任务完成率、Agent 工作量、瓶颈分析

## 数据结构

```sql
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    workspace_id TEXT,
    parent_id TEXT,         -- 子任务树
    idea_id TEXT,           -- 关联 Idea
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'backlog',
    priority INTEGER DEFAULT 2,
    assignee_type TEXT,     -- human/agent
    assignee_id TEXT,
    tags JSON,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE task_executions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    agent_id TEXT,
    status TEXT,            -- running/completed/failed
    output TEXT,
    token_usage JSON,
    started_at DATETIME,
    completed_at DATETIME
);
```

## 参考代码
- Multica: Agent 任务看板 — Agent 一等公民的任务系统
- agtx: 终端看板 — 简洁的状态管理
- Archon: DAG 工作流 — 任务依赖排序
- Aperant: 多 Agent 编排 — planner → coder → QA

## 依赖
Task 03 (App Shell), Task 04 (Agent Runtime), Task 07 (Ideas)

## 预估复杂度
高 — 核心业务逻辑，多视图 + 实时更新
