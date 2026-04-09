# Capture TUI 输入模块 - 任务分解

## 任务总览

```
Phase 1: 基础架构 (P0) ──────────────────────────────┐
  ├── Task 1.1: 目录结构设计                        │
  ├── Task 1.2: 核心数据模型设计                    │
  ├── Task 1.3: 配置系统实现                        │
  └── Task 1.4: 基础存储层实现                      │
                                                    │
Phase 2: CLI直接输入 (P0) ───────────────────────────┤
  ├── Task 2.1: 命令行接口设计                      │
  ├── Task 2.2: 输入解析器实现                      │
  ├── Task 2.3: 分类管理系统                        │
  ├── Task 2.4: 文件存储格式实现                    │
  └── Task 2.5: 索引系统实现                        │
                                                    │
Phase 3: AI处理 (P1) ────────────────────────────────┤
  ├── Task 3.1: AI分析接口封装                      │
  ├── Task 3.2: 内容摘要生成                        │
  ├── Task 3.3: 任务提取功能                        │
  └── Task 3.4: 分类汇总报告                        │
                                                    │
Phase 4: 对话记录 (P1) ──────────────────────────────┤
  ├── Task 4.1: conversation-recorder Skill设计     │
  ├── Task 4.2: 会话捕获机制实现                    │
  ├── Task 4.3: 思考过程记录                        │
  └── Task 4.4: 会话导出功能                        │
                                                    │
Phase 5: 导出与集成 (P2) ────────────────────────────┤
  ├── Task 5.1: CSV导出功能                         │
  ├── Task 5.2: JSON导出功能                        │
  ├── Task 5.3: 飞书多维表格对接                    │
  └── Task 5.4: TODO Dashboard生成                │
                                                    │
Phase 6: 优化与文档 (P2) ────────────────────────────┘
  ├── Task 6.1: 性能优化
  ├── Task 6.2: 测试覆盖
  └── Task 6.3: 文档完善
```

---

## Phase 1: 基础架构 (P0)

### Task 1.1: 目录结构设计
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 2h

**描述**:
设计并实现 Capture TUI 的目录结构，包括系统目录、数据目录、模板目录等。

**验收标准**:
- [ ] 创建 `ideas/` 根目录
- [ ] 创建 `.capture/` 系统目录
- [ ] 创建分类目录结构
- [ ] 目录初始化脚本

**输出物**:
- `scripts/init_directories.sh` - 目录初始化脚本

---

### Task 1.2: 核心数据模型设计
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 3h

**描述**:
设计 Entry、Category、Session 等核心数据模型。

**验收标准**:
- [ ] Entry 模型定义（id, title, content, category, tags, created_at, etc.）
- [ ] Category 模型定义（name, count, last_updated）
- [ ] Session 模型定义（session_id, start_time, end_time, turns）
- [ ] 模型验证逻辑

**输出物**:
- `capture_tui/models/entry.py`
- `capture_tui/models/category.py`
- `capture_tui/models/session.py`

---

### Task 1.3: 配置系统实现
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 2h

**描述**:
实现 YAML 配置文件解析和管理系统。

**验收标准**:
- [ ] 配置模型定义
- [ ] 默认配置生成
- [ ] 环境变量支持
- [ ] 配置验证

**输出物**:
- `capture_tui/config.py`
- `.capture/config.yaml` 模板

---

### Task 1.4: 基础存储层实现
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 4h

**描述**:
实现基础的文件读写、索引管理功能。

**验收标准**:
- [ ] 文件读写接口
- [ ] 目录管理接口
- [ ] 索引读写接口
- [ ] 原子操作保证

**输出物**:
- `capture_tui/storage/file_store.py`
- `capture_tui/storage/index_manager.py`

---

## Phase 2: CLI直接输入 (P0)

### Task 2.1: 命令行接口设计
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 3h

**描述**:
使用 Click 或 Argparse 实现命令行接口。

**验收标准**:
- [ ] `capture add` 命令
- [ ] `capture categories` 命令组
- [ ] `capture analyze` 命令
- [ ] `capture export` 命令
- [ ] 参数解析和验证
- [ ] 帮助文档生成

**输出物**:
- `capture_tui/cli/main.py`
- `capture_tui/cli/commands/` 目录

---

### Task 2.2: 输入解析器实现
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 4h

**描述**:
实现多类型输入解析，支持文本、文件、Markdown等。

**验收标准**:
- [ ] 文本输入解析
- [ ] 文件输入读取
- [ ] 任务提取（正则匹配）
- [ ] 标签提取
- [ ] 优先级识别

**输出物**:
- `capture_tui/parser/input_parser.py`
- `capture_tui/parser/extractors.py`

---

### Task 2.3: 分类管理系统
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 3h

**描述**:
实现分类的创建、列表、验证功能。

**验收标准**:
- [ ] 分类创建（自动/手动）
- [ ] 分类数量限制检查（最多10个）
- [ ] 分类列表
- [ ] 分类统计
- [ ] 分类重命名

**输出物**:
- `capture_tui/core/category_manager.py`

---

### Task 2.4: 文件存储格式实现
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 3h

**描述**:
实现带 YAML Frontmatter 的 Markdown 文件存储格式。

**验收标准**:
- [ ] Frontmatter 生成
- [ ] Markdown 内容生成
- [ ] 文件命名规范
- [ ] 模板系统

**输出物**:
- `capture_tui/storage/entry_store.py`
- `.capture/templates/idea.md.tpl`

---

### Task 2.5: 索引系统实现
**状态**: 📝 待开始
**优先级**: P0
**预计工时**: 4h

**描述**:
实现全局索引文件的管理，支持快速检索。

**验收标准**:
- [ ] 索引结构设计
- [ ] 索引自动更新
- [ ] 索引搜索功能
- [ ] 索引重建功能

**输出物**:
- `capture_tui/core/indexer.py`

---

## Phase 3: AI处理 (P1)

### Task 3.1: AI分析接口封装
**状态**: 📝 待开始
**优先级**: P1
**预计工时**: 3h

**描述**:
封装 kimi-cli 的 Agent 能力，提供统一的 AI 调用接口。

**验收标准**:
- [ ] AI 客户端封装
- [ ] 提示词管理
- [ ] 错误处理
- [ ] 结果解析

**输出物**:
- `capture_tui/ai/client.py`
- `capture_tui/ai/prompts.py`

---

### Task 3.2: 内容摘要生成
**状态**: 📝 待开始
**优先级**: P1
**预计工时**: 2h

**描述**:
实现 AI 驱动的内容摘要功能。

**验收标准**:
- [ ] 单条内容摘要
- [ ] 分类批量摘要
- [ ] 摘要模板

**输出物**:
- `capture_tui/ai/summarizer.py`

---

### Task 3.3: 任务提取功能
**状态**: 📝 待开始
**优先级**: P1
**预计工时**: 2h

**描述**:
实现从内容中提取可执行任务的功能。

**验收标准**:
- [ ] 自动任务识别
- [ ] 任务列表生成
- [ ] 任务去重

**输出物**:
- `capture_tui/ai/task_extractor.py`

---

### Task 3.4: 分类汇总报告
**状态**: 📝 待开始
**优先级**: P1
**预计工时**: 4h

**描述**:
实现 `capture analyze` 命令，生成结构化的分类分析报告。

**验收标准**:
- [ ] 主题趋势分析
- [ ] 重复内容识别
- [ ] 行动项提取
- [ ] 优先级分组
- [ ] 报告输出（Markdown）

**输出物**:
- `capture_tui/ai/analyzer.py`
- `capture_tui/reports/category_report.py`

---

## Phase 4: 对话记录 (P1)

### Task 4.1: conversation-recorder Skill设计
**状态**: 📝 待开始
**优先级**: P1
**预计工时**: 4h

**描述**:
设计并编写 conversation-recorder Skill 的配置和功能规范。

**验收标准**:
- [ ] Skill 配置设计
- [ ] Hook 点设计
- [ ] 数据收集规范
- [ ] 元数据定义

**输出物**:
- `.kimi/skills/conversation-recorder/SKILL.md`
- `.kimi/skills/conversation-recorder/config.yaml`

---

### Task 4.2: 会话捕获机制实现
**状态**: 📝 待开始
**优先级**: P1
**预计工时**: 4h

**描述**:
实现会话的启动、记录、结束功能。

**验收标准**:
- [ ] 会话启动命令
- [ ] 会话结束命令
- [ ] 对话轮次记录
- [ ] 会话列表查看

**输出物**:
- `capture_tui/session/manager.py`
- `capture_tui/session/recorder.py`

---

### Task 4.3: 思考过程记录
**状态**: 📝 待开始
**优先级**: P1
**预计工时**: 3h

**描述**:
记录 AI 的思考过程、使用的技能和思维方式。

**验收标准**:
- [ ] 技能使用记录
- [ ] 模型信息记录
- [ ] 分析思路记录
- [ ] 决策原因记录

**输出物**:
- `capture_tui/session/thinking_recorder.py`

---

### Task 4.4: 会话导出功能
**状态**: 📝 待开始
**优先级**: P1
**预计工时**: 2h

**描述**:
实现会话记录的导出功能。

**验收标准**:
- [ ] Markdown 格式导出
- [ ] JSON 格式导出
- [ ] 技能使用统计
- [ ] 行动项提取

**输出物**:
- `capture_tui/session/exporter.py`

---

## Phase 5: 导出与集成 (P2)

### Task 5.1: CSV导出功能
**状态**: 📝 待开始
**优先级**: P2
**预计工时**: 2h

**验收标准**:
- [ ] CSV 格式生成
- [ ] 字段映射
- [ ] 编码处理
- [ ] 大文件分片

**输出物**:
- `capture_tui/exporters/csv_exporter.py`

---

### Task 5.2: JSON导出功能
**状态**: 📝 待开始
**优先级**: P2
**预计工时**: 1h

**验收标准**:
- [ ] JSON 格式生成
- [ ] 嵌套结构支持
- [ ] Schema 定义

**输出物**:
- `capture_tui/exporters/json_exporter.py`

---

### Task 5.3: 飞书多维表格对接
**状态**: 📝 待开始
**优先级**: P2
**预计工时**: 4h

**验收标准**:
- [ ] 飞书 API 封装
- [ ] 认证机制
- [ ] 数据同步
- [ ] 字段映射

**输出物**:
- `capture_tui/exporters/feishu_exporter.py`

---

### Task 5.4: TODO Dashboard生成
**状态**: 📝 待开始
**优先级**: P2
**预计工时**: 3h

**验收标准**:
- [ ] HTML Dashboard 生成
- [ ] 任务筛选
- [ ] 状态统计
- [ ] 交互功能

**输出物**:
- `capture_tui/exporters/dashboard_generator.py`
- `capture_tui/templates/dashboard.html`

---

## Phase 6: 优化与文档 (P2)

### Task 6.1: 性能优化
**状态**: 📝 待开始
**优先级**: P2
**预计工时**: 3h

**验收标准**:
- [ ] 大文件处理优化
- [ ] 索引查询优化
- [ ] 并发处理支持

---

### Task 6.2: 测试覆盖
**状态**: 📝 待开始
**优先级**: P2
**预计工时**: 6h

**验收标准**:
- [ ] 单元测试 (>80%)
- [ ] 集成测试
- [ ] CLI 测试
- [ ] 性能测试

**输出物**:
- `tests/` 目录

---

### Task 6.3: 文档完善
**状态**: 📝 待开始
**优先级**: P2
**预计工时**: 4h

**验收标准**:
- [ ] README.md
- [ ] 使用指南
- [ ] API 文档
- [ ] Skill 使用说明

**输出物**:
- `docs/` 文档目录

---

## 任务统计

| Phase | 任务数 | 预计总工时 | 优先级 |
|-------|--------|-----------|--------|
| Phase 1: 基础架构 | 4 | 11h | P0 |
| Phase 2: CLI直接输入 | 5 | 17h | P0 |
| Phase 3: AI处理 | 4 | 11h | P1 |
| Phase 4: 对话记录 | 4 | 13h | P1 |
| Phase 5: 导出与集成 | 4 | 10h | P2 |
| Phase 6: 优化与文档 | 3 | 13h | P2 |
| **总计** | **24** | **75h** | - |

---

## 里程碑

| 里程碑 | 包含任务 | 预计完成 |
|--------|---------|---------|
| M1: 基础框架完成 | Phase 1 | 第1周 |
| M2: CLI输入可用 | Phase 1-2 | 第3周 |
| M3: AI分析可用 | Phase 1-3 | 第5周 |
| M4: 对话记录可用 | Phase 1-4 | 第7周 |
| M5: v1.0 发布 | Phase 1-6 | 第10周 |
