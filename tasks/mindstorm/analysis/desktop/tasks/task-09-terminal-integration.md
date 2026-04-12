# Task 09: Terminal 集成

## Feature
在桌面应用中嵌入终端: Agent 终端、系统 Shell、多 Tab 管理。

## 优先级
P2 - 重要但可延后

## 验收标准
- [ ] xterm.js 集成: 基础终端渲染
- [ ] tauri-plugin-pty: Rust 端 PTY 集成
- [ ] 多终端 Tab: 新建/关闭/切换终端 Tab
- [ ] Agent 终端: PTY 内运行 Agent CLI (claude, codex 等)
- [ ] 系统终端: bash/zsh/powershell 访问
- [ ] 终端分屏: 水平/垂直分屏
- [ ] 终端复制/粘贴 + 快捷键
- [ ] 终端主题: 跟随应用暗色/亮色主题
- [ ] 终端输出到 Agent: 终端内容作为 Agent 输入
- [ ] 终端在 AI Panel 中显示，或独立窗口

## 技术方案

```
Frontend:  xterm.js (npm)
Backend:   tauri-plugin-pty (Rust → portable-pty)
通信:      Tauri Events (onData/write)
```

```typescript
// 基础用法
import { Terminal } from "xterm";
import { spawn } from "tauri-pty";

const term = new Terminal();
term.open(document.getElementById("terminal"));
const pty = spawn("bash", [], { cols: term.cols, rows: term.rows });
pty.onData(data => term.write(data));
term.onData(data => pty.write(data));
```

## 注意事项
- 依赖大小: 18-64MB (portable-pty)
- Resize 事件需手动转发
- 早期阶段插件，可能有边界问题

## 参考代码
- Aperant: Agent Terminal PTY 集成
- LobsterAI: 终端集成模式

## 依赖
Task 03 (App Shell)

## 预估复杂度
中 — xterm.js 成熟，但 tauri-plugin-pty 早期
