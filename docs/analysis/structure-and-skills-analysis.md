# Innate 项目结构分析与 Skill 提炼报告

> 分析日期：2026-04-08

---

## Part 1：目录结构问题与改进建议

### 1.1 现状问题

#### 命名不一致
| 当前目录 | 问题 | 建议改为 |
|----------|------|----------|
| `innate-selfhostAgent` | 混用 camelCase | `innate-selfhost-agent` |
| `innate-keepthem` | 与 current.md 中的 `innate-keep-them` 不一致 | `innate-keep-them` |

#### 缺少逻辑分组
`current.md` 描述了 4 层架构（spark / innate / shared / infra），但实际所有项目平铺在 `/Users/patrick/innate/` 根目录，没有分组。

#### 文档与实际不一致
- `current.md` 未记录 `innate-executable`、`dpp-market-intel`、`meet-again`
- `.github/README.md` 缺少多个项目
- `innate-chaos` 在 current.md 描述为交易信号仪表盘，但实际是 YouTube 下载器（Go + yt-dlp）

#### 项目归类混乱
- `copy-modify` 应归属 infra/solutions，但平铺在根目录
- `dpp-market-intel` 和 `meet-again` 未被任何文档提及
- `innate-executable` 作为重要项目未纳入架构图

### 1.2 建议的目标结构

```
/Users/patrick/innate/
├── spark/                      # 工程工具层
│   ├── spark-cli/             # CLI 基础设施 (Go)
│   └── spark-skills/          # AI 技能扩展 (Node.js)
│
├── products/                   # 产品层（面向用户）
│   ├── innate-capture/        # 任务捕获（入口）
│   ├── innate-feeds/          # 信息流
│   ├── innate-susu/           # 教育平台
│   ├── innate-chaos/          # 交易信号
│   ├── innate-keep-them/      # 媒体下载
│   ├── innate-executable/     # AI 学习环境
│   └── innate-websites/       # 个人网站
│
├── shared/                     # 共享层
│   ├── innate-next-mono/      # UI 组件库
│   └── web/                   # Web 基础设施
│
├── infra/                      # 基础设施层
│   ├── innate-selfhost-agent/ # 自托管指南
│   ├── solutions/             # 解决方案集合
│   │   └── dpp-market-intel/  # DPP/CBAM 市场情报
│   └── copy-modify/           # Token 使用排行
│
├── experiments/                # 实验性项目
│   ├── meet-again/            # 待定
│   └── innate-smalllove/      # 关系沙箱
│
└── innate-way/                 # 规划与文档中心
```

### 1.3 知识管理建议

针对用户提到的知识管理需求，建议：

1. **LLM-wiki 模式**：在 `innate-way/docs/` 下建立结构化知识库，每个项目的 AGENTS.md 作为知识入口
2. **qmd 模式**：用 Markdown + 元数据管理想法，`innate-capture` 的任务流可以扩展为想法管理
3. **mempalace 模式**：利用项目间的关联关系建立知识图谱，`innate-way` 作为索引中心

---

## Part 2：Skill 提炼分析

### 2.1 Skill 优先级矩阵

| 优先级 | 项目 | Skill 方向 | 复用价值 |
|--------|------|------------|----------|
| **P0** | innate-executable | Tauri + Next.js 前端开发 Skill | 极高 |
| **P0** | innate-next-mono | UI 组件库 Skill（50+ 组件） | 极高 |
| **P1** | spark-cli | CLI 自动化 Skill（Go + Cobra） | 高 |
| **P1** | innate-capture | 任务管理 Skill（Go TUI） | 高 |
| **P2** | innate-feeds | GitHub API 集成 Skill | 中 |
| **P2** | innate-susu | AI 教育平台 Skill | 中 |
| **P2** | dpp-market-intel | Provider 模式 + 仪表盘 Skill | 中 |
| **P2** | innate-websites | 项目追踪 + 文档生成 Skill | 中 |
| **P3** | innate-selfhost-agent | 环境搭建 Skill | 低 |

### 2.2 详细 Skill 分析

#### Skill 1：Tauri Desktop App Skill（P0）
- **来源项目**：innate-executable
- **技术栈**：Tauri + Next.js 16 + React 19 + TypeScript + Tailwind CSS + shadcn-ui
- **可复用内容**：
  - 60+ UI 组件（基于 Radix UI）
  - 侧边栏导航布局
  - 平台检测工具（macOS/Windows/Linux）
  - Tauri IPC 通信模式
  - Markdown/MDX 教程系统
  - 卡片式技能展示系统
- **适用场景**：快速搭建 Tauri 桌面应用

#### Skill 2：UI Component Library Skill（P0）
- **来源项目**：innate-next-mono
- **技术栈**：Next.js 14 + React 19 + TypeScript + Radix UI + Tailwind CSS
- **可复用内容**：
  - 50+ 共享 UI 组件
  - pnpm workspace monorepo 架构
  - class-variance-authority 组件变体管理
  - 暗色模式（next-themes）
  - React Hook Form + Zod 表单验证
- **适用场景**：任何需要组件库的前端项目

#### Skill 3：CLI Automation Skill（P1）
- **来源项目**：spark-cli
- **技术栈**：Go + Cobra + Viper + Bubble Tea
- **可复用内容**：
  - CLI 框架（Cobra 命令组织）
  - AI Agent 配置管理（Claude Code, Codex, Kimi, GLM）
  - Git 仓库操作封装
  - 镜像切换（pip, go, npm）
  - 自定义脚本执行系统
- **适用场景**：快速构建新的 CLI 工具

#### Skill 4：Task Management Skill（P1）
- **来源项目**：innate-capture
- **技术栈**：Go + Cobra + Bubble Tea + SQLite + 飞书 SDK
- **可复用内容**：
  - TUI Kanban 看板界面
  - 任务工作流（inbox → mindstorm → analysis → dispatch → execution → review）
  - Markdown + YAML frontmatter 存储
  - 飞书机器人集成
  - Agent 上下文追踪
- **适用场景**：任何需要任务管理的项目

#### Skill 5：Provider + Dashboard Skill（P2）
- **来源项目**：dpp-market-intel
- **技术栈**：Next.js 16 + React 19 + FastAPI + SQLite
- **可复用内容**：
  - Provider 工厂模式（多数据源抽象）
  - 分类仪表盘组件
  - 静态 + 动态混合架构
  - 新闻聚合系统
- **适用场景**：构建数据仪表盘类应用

#### Skill 6：Education Platform Skill（P2）
- **来源项目**：innate-susu
- **技术栈**：Next.js 14 + Tauri + TypeScript
- **可复用内容**：
  - PDF 教材解析管道
  - AI 内容生成流程
  - 闪卡/测验系统
  - 学习进度追踪
  - 多应用 monorepo 架构
- **适用场景**：教育类产品开发

#### Skill 7：Project Tracking Skill（P2）
- **来源项目**：innate-websites
- **技术栈**：Next.js 16 + pnpm workspaces + GitHub Pages
- **可复用内容**：
  - GitHub API 集成（Issues 追踪）
  - AGENTS.md 文档系统
  - 周报 AI 分析生成
  - 双语内容管理
  - GitHub Pages 自动部署
- **适用场景**：项目文档和追踪

### 2.3 前端技术栈统一建议

用户提到想统一前端技术栈，当前项目使用的技术：

| 项目 | Next.js | React | TypeScript | Tailwind | shadcn/ui | Tauri |
|------|---------|-------|------------|----------|-----------|-------|
| innate-executable | 16 | 19 | ✅ | ✅ | ✅ | ✅ |
| innate-next-mono | 14 | 19 | ✅ | ✅ | Radix | — |
| innate-susu | 14 | 19 | ✅ | ✅ | — | ✅ |
| innate-feeds | 14 | 18 | ✅ | ✅ | Radix | — |
| innate-websites | 16 | 19 | ✅ | ✅ | — | — |
| dpp-market-intel | 16 | 19 | ✅ | ✅ | — | — |

**建议统一到**：Next.js 16 + React 19 + TypeScript + Tailwind CSS + shadcn-ui + Tauri（桌面端）

### 2.4 立即行动建议

1. **创建 `frontend-tauri` Skill**：从 innate-executable 提取，作为前端开发标准 Skill
2. **创建 `ui-components` Skill**：从 innate-next-mono 提取组件库配置
3. **更新 `current.md`**：补全缺失项目，修正不一致信息
4. **统一命名**：`innate-selfhostAgent` → `innate-selfhost-agent`
5. **考虑分组**：用 symlink 或子目录实现逻辑分组（不破坏现有 git 仓库）

---

## 附录：项目完整扫描清单

| 项目 | 类型 | 技术栈 | 代码状态 | Skill 潜力 |
|------|------|--------|----------|------------|
| innate-executable | 产品 | Tauri + Next.js 16 | 活跃 | ⭐⭐⭐⭐⭐ |
| innate-next-mono | 共享 | Next.js 14 + pnpm | 活跃 | ⭐⭐⭐⭐⭐ |
| spark-cli | 工具 | Go + Cobra | 活跃 | ⭐⭐⭐⭐ |
| spark-skills | 工具 | Node.js | 活跃 | ⭐⭐⭐⭐⭐ |
| innate-capture | 产品 | Go + TUI | 活跃 | ⭐⭐⭐⭐ |
| innate-feeds | 产品 | Go + Next.js | 活跃 | ⭐⭐⭐ |
| innate-susu | 产品 | Tauri + Next.js | 活跃 | ⭐⭐⭐ |
| innate-websites | 产品 | Next.js 16 | 活跃 | ⭐⭐⭐ |
| dpp-market-intel | 解决方案 | Next.js + FastAPI | 活跃 | ⭐⭐⭐ |
| innate-chaos | 产品 | Go + yt-dlp | 活跃 | ⭐⭐ |
| innate-selfhostAgent | 基础设施 | 文档 + 脚本 | 维护 | ⭐⭐ |
| innate-keep-them | 产品 | — | 规划中 | ⭐⭐ |
| copy-modify | 基础设施 | Node.js/Bun | 维护 | ⭐ |
| meet-again | 实验 | — | 最小 | ⭐ |
