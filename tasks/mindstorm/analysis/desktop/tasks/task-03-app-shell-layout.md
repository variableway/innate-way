# Task 03: App Shell 布局

## Feature
实现主应用框架: Toolbar + Sidebar + Content(两列) + AI/Detail Panel 的可调整四栏布局。

## 优先级
P0 - 阻塞所有页面任务

## UI 布局

```
┌──────────────────────────────────────────────────────────────────┐
│  Toolbar: [项目▾] [工作空间▾] [搜索🔍]        [通知🔔] [设置⚙]  │
├────────┬────────────────────────────────────┬───────────────────┤
│  Side  │        Content Area                │   Detail/AI       │
│  bar   │        (Two Columns)               │   Panel           │
│        │                                    │                   │
│  ■ 💡  │  ┌──────────────┬─────────────┐   │                   │
│  Ideas  │  │  List View   │  Detail     │   │   AI Chat /       │
│  ■ 📋  │  │              │  View       │   │   Agent Terminal   │
│  Tasks  │  │              │             │   │                   │
│  ■ 🤖  │  │              │             │   │                   │
│  Agents │  └──────────────┴─────────────┘   │                   │
│  ■ 🔧  │                                    │                   │
│  Skills │                                    │                   │
│  ■ ⚙   │                                    │                   │
│  Config │                                    │                   │
├────────┴────────────────────────────────────┴───────────────────┤
│  Status Bar                                                      │
└──────────────────────────────────────────────────────────────────┘
```

## 验收标准
- [ ] Toolbar 组件: 项目切换、工作空间切换、全局搜索框、通知、设置入口
- [ ] Sidebar 组件: 图标导航栏，支持 hover 展开标签
- [ ] Content 区域: 两列可调布局 (列表 + 详情)
- [ ] AI/Detail Panel: 右侧可折叠面板
- [ ] Status Bar: Agent 状态指示、版本号
- [ ] 所有面板支持拖拽调整大小
- [ ] 面板折叠/展开动画
- [ ] 窗口最小尺寸: 1024 × 640
- [ ] 窗口状态持久化 (tauri-plugin-window-state)
- [ ] Sidebar 导航切换内容区域
- [ ] Tauri 窗口拖拽 (Toolbar drag region)

## 技术要点
- ResizablePanel 组件 (shadcn resizable)
- Zustand 管理 UI 状态 (面板宽度、折叠状态)
- 窗口拖拽使用 Tauri `data-tauri-drag-region`
- 窗口状态通过 tauri-plugin-window-state 持久化

## 参考代码
- GitButler: `AppLayout.svelte` + `MainViewport.svelte` — Chrome 布局模式
- Holaboss: `AppShell` + `LeftNavigationRail` — 三栏工作空间布局
- Multica: Tab-based 导航系统

## 依赖
Task 01, Task 02

## 预估复杂度
高 — 核心架构，需要仔细处理布局和状态
