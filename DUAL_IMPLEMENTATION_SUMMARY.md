# Capture TUI - 双语言实现总结

## 项目概述

本项目提供了 Capture TUI 的 **Go** 和 **Python** 双语言实现，功能完全一致，满足不同场景需求。

| 特性 | Python 版本 | Go 版本 |
|------|-------------|---------|
| **CLI 框架** | Typer (基于 Click) | Cobra |
| **配置管理** | PyYAML | Viper |
| **测试框架** | pytest | Ginkgo + Gomega |
| **项目管理** | uv | go modules |
| **UI 增强** | Rich | - |

---

## 目录结构

```
workspace/
├── capture_tui/                    # Python 实现
│   ├── __init__.py
│   ├── cli_typer.py               # [新] Typer CLI
│   ├── cli/main.py                # [旧] Click CLI (向后兼容)
│   ├── core/                      # 核心逻辑
│   ├── models/                    # 数据模型
│   ├── storage/                   # 存储层
│   ├── parser/                    # 输入解析
│   ├── ai/                        # AI 分析
│   ├── exporters/                 # 导出功能
│   ├── session/                   # 会话管理
│   └── config.py                  # 配置管理
│
├── capture-tui-go/                 # Go 实现
│   ├── go.mod
│   ├── cmd/capture/main.go        # CLI 入口
│   ├── internal/
│   │   ├── config/                # Viper 配置
│   │   ├── models/                # 数据模型
│   │   ├── storage/               # 存储层
│   │   ├── parser/                # 输入解析
│   │   ├── ai/                    # AI 分析
│   │   ├── exporters/             # 导出功能
│   │   ├── session/               # 会话管理
│   │   └── core/                  # 核心逻辑
│   ├── specs/
│   │   └── api-spec.md            # 完整 API 规范
│   ├── features/                  # BDD Features
│   │   ├── init.feature
│   │   ├── add.feature
│   │   ├── categories.feature
│   │   ├── analyze.feature
│   │   ├── export.feature
│   │   └── session.feature
│   └── test/                      # BDD 测试
│       ├── entry_test.go
│       ├── category_test.go
│       └── parser_test.go
│
├── pyproject.toml                  # Python 项目配置 (uv)
├── setup.py                        # 向后兼容
└── requirements.txt                # 依赖
```

---

## Python 版本 (Typer + uv)

### 安装

```bash
# 使用 uv 安装
uv pip install -e .

# 或使用 pip
pip install -e .
```

### 使用 Typer CLI

```bash
# 新命令 (Typer)
capture init --root-dir=./ideas
capture add "想法内容" --category=features -t tag1,tag2
capture categories list
capture analyze features
capture export -f csv -o ./export.csv

# 查看帮助
capture --help
capture categories --help
capture session --help
```

### 特点

- **Rich 集成**: 漂亮的表格和面板输出
- **自动补全**: 支持 shell 补全
- **类型提示**: 完整的类型注解
- **现代化**: 使用 Typer 的声明式 CLI 定义

### 测试

```bash
# 运行测试
pytest tests/ -v

# 覆盖率
pytest --cov=capture_tui --cov-report=html

# 代码格式化
black capture_tui/
ruff check capture_tui/
```

---

## Go 版本 (Viper + Cobra)

### 安装

```bash
cd capture-tui-go
go mod download
go build -o capture ./cmd/capture
```

### 使用

```bash
# 初始化
./capture init --root-dir=./ideas

# 添加想法
./capture add "想法内容" -c features -t tag1,tag2

# 分类管理
./capture categories list
./capture categories create bugs --display-name="缺陷跟踪"

# 分析
./capture analyze features -o ./analysis.md

# 导出
./capture export -f csv -o ./export.csv

# 会话
./capture session start -n "设计讨论" -g "设计API"
./capture session end -s "完成了设计"
```

### 测试 (BDD)

```bash
# 安装测试依赖
go install github.com/onsi/ginkgo/v2/ginkgo@latest

# 运行测试
ginkgo -v ./test/

# 或
go test -v ./test/
```

### 特点

- **单二进制**: 单文件部署，无需依赖
- **性能**: 启动快，内存占用低
- **Viper 配置**: 支持 YAML/JSON/TOML，环境变量
- **Cobra**: 强大的 CLI 框架，标准帮助格式

---

## API 规范

详见 `capture-tui-go/specs/api-spec.md`

### 数据类型

| 类型 | Go | Python |
|------|-----|--------|
| Entry | `internal/models/entry.go` | `models/entry.py` |
| Category | `internal/models/category.go` | `models/category.py` |
| Session | `internal/models/session.go` | `models/session.py` |
| Config | `internal/config/config.go` | `config.py` |

### CLI 参数对照

| 功能 | Go | Python |
|------|-----|--------|
| 初始化 | `./capture init -r ./ideas` | `capture init -r ./ideas` |
| 添加 | `./capture add "text" -c cat` | `capture add "text" -c cat` |
| 分类列表 | `./capture categories list` | `capture categories list` |
| 分析 | `./capture analyze cat -o out.md` | `capture analyze cat -o out.md` |
| 导出 | `./capture export -f csv -o out.csv` | `capture export -f csv -o out.csv` |

---

## Features (BDD)

所有功能都有对应的 Gherkin 格式 feature 文件：

```
capture-tui-go/features/
├── init.feature       # 项目初始化
├── add.feature        # 添加条目
├── categories.feature # 分类管理
├── analyze.feature    # 分析功能
├── export.feature     # 导出功能
└── session.feature    # 会话管理
```

每个 feature 文件包含：
- **Scenario**: 测试场景
- **Given/When/Then**: BDD 步骤
- **Context**: 不同上下文
- **Examples**: 数据表格

---

## 技术对比

| 方面 | Python | Go |
|------|--------|-----|
| **开发速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **运行时性能** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **启动速度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **二进制大小** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **依赖管理** | ⭐⭐⭐⭐ (uv) | ⭐⭐⭐⭐⭐ (go mod) |
| **类型安全** | ⭐⭐⭐⭐ (类型注解) | ⭐⭐⭐⭐⭐ (静态类型) |
| **生态丰富度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **部署复杂度** | ⭐⭐⭐ (需 Python) | ⭐⭐⭐⭐⭐ (单二进制) |

---

## 推荐场景

### 使用 Python 版本

- 需要快速迭代开发
- 需要丰富的第三方库集成
- 需要 REPL 交互式调试
- 团队熟悉 Python

### 使用 Go 版本

- 需要高性能和快速启动
- 需要单文件部署
- 需要静态类型安全
- 需要交叉编译多平台

---

## 快速开始

### Python

```bash
# 安装
uv pip install -e .

# 初始化
capture init

# 添加想法
capture add "我的第一个想法" -c ideas

# 查看统计
capture stats
```

### Go

```bash
# 构建
cd capture-tui-go
go build -o capture ./cmd/capture

# 初始化
./capture init

# 添加想法
./capture add "我的第一个想法" -c ideas

# 查看统计
./capture stats
```

---

## 贡献指南

### Python

```bash
# 代码格式化
black capture_tui/

# 代码检查
ruff check capture_tui/
mypy capture_tui/

# 测试
pytest tests/ -v
```

### Go

```bash
# 格式化
go fmt ./...

# 检查
golangci-lint run

# 测试
ginkgo -v ./test/
```

---

## 许可证

MIT License

---

**双语言实现完成！** 🎉
