# Innate

> 每个人都应该有一个属于自己的"IDE"——不只是开发者的工具，而是普通人管理生活、触发AI、捕获灵感的起点。

## 设计理念

如果 IDE 是开发者的必备工具，那么普通人也需要一个属于自己的"IDE"：

- **Feeds** — 获取感兴趣的新闻和社交媒体信息
- **AI 触发器** — 在工具中使用 AI 完成任务，工具是触发 AI 的起点
- **Idea 收集** — 捕获灵感，保存并筛选，AI 辅助执行
- **AI Coding** — 想做的事用 AI 来 coding，工具发起调用
- **过程可见** — 中间结果和最终结果都可检查

理想的工作流：不焦虑、有序，任务进来分析决定是否执行，AI 24小时运行，人可以放松。

---

## Spark 系列：工程工具

开发效率工具集，CLI 和 AI 技能是核心。

| 项目 | 说明 | 技术栈 |
|------|------|--------|
| [spark-cli](./spark-cli) | CLI 工具，提升开发效率，同时暴露接口给 AI 调用。支持 Git 仓库管理、系统工具、脚本管理、AI Agent 配置和任务工作流 | Go (Cobra, Viper, Bubble Tea) |
| [spark-skills](./spark-skills) | AI Agent 技能集合，兼容 Claude Code、Kimi CLI、Codex、OpenCode 等多种 AI 编程工具 | Node.js |

---

## Innate 系列：产品与模块

面向用户的产品集合，每个模块解决一个具体场景。

| 项目 | 说明 | 技术栈 |
|------|------|--------|
| [innate-capture](./innate-capture) | 任务捕获 CLI，支持终端任务管理和飞书集成，任务流程：inbox → mindstorm → analysis → dispatch → execution → review | Go (Bubble Tea TUI) |
| [innate-feeds](./innate-feeds) | GitHub Star 仓库收集器，支持按 star 数、语言、标签筛选，自动收集和 Web UI 展示 | Go (PocketBase) + Next.js |
| [innate-chaos](./innate-chaos) | HyperTrace 交易信号仪表盘，ETH/BTC/GOLD 多资产交易信号和风险管理 | Next.js + FastAPI + TimescaleDB |
| [innate-keep-them](./innate-keep-them) | YouTube 下载器 (vYtDL)，支持视频/播放列表下载、格式选择、字幕下载 | Go (yt-dlp) |
| [innate-susu](./innate-susu) | AI 教育平台，AI 内容生成、互动学习（闪卡/测验）、进度追踪 | Next.js monorepo (Tauri) |
| [innate-smalllove](./innate-smalllove) | 关系沙箱，AI 驱动的关系冲突模拟和沟通辅助 | Python (Flask + OpenAI) |
| [innate-websites](./innate-websites) | 个人作品网站，GitHub 集成和项目展示 | Next.js |
| [innate-next-mono](./innate-next-mono) | 共享 UI 组件库，50+ 组件 (Radix UI + Tailwind CSS)，monorepo 基础设施 | Next.js + TypeScript (pnpm) |
| [innate-way](./innate-way) | 文档和任务管理，项目级工作流追踪 | — |

---

## 基础设施与资源

| 项目 | 说明 | 技术栈 |
|------|------|--------|
| [web](./web) | Web 应用集合，CMS、UI 导航和组件库 | Next.js monorepo (shadcn-ui) |
| [selfhost-agent](./selfhost-agent) | 自托管 AI 开发环境搭建指南 | 文档 + 脚本 |
| [solutions](./solutions) | 解决方案集合，包括 quick-cbam (EU 碳关税工具) 等 | Go (PocketBase) |
| [copy-modify](./copy-modify) | Token 使用排行榜 (my-tokscale)，追踪 AI 开发工具的 Token 消耗 | Node.js/Bun monorepo |

---

## 架构关系

```
innate/
├── spark/                    # 工程工具层
│   ├── spark-cli            # CLI 基础设施
│   └── spark-skills         # AI 技能扩展
│
├── innate/                   # 产品层
│   ├── innate-capture       # 任务捕获（入口）
│   ├── innate-feeds         # 信息流
│   ├── innate-susu          # 教育
│   ├── innate-chaos         # 交易
│   ├── innate-smalllove     # 关系模拟
│   ├── innate-keep-them     # 媒体下载
│   └── innate-websites      # 展示
│
├── shared/                   # 共享层
│   ├── innate-next-mono     # UI 组件库
│   └── web                  # Web 基础设施
│
└── infra/                    # 基础设施
    ├── selfhost-agent        # 自托管指南
    └── solutions             # 解决方案
```

