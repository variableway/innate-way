# Feature: Agent Daemon - Local Task Orchestration

## Priority: P0
## Task Reference: Task 3 (Long Running Session)
## Related Issue: #4
## Depends On: innate-capture task queue

## Description

Build a local daemon that polls for pending tasks, dispatches them to AI agents (Claude, Codex, Kimi), monitors execution, and reports results. The daemon is the core enabler for long-running autonomous sessions.

## Acceptance Criteria

- [ ] `capture daemon start` runs daemon in foreground or background
- [ ] `capture daemon stop` gracefully shuts down
- [ ] `capture daemon status` shows agents, active tasks, queue size
- [ ] Polls SQLite task queue and claims pending tasks
- [ ] Executes tasks via Claude Code adapter (subprocess)
- [ ] Captures agent output to log files
- [ ] Updates task status (pending → running → done/failed)
- [ ] Health endpoint at `http://localhost:19514/health`
- [ ] Feishu notification on task start/completion/failure
- [ ] Retry once on failure before marking as failed
- [ ] Graceful shutdown: finish current task, then stop

## Implementation

### Phase 1: Daemon Skeleton

```go
// internal/daemon/daemon.go
type Daemon struct {
    config    DaemonConfig
    agents    map[string]agent.Backend
    queue     queue.TaskQueue
    notifier  notify.Notifier
    sem       chan struct{} // concurrency semaphore
    cancel    context.CancelFunc
}

func (d *Daemon) Run(ctx context.Context) error {
    // Start health endpoint
    go d.serveHealth(ctx)

    // Poll loop
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            task, err := d.queue.Claim(d.agentID)
            if err != nil || task == nil {
                time.Sleep(d.config.PollInterval)
                continue
            }
            d.executeTask(ctx, task)
        }
    }
}
```

### Phase 2: Claude Code Adapter

```go
// internal/agent/claude.go
type ClaudeBackend struct {
    executable string
    model      string
}

func (c *ClaudeBackend) Execute(ctx context.Context, prompt string, opts ExecOptions) (*Result, error) {
    cmd := exec.CommandContext(ctx, c.executable, "--print", "--output-format", "json")
    cmd.Stdin = strings.NewReader(prompt)
    cmd.Dir = opts.WorkDir
    output, err := cmd.CombinedOutput()
    // Parse result...
}
```

### Phase 3: Feishu Notifier

```go
// internal/notify/feishu.go
type FeishuNotifier struct {
    webhookURL string
    botName    string
}

func (f *FeishuNotifier) Notify(event Event) error {
    // Format message based on event type
    // POST to Feishu webhook
}
```

### CLI Commands

```bash
# Start daemon
capture daemon start [--foreground] [--config ~/.capture/agents.yaml]

# Stop daemon
capture daemon stop

# Check status
capture daemon status

# View logs
capture daemon logs [-f] [-n 100]

# Queue tasks
capture task queue tasks/features/*.md --agent claude

# Manual task dispatch
capture task run tasks/features/001-setup-monorepo.md --agent claude
```

## Files to Create

| File | Description |
|------|-------------|
| `projects/capture/cmd/daemon.go` | Daemon CLI commands (start/stop/status/logs) |
| `projects/capture/internal/daemon/daemon.go` | Daemon main loop |
| `projects/capture/internal/daemon/scheduler.go` | Task claiming, priority, dependencies |
| `projects/capture/internal/daemon/health.go` | HTTP health endpoint |
| `projects/capture/internal/agent/backend.go` | Agent interface |
| `projects/capture/internal/agent/claude.go` | Claude Code adapter |
| `projects/capture/internal/agent/codex.go` | Codex adapter |
| `projects/capture/internal/agent/kimi.go` | Kimi adapter |
| `projects/capture/internal/notify/notifier.go` | Notifier interface |
| `projects/capture/internal/notify/feishu.go` | Feishu notification |
| `projects/capture/internal/queue/queue.go` | SQLite task queue |

## Config File

```yaml
# ~/.capture/agents.yaml
machine:
  id: "macbook-pro-001"
  name: "MacBook Pro"

agents:
  claude:
    type: "claude"
    executable: "claude"
    model: "claude-sonnet-4"
    max_concurrent: 2
  codex:
    type: "codex"
    executable: "codex"
    max_concurrent: 1

runtime:
  poll_interval: 30s
  task_timeout: 30m
  health_port: 19514

notify:
  feishu_webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
  events: ["task_started", "task_completed", "task_failed"]
```
