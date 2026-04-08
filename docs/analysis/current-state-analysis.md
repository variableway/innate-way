# Task 1: 当前目录结构分析与改善建议

> 来源: tasks/mindstorm/overview.md - Task 1
> 日期: 2026-04-08

## 一、当前状态

innate 目录下 15 个项目全部平铺在同一层级，没有分组：

```
innate/
├── copy-modify          # my-tokscale (Token 排行榜)
├── innate-capture       # 任务捕获 CLI
├── innate-chaos         # 交易信号仪表盘
├── innate-feeds         # GitHub Stars 收集器
├── innate-keep-them     # YouTube 下载器
├── innate-next-mono     # 共享 UI 组件库
├── innate-smalllove     # 关系模拟沙箱
├── innate-susu          # AI 教育平台
├── innate-way           # 文档和任务管理
├── innate-websites      # 个人作品网站
├── selfhost-agent       # 自托管 AI 环境指南
├── solutions            # 解决方案集合
├── spark-cli            # CLI 工具
├── spark-skills         # AI 技能
└── web                  # Web 应用集合
```

## 二、发现的问题

### 2.1 结构层面

| 问题 | 说明 |
|------|------|
| **扁平无分组** | 15 个项目全部同级，无法一眼看出归属关系 |
| **命名不统一** | `spark-*`、`innate-*`、独立名称混用，无法从名字判断类型 |
| **共享资源混入产品** | `innate-next-mono` 是共享组件库，`web` 是多项目集合，但和产品平级 |
| **定位模糊的项目** | `copy-modify`（token 排行榜）、`web`（多项目杂烩）归属不清 |

### 2.2 文档层面

| 问题 | 说明 |
|------|------|
| **缺少中心文档** | 没有总览 README 解释整个生态 |
| **部分项目缺 README** | `innate-smalllove`、`web`、`solutions` 缺少说明文档 |
| **项目关系不明** | 哪些产品用了 `innate-next-mono` 的组件？不清楚 |

### 2.3 核心缺失：知识管理

当前最大的缺口是**从想法到实现的过程没有被系统记录**。整个工作流是：

```
想法 → 捕获 → 选择 → AI 实现 → 产品
```

但目前只有首尾有对应工具（innate-capture 捕获，产品代码是结果），中间的**选择、实现过程、决策记录**散落在各处或丢失。

## 三、参考项目研究

### 3.1 qmd (Tobi Lutke / Shopify 创始人)

**定位**：本地知识搜索引擎

**核心理念**：知识管理 = 检索问题。把所有文件（Markdown、代码、文档）索引进 SQLite，用混合搜索（BM25 + 向量 + LLM 重排序）检索。

**值得借鉴的**：
- **混合搜索管线**：关键词 + 语义 + LLM 重排序，三层逐步精确
- **Collection 概念**：按目录分组建立命名集合，各自独立索引
- **Context 系统**：给目录附加描述性元数据，搜索结果带着上下文返回
- **MCP Server**：暴露搜索工具给 AI Agent，让 AI 能检索你的知识库
- **完全本地**：不依赖外部 API，数据不离开机器

### 3.2 MemPalace

**定位**：AI 对话记忆持久化系统

**核心理念**：存储一切原始对话，用空间结构（宫殿隐喻）组织，不做摘要压缩（因为会丢失"为什么"的上下文）。

**值得借鉴的**：
- **四层记忆栈**：L0 身份（~50 tokens，始终加载）→ L1 关键事实 → L2 按需检索 → L3 深度语义搜索
- **时间线知识图谱**：事实有时间窗口，可以查询"某天什么是真的"
- **专家 Agent 日记**：不同 Agent 各自维护领域记忆
- **"存储一切"哲学**：不做蒸馏，保留原始对话和决策上下文

### 3.3 对比与适用性

| 维度 | qmd | MemPalace | 你的需求 |
|------|-----|-----------|----------|
| **解决的核心问题** | 文件/文档检索 | AI 对话记忆 | **想法→实现过程记录** |
| **数据源** | 现有文件 | AI 聊天记录 | task 文件 + 实现过程 + 产品代码 |
| **搜索** | 混合 BM25+向量+重排序 | 语义+元数据过滤 | 都需要 |
| **AI 集成** | MCP Server | MCP Server + 自动保存 | MCP 是好的接口标准 |

**结论**：两者互补。qmd 适合检索已有文档和代码，MemPalace 适合记录 AI 协作过程。但你的场景更偏向需要一个**过程记录系统**——把从想法到产品的每一步（包括 AI 实现）留存下来。

## 四、改善建议

### 4.1 目录结构重组（建议方案）

```
innate/
├── README.md                     # 生态总览
│
├── spark/                        # 工程工具层
│   ├── spark-cli
│   └── spark-skills
│
├── products/                     # 产品层
│   ├── innate-capture            # 任务捕获
│   ├── innate-feeds              # 信息流
│   ├── innate-chaos              # 交易
│   ├── innate-keep-them          # 媒体下载
│   ├── innate-susu               # 教育
│   └── innate-smalllove          # 关系模拟
│
├── infra/                        # 基础设施层
│   ├── innate-next-mono          # 共享 UI 组件
│   ├── innate-websites           # 作品网站
│   ├── web                       # Web 应用集合
│   └── selfhost-agent            # 自托管指南
│
├── solutions/                    # 解决方案（保持独立）
│   └── ...
│
├── innate-way/                   # 知识与规划中心（不变）
│   ├── docs/
│   ├── tasks/
│   └── tracing/                  # 过程追踪
│
└── copy-modify                   # 独立工具（或移入 spark）
```

**核心变化**：
1. `spark/`、`products/`、`infra/` 分层目录，从名字就能定位
2. `innate-way` 定位为**知识与规划中心**，不变
3. `solutions` 保持独立，因为它产出的是面向客户的方案

### 4.2 补充知识管理系统

当前最缺的是**过程记录**。建议在 innate-way 中建立 tracing 体系：

```
innate-way/
├── tasks/                        # 任务定义（已有）
├── docs/                         # 文档（已有）
├── tracing/                      # 过程追踪（新增）
│   ├── tracing.md                # 某个任务的完整过程记录
│   └── ...
└── knowledge/                    # 知识库（新增，未来可接入 qmd）
    ├── decisions/                # 决策记录
    ├── learnings/                # 经验总结
    └── patterns/                 # 代码/架构模式
```

**短期**（立即可做）：
- 利用 github-task-workflow 的 tracing 功能，每个任务自动记录过程
- 在 innate-way/docs 中积累决策和经验文档

**中期**（1-2 周后）：
- 引入 qmd 做本地知识检索，索引 innate-way 和各项目的文档
- 通过 MCP Server 让 AI Agent 能搜索历史知识

**长期**：
- 考虑 MemPalace 的四层记忆架构，给 AI Agent 持久的上下文
- 专家 Agent 各自维护领域知识（spark Agent 记工程知识，产品 Agent 记业务知识）

### 4.3 优先级排序

| 优先级 | 事项 | 原因 |
|--------|------|------|
| **P0** | 确认目录重组方案 | 一切的基础，早做早受益 |
| **P0** | innate-way 中建立 tracing 体系 | 解决核心缺失：过程记录 |
| **P1** | 补齐缺失的 README | 降低认知成本 |
| **P2** | 引入 qmd 做本地检索 | 需要先有足够内容再建索引 |
| **P3** | 考虑 MemPalace 架构 | 需要更多 input 和验证 |

## 五、待讨论

1. **目录重组是否要做？** 建议是做，但可以渐进式——先把新项目按新结构放，旧项目逐步迁移
2. **knowledge 目录放在 innate-way 还是独立仓库？** 如果未来要接入 qmd，可能独立更好
3. **copy-modify 归属？** 是工具（归 spark）还是独立项目？
4. **web 目录的处理？** 里面包含多个不相关项目，需要拆分或明确用途
