# Capture TUI - 可执行教程

本教程提供可执行的步骤来学习 Capture TUI 工具的使用。

## 目录

1. [快速开始](#快速开始)
2. [核心功能教程](#核心功能教程)
3. [高级用法](#高级用法)

---

## 快速开始

### 1. 初始化项目

```bash
# 进入工作目录
cd /Users/patrick/innate/innate-way

# 初始化 capture 项目
capture init --root-dir=./kimi-ana/ideas

# 或使用 Python 直接运行
python -m capture_tui init --root-dir=./kimi-ana/ideas
```

### 2. 验证安装

```bash
# 检查版本
capture --help

# 查看统计信息
capture stats
```

---

## 核心功能教程

### 教程 1: 添加想法

**目标**: 学习如何记录想法和任务

```bash
# 方式 1: 直接添加
capture add "优化登录页面性能" --category=features -t performance,ui -p P1

# 方式 2: 交互式添加
capture add --interactive

# 方式 3: 从文件添加
echo "- [ ] 实现用户认证" > /tmp/todo.txt
capture add --file=/tmp/todo.txt --category=backlog
```

**验证**:
```bash
# 查看已添加的想法
capture categories show features
```

### 教程 2: 管理分类

**目标**: 创建和管理分类

```bash
# 列出所有分类
capture categories list

# 创建新分类
capture categories create bugs --display-name="缺陷跟踪" --description="记录系统缺陷"
capture categories create docs --display-name="文档任务" --description="文档相关任务"

# 查看分类详情
capture categories show bugs
capture categories show docs
```

### 教程 3: AI 分析

**目标**: 使用 AI 分析分类内容

```bash
# 先添加一些示例数据
capture add "实现响应式设计" --category=features -t ui,mobile
capture add "添加暗黑模式" --category=features -t ui,theming
capture add "修复登录超时问题" --category=bugs -t auth,critical

# 分析分类
capture analyze features --output=./kimi-ana/analysis-features.md
capture analyze bugs --output=./kimi-ana/analysis-bugs.md --format=json
```

**查看结果**:
```bash
cat ./kimi-ana/analysis-features.md
```

### 教程 4: 数据导出

**目标**: 学习多种导出格式

```bash
# 导出为 Markdown
capture export --format=md --output=./kimi-ana/export.md

# 导出为 CSV
capture export --format=csv --output=./kimi-ana/export.csv

# 导出为 JSON
capture export --format=json --output=./kimi-ana/export.json

# 仅导出任务
capture export --format=md --tasks-only --output=./kimi-ana/todos.md
```

### 教程 5: 会话记录

**目标**: 记录 AI 对话会话

```bash
# 开始会话
capture session start --name="功能设计讨论" --goal="设计新的API接口"

# 此时进行 AI 对话...
# 对话内容会被自动记录

# 结束会话
capture session end --summary="完成了API设计的初步方案"

# 查看会话列表
capture session list
```

---

## 高级用法

### 完整工作流示例

```bash
#!/bin/bash
# 完整工作流示例脚本

# 1. 确保项目已初始化
if [ ! -d "./kimi-ana/ideas/.capture" ]; then
    capture init --root-dir=./kimi-ana/ideas
fi

# 2. 创建必要的分类
capture categories create roadmap --display-name="产品路线图" 2>/dev/null || true
capture categories create ideas --display-name="创意池" 2>/dev/null || true

# 3. 添加想法
capture add "# 新功能想法

## 描述
实现一个智能推荐系统

## 任务
- [ ] 调研推荐算法
- [ ] 设计数据模型
- [ ] 实现核心逻辑" \
    --category=roadmap \
    -t ai,recommendation \
    -p P0

# 4. 分析
capture analyze roadmap --output=./kimi-ana/roadmap-analysis.md

# 5. 导出任务列表
capture export --category=roadmap --tasks-only --format=md --output=./kimi-ana/tasks.md

echo "✅ 工作流完成！"
echo "📊 分析报告: ./kimi-ana/roadmap-analysis.md"
echo "📝 任务列表: ./kimi-ana/tasks.md"
```

### 使用配置文件

创建配置文件 `./kimi-ana/.capture-config.yaml`:

```yaml
version: "1.0"

storage:
  root_dir: "./ideas"
  max_categories: 10

input:
  default_category: "ideas"
  extract_tasks_auto: true

ai:
  enabled: true
  model: "kimi"
  summarize_on_analyze: true

export:
  formats: ["md", "csv", "json"]

session:
  capture_dir: "./sessions"
  auto_capture: true
```

使用配置:
```bash
capture --config=./kimi-ana/.capture-config.yaml stats
```

### 自动化脚本示例

**每日想法收集** (`./kimi-ana/daily-capture.sh`):

```bash
#!/bin/bash
# 每日想法收集脚本

DATE=$(date +%Y-%m-%d)
CATEGORY="daily-${DATE}"

# 创建日期分类
capture categories create "daily-${DATE}" --display-name="${DATE} 想法" 2>/dev/null || true

# 添加今日想法
capture add "# ${DATE} 思考

$(cat << 'EOF'
今日主要工作：
- 完成了 XXX 功能
- 遇到了 YYY 问题
- 计划明天做 ZZZ
EOF
)" --category="daily-${DATE}"

echo "✅ 已记录 ${DATE} 的想法"
```

---

## 练习任务

完成以下练习以掌握 Capture TUI:

1. **基础练习**
   - [ ] 初始化一个新的 ideas 目录
   - [ ] 添加至少 3 个不同分类的想法
   - [ ] 查看统计信息

2. **进阶练习**
   - [ ] 创建一个项目规划分类
   - [ ] 添加包含任务的复杂想法
   - [ ] 运行 AI 分析
   - [ ] 导出为 Markdown 和 CSV

3. **高级练习**
   - [ ] 创建一个自动化脚本
   - [ ] 设置会话记录
   - [ ] 完成一个完整的工作流

---

## 故障排除

### 常见问题

**Q: 命令未找到**
```bash
# 确保已安装
pip install -e .

# 或使用 Python 模块方式
python -m capture_tui --help
```

**Q: 权限问题**
```bash
# 检查目录权限
ls -la ./kimi-ana/ideas/.capture/

# 修复权限
chmod -R 755 ./kimi-ana/ideas/
```

**Q: 配置未生效**
```bash
# 检查配置文件路径
capture --config=./kimi-ana/.capture-config.yaml categories list

# 查看当前配置
cat ./kimi-ana/ideas/.capture/config.yaml
```

---

## 下一步

- 查看完整文档: [README.md](../README.md)
- 探索示例代码: [capture_tui/](../capture_tui/)
- 阅读开发文档: [docs/](../docs/)
