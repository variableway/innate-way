# Karpathy Wiki 模式与 Issue 系统整合分析报告

> **分析来源**: [karpathy/gist - LLM Knowledge Base Pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

---

## 1. Karpathy Wiki 模式核心概念

### 1.1 三层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Schema (CLAUDE.md)                          │
│              - Wiki 结构定义                                     │
│              - 约定和规范                                        │
│              - 工作流程                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        The Wiki                                 │
│              - LLM 生成的 Markdown 文件                          │
│              - 实体页面、概念页面、对比页面                       │
│              - 交叉引用、综合总结                                │
│              - 持续累积、自动维护                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Raw Sources                                │
│              - 原始文档（只读）                                  │
│              - 文章、论文、图片、数据文件                         │
│              - 添加新源触发 Ingest 流程                          │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心操作

| 操作 | 描述 | 输出 |
|------|------|------|
| **Ingest** | 处理新资源，提取关键信息 | 更新 10-15 个 wiki 页面 |
| **Query** | 基于 wiki 回答问题 | 答案可归档为新页面 |
| **Lint** | 健康检查 wiki | 发现矛盾、缺失、过期内容 |

### 1.3 关键文件

```
wiki/
├── index.md          # 内容导向的目录（自动更新）
├── log.md            # 时间线日志（追加模式）
├── entities/         # 实体页面
├── concepts/         # 概念页面  
├── sources/          # 源文档摘要
├── comparisons/      # 对比分析
└── synthesis.md      # 综合总结
```

---

## 2. 与 Issue 系统的相似性分析

### 2.1 结构对比

| 维度 | Karpathy Wiki | Current Issue System |
|------|---------------|---------------------|
| **存储** | Markdown + Git | Markdown + SQLite |
| **元数据** | YAML Frontmatter | YAML Frontmatter |
| **索引** | index.md | SQLite + Feishu Bitable |
| **日志** | log.md (时间线) | Task 状态变更历史 |
| **状态** | 隐式（通过更新） | 显式 Stage Pipeline |
| **来源** | Raw sources | Terminal / Feishu / GitHub |

### 2.2 核心相似点

1. **Markdown 为中心**: 两者都以 Markdown 作为主要存储格式
2. **元数据驱动**: 都使用 YAML Frontmatter 存储结构化元数据
3. **累积性**: 都强调知识的持续积累和复利效应
4. **LLM 参与**: 都依赖 LLM 进行内容生成和维护

---

## 3. 整合方案设计

### 3.1 整合架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Unified Knowledge & Task System                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         Input Layer                                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │  │
│  │  │ Terminal │  │ Feishu   │  │ GitHub   │  │  External Sources    │  │  │
│  │  │ (capture)│  │ (bot)    │  │ (issues) │  │  (docs/papers/etc)   │  │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘  │  │
│  │       └─────────────┴─────────────┴───────────────────┘               │  │
│  │                              │                                        │  │
│  │                              ▼                                        │  │
│  │                   ┌─────────────────────┐                             │  │
│  │                   │   Issue Adapter     │                             │  │
│  │                   │  (统一入口)          │                             │  │
│  │                   └──────────┬──────────┘                             │  │
│  └──────────────────────────────┼───────────────────────────────────────┘  │
│                                 │                                          │
│  ┌──────────────────────────────┼───────────────────────────────────────┐  │
│  │                      Core Processing Layer                            │  │
│  │                              │                                        │  │
│  │  ┌───────────────────────────┴────────────────────────────────────┐  │  │
│  │  │                    Issue Lifecycle                              │  │  │
│  │  │                                                                  │  │  │
│  │  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    │  │  │
│  │  │   │  Inbox  │───►│ Analysis│───►│ Planning│───►│ Dispatch│    │  │  │
│  │  │   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    │  │  │
│  │  │        │              │              │              │         │  │  │
│  │  │        ▼              ▼              ▼              ▼         │  │  │
│  │  │   ┌─────────────────────────────────────────────────────────┐  │  │  │
│  │  │   │                  Wiki Ingestion                          │  │  │  │
│  │  │   │  - Issue 分析结果 → 实体页面                             │  │  │  │
│  │  │   │  - Task 执行结果 → 知识页面                              │  │  │  │
│  │  │   │  - Agent 输出 → 技术文档                                 │  │  │  │
│  │  │   └─────────────────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      Storage Layer                                    │  │
│  │                                                                       │  │
│  │   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │  │
│  │   │   Issues/       │    │    Wiki/        │    │   Raw/          │  │  │
│  │   │   - TASK-001.md │    │   - entities/   │    │   - sources/    │  │  │
│  │   │   - TASK-002.md │    │   - concepts/   │    │   - assets/     │  │  │
│  │   │   (可执行)       │    │   - index.md    │    │   (参考资源)     │  │  │
│  │   │   (有状态)       │    │   - log.md      │    │                 │  │  │
│  │   │                 │    │   (知识库)       │    │                 │  │  │
│  │   └─────────────────┘    └─────────────────┘    └─────────────────┘  │  │
│  │                                                                       │  │
│  │   SQLite (索引)  +  Feishu Bitable (同步)  +  Git (版本控制)           │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    Execution Layer                                    │  │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │  │
│  │   │ Agent 1 │  │ Agent 2 │  │ Agent 3 │  │ Agent N │  (Multi-Machine)│  │
│  │   │(claude) │  │(codex)  │  │(opencode│  │(custom) │                 │  │
│  │   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                 │  │
│  │        └─────────────┴─────────────┴─────────────┘                    │  │
│  │                              │                                        │  │
│  │                              ▼                                        │  │
│  │                   ┌─────────────────────┐                             │  │
│  │                   │  Output → Wiki      │                             │  │
│  │                   │  (执行结果归档)      │                             │  │
│  │                   └─────────────────────┘                             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Issue ↔ Wiki 双向整合

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Issue ↔ Wiki Integration                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Direction 1: Issue → Wiki (Ingest)                                     │
│  ─────────────────────────────────                                     │
│                                                                          │
│  当 Issue 进入 Analysis Stage:                                          │
│                                                                          │
│  ┌─────────────┐         ┌─────────────────────────────────────────┐   │
│  │  Issue      │         │  Wiki Updates                           │   │
│  │  TASK-001   │────────►│                                         │   │
│  │  Title      │         │  1. entities/TASK-001.md               │   │
│  │  Description│         │     - Issue 摘要页面                    │   │
│  │  Context    │         │     - 关联的 entities                   │   │
│  │  Analysis   │         │                                         │   │
│  └─────────────┘         │  2. concepts/相关概念.md                │   │
│                          │     - 提取的技术概念                      │   │
│                          │                                         │   │
│                          │  3. sources/原始输入.md                 │   │
│                          │     - Terminal/Feishu 原始内容           │   │
│                          │                                         │   │
│                          │  4. index.md (更新索引)                 │   │
│                          │                                         │   │
│                          │  5. log.md (添加时间线)                 │   │
│                          │     ## [2026-04-06] issue | TASK-001   │   │
│                          └─────────────────────────────────────────┘   │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  Direction 2: Wiki → Issue (Query/Action)                               │
│  ─────────────────────────────────────────────────                     │
│                                                                          │
│  当需要基于已有知识创建 Task:                                           │
│                                                                          │
│  ┌─────────────────────────────────────────┐         ┌─────────────┐   │
│  │  Wiki Query                             │         │  New Issue  │   │
│  │                                         │────────►│  Generated  │   │
│  │  "基于 concepts/auth-system.md          │         │             │   │
│  │   实现 JWT 认证"                        │         │  Reference: │   │
│  │                                         │         │  wiki:auth  │   │
│  │  LLM 读取相关 wiki 页面                 │         │             │   │
│  │  生成具体实现计划                       │         │  Context:   │   │
│  │  创建新 Issue 或 Sub-Tasks              │         │  - entities │   │
│  │                                         │         │  - concepts │   │
│  └─────────────────────────────────────────┘         └─────────────┘   │
│                                                                          │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  Direction 3: Agent Execution → Wiki (Result Archival)                  │
│  ────────────────────────────────────────────────────────              │
│                                                                          │
│  当 Agent 完成 Task 执行:                                               │
│                                                                          │
│  ┌─────────────┐         ┌─────────────────────────────────────────┐   │
│  │  Agent      │         │  Wiki Updates                           │   │
│  │  Output     │────────►│                                         │   │
│  │             │         │  1. executions/TASK-001-result.md      │   │
│  │  - Code     │         │     - 执行摘要                          │   │
│  │  - Summary  │         │     - 关键输出                          │   │
│  │  - Learnings│         │     - 经验教训                          │   │
│  └─────────────┘         │                                         │   │
│                          │  2. entities/代码组件.md                │   │
│                          │     - 新生成的组件文档                    │   │
│                          │                                         │   │
│                          │  3. log.md                              │   │
│                          │     ## [2026-04-06] execute | TASK-001 │   │
│                          │         Result: success                  │   │
│                          │         Output: wiki:executions/TASK-001 │   │
│                          └─────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 具体整合场景

### 4.1 场景 1: 任务分析自动生成知识库

```yaml
# 原始 Issue: ~/.capture/issues/2026/04/TASK-001.md
---
id: TASK-001
title: "实现用户认证系统"
stage: analysis
source: terminal
---

实现基于 JWT 的用户认证系统...
```

**触发 Ingest 流程后自动生成的 Wiki 结构:**

```
wiki/
├── index.md                          # 更新索引
├── log.md                            # 添加记录
│   ## [2026-04-06] issue | TASK-001
│   - Title: 实现用户认证系统
│   - Source: terminal
│   - Entities: auth-system, jwt, user-management
│
├── entities/
│   ├── TASK-001.md                   # Issue 实体页面
│   │   # TASK-001: 实现用户认证系统
│   │   - **Status**: Analysis
│   │   - **Source**: Terminal
│   │   - **Related**: [[entities/jwt]], [[entities/auth-system]]
│
│   ├── auth-system.md                # 自动创建/更新
│   │   # Auth System
│   │   ## Related Issues
│   │   - [[entities/TASK-001]]
│   │   ## Concepts
│   │   - [[concepts/jwt]], [[concepts/bcrypt]]
│
│   └── jwt.md                        # 自动创建/更新
│       # JWT (JSON Web Token)
│       ## Mentioned In
│       - [[entities/TASK-001]]
│
├── concepts/
│   ├── authentication.md             # 认证概念
│   ├── authorization.md              # 授权概念
│   └── token-storage.md              # Token 存储
│
└── sources/
    └── terminal-2026-04-06-task-001.md  # 原始输入备份
```

### 4.2 场景 2: Agent 执行结果归档到 Wiki

```
Agent 完成 TASK-001 后，自动归档：

wiki/
├── executions/
│   └── TASK-001-2026-04-06.md
│       # TASK-001 执行结果
│       
│       ## 执行摘要
│       - **Agent**: claude@macbook
│       - **Duration**: 45min
│       - **Status**: ✅ Completed
│       
│       ## 生成的文件
│       - `auth/jwt.go` - JWT 中间件实现
│       - `auth/password.go` - bcrypt 密码哈希
│       - `docker-compose.yml` - Redis 配置
│       
│       ## 技术决策
│       - 使用 github.com/golang-jwt/jwt/v5
│       - Access token 有效期: 15min
│       - Refresh token 有效期: 7d
│       
│       ## 关联知识
│       - [[entities/auth-system]]
│       - [[concepts/jwt-best-practices]]
│
├── entities/
│   ├── jwt-middleware.md             # 新实体
│   ├── bcrypt-impl.md                # 新实体
│   └── redis-config.md               # 新实体
│
└── log.md
    ## [2026-04-06] execute | TASK-001
    - Agent: claude@macbook
    - Result: success
    - Output: wiki:executions/TASK-001-2026-04-06
    - Artifacts: 
      - git: commit/abc123
      - wiki: entities/jwt-middleware
```

### 4.3 场景 3: Wiki 知识驱动新 Issue 创建

```
用户在 Wiki 中查询已有知识后创建新任务：

1. 用户 Query: "基于 wiki 中已有的认证知识，如何实现 OAuth2?"

2. LLM 读取相关页面：
   - entities/auth-system.md
   - concepts/jwt.md
   - executions/TASK-001-result.md

3. LLM 生成分析：
   - 已有 JWT 基础
   - 需要新增: OAuth2 provider, callback handler, token exchange
   - 建议拆分为 3 个 Sub-Tasks

4. 自动创建新 Issue:
   
   # TASK-005: 基于现有认证系统实现 OAuth2
   
   ## 前置知识 (来自 Wiki)
   - 已有 JWT 实现: [[entities/jwt-middleware]]
   - 用户系统: [[entities/auth-system]]
   
   ## Sub-Tasks
   - [ ] TASK-005-1: 集成 Google OAuth2 provider
   - [ ] TASK-005-2: 实现 callback handler
   - [ ] TASK-005-3: token exchange & user linking
   
   ## References
   - 相关概念: [[concepts/oauth2-flow]]
   - 前置任务: [[entities/TASK-001]]
```

---

## 5. 技术实现方案

### 5.1 目录结构整合

```
~/.capture/
├── config.yaml                 # 主配置
├── issues/                     # Issue 存储 (可执行单元)
│   └── 2026/
│       └── 04/
│           ├── TASK-001.md
│           └── TASK-002.md
│
├── wiki/                       # 知识库 (累积性)
│   ├── index.md               # 内容索引
│   ├── log.md                 # 时间线日志
│   ├── entities/              # 实体页面
│   │   ├── TASK-001.md       # Issue 实体
│   │   ├── auth-system.md    # 系统实体
│   │   └── jwt.md            # 技术实体
│   ├── concepts/              # 概念页面
│   ├── sources/               # 原始资源摘要
│   ├── executions/            # 执行结果归档
│   └── comparisons/           # 对比分析
│
├── raw/                       # 原始资源 (Karpathy 模式)
│   ├── sources/              # 外部文档
│   └── assets/               # 图片等资源
│
└── agents/                    # Agent 配置
    └── agents.yaml
```

### 5.2 Schema 设计 (CLAUDE.md 扩展)

```markdown
# CLAUDE.md - Capture System Schema

## 系统架构

本系统整合了两个核心模式：
1. **Issue-Driven Execution** (当前系统) - 可执行的任务管理
2. **Wiki-Based Knowledge** (Karpathy 模式) - 累积的知识库

## Issue 规范

- Issue 存储在 `issues/YYYY/MM/TASK-XXXXX.md`
- 必须有 id, title, stage, status 字段
- Stage Pipeline: inbox → analysis → planning → dispatch → execution → review

## Wiki 规范

### 目录结构
- `wiki/entities/` - 实体页面 (Issue, 系统组件, 技术栈)
- `wiki/concepts/` - 概念页面 (设计模式, 架构决策)
- `wiki/sources/` - 资源摘要 (外部文档的本地总结)
- `wiki/executions/` - 执行结果归档
- `wiki/index.md` - 自动维护的内容索引
- `wiki/log.md` - 时间线日志

### 页面模板

**Entity Page** (`wiki/entities/*.md`):
```yaml
---
type: entity
entity_type: issue|system|tech|component
created: 2026-04-06
updated: 2026-04-06
related: ["entity-1", "entity-2"]
---

# Entity Name

## Description
...

## Related
- [[entities/related-1]]
- [[concepts/concept-1]]

## History
- [2026-04-06] Created from [[sources/source-1]]
```

**Concept Page** (`wiki/concepts/*.md`):
```yaml
---
type: concept
domain: architecture|security|performance
created: 2026-04-06
---

# Concept Name

## Definition
...

## Applications
- [[entities/entity-1]]

## See Also
- [[concepts/related-concept]]
```

## 工作流程

### 1. Issue Ingestion (Issue → Wiki)

当 Issue 创建或进入 Analysis Stage 时：

1. 创建 `wiki/entities/TASK-XXXX.md`
2. 提取关键概念 → 创建/更新 `wiki/concepts/*.md`
3. 更新 `wiki/index.md`
4. 追加到 `wiki/log.md`

### 2. Agent Execution (Execution → Wiki)

当 Agent 完成 Task 时：

1. 创建 `wiki/executions/TASK-XXXX-YYYYMMDD.md`
2. 提取生成的组件 → 创建 `wiki/entities/*.md`
3. 更新相关概念页面
4. 追加到 `wiki/log.md`

### 3. Knowledge Query (Wiki → Issue)

当用户基于 Wiki 知识创建新任务时：

1. LLM 读取相关 Wiki 页面
2. 生成分析和 Sub-Tasks
3. 创建新 Issue，引用 Wiki 实体

## 命名约定

- Issue ID: TASK-XXXXX
- Entity ID: 小写 + 连字符 (auth-system, jwt-middleware)
- Concept ID: 小写 + 连字符 (dependency-injection)
```

### 5.3 关键接口设计

```go
// WikiService - 知识库服务
type WikiService interface {
    // Ingest Issue 到 Wiki
    IngestIssue(ctx context.Context, issue *model.Task) error
    
    // 归档 Agent 执行结果
    ArchiveExecution(ctx context.Context, taskID string, result *ExecutionResult) error
    
    // 基于 Wiki 知识创建 Issue
    CreateIssueFromKnowledge(ctx context.Context, query string) (*model.Task, error)
    
    // 查询 Wiki
    Query(ctx context.Context, query string) (*WikiQueryResult, error)
    
    // Lint Wiki 健康状态
    Lint(ctx context.Context) (*WikiLintReport, error)
    
    // 获取 Entity 页面
    GetEntity(ctx context.Context, entityID string) (*EntityPage, error)
    
    // 更新 Index
    UpdateIndex(ctx context.Context) error
}

// Wiki 页面类型
type EntityPage struct {
    Type       string   // entity
    EntityType string   // issue, system, tech, component
    ID         string
    Title      string
    Content    string
    Related    []string // 关联实体
    Created    time.Time
    Updated    time.Time
    Source     string   // 来源 Issue/Source
}
```

---

## 6. 与现有系统的整合点

### 6.1 Stage Pipeline 集成

```
┌─────────┐     ┌───────────┐     ┌─────────────────────────────────────┐
│  Stage  │────►│  Trigger  │────►│  Wiki Action                        │
└─────────┘     └───────────┘     └─────────────────────────────────────┘

Inbox     ─────► Issue 创建 ─────► 创建 entities/TASK-XXX.md
                                   更新 index.md
                                   追加 log.md

Analysis  ─────► 分析完成 ──────► 更新 entities/TASK-XXX.md
                                   创建/更新 concepts/*.md
                                   提取 technical decisions

Planning  ─────► 规划完成 ──────► 创建 wiki/plans/TASK-XXX-plan.md
                                   关联相关 entities

Execution ─────► Agent 完成 ────► 创建 executions/TASK-XXX-YYYYMMDD.md
                                   创建 entities/组件-XXX.md
                                   更新相关 concepts

Review    ─────► 审核完成 ──────► 标记为 completed
                                   更新综合总结
```

### 6.2 Feishu 同步扩展

| 数据类型 | 当前同步 | Wiki 同步扩展 |
|---------|---------|--------------|
| Issue | Feishu Bitable | 同步 Wiki index 作为只读视图 |
| Task Status | 状态变更通知 | Wiki log 变更通知 |
| Agent Result | 结果摘要 | Wiki execution 页面链接 |
| Knowledge | N/A | Feishu 文档作为 Source Ingest |

---

## 7. 收益分析

### 7.1 带来的价值

| 维度 | 收益 |
|------|------|
| **知识累积** | Issue 执行结果自动归档，形成可复用的技术资产 |
| **上下文保持** | 新 Issue 可基于已有 Wiki 知识，无需重复分析 |
| **团队共享** | Wiki 作为团队知识库，降低 onboarding 成本 |
| **AI 增强** | LLM 基于丰富上下文提供更精准的建议 |
| **可追溯性** | 完整的时间线 log，任何决策都有据可查 |

### 7.2 成本考量

| 成本项 | 说明 |
|--------|------|
| 存储 | Markdown 文本，成本极低 |
| LLM Token | Ingest 和 Archive 时消耗，可控 |
| 维护 | LLM 自动维护，人工仅需定期 Lint |
| 学习 | 需要理解 Wiki 模式，有学习曲线 |

---

## 8. 实施建议

### 8.1 分阶段实施

**Phase 1: 基础 Wiki 集成** (2-3 周)
- [ ] 创建 wiki/ 目录结构
- [ ] 实现 Issue → Wiki Ingest
- [ ] 自动生成 entities/ 和 index.md
- [ ] 更新 CLAUDE.md Schema

**Phase 2: Agent 结果归档** (2 周)
- [ ] 实现 Execution → Wiki Archive
- [ ] 自动提取组件文档
- [ ] 更新 log.md 时间线

**Phase 3: 知识驱动 Issue** (2 周)
- [ ] 实现 Wiki Query 接口
- [ ] 基于知识生成 Sub-Tasks
- [ ] Wiki → Issue 反向链接

**Phase 4: 高级功能** (2-3 周)
- [ ] Lint 功能 (矛盾检测、过期检查)
- [ ] Feishu Wiki 同步
- [ ] Obsidian 集成优化

### 8.2 与 Obsidian 的协作

```
推荐工作流:

1. 在 Terminal 中使用 capture CLI 管理 Issue
2. Agent 执行时，自动更新 Wiki
3. 在 Obsidian 中浏览 Wiki，查看:
   - Graph View: 知识关联图谱
   - 实体页面: Issue、组件、概念
   - 时间线: log.md 的历史记录
4. 在 Obsidian 中编辑 Schema，优化 LLM 行为
5. 基于 Wiki 知识，在 Terminal 创建新 Issue
```

---

## 9. 结论

### 9.1 可行性: ✅ 高度可行

Karpathy Wiki 模式与当前 Issue 系统的整合具有高度可行性：

1. **技术兼容**: 两者都基于 Markdown + YAML Frontmatter
2. **架构互补**: Issue 负责"执行"，Wiki 负责"知识"
3. **场景丰富**: 覆盖任务全生命周期的知识管理
4. **工具成熟**: Obsidian 提供优秀的 Wiki 浏览体验

### 9.2 关键设计原则

1. **Issue 优先**: Issue 仍是主要工作单元，Wiki 是增强
2. **自动维护**: Wiki 更新由 LLM 自动完成，减少人工负担
3. **双向链接**: Issue ↔ Wiki 互相引用，形成知识网络
4. **Local First**: Wiki 本地存储，Git 版本控制

### 9.3 下一步行动

1. **立即开始**: 创建 wiki/ 基础目录结构
2. **本周完成**: 实现简单的 Issue → Entity Ingest
3. **下周开始**: 集成到 Stage Pipeline
4. **验证**: 用一个实际 Issue 测试完整流程

---

*分析报告完成时间: 2026-04-06*
