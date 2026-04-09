# Capture TUI 输入模块 - 技术架构设计

## 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Capture TUI 系统                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   CLI Layer     │    │  Input Parser   │    │  Storage Layer  │         │
│  │   (交互入口)     │◄──►│   (输入解析)     │◄──►│   (存储管理)     │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│         │                      │                      │                     │
│         ▼                      ▼                      ▼                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │  Command Router │    │  AI Processor   │    │  Output Adapter │         │
│  │   (命令路由)     │◄──►│   (AI处理)      │◄──►│   (输出适配)     │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│         │                      │                      │                     │
│         ▼                      ▼                      ▼                     │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                      Skill Integration                           │       │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │       │
│  │  │ github-web-  │  │ local-work-  │  │ conversation-        │  │       │
│  │  │   follow     │  │   flow       │  │   recorder           │  │       │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘  │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 模块详细设计

### 2.1 CLI Layer (命令行接口层)

#### 2.1.1 命令设计

```bash
# ===== 场景1: CLI直接输入 =====

# 添加想法
capture add "想法内容" --category=features

# 添加想法（交互式）
capture add --interactive

# 从文件导入
capture add --file=./my-ideas.md --category=notes

# 列出所有分类
capture categories list

# 查看分类内容
capture categories show features

# AI 分析分类
capture analyze features --output=summary.md

# 导出为 TODO
capture export --format=csv --output=todos.csv
capture export --format=feishu  # 同步到飞书

# ===== 场景2: 对话记录 =====

# 启动对话记录会话
capture session start --name="架构讨论"

# 结束并保存会话
capture session end

# 查看历史会话
capture sessions list

# 导出会话
capture session export <session-id> --format=markdown
```

#### 2.1.2 参数规范

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| --category, -c | string | 否 | 分类名称，默认 "uncategorized" |
| --tags, -t | string[] | 否 | 标签列表 |
| --file, -f | path | 否 | 从文件读取内容 |
| --interactive, -i | boolean | 否 | 交互式输入 |
| --output, -o | path | 否 | 输出路径 |
| --format | string | 否 | 导出格式: md, csv, json, feishu |

---

### 2.2 Input Parser (输入解析层)

#### 2.2.1 输入类型支持

```python
from enum import Enum
from typing import Union

class InputType(Enum):
    TEXT = "text"           # 纯文本
    FILE = "file"           # 文件路径
    URL = "url"             # URL链接
    MARKDOWN = "markdown"   # Markdown格式

class ParsedInput:
    def __init__(self):
        self.raw_content: str
        self.input_type: InputType
        self.metadata: dict
        self.extracted_tasks: list
        self.tags: list
```

#### 2.2.2 内容提取规则

```python
# 任务提取正则
TASK_PATTERNS = [
    r'- \[ \] (.+)',           # Markdown todo
    r'TODO[:：]\s*(.+)',       # TODO: 任务
    r'任务[:：]\s*(.+)',       # 任务: 任务
    r'ACTION[:：]\s*(.+)',      # ACTION: 动作
]

# 标签提取
TAG_PATTERN = r'#(\w+)'

# 优先级标记
PRIORITY_PATTERNS = {
    'P0': r'\bP0\b|【紧急】|【高优先级】',
    'P1': r'\bP1\b|【重要】',
    'P2': r'\bP2\b|【一般】',
}
```

---

### 2.3 Storage Layer (存储层)

#### 2.3.1 目录结构设计

```
ideas/                              # 根目录
├── .capture/                       # 系统文件
│   ├── config.yaml                 # 配置
│   ├── index.json                  # 全局索引
│   └── templates/                  # 模板
│       ├── idea.md.tpl
│       ├── session.md.tpl
│       └── summary.md.tpl
├── uncategorized/                  # 默认分类
│   └── 2024-01/
│       └── 15-001-untitled.md
├── features/                       # 功能分类
│   ├── 2024-01/
│   │   ├── 15-001-dashboard.md
│   │   └── 16-002-export-csv.md
│   └── summary.md                  # 分类汇总
├── bugs/                           # Bug分类
│   └── ...
└── archive/                        # 归档
    └── 2023-12/
        └── ...
```

#### 2.3.2 文件命名规范

```python
# 命名格式: {YY}-{MM}/{DD}-{SEQ}-{slug}.md
# 示例: 2024-01/15-001-dashboard-redesign.md

def generate_filename(title: str, category: str, seq: int) -> str:
    """生成文件名"""
    date = datetime.now()
    slug = slugify(title)[:30]  # 限制长度
    return f"{date.strftime('%Y-%m')}/{date.strftime('%d')}-{seq:03d}-{slug}.md"
```

#### 2.3.3 索引设计

```json
{
  "version": "1.0",
  "last_updated": "2024-01-15T10:30:00+08:00",
  "categories": [
    {
      "name": "features",
      "count": 15,
      "last_entry": "2024-01-15T10:30:00+08:00"
    }
  ],
  "entries": [
    {
      "id": "ideas-20240115-001",
      "path": "features/2024-01/15-001-dashboard.md",
      "category": "features",
      "title": "Dashboard  redesign",
      "tags": ["ui", "improvement"],
      "created_at": "2024-01-15T10:30:00+08:00",
      "has_tasks": true
    }
  ],
  "stats": {
    "total_entries": 42,
    "total_categories": 5,
    "pending_tasks": 18
  }
}
```

---

### 2.4 AI Processor (AI处理层)

#### 2.4.1 分析任务类型

```python
class AnalysisTask(Enum):
    SUMMARIZE = "summarize"         # 内容摘要
    EXTRACT_TASKS = "extract_tasks" # 提取任务
    CATEGORIZE = "categorize"       # 智能分类
    PRIORITIZE = "prioritize"       # 优先级排序
    LINK_RELATED = "link_related"   # 关联分析
```

#### 2.4.2 AI 分析提示词模板

```python
SUMMARIZE_PROMPT = """
请分析以下 {category} 分类中的所有想法，并生成一份结构化的汇总报告。

要求：
1. 提取核心主题和趋势
2. 识别重复或相关的想法
3. 提炼出可执行的行动项
4. 按优先级分组

输出格式：
## 核心主题
...

## 趋势分析
...

## 行动项 (按优先级)
### P0 - 紧急
- [ ] 任务1

### P1 - 重要
- [ ] 任务2

## 相关想法分组
...
"""
```

---

### 2.5 Output Adapter (输出适配层)

#### 2.5.1 导出格式支持

| 格式 | 文件扩展名 | 用途 |
|------|-----------|------|
| Markdown | .md | 本地查看、版本控制 |
| CSV | .csv | Excel处理、简单导入 |
| JSON | .json | 程序处理、API对接 |
| YAML | .yaml | 配置文件、 Hugo/Jekyll |
| 飞书 | - | 同步到飞书多维表格 |

#### 2.5.2 CSV 导出格式

```csv
id,category,title,tags,created_at,content,tasks,priority
ideas-20240115-001,features,Dashboard redesign,"ui,improvement",2024-01-15T10:30:00+08:00,"重新设计dashboard...","[task1|task2]",P1
```

#### 2.5.3 飞书多维表格对接

```python
class FeishuExporter:
    """飞书多维表格导出器"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.client = FeishuClient(app_id, app_secret)
    
    def export_entries(self, entries: list, table_id: str):
        """导出条目到飞书表格"""
        records = [self._convert_to_record(e) for e in entries]
        self.client.batch_create_records(table_id, records)
    
    def _convert_to_record(self, entry: dict) -> dict:
        return {
            "ID": entry["id"],
            "标题": entry["title"],
            "分类": entry["category"],
            "标签": ",".join(entry["tags"]),
            "创建时间": entry["created_at"],
            "内容": entry["content"][:5000],  # 限制长度
            "待办任务": len(entry.get("tasks", [])),
            "状态": "待处理"
        }
```

---

## 3. Skill 集成设计

### 3.1 conversation-recorder Skill

#### 功能说明
用于捕获和记录完整的 AI 对话过程。

#### 工作原理

```
┌──────────────┐      ┌────────────────────┐      ┌──────────────┐
│   User Input │─────►│  kimi-cli Process  │─────►│  AI Response │
└──────────────┘      └────────────────────┘      └──────────────┘
                            │
                            ▼
                    ┌────────────────────┐
                    │ conversation-      │
                    │ recorder Skill     │
                    │ • 记录输入          │
                    │ • 记录输出          │
                    │ • 记录元数据        │
                    └────────────────────┘
                            │
                            ▼
                    ┌────────────────────┐
                    │ 保存到会话文件      │
                    │ sessions/          │
                    │   {date}/          │
                    │   {session-id}.md  │
                    └────────────────────┘
```

#### Skill 配置

```yaml
# .kimi/skills/conversation-recorder/config.yaml
name: conversation-recorder
version: 1.0.0
type: hook  # hook / command / agent

triggers:
  - before_request
  - after_response

config:
  capture_dir: "./docs/capture-tui/sessions"
  capture_thinking: true
  capture_skills: true
  max_session_duration: 3600  # 秒
```

---

### 3.2 Skill 集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                      kimi-cli 环境                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ github-web-  │  │ local-work-  │  │ conversation │      │
│  │ follow       │  │ flow         │  │ recorder     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            ▼                                │
│                   ┌─────────────────┐                       │
│                   │  Skill Manager  │                       │
│                   │  (技能调度中心)  │                       │
│                   └─────────────────┘                       │
│                            │                                │
│         ┌──────────────────┼──────────────────┐            │
│         ▼                  ▼                  ▼            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  External    │  │  Project     │  │  Session     │      │
│  │  Resources   │  │  Files       │  │  Records     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 数据流设计

### 4.1 CLI输入流程

```
用户输入 ──► 命令解析 ──► 输入验证 ──► 内容解析 ──► 元数据提取
                                              │
                                              ▼
存储到文件 ◄── 更新索引 ◄── 生成分类目录 ◄── 分类判断
                                              │
                                              ▼
                                         AI分析(可选)
                                              │
                                              ▼
                                         导出/同步(可选)
```

### 4.2 对话记录流程

```
会话开始 ──► 初始化记录器 ──► 循环: ┬──► 用户输入 ──► 记录输入
                                  │
                                  ├──► AI处理 ──► 记录技能/模型
                                  │
                                  └──► AI输出 ──► 记录输出
                                             │
                                             ▼
会话结束 ──► 生成摘要 ──► 保存会话文件 ──► 更新索引
```

---

## 5. 配置设计

### 5.1 全局配置

```yaml
# .capture/config.yaml
version: "1.0"

# 存储配置
storage:
  root_dir: "./ideas"
  max_categories: 10
  auto_create_category: true
  archive_after_days: 90

# 输入配置
input:
  default_category: "uncategorized"
  extract_tasks_auto: true
  extract_tags_auto: true

# AI配置
ai:
  enabled: true
  model: "kimi"
  summarize_on_analyze: true
  auto_categorize: false

# 导出配置
export:
  formats: ["md", "csv", "json"]
  feishu:
    enabled: false
    app_id: "${FEISHU_APP_ID}"
    app_secret: "${FEISHU_APP_SECRET}"
    default_table: ""

# 会话配置
session:
  capture_dir: "./docs/capture-tui/sessions"
  auto_capture: true
  capture_thinking: true
```

---

## 6. 接口设计

### 6.1 Python API

```python
from capture_tui import CaptureClient

# 初始化
client = CaptureClient(config_path="./.capture/config.yaml")

# 添加想法
entry = client.add_idea(
    content="优化Dashboard性能",
    category="features",
    tags=["performance", "ui"]
)

# 获取分类
entries = client.get_category("features")

# 分析分类
analysis = client.analyze_category("features")

# 导出
client.export(format="csv", output="./export.csv")
```

---

## 7. 扩展性设计

### 7.1 插件机制

```python
class CapturePlugin:
    """插件基类"""
    
    def on_init(self, config: dict):
        """初始化时调用"""
        pass
    
    def before_add(self, content: str, metadata: dict) -> tuple:
        """添加前处理，返回修改后的内容"""
        return content, metadata
    
    def after_add(self, entry_id: str, entry_path: str):
        """添加后处理"""
        pass
    
    def on_export(self, entries: list, format: str) -> list:
        """导出前处理"""
        return entries
```

### 7.2 支持的扩展点

- 自定义存储后端 (S3, Database, etc.)
- 自定义导出格式
- 自定义 AI 处理器
- 自定义输入解析器

---

## 8. 部署与使用

### 8.1 安装

```bash
# 通过 pip 安装
pip install capture-tui

# 或通过源码安装
git clone https://github.com/xxx/capture-tui
cd capture-tui
pip install -e .
```

### 8.2 初始化项目

```bash
capture init
# 创建目录结构
# 生成默认配置
```

### 8.3 日常使用

```bash
# 快速记录想法
capture add "需要优化登录页面"

# 分类记录
capture add "Dashboard API设计" -c features -t api,design

# 查看汇总
capture analyze features

# 导出任务
capture export --tasks-only --format=csv
```
