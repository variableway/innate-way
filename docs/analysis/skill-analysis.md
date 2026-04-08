# Skill 分析报告

> 扫描日期：2026-04-08
> 扫描范围：/Users/patrick/workspace/variableway/innate/ 下所有项目
> 关联 Issue：variableway/innate-way#2

## 一、总览

| 分类 | 项目 | 技术栈 | Skill 潜力 |
|------|------|--------|-----------|
| 前端框架 | innate-next-mono | Next.js 16 + React 19 + Tailwind v4 + Radix UI | ★★★★★ |
| 桌面应用 | innate-executable | Tauri 2 + Next.js 16 + xterm.js | ★★★★★ |
| 网站展示 | innate-websites | Next.js 16 + React 19 + Tailwind | ★★★★ |
| 教育平台 | innate-susu | Next.js + Tauri + PDF解析 | ★★★★ |
| 市场分析 | innate-chaos | Next.js 14 + FastAPI + TimescaleDB | ★★★ |
| 项目收藏 | innate-feeds | Next.js 14 + PocketBase + GitHub API | ★★★ |
| 任务管理 | innate-capture | Go + Cobra + 飞书SDK + SQLite | ★★★ |
| 关系预演 | innate-smalllove | OpenClaw + Python + LLM | ★★★ |
| 视频下载 | innate-keep-them | Go + yt-dlp + TUI | ★★★ |
| Token追踪 | copy-modify | Node.js + Rust + Solid.js | ★★★ |
| 市场智能 | solutions/dpp-market-intel | Next.js 16 + Python | ★★ |
| 基础工具 | web/allone | TypeScript + pnpm | ★★ |

---

## 二、已存在的 Skill 基础设施

### spark-cli（Go 编写的 CLI 工具链）
- **定位**：AI 开发基础设施 CLI
- **能力**：Git 仓库管理、AI 代理配置、任务工作流、脚本执行
- **已有 Skill**：
  - `github-task-workflow` — GitHub Issue 全生命周期管理
  - `ai-config` — AI Provider 配置管理
  - `spark-task-init` — 任务目录初始化
  - `local-workflow` — 本地任务追踪
  - `superpowers` — 高级开发模式技能集

### spark-skills（技能定义仓库）
- **定位**：跨 Agent 的技能分发中心
- **格式**：每个技能以 `SKILL.md` 为入口
- **支持**：Claude Code、Kimi CLI、Codex、OpenCode

---

## 三、推荐形成的 Skill

### Skill 1：前端 UI 组件库 Skill（★★★★★ 优先级最高）

**来源项目**：`innate-next-mono`

**技术栈**：Next.js 16 + React 19 + TypeScript 6 + Tailwind CSS v4 + Radix UI + shadcn/ui

**Skill 内容**：
- 49 个基础 UI 组件（Button、Card、Dialog、Table 等）
- 4 类业务区块（Landing、Auth、Mail、Chat）
- `cn()` 工具函数、主题系统、暗色模式
- OKLCH 色彩系统

**Skill 定义建议**：
```
触发词：创建前端页面、使用 innate-ui 组件、UI 开发
能力：
  - 自动从 @innate/ui 导入组件
  - 遵循项目既定的组件模式（Radix UI + CVA + Tailwind）
  - 使用 OKLCH 色彩系统
  - Landing Page / Auth / Chat / Mail 区块的快速组装
```

**价值**：统一所有前端项目的 UI 标准，减少重复设计

---

### Skill 2：Tauri 桌面应用 Skill（★★★★★ 用户指定）

**来源项目**：`innate-executable`

**技术栈**：Tauri 2 + Next.js 16 + TypeScript + xterm.js

**Skill 内容**：
- Tauri + Next.js 项目初始化模板
- 终端集成组件（命令执行 + 历史管理）
- 教程/学习系统（MDX 渲染 + 交互式代码块）
- 桌面应用布局系统（侧边栏、状态栏）
- Shell 插件集成

**Skill 定义建议**：
```
触发词：创建桌面应用、Tauri 应用、桌面端开发
能力：
  - 使用 innate-executable 的项目结构作为模板
  - 复用终端执行组件和教程渲染系统
  - 遵循 Tauri 2 IPC 通信模式
  - 自动配置 shell 插件和 Tauri 权限
```

**价值**：标准化所有桌面应用的开发流程

---

### Skill 3：Go CLI 工具 Skill（★★★★）

**来源项目**：`innate-capture`

**技术栈**：Go + Cobra + Bubble Tea + Viper + SQLite + 飞书SDK

**Skill 内容**：
- Cobra CLI 项目初始化（命令定义、参数解析）
- Bubble Tea TUI 开发模式（交互式终端界面）
- Viper 配置管理模式（多层配置加载）
- SQLite 集成模式（数据持久化）
- 飞书 Bot 集成模式（消息处理、多维表格同步）

**Skill 定义建议**：
```
触发词：创建 Go CLI、Go 命令行工具、终端工具
能力：
  - 使用 Cobra 框架初始化项目结构
  - 集成 Bubble Tea TUI 组件
  - 标准 Viper 配置加载
  - SQLite 数据访问层模式
```

**价值**：统一 Go CLI 工具的开发范式，可复用到新的 CLI 项目

---

### Skill 4：Next.js 全栈应用 Skill（★★★★）

**来源项目**：`innate-websites`、`innate-susu`、`innate-feeds`

**技术栈**：Next.js 14-16 + React 19 + TypeScript + Tailwind CSS

**共性模式**：
- Next.js App Router 页面结构
- pnpm workspace monorepo 管理
- GitHub Pages / Vercel 部署配置
- API Routes 后端集成
- PocketBase / SQLite 数据层

**Skill 定义建议**：
```
触发词：创建 Web 应用、Next.js 项目、全栈开发
能力：
  - 标准化的 Next.js 项目初始化
  - App Router 路由设计
  - pnpm workspace 配置
  - 部署配置（GitHub Pages / Vercel）
```

**价值**：3 个以上项目已验证的通用模式

---

### Skill 5：AI 集成 Skill（★★★）

**来源项目**：`innate-smalllove`、`innate-capture`

**技术栈**：LLM API + 飞书 SDK + Python/Go

**共性模式**：
- LLM 多 Provider 集成（OpenAI、阿里云百炼、Anthropic）
- 飞书 Bot 开发（消息处理、事件订阅）
- AI Agent 上下文管理
- 对话状态跟踪

**Skill 定义建议**：
```
触发词：AI 集成、LLM 对话、飞书机器人
能力：
  - LLM API 调用封装
  - 飞书 Bot 事件处理
  - 对话上下文管理
  - 多 Provider 切换
```

---

### Skill 6：数据可视化 Skill（★★★）

**来源项目**：`innate-chaos`、`solutions/dpp-market-intel`

**技术栈**：Next.js + Recharts + FastAPI + TimescaleDB

**共性模式**：
- 实时数据仪表板布局
- 图表组件封装（Recharts）
- 后端 API 数据聚合
- 时间序列数据处理

**Skill 定义建议**：
```
触发词：创建仪表板、数据可视化、图表页面
能力：
  - 仪表板布局模板
  - Recharts 图表组件配置
  - 实时数据订阅模式
  - 时间序列查询优化
```

---

### Skill 7：视频/媒体处理 Skill（★★★）

**来源项目**：`innate-keep-them`（vYtDL）

**技术栈**：Go + yt-dlp + TUI

**Skill 内容**：
- yt-dlp 封装和调用模式
- 媒体下载任务管理
- 进度跟踪和恢复机制
- 交互式格式选择 UI

---

## 四、优先级排序

### 第一优先级（立即实施）
1. **前端 UI 组件库 Skill** — 49+ 组件已就绪，6 个前端项目可受益
2. **Tauri 桌面应用 Skill** — 用户明确指定，有完整模板

### 第二优先级（短期实施）
3. **Next.js 全栈应用 Skill** — 3+ 项目已验证模式
4. **Go CLI 工具 Skill** — 2+ 项目可复用，模式成熟

### 第三优先级（按需实施）
5. **AI 集成 Skill** — 2 个项目可提取模式
6. **数据可视化 Skill** — 2 个项目可提取模式
7. **视频/媒体处理 Skill** — 1 个项目，较垂直

---

## 五、实施建议

### 统一前端技术栈 Skill

按用户要求，前端统一使用：
- **框架**：Tauri（桌面端）+ Next.js（Web 端）
- **语言**：TypeScript
- **样式**：Tailwind CSS + shadcn/ui
- **组件库**：@innate/ui（来自 innate-next-mono）

建议创建一个综合的 **"innate-frontend" Skill**，包含：
1. 从 `innate-next-mono` 提取 UI 组件库使用规范
2. 从 `innate-executable` 提取 Tauri 集成模板
3. 统一 pnpm workspace 配置标准
4. 统一部署流程（GitHub Pages / Vercel / Tauri 打包）

### Skill 定义格式

每个 Skill 应遵循 spark-skills 的标准格式：
```
skill-name/
├── SKILL.md          # 技能入口（触发条件、能力描述）
├── scripts/          # 辅助脚本（如需要）
└── references/       # 扩展文档
```

---

## 六、总结

| 维度 | 数量 |
|------|------|
| 扫描项目总数 | 14 |
| 可形成 Skill 的项目 | 12 |
| 推荐形成的 Skill 数量 | 7 |
| 第一优先级 Skill | 2（前端 UI 组件库 + Tauri 桌面应用）|
| 已有 Skill 基础设施 | spark-cli + spark-skills |

核心发现：
1. **前端生态最为成熟** — 6 个前端项目共享相同技术栈，应优先形成统一前端 Skill
2. **组件库 @innate/ui 已生产就绪** — 49 个基础组件 + 4 类业务区块，可直接作为 Skill 核心
3. **Tauri 模板已完整** — innate-executable 提供了完整的 Tauri + Next.js 模板
4. **Go CLI 模式可复用** — innate-capture 和 innate-keep-them 的 Go CLI 开发模式高度一致
5. **已有 Skill 基础设施完善** — spark-skills 的分发机制和标准可直接复用
