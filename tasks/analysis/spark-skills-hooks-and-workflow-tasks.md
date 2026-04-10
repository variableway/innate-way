# Spark-Skills Hook 与工作流改造任务

> 基于分析：`tasks/analysis/claude-code-hooks-reference.md` + `tasks/analysis/skill-workflow-composition.md`
> 目标：借鉴 superpowers 的 Hook 机制和 Skill 工作流编排，增强 spark-skills 的自动化能力
> 日期：2026-04-10

## 当前差距

| 能力 | Superpowers 已有 | spark-skills 现状 |
|------|-----------------|-------------------|
| SessionStart 自动注入上下文 | hooks.json + session-start 脚本 | 无 |
| Skill 自动发现与加载 | using-superpowers 入口 Skill | 无，需手动引用 |
| Claude Code 插件机制 | .claude-plugin/plugin.json | 无 |
| 跨平台 Hook 脚本 | run-hook.cmd（Windows/Unix） | 仅 Git hooks |
| Kimi CLI Hooks | kimi-auto-issue.sh + kimi-stop-update.sh | 有但无 Claude Code 对应版本 |
| 领域 Skill 集成到工作流 | 自动根据任务类型引入 | 无关联机制 |
| PostToolUse 安全/追踪 | 无（但有 PreToolUse 概念） | 无 |
| Stop 事件质量门控 | 无 | 无 |

---

## Task 1：创建 SessionStart Hook 自动注入 Skill 上下文

**优先级**：P0 — 最高，所有后续 Hook 的基础

### 做什么

在 spark-skills 根目录创建 `.claude/hooks/` 目录，实现一个 SessionStart Hook，在每次 Claude Code 会话开始时自动注入已安装 Skill 的摘要信息，让 AI 知道有哪些 Skill 可用。

### 具体产出

#### 文件 1：`hooks/hooks.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\"",
            "async": false
          }
        ]
      }
    ]
  }
}
```

#### 文件 2：`hooks/session-start`

脚本逻辑（bash）：

1. 扫描 `~/.claude/skills/` 目录下所有含 `SKILL.md` 的子目录
2. 读取每个 SKILL.md 的 YAML frontmatter（name、description 字段）
3. 组装成上下文摘要：

```
<spark-skills-context>
已安装的 Skills：
- github-task-workflow: 通过 GitHub Issues 管理任务全生命周期
- innate-frontend: 使用 @innate/ui 组件库快速搭建 Web 前端应用（57 组件+13 业务区块）
- tauri-desktop-app: Tauri + Next.js 跨平台桌面应用开发
- ai-config: 一键配置 AI Agent Provider

触发词：说"执行 task"触发 github-task-workflow，说"创建前端页面"触发 innate-frontend，说"创建桌面应用"触发 tauri-desktop-app。
</spark-skills-context>
```

4. 输出 JSON：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<spark-skills-context>..."
  }
}
```

#### 文件 3：`hooks/run-hook.cmd`

跨平台包装器（参考 superpowers 的实现）：

- Windows: 使用 Git Bash 执行
- Unix: 直接 bash 执行
- 支持 `.sh` 扩展名自动查找

### 安装方式

在 `install.sh` 的 `install_system()` 中增加：

```bash
# 安装 hooks 到 Claude Code
if [ -d "$HOME/.claude" ]; then
    cp "$SCRIPT_DIR/hooks/hooks.json" "$HOME/.claude/settings.json"
    # 或合并到已有 settings.json 的 hooks 字段
fi
```

### 验收标准

- [ ] hooks.json 格式正确
- [ ] session-start 脚本可执行，输出合法 JSON
- [ ] Claude Code 启动时自动显示已安装 Skill 列表
- [ ] 跨平台兼容（macOS/Linux/Windows）

---

## Task 2：将 spark-skills 注册为 Claude Code Plugin

**优先级**：P0 — 让 Hook 机制生效的前提

### 做什么

创建 `.claude-plugin/` 目录，将 spark-skills 注册为 Claude Code 插件，使 hooks.json 被自动识别和加载。

### 具体产出

#### 文件 1：`.claude-plugin/plugin.json`

```json
{
  "name": "spark-skills",
  "version": "1.0.0",
  "description": "AI Agent Skill 仓库 - 统一收集、管理和分发 Skills",
  "hooks": "hooks/hooks.json"
}
```

#### 文件 2：更新 `install.sh`

在安装流程中增加 plugin 注册步骤：

```bash
# 注册为 Claude Code Plugin
if [ -d "$HOME/.claude" ]; then
    mkdir -p "$HOME/.claude/plugins"
    ln -sf "$SCRIPT_DIR" "$HOME/.claude/plugins/spark-skills"
    echo "  Registered as Claude Code plugin"
fi
```

### 验收标准

- [ ] plugin.json 格式正确
- [ ] `claude` 命令启动时自动加载 spark-skills 的 hooks
- [ ] `/hooks` 命令能看到已注册的 hooks

---

## Task 3：创建 Claude Code 版 Kimi Hooks（github-task-workflow 增强）

**优先级**：P1 — github-task-workflow 的 Claude Code 原生集成

### 做什么

将 github-task-workflow 中已有的 Kimi CLI Hooks 转化为 Claude Code Hook 格式，实现 task 文件写入时自动创建 Issue、会话结束时自动更新 Issue。

### 具体产出

#### 文件 1：`github-task-workflow/hooks/claude-auto-issue.sh`

Claude Code PostToolUse Hook，当 AI 写入 `tasks/*.md` 文件时自动创建 GitHub Issue：

```bash
#!/usr/bin/env bash
# Claude Code PostToolUse Hook - 自动为 task 文件创建 GitHub Issue
set -euo pipefail

# 读取 stdin JSON
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // empty')

# 仅处理 Write/Edit 工具操作 tasks/ 目录的文件
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    exit 0
fi

FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty')
if [[ "$FILE_PATH" != *"/tasks/"* ]]; then
    exit 0
fi

# 检查是否已有活跃 Issue（防止重复创建）
STATE_FILE=".github-task-workflow.state.json"
if [ -f "$STATE_FILE" ]; then
    exit 0  # 已有活跃 Issue，跳过
fi

# 提取标题（第一行去掉 # ）
TITLE=$(head -1 "$FILE_PATH" | sed 's/^# //')
BODY=$(cat "$FILE_PATH")

# 创建 Issue
ISSUE_URL=$(gh issue create --title "$TITLE" --body "$BODY" 2>/dev/null || echo "")
if [ -n "$ISSUE_URL" ]; then
    ISSUE_NUM=$(echo "$ISSUE_URL" | grep -oE '[0-9]+$')
    echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"✅ 已自动创建 GitHub Issue #${ISSUE_NUM}: ${ISSUE_URL}\"}}"
else
    exit 0
fi
```

#### 文件 2：`github-task-workflow/hooks/claude-stop-update.sh`

Claude Code Stop Hook，会话结束时自动更新活跃 Issue：

```bash
#!/usr/bin/env bash
# Claude Code Stop Hook - 会话结束时更新活跃 GitHub Issue
set -euo pipefail

STATE_FILE=".github-task-workflow.state.json"
if [ ! -f "$STATE_FILE" ]; then
    exit 0
fi

ISSUE_NUM=$(jq -r '.issue_number // empty' "$STATE_FILE" 2>/dev/null || echo "")
if [ -z "$ISSUE_NUM" ]; then
    exit 0
fi

# 获取本次会话的 git diff 摘要
CHANGED_FILES=$(git diff --name-only HEAD~5..HEAD 2>/dev/null | head -20 || echo "")
COMMIT_COUNT=$(git log --oneline -5 2>/dev/null | wc -l || echo "0")

COMMENT="## 会话暂停更新

- 最近提交数: ${COMMIT_COUNT}
- 变更文件:
$(echo "$CHANGED_FILES" | sed 's/^/  - /')

_此更新由 spark-skills Stop Hook 自动添加_"

gh issue comment "$ISSUE_NUM" --body "$COMMENT" 2>/dev/null || true

exit 0
```

#### 文件 3：`github-task-workflow/hooks/claude-hooks.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/github-task-workflow/hooks/claude-auto-issue.sh\"",
            "async": false,
            "timeout": 15
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/github-task-workflow/hooks/claude-stop-update.sh\"",
            "async": false,
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

### 验收标准

- [ ] 写入 `tasks/*.md` 时自动创建 GitHub Issue
- [ ] 不会重复创建（已有活跃 Issue 时跳过）
- [ ] 会话结束时自动更新 Issue 评论
- [ ] Hook 脚本有超时保护（15 秒）

---

## Task 4：创建 PreToolUse 安全防护 Hook

**优先级**：P1 — 防止 AI 执行危险操作

### 做什么

创建一个 PreToolUse Hook，在 AI 执行 Bash 命令前进行检查，阻止危险操作。

### 具体产出

#### 文件 1：`hooks/block-dangerous.sh`

```bash
#!/usr/bin/env bash
# PreToolUse Hook - 阻止危险的 Bash 命令
set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

if [ "$TOOL_NAME" != "Bash" ]; then
    exit 0
fi

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# 危险命令模式
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "git push --force"
    "git push -f"
    "git reset --hard"
    "git clean -f"
    "DROP TABLE"
    "DROP DATABASE"
    "dd if="
    "mkfs"
    ":(){:|:&};:"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$pattern"* ]]; then
        cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "阻止危险命令: ${pattern}。如确认需要执行，请用户手动操作。"
  }
}
EOF
        exit 0
    fi
done

exit 0
```

#### 文件 2：更新 `hooks/hooks.json`

在 hooks.json 中增加 PreToolUse 条目：

```json
{
  "hooks": {
    "SessionStart": [ "..." ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/block-dangerous.sh\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### 验收标准

- [ ] `rm -rf /` 被阻止并返回 deny
- [ ] `git push --force` 被阻止
- [ ] 正常命令（如 `npm test`）不被影响
- [ ] 10 秒内完成检查

---

## Task 5：创建 PostToolUse 前端规范检查 Hook

**优先级**：P2 — 结合 innate-frontend Skill 的自动规范检查

### 做什么

当 AI 在前端项目中修改 `.tsx`/`.css` 文件时，自动检查是否符合 innate-frontend Skill 的组件规范。

### 具体产出

#### 文件 1：`innate-frontend/hooks/check-frontend-spec.sh`

```bash
#!/usr/bin/env bash
# PostToolUse Hook - 前端代码规范检查
set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

if [ "$TOOL_NAME" != "Write" ] && [ "$TOOL_NAME" != "Edit" ]; then
    exit 0
fi

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# 仅检查 .tsx 和 .css 文件
if [[ "$FILE_PATH" != *.tsx && "$FILE_PATH" != *.css ]]; then
    exit 0
fi

WARNINGS=""

if [ "$TOOL_NAME" = "Write" ]; then
    CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')
else
    # Edit 操作，读取文件当前内容
    CONTENT=$(cat "$FILE_PATH" 2>/dev/null || echo "")
fi

# 检查规则
# 1. .tsx 文件中不应直接使用 className 拼接（应使用 cn()）
if [[ "$FILE_PATH" == *.tsx ]]; then
    if echo "$CONTENT" | grep -q 'className={"' && ! echo "$CONTENT" | grep -q 'cn('; then
        WARNINGS="${WARNINGS}\n- 发现 className 拼接，建议使用 cn() 工具函数合并类名"
    fi
    # 2. 组件应有 data-slot 属性
    if echo "$CONTENT" | grep -q 'function.*Section\|function.*Component' && ! echo "$CONTENT" | grep -q 'data-slot'; then
        WARNINGS="${WARNINGS}\n- 组件缺少 data-slot 属性（innate-frontend 规范）"
    fi
fi

if [ -n "$WARNINGS" ]; then
    CONTEXT="前端规范提醒：${WARNINGS}\n\n这些是建议性检查，不影响执行。详见 innate-frontend Skill。"
    printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$(echo "$CONTEXT" | sed 's/"/\\"/g' | tr '\n' ' ')"
fi

exit 0
```

### 验收标准

- [ ] 写入 .tsx 文件时自动检查 cn() 使用
- [ ] 检查 data-slot 属性
- [ ] 以建议性提示输出（不阻止操作）
- [ ] 不影响非前端文件

---

## Task 6：创建 Stop 事件质量门控 Hook

**优先级**：P2 — 提高代码质量

### 做什么

使用 prompt 类型 Hook，在 Claude 完成响应前自动进行质量检查。

### 具体产出

#### 在 `hooks/hooks.json` 中增加：

```json
{
  "hooks": {
    "SessionStart": [ "..." ],
    "PreToolUse": [ "..." ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Before completing this response, do a quick self-check. If you wrote or modified code in this turn: 1) Did you leave any TODO/FIXME placeholders? 2) Did you verify the code compiles/runs? 3) Did you import all needed dependencies? If any check fails, briefly mention what should be fixed. Context: $ARGUMENTS",
            "model": "claude-haiku-4-5-20251022",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

### 验收标准

- [ ] Claude 完成响应前自动检查
- [ ] 检查结果以 systemMessage 方式呈现
- [ ] 不影响正常对话（15 秒超时保护）

---

## Task 7：创建 Skill 工作流编排 Skill

**优先级**：P1 — 借鉴 superpowers 的核心价值

### 做什么

创建一个 `skill-workflow` Skill，定义 spark-skills 各 Skill 之间的编排关系，让 AI 自动根据任务类型选择正确的 Skill 组合。

### 具体产出

#### 文件 1：`skill-workflow/SKILL.md`

```yaml
---
name: skill-workflow
description: "当用户要求开发新功能、修复 bug、创建项目时自动触发。根据任务类型编排正确的 Skill 组合：设计→计划→实现→收尾。"
type: skill
supported_agents:
  - claude-code
  - kimi
  - codex
  - opencode
---
```

SKILL.md 核心内容：

**工作流编排规则**：

```
1. 新功能开发 →
   github-task-workflow init
   → innate-frontend / tauri-desktop-app（根据项目类型选择领域 Skill）
   → github-task-workflow finish

2. Bug 修复 →
   github-task-workflow init
   → 定位问题 → 修复
   → github-task-workflow finish

3. 创建新项目 →
   innate-frontend（Web 项目）
   tauri-desktop-app（桌面项目）
   → ai-config（配置 AI 工具）

4. 任务分析/规划 →
   innate-frontend Skill 的组件清单
   → 输出设计方案
```

**Skill 选择决策树**：

```
用户请求
├── 涉及 task 文件？
│   └── 是 → github-task-workflow / local-workflow
├── 涉及前端开发？
│   ├── Web → innate-frontend
│   └── 桌面 → tauri-desktop-app
├── 涉及 AI 配置？
│   └── 是 → ai-config
├── 涉及项目初始化？
│   └── 是 → spark-task-init
└── 不确定 → github-task-workflow（通用任务管理）
```

### 验收标准

- [ ] SKILL.md 定义清晰的触发条件和编排规则
- [ ] AI 能根据任务类型自动选择正确的 Skill 组合
- [ ] 与 SessionStart Hook 配合（Task 1 的输出包含此 Skill 信息）

---

## Task 8：更新 install.sh 支持完整 Hook 安装

**优先级**：P1 — 让所有 Hook 可以一键安装

### 做什么

增强 `install.sh`，支持安装时自动配置所有 Hooks。

### 具体改动

在 `install.sh` 的 `install_system()` 末尾增加：

```bash
# 安装 Claude Code Hooks
install_hooks() {
    local claude_dir="$HOME/.claude"
    if [ ! -d "$claude_dir" ]; then
        echo -e "${YELLOW}  [SKIP] Claude Code not found${NC}"
        return
    fi

    echo ""
    echo -e "${BLUE}Installing Claude Code hooks...${NC}"

    # 合并 hooks 到 settings.json
    local settings="$claude_dir/settings.json"
    if [ -f "$settings" ]; then
        # 已有 settings.json，合并 hooks 配置
        # 使用 jq 合并 JSON（如果可用）
        if command -v jq &>/dev/null; then
            local tmp=$(mktemp)
            jq -s '.[0] * .[1]' "$settings" "$SCRIPT_DIR/hooks/hooks.json" > "$tmp"
            mv "$tmp" "$settings"
            echo -e "${GREEN}  [OK]${NC} Merged hooks into $settings"
        else
            echo -e "${YELLOW}  [WARN] jq not found, manual merge required${NC}"
            echo -e "  Add contents of hooks/hooks.json to $settings"
        fi
    else
        # 无 settings.json，直接复制
        cp "$SCRIPT_DIR/hooks/hooks.json" "$settings"
        echo -e "${GREEN}  [OK]${NC} Created $settings with hooks"
    fi

    # 注册为 Plugin
    mkdir -p "$claude_dir/plugins"
    local plugin_link="$claude_dir/plugins/spark-skills"
    if [ ! -e "$plugin_link" ]; then
        ln -s "$SCRIPT_DIR" "$plugin_link"
        echo -e "${GREEN}  [OK]${NC} Registered as plugin"
    fi
}
```

### 验收标准

- [ ] `./install.sh --system --all` 自动安装所有 Hooks
- [ ] 不覆盖已有的 settings.json 配置（合并模式）
- [ ] 有 jq 时自动合并，无 jq 时给出手动提示

---

## Task 9：创建 setup-project.sh 增强（项目级 Hooks）

**优先级**：P2 — 项目级 Hook 配置

### 做什么

增强 `setup-project.sh`，除了安装 Git hooks，还安装 Claude Code 项目级 Hooks。

### 具体改动

在 `setup-project.sh` 的 5 步流程后增加第 6 步：

```bash
# 6. Install Claude Code project-level hooks
echo ""
echo "[6/6] Setting up Claude Code project hooks..."

mkdir -p .claude

# 创建项目级 settings.json
if [ ! -f ".claude/settings.json" ]; then
    cat > .claude/settings.json <<'SETTINGS_EOF'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/auto-issue.sh",
            "async": false,
            "timeout": 15
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/stop-update-issue.sh",
            "async": false,
            "timeout": 15
          }
        ]
      }
    ]
  }
}
SETTINGS_EOF
    echo "  Created: .claude/settings.json"
else
    echo "  Already exists: .claude/settings.json"
fi

# 复制 Hook 脚本
mkdir -p .claude/hooks
cp "$SKILL_DIR/hooks/claude-auto-issue.sh" .claude/hooks/auto-issue.sh 2>/dev/null || true
cp "$SKILL_DIR/hooks/claude-stop-update.sh" .claude/hooks/stop-update-issue.sh 2>/dev/null || true
chmod +x .claude/hooks/*.sh 2>/dev/null || true
echo "  Installed: .claude/hooks/"
```

### 验收标准

- [ ] `bash setup-project.sh` 一键安装 Git hooks + Claude Code hooks
- [ ] `.claude/settings.json` 包含 PostToolUse 和 Stop hooks
- [ ] `.claude/hooks/` 目录包含可执行脚本

---

## 实施顺序

```
Phase 1（基础）
  Task 2: 注册 Plugin    ──┐
  Task 1: SessionStart   ──┤── 让 Hook 机制跑起来
  Task 8: install.sh     ──┘

Phase 2（核心 Hooks）
  Task 3: task auto-issue ──┐
  Task 4: 安全防护          ├── 实用 Hook
  Task 6: 质量门控         ──┘

Phase 3（集成）
  Task 7: Skill 工作流编排  ── Skill 组合
  Task 5: 前端规范检查      ── 领域 Hook
  Task 9: setup-project.sh  ── 项目级安装
```

## 预期最终 hooks.json

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/session-start\"",
            "async": false
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/block-dangerous.sh\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/github-task-workflow/hooks/claude-auto-issue.sh\"",
            "async": false,
            "timeout": 15
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/github-task-workflow/hooks/claude-stop-update.sh\"",
            "async": false,
            "timeout": 15
          },
          {
            "type": "prompt",
            "prompt": "Quick self-check before completing. If you wrote code: 1) Any TODO/FIXME? 2) Did it compile? 3) All imports present? Briefly note issues if any. Context: $ARGUMENTS",
            "model": "claude-haiku-4-5-20251022",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```
