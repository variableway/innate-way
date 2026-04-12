# Task 02: 设计系统与主题

## Feature
建立完整的设计系统: OKLCH 主题、shadcn/ui 桌面适配、图标系统、布局组件。

## 优先级
P0 - 阻塞所有 UI 任务

## 技术栈
- Tailwind CSS v4 (OKLCH 色彩空间)
- shadcn/ui 组件库
- Lucide React 图标
- CSS 自定义属性主题系统

## 验收标准
- [ ] OKLCH 色彩系统定义 (primary/secondary/destructive/success/warning)
- [ ] 亮色/暗色主题 + 系统跟随
- [ ] 多预设主题支持 (参考 Holaboss: amber-minimal, cosmic-night 等)
- [ ] 语义化设计 tokens: --bg-base/surface/elevated, --text-primary/secondary
- [ ] shadcn/ui 桌面端适配 (hover 优先、快捷键提示)
- [ ] 核心 shadcn 组件安装: Button, Card, Input, Select, Tabs, Dropdown, Dialog, Toast, Tooltip, ScrollArea, Resizable
- [ ] 图标系统 (Lucide React)
- [ ] 通用布局组件: ResizablePanel, SplitPane
- [ ] Typography 排版系统

## 参考代码
- Holaboss: `innate-desktop-reference/holaboss-ai/desktop/` — OKLCH 主题系统、7+ 预设主题
- GitButler: `innate-desktop-reference/gitbutler/` — CSS 变量主题、暗色/亮色
- 项目 Skill: `innate-frontend` — @innate/ui 组件库

## 依赖
Task 01 (项目脚手架)

## 预估复杂度
中等 — 大量配置但模式成熟
