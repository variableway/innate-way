# Task 07: Ideas 收集与管理

## Feature
实现 Ideas 收集箱: 多来源输入、AI 自动分析、分类标签、优先级评估。

## 优先级
P1 - 核心功能

## 验收标准
- [ ] Ideas 列表视图 (卡片/列表切换)
- [ ] Idea 创建: 标题 + 描述 + 来源 + 标签
- [ ] 快速捕获: 全局快捷键 (Cmd+Shift+I)
- [ ] AI 自动分析: 可行性评估、技术建议、工作量估算
- [ ] 标签系统: 自动标签 + 手动标签
- [ ] 优先级: P0-P3 + AI 建议
- [ ] 状态流转: Draft → Analyzed → Planned → Task → Done
- [ ] 搜索过滤: 全文搜索 + 标签 + 状态
- [ ] Idea 详情页: 描述、AI 分析、关联任务
- [ ] 关联: Idea → Tasks 映射
- [ ] 批量操作 + 统计面板

## 数据结构

```sql
CREATE TABLE ideas (
    id TEXT PRIMARY KEY,
    workspace_id TEXT,
    title TEXT NOT NULL,
    content TEXT,
    source TEXT,        -- manual/chat/clip/file/feishu
    status TEXT DEFAULT 'draft',
    priority INTEGER DEFAULT 2,
    ai_analysis JSON,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE idea_tags (
    idea_id TEXT,
    tag TEXT,
    PRIMARY KEY (idea_id, tag)
);
```

## 参考代码
- Holaboss: Task Proposals — 主动任务提议
- Multica: Issue 管理 — 任务生命周期

## 依赖
Task 03 (App Shell), Task 04 (Agent Runtime)

## 预估复杂度
中等
