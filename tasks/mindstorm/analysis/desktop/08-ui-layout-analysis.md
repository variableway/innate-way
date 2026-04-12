# UI 布局方案分析与确认

## 1. 参考项目 UI 布局对比

### 1.1 Holaboss AI 布局

```
┌─────────────────────────────────────────────────────────────┐
│ TopTabsBar: [Workspace] [Settings] [Marketplace]           │
├──────┬──────────────┬──────────────────┬───────────────────┤
│      │ File         │                  │                   │
│ Nav  │ Explorer     │   Display Pane   │   Agent/Chat      │
│ Rail │ (左侧)       │   (中间主内容)    │   Pane (右侧)     │
│      │              │                  │                   │
│ ■ Space            │                  │                   │
│ ■ Auto             │                  │                   │
│ ■ Skills           │                  │                   │
│ ■ Market           │                  │                   │
│ ■ Apps             │                  │                   │
├──────┴──────────────┴──────────────────┴───────────────────┤
```

**特点**:
- 左侧导航栏 (固定): Space/Automations/Skills/Marketplace/Apps
- 内容区三栏: 文件浏览器 | 展示面板 | Agent 聊天
- 面板可调整大小，可折叠
- 工作空间切换器在顶部

**技术**: React 19 + Shadcn/ui + Tailwind v4 (OKLCH) + 自定义主题系统

### 1.2 GitButler 布局

```
┌─────────────────────────────────────────────────────────────┐
│ AppHeader: [Sync] [Project▾] [Branch▾] [+Branch] [AI✨]   │
├──────┬──────────────────────────────────────────────────────┤
│      │  Unassigned  │  Multi-Stack View  │  Preview Panel   │
│ Side │  (280px)     │  (flexible)        │  (480px)         │
│ bar  │              │                    │                   │
│      │              │                    │                   │
│ ■ WS │              │                    │                   │
│ ■ BR │              │                    │                   │
│ ■ HI │              │                    │                   │
│ ■ ⚙  │              │                    │                   │
├──────┴──────────────┴────────────────────┴──────────────────┤
```

**特点**:
- 顶部工具栏: 同步、项目选择、分支选择、AI 功能
- 左侧图标侧栏 (窄): Workspace/Branches/History/Settings
- 内容区三栏: 未分配文件 | 多栈视图 | 预览面板
- 面板可拖拽调整大小
- Header 区域支持窗口拖拽

**技术**: Svelte + 自定义 CSS (PostCSS) + 自定义 CSS 变量主题

## 2. 推荐布局方案

### 结合 Holaboss + GitButler 优势

```
┌──────────────────────────────────────────────────────────────────┐
│  Toolbar: [项目▾] [工作空间▾] [搜索🔍]        [通知🔔] [设置⚙]  │
├────────┬────────────────────────────────────┬───────────────────┤
│        │                                    │                   │
│  Side  │        Content Area                │   Detail/AI       │
│  bar   │        (Two Columns)               │   Panel           │
│        │                                    │                   │
│  ■ 💡  │  ┌──────────────┬─────────────┐   │                   │
│  Ideas  │  │              │             │   │   ┌───────────┐  │
│  ■ 📋  │  │  List View   │  Detail     │   │   │           │  │
│  Tasks  │  │              │  View       │   │   │  AI Chat  │  │
│  ■ 🤖  │  │  (任务列表/   │             │   │   │  / Agent  │  │
│  Agents │  │   Ideas列表)  │             │   │   │  Terminal │  │
│  ■ 📁  │  │              │             │   │   │           │  │
│  Files  │  │              │             │   │   │           │  │
│  ■ 🔧  │  └──────────────┴─────────────┘   │   └───────────┘  │
│  Skills │                                    │                   │
│  ■ ⚙   │                                    │                   │
│  Config │                                    │                   │
│        │                                    │                   │
├────────┴────────────────────────────────────┴───────────────────┤
│  Status Bar: [Agent状态] [Git分支]                     [v0.1.0]  │
└──────────────────────────────────────────────────────────────────┘
```

### 布局组件拆解

| 区域 | 来源参考 | 功能 |
|------|----------|------|
| **Toolbar** | GitButler AppHeader | 项目/工作空间切换、全局搜索、通知、设置 |
| **Sidebar** | Holaboss LeftNavRail | 导航: Ideas/Tasks/Agents/Files/Skills/Config |
| **Content (左列)** | GitButler Unassigned | 列表视图 (任务/Ideas/Agent 列表) |
| **Content (右列)** | GitButler Multi-Stack | 详情视图 (选中项的详细信息) |
| **Detail/AI Panel** | Holaboss Chat Pane | AI 聊天 / Agent 终端 / 详情面板 |
| **Status Bar** | VS Code 模式 | Agent 状态、Git 信息、版本号 |

### 可调面板规格

| 面板 | 默认宽度 | 最小 | 最大 | 可折叠 |
|------|----------|------|------|--------|
| Sidebar | 48px (图标) / 200px (展开) | 48px | 280px | ✅ |
| Content 左列 | 320px | 240px | 500px | ✅ |
| Content 右列 | flex | 300px | - | ❌ |
| Detail/AI Panel | 400px | 320px | 600px | ✅ |

## 3. 导航结构

### Sidebar 导航项

```
💡 Ideas        → Ideas 收集箱 + 分析
📋 Tasks        → 任务看板 + 列表
🤖 Agents       → Agent 管理 + 监控
📁 Files        → 文件浏览器 (可选)
🔧 Skills       → 技能管理 + 市场
⚙ Settings      → 设置 (模型/工作空间/集成)
```

### 内容区模式

根据侧栏选择切换内容：

| 导航 | 左列 | 右列 |
|------|------|------|
| Ideas | Ideas 列表 (卡片) | Idea 详情 + AI 分析 |
| Tasks | 看板视图 | 任务详情 + 子任务 |
| Agents | Agent 列表 | Agent 终端 + 日志 |
| Files | 文件树 | 文件预览 + 编辑 |
| Skills | 技能列表 | 技能详情 + 配置 |

## 4. 设计系统

### 主题: 基于 Holaboss 的 OKLCH 主题系统

```css
:root {
  /* 语义化颜色 (OKLCH) */
  --primary: oklch(0.7 0.15 250);
  --secondary: oklch(0.85 0.05 250);
  --destructive: oklch(0.6 0.2 25);
  --success: oklch(0.65 0.2 145);
  --warning: oklch(0.75 0.15 85);

  /* 背景层次 */
  --bg-base: oklch(0.98 0.005 250);      /* 最底层 */
  --bg-surface: oklch(1.0 0 0);           /* 卡片/面板 */
  --bg-elevated: oklch(1.0 0 0);          /* 弹出层 */

  /* 文字层次 */
  --text-primary: oklch(0.2 0.02 250);
  --text-secondary: oklch(0.45 0.02 250);
  --text-tertiary: oklch(0.65 0.01 250);
}
```

### 暗色主题
```css
:root.dark {
  --bg-base: oklch(0.15 0.01 250);
  --bg-surface: oklch(0.2 0.01 250);
  --bg-elevated: oklch(0.25 0.01 250);
  --text-primary: oklch(0.95 0.01 250);
  --text-secondary: oklch(0.7 0.01 250);
}
```

### 组件: shadcn/ui + 桌面适配

```bash
# 初始化 shadcn/ui
npx shadcn@latest init

# 添加核心组件
npx shadcn@latest add button card input select tabs
npx shadcn@latest add dropdown-menu dialog toast tooltip
npx shadcn@latest add separator scroll-area resizable
```

**桌面端特殊处理**:
- 默认 hover 状态而非 touch
- 快捷键提示 (Cmd+K, Cmd+P 等)
- 右键上下文菜单
- 拖拽操作 (面板调整、卡片排序)

## 5. 响应式策略

### 窗口尺寸适配

| 宽度 | 布局变化 |
|------|----------|
| ≥1440px | 完整四栏布局 |
| 1024-1440px | AI Panel 可折叠 |
| 768-1024px | Content 单列 + AI Panel overlay |
| <768px | 全部 overlay 模式 |

### 最小支持窗口: 1024 × 640

## 6. 验证确认项

在开始实现前，需要用户确认以下选项：

1. ✅ 基本布局: Toolbar + Sidebar + Content(两列) + AI Panel
2. ❓ Sidebar 宽度: 窄图标 (48px) 还是宽列表 (200px)?
3. ❓ AI Panel 位置: 固定右侧 还是 可切换 overlay?
4. ❓ 主题偏好: 默认亮色 还是 默认暗色?
5. ❓ 内容区默认视图: 看板 还是 列表?
