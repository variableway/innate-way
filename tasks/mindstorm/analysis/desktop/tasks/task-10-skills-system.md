# Task 10: Skills 技能系统

## Feature
实现可复用技能系统: 技能定义、积累、市场、热重载。

## 优先级
P2 - Agent 能力的积累机制

## 验收标准
- [ ] 技能定义: YAML/Markdown 格式定义技能
- [ ] 技能类型: prompt 技能、工作流技能、工具技能
- [ ] 技能注入: Agent 执行时注入相关技能到上下文
- [ ] 技能积累: 任务完成后自动提取可复用模式
- [ ] 技能市场: 浏览、安装、分享技能 (参考 rivonclaw)
- [ ] 技能热重载: 修改技能无需重启 Agent
- [ ] 技能版本管理
- [ ] 技能配置: 参数化技能配置
- [ ] 技能搜索: 按名称/标签搜索

## 数据结构

```sql
CREATE TABLE skills (
    id TEXT PRIMARY KEY,
    workspace_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT,          -- prompt/workflow/tool
    content TEXT,       -- 技能内容 (Markdown/YAML)
    config JSON,        -- 参数配置
    tags JSON,
    version TEXT,
    source TEXT,        -- built-in/marketplace/custom
    created_at DATETIME,
    updated_at DATETIME
);
```

## 参考代码
- Multica: 技能积累系统 — 随时间积累组织记忆
- rivonclaw: 技能市场 — 浏览、安装、分享
- Holaboss: 技能框架 — 可复用工作空间级技能
- OpenASE: Skills + Harness — 技能注入机制

## 依赖
Task 04 (Agent Runtime)

## 预估复杂度
中等
