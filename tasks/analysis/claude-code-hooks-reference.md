# Claude Code Hooks 完整参考

> 分析来源：superpowers 项目 + Claude Code 官方文档
> 分析日期：2026-04-10

## 一、Hooks 概述

Hooks 是 Claude Code 的自动化机制，允许在特定事件发生时执行自定义逻辑。通过 JSON 配置文件定义，支持 4 种 handler 类型。

### 配置文件位置（优先级从低到高）

| 位置 | 作用域 | 可提交到仓库 |
|------|--------|-------------|
| `~/.claude/settings.json` | 所有项目 | 否 |
| `.claude/settings.json` | 单个项目 | 是 |
| `.claude/settings.local.json` | 单个项目 | 否 |
| Plugin `hooks/hooks.json` | 插件启用时 | 是 |
| Skill/Agent frontmatter | 组件活跃时 | 是 |

### 配置结构（三层嵌套）

```json
{
  "hooks": {
    "<EventName>": [
      {
        "matcher": "<optional filter>",
        "hooks": [
          {
            "type": "command|http|prompt|agent",
            "command": "...",
            "timeout": 600,
            "async": false
          }
        ]
      }
    ]
  }
}
```

## 二、所有 Hook 事件（26 个）

### 开发流程事件

| 事件 | 触发时机 | 支持 Matcher |
|------|---------|-------------|
| `SessionStart` | 会话开始/恢复 | `startup\|resume\|clear\|compact` |
| `SessionEnd` | 会话终止 | `clear\|resume\|logout\|prompt_input_exit` |
| `InstructionsLoaded` | CLAUDE.md 加载到上下文 | `session_start\|compact\|include` |
| `ConfigChange` | 配置文件变更 | `user_settings\|project_settings\|...` |
| `CwdChanged` | 工作目录变更 | 不支持 |
| `FileChanged` | 监视文件在磁盘变更 | 文件名（`\|` 分隔） |

### 工具调用事件

| 事件 | 触发时机 | Matcher |
|------|---------|---------|
| `PreToolUse` | 工具调用执行前（可阻止） | 工具名：`Bash`, `Edit\|Write`, `mcp__.*` |
| `PostToolUse` | 工具调用成功完成后 | 工具名 |
| `PostToolUseFailure` | 工具调用失败后 | 工具名 |
| `PermissionRequest` | 权限对话框出现 | 工具名 |
| `PermissionDenied` | 权限被拒绝 | 工具名 |

### 代理/任务事件

| 事件 | 触发时机 | Matcher |
|------|---------|---------|
| `SubagentStart` | 子代理启动 | Agent 类型 |
| `SubagentStop` | 子代理完成 | Agent 类型 |
| `TaskCreated` | 任务创建 | 不支持 |
| `TaskCompleted` | 任务完成 | 不支持 |
| `TeammateIdle` | 团队成员空闲 | 不支持 |

### 其他事件

| 事件 | 触发时机 | Matcher |
|------|---------|---------|
| `UserPromptSubmit` | 用户提交 prompt | 不支持 |
| `Notification` | 发送通知 | 通知类型 |
| `Stop` | Claude 完成响应 | 不支持 |
| `StopFailure` | API 错误导致结束 | 错误类型 |
| `PreCompact` | 上下文压缩前 | `manual\|auto` |
| `PostCompact` | 上下文压缩后 | `manual\|auto` |
| `WorktreeCreate` | 创建 worktree | 不支持 |
| `WorktreeRemove` | 移除 worktree | 不支持 |
| `Elicitation` | MCP 请求用户输入 | MCP 服务器名 |
| `ElicitationResult` | 用户响应 MCP 请求 | MCP 服务器名 |

## 三、Handler 类型

### 1. Command Handler（最常用）

执行 shell 命令，通过 stdin 接收 JSON 输入。

```json
{
  "type": "command",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/my-hook.sh",
  "timeout": 600,
  "async": false,
  "if": "Bash(rm *)",
  "statusMessage": "Checking...",
  "shell": "bash"
}
```

### 2. HTTP Handler

POST 事件数据到 URL。

```json
{
  "type": "http",
  "url": "http://localhost:3000/hook",
  "headers": { "Authorization": "Bearer $MY_TOKEN" },
  "allowedEnvVars": ["MY_TOKEN"],
  "timeout": 30
}
```

### 3. Prompt Handler（单轮 LLM 评估）

```json
{
  "type": "prompt",
  "prompt": "Evaluate: $ARGUMENTS",
  "model": "claude-haiku-4-5-20241022",
  "timeout": 30
}
```

响应格式：`{ "ok": true/false, "reason": "..." }`

### 4. Agent Handler（多轮代理，最多 50 轮）

```json
{
  "type": "agent",
  "prompt": "Verify: $ARGUMENTS",
  "model": "claude-sonnet-4-6",
  "timeout": 60
}
```

## 四、Handler 类型支持矩阵

| 事件 | command | http | prompt | agent |
|------|---------|------|--------|-------|
| `PreToolUse` | ✓ | ✓ | ✓ | ✓ |
| `PostToolUse` | ✓ | ✓ | ✓ | ✓ |
| `Stop` | ✓ | ✓ | ✓ | ✓ |
| `SubagentStop` | ✓ | ✓ | ✓ | ✓ |
| `UserPromptSubmit` | ✓ | ✓ | ✓ | ✓ |
| `TaskCreated` / `TaskCompleted` | ✓ | ✓ | ✓ | ✓ |
| `SessionStart` | ✓ | - | - | - |
| `Notification` | ✓ | ✓ | - | - |
| `ConfigChange` | ✓ | ✓ | - | - |
| `FileChanged` | ✓ | ✓ | - | - |
| `PermissionDenied` | ✓ | ✓ | - | - |

## 五、输入/输出格式

### 输入（JSON via stdin）

```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test" }
}
```

### 输出（退出码 + JSON stdout）

| 退出码 | 含义 |
|--------|------|
| **0** | 成功，解析 stdout JSON |
| **2** | 阻塞错误，stderr 反馈给 Claude |
| **其他** | 非阻塞错误，继续 |

### 关键输出字段

```json
{
  "continue": true,
  "stopReason": "continue=false 时显示给用户",
  "suppressOutput": false,
  "systemMessage": "显示给用户的警告",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "原因",
    "updatedInput": {},
    "additionalContext": "额外上下文"
  }
}
```

### 各事件的 hookSpecificOutput

**PreToolUse**：
- `permissionDecision`: `allow` / `deny` / `ask` / `defer`
- `updatedInput`: 修改后的工具输入

**SessionStart**：
- `additionalContext`: 注入到 Claude 上下文的文本

**PermissionRequest**：
- `decision.behavior`: `allow` / `deny`

**PostToolUse / Stop / SubagentStop**：
- `decision`: `block`（阻止继续）

## 六、异步 vs 同步

| 特性 | 同步（默认） | 异步（`async: true`） |
|------|-------------|---------------------|
| 阻塞 Claude | 是 | 否 |
| 可阻止操作 | 是 | 否 |
| 输出生效时机 | 立即 | 下一轮对话 |
| 去重 | 相同命令去重 | 不去重 |

异步 hook 仅 `command` 类型支持。控制字段（`decision`、`permissionDecision`）无效。

## 七、环境变量

| 变量 | 说明 |
|------|------|
| `$CLAUDE_PROJECT_DIR` | 项目根目录 |
| `${CLAUDE_PLUGIN_ROOT}` | 插件安装目录 |
| `${CLAUDE_PLUGIN_DATA}` | 插件数据目录 |
| `$CLAUDE_ENV_FILE` | 环境变量持久化文件 |

## 八、Superpowers 中的 Hook 实现（实例分析）

### hooks.json（插件级配置）

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

### session-start 脚本流程

1. 检测遗留 skills 目录，生成警告
2. 读取 `using-superpowers` 技能内容
3. 转义为 JSON 字符串
4. 根据平台输出不同格式：
   - **Claude Code** → `hookSpecificOutput.additionalContext`
   - **Cursor** → `additional_context`
   - **其他** → `additional_context`（fallback）

核心价值：在每次会话开始时自动注入技能使用规则，无需用户手动加载。

## 九、推荐的 Hook 配置模式

### 模式 1：安全防护（PreToolUse）

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/block-dangerous.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

阻止 `rm -rf /`、`git push --force` 等危险命令。

### 模式 2：自动提交关联（PostToolUse）

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/track-changes.sh",
            "async": true
          }
        ]
      }
    ]
  }
}
```

文件修改后自动记录变更到任务追踪系统。

### 模式 3：会话上下文注入（SessionStart）

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/load-context.sh",
            "async": false
          }
        ]
      }
    ]
  }
}
```

注入项目特定的 AI 上下文（如组件库使用规范）。

### 模式 4：质量门控（Stop）

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Before stopping, verify: 1) No TODO/FIXME left 2) Tests pass 3) Code reviewed. Args: $ARGUMENTS",
            "model": "claude-haiku-4-5-20241022",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Claude 完成前自动进行质量检查。
