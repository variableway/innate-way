# Capture TUI

终端输入捕获与管理工具 - 通过 TUI (Terminal User Interface) 记录、管理和分析你的想法、任务和计划。

## 功能特性

### 1. CLI 直接输入

通过命令行快速记录想法：

```bash
# 直接输入
capture add "需要优化登录页面性能" --category=features -t performance,ui

# 从文件导入
capture add --file=./my-ideas.md --category=backlog

# 交互式输入
capture add
```

### 2. 智能分类管理

- 自动按分类存储到 `ideas/` 目录
- 最多支持 10 个分类
- 分类统计和分析

```bash
# 列出分类
capture categories list

# 创建分类
capture categories create bugs --display-name="缺陷跟踪"

# 查看分类详情
capture categories show features
```

### 3. AI 分析

智能分析分类内容，提取主题、任务和趋势：

```bash
# 生成分类分析报告
capture analyze features --output=./analysis.md
```

### 4. 多格式导出

支持多种格式导出：

```bash
# 导出为 CSV
capture export --format=csv --output=todos.csv

# 导出为 Markdown
capture export --format=md --output=summary.md

# 仅导出任务
capture export --format=csv --tasks-only --output=tasks.csv
```

### 5. 对话记录

记录完整的 AI 对话过程：

```bash
# 开始会话
capture session start --name="架构设计讨论" --goal="设计系统架构"

# 结束会话
capture session end --summary="完成了初步设计"

# 列会话
capture session list
```

## 安装

```bash
# 从源码安装
git clone <repository>
cd capture-tui
pip install -e .

# 或使用 pip
pip install capture-tui
```

## 快速开始

### 1. 初始化项目

```bash
capture init --root-dir=./ideas
```

这将创建以下目录结构：

```
ideas/
├── .capture/
│   ├── config.yaml          # 配置文件
│   ├── index.json           # 全局索引
│   └── templates/           # 模板文件
│       └── idea.md.tpl
└── uncategorized/           # 默认分类
```

### 2. 添加第一个想法

```bash
capture add "优化首页加载速度\n\nTODO:\n- [ ] 分析性能瓶颈\n- [ ] 实现懒加载" --category=features -t performance -p P1
```

### 3. 查看统计

```bash
capture stats
```

## 配置

编辑 `ideas/.capture/config.yaml`：

```yaml
version: "1.0"

storage:
  root_dir: "./ideas"
  max_categories: 10
  auto_create_category: true

input:
  default_category: "uncategorized"
  extract_tasks_auto: true

ai:
  enabled: true
  model: "kimi"
  summarize_on_analyze: true

export:
  formats: ["md", "csv", "json"]

session:
  capture_dir: "./docs/capture-tui/sessions"
  auto_capture: true
```

## 数据结构

### Entry 格式

```markdown
---
id: "ideas-20240115-103000-abc123"
category: "features"
created_at: "2024-01-15T10:30:00+08:00"
tags: ["ui", "performance"]
priority: "P1"
source: "cli"
---

# 优化首页加载速度

详细描述...

## 关联任务

- [ ] 分析性能瓶颈
- [ ] 实现懒加载
```

## Skill 集成

使用 `conversation-recorder` Skill 自动记录对话：

```bash
# 在 .kimi/skills/conversation-recorder/config.yaml 中配置
capture session start --name="设计讨论"

# 进行对话...

# 对话结束
capture session end
```

## 开发

### 运行测试

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行所有测试
./run_tests.sh

# 或手动运行
pytest tests/unit -v
pytest tests/integration -v
```

### 项目结构

```
capture_tui/
├── __init__.py
├── cli/
│   └── main.py              # CLI 命令
├── core/
│   ├── client.py            # 核心客户端
│   └── category_manager.py  # 分类管理
├── models/
│   ├── entry.py             # 条目模型
│   ├── category.py          # 分类模型
│   └── session.py           # 会话模型
├── storage/
│   ├── file_store.py        # 文件存储
│   ├── index_manager.py     # 索引管理
│   └── entry_store.py       # 条目存储
├── parser/
│   ├── input_parser.py      # 输入解析
│   └── extractors.py        # 内容提取
├── ai/
│   ├── analyzer.py          # 分类分析
│   ├── summarizer.py        # 内容摘要
│   └── task_extractor.py    # 任务提取
├── exporters/
│   ├── csv_exporter.py      # CSV 导出
│   ├── json_exporter.py     # JSON 导出
│   └── markdown_exporter.py # Markdown 导出
└── session/
    ├── manager.py           # 会话管理
    ├── recorder.py          # 会话记录
    └── exporter.py          # 会话导出

tests/
├── unit/                    # 单元测试
└── integration/             # 集成测试
```

## 命令参考

### 核心命令

| 命令 | 描述 |
|------|------|
| `capture init` | 初始化项目 |
| `capture add` | 添加想法 |
| `capture categories list` | 列出分类 |
| `capture categories create` | 创建分类 |
| `capture analyze` | 分析分类 |
| `capture export` | 导出数据 |
| `capture session start` | 开始会话 |
| `capture session end` | 结束会话 |
| `capture session list` | 列出会话 |
| `capture stats` | 显示统计 |

## 许可证

MIT License
