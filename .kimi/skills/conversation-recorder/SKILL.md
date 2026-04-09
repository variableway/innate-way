# Conversation Recorder Skill

## 描述

用于捕获和记录与 AI 的完整对话过程，包括用户输入、AI 输出、思考过程、技能使用等信息。

## 适用场景

- 记录重要的 AI 对话过程
- 分析 AI 使用的技能和思维方式
- 从对话中提取行动项
- 知识沉淀和复盘

## 使用方法

### 1. 启动会话记录

```bash
# 在对话开始前启动记录
capture session start --name="功能设计讨论" --goal="设计新的API接口"
```

### 2. 使用 Skill 记录

在对话过程中，此 Skill 会自动记录：
- 用户输入
- AI 响应
- 使用的技能
- 思考过程（如果启用）

### 3. 结束会话

```bash
# 对话结束后
capture session end --summary="完成了API设计，确定了RESTful规范"
```

### 4. 查看记录

```bash
# 列所有会话
capture session list

# 查看会话详情（在生成的 Markdown 文件中）
cat docs/capture-tui/sessions/2024-01/sess-xxxxx.md
```

## 配置

在 `.capture/config.yaml` 中配置：

```yaml
session:
  capture_dir: "./docs/capture-tui/sessions"
  auto_capture: true      # 自动开始记录
  capture_thinking: true  # 记录思考过程
  max_duration: 3600      # 最大会话时长（秒）
```

## 数据结构

### 会话记录文件

会话记录以 JSON 和 Markdown 两种格式保存：

```
docs/capture-tui/sessions/
├── 2024-01/
│   ├── sess-20240115-103000-abc123.json
│   ├── sess-20240115-103000-abc123.md
│   └── sess-20240115-110000-def456.json
└── ...
```

### JSON 格式

```json
{
  "id": "sess-20240115-103000-abc123",
  "name": "功能设计讨论",
  "start_time": "2024-01-15T10:30:00+08:00",
  "end_time": "2024-01-15T11:00:00+08:00",
  "tool": "kimi-cli",
  "goal": "设计新的API接口",
  "summary": "完成了API设计...",
  "turns": [
    {
      "turn_number": 1,
      "user_input": "请帮我设计一个用户管理API",
      "ai_response": "好的，我建议使用RESTful风格...",
      "thinking": "用户需要API设计，我应该...",
      "skills_used": ["plan", "design"],
      "model": "kimi",
      "timestamp": "2024-01-15T10:30:05+08:00"
    }
  ]
}
```

## 注意事项

1. **隐私**: 会话记录包含完整对话内容，请注意隐私保护
2. **存储**: 定期清理旧的会话记录以节省空间
3. **性能**: 长时间会话可能影响性能，建议适时结束

## 相关命令

- `capture session start` - 开始会话
- `capture session end` - 结束会话
- `capture session list` - 列会话
- `capture add` - 添加想法
- `capture analyze` - 分析分类
