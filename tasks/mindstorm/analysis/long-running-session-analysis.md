# Long Running Session - Autonomous AI Agent Orchestration

## Source
Mindstorm file: `tasks/mindstorm/capture/Desktop-Web.md` (Task 3)
GitHub Issue: #4
Reference: `innate-capture` project specs (agent-runtime-spec, distribute-task-architecture)

---

## 1. Is It Doable?

**Yes, with phased approach.** The core building blocks already exist or are well-understood:

| Building Block | Status | Effort |
|---|---|---|
| Task file format (Markdown + YAML) | Done in innate-capture | 0 |
| Agent backend interface (Claude, Codex, Kimi) | Spec'd in agent-runtime-spec | Medium |
| Feishu Bot integration | Done in innate-capture | Low |
| Local daemon service | Spec'd in issue #005 | Medium |
| Desktop monitoring UI | Client monorepo created | Medium |
| Multi-machine dispatch | Arch designed in distribute-task-architecture | High |

**Risk factors:**
- Agent session stability over long runs (context window limits, token exhaustion)
- Error recovery complexity across heterogeneous agents (Claude vs Codex vs Kimi)
- Feishu API rate limits for high-frequency notifications

---

## 2. Architecture Design

### 2.1 System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        Desktop / Web App                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌────────────┐ │
│  │ Dashboard │  │ Task Board   │  │ Agent     │  │ Notification│ │
│  │ (Monitor) │  │ (Kanban)     │  │ Console   │  │ (Feishu)   │ │
│  └─────┬─────┘  └──────┬──────┘  └─────┬─────┘  └──────┬─────┘ │
│        └────────────────┴───────────────┴───────────────┘       │
│                              │ REST API                         │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                     Local Daemon (Go)                            │
│  ┌───────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ Task      │  │ Agent      │  │ Notifier  │  │ Health       │ │
│  │ Scheduler │  │ Runner     │  │ (Feishu)  │  │ Monitor      │ │
│  └───────────┘  └────────────┘  └──────────┘  └──────────────┘ │
│        │              │              │              │             │
│        └──────────────┴──────────────┴──────────────┘           │
│                       Task Queue (SQLite)                        │
└──────────────────────────────────────────────────────────────────┘
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐    ┌───────────┐    ┌───────────┐
   │ Claude  │    │ Codex     │    │ Kimi/     │
   │ Agent   │    │ Agent     │    │ OpenClaw  │
   └─────────┘    └───────────┘    └───────────┘
```

### 2.2 Component Responsibilities

#### Daemon (Go - `capture daemon`)
The core orchestrator. Runs as a background process on each machine.

- **Task Scheduler**: Polls task queue, claims tasks, manages priorities
- **Agent Runner**: Spawns agent processes, manages lifecycle, captures output
- **Notifier**: Sends status updates to Feishu (start/done/error/progress)
- **Health Monitor**: Exposes HTTP health endpoint, tracks agent heartbeats

#### Agent Backends (Multi-language)
Each agent type has a thin adapter implementing a unified interface.

| Agent | Language | Interface | Session Resume |
|-------|----------|-----------|----------------|
| Claude Code | CLI subprocess | `claude --print` with stdin | Via session ID |
| Codex | CLI subprocess | `codex` with prompt file | Via session ID |
| Kimi | CLI subprocess | `kimi` command | Via session ID |
| OpenClaw | HTTP API | REST calls | Token-based |

#### Desktop/Web App (TypeScript/Next.js)
Monitoring and control surface.

- **Dashboard**: Real-time agent status, active tasks, system health
- **Task Board**: Kanban view of task pipeline stages
- **Agent Console**: View agent output streams, send commands
- **Notification Panel**: Feishu message history, alert configuration

#### Feishu Integration
Communication channel for notifications and remote control.

- **Notifications**: Task started/completed/failed, error alerts
- **Remote Control**: Send commands via Feishu messages to daemon
- **Status Queries**: "How's it going?" → daemon replies with summary

### 2.3 Data Flow

```
Mindstorm Files → Analysis → Feature Tasks → Task Queue
                                              │
                    ┌─────────────────────────┤
                    │                         │
                    ▼                         ▼
             Daemon picks task         Feishu: "Task X claimed by Claude"
                    │
                    ▼
             Agent executes (30min+)
             ├── streaming logs → file
             ├── periodic heartbeat → SQLite
             └── on progress → Feishu notification
                    │
                    ▼
             Task completed/failed
             ├── result → SQLite + Markdown
             ├── git commit + push
             └── Feishu: "Task X done. Commit: abc123"
                    │
                    ▼
             Next task in queue...
```

### 2.4 Tech Stack Mapping

Per the mindstorm requirements:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Desktop client** | Tauri + Next.js + shadcn-ui | Monitor dashboard |
| **Web client** | Next.js + shadcn-ui | Remote monitoring |
| **Daemon** | Go | Task orchestration, agent management |
| **Agent adapters** | Go (subprocess) | Spawn and manage CLI agents |
| **Notification** | Python (Feishu SDK) | Lark API integration, CLI bot |
| **Task storage** | SQLite + Markdown files | Local task queue + source of truth |
| **Database** | PostgreSQL (future) | Multi-machine centralized state |
| **Skills** | YAML/Markdown | Task templates, agent instructions |

---

## 3. Detailed Design: Core Scenarios

### 3.1 Scenario: Batch Task Execution Without Interaction

```
User: "Execute all tasks in tasks/mindstorm/analysis/"

1. Desktop app reads all .md files in the directory
2. Creates task entries in SQLite queue (status: pending)
3. Daemon picks up tasks in priority order
4. For each task:
   a. Claim task → set status to "running"
   b. Spawn agent process with task prompt
   c. Monitor output stream, write to log file
   d. On completion → update status, commit code, notify
   e. On failure → set status to "failed", notify, continue next
5. After all tasks → Feishu summary notification
```

**Key design: Task dependencies.** Tasks can declare dependencies:
```yaml
---
depends_on: ["001-setup-monorepo"]
---
```
Daemon resolves dependency graph and executes in topological order.

### 3.2 Scenario: Error Recovery

```
Agent fails mid-task (crash, timeout, context limit):

1. Daemon detects failure (exit code != 0, timeout, no heartbeat)
2. Saves partial state:
   - Agent session ID (for resume)
   - Last successful checkpoint
   - Error output
3. Sets task status to "failed" with error details
4. Sends Feishu notification with error summary
5. User options:
   a. Resume: daemon restarts agent with session ID
   b. Retry: daemon re-runs from scratch
   c. Skip: daemon moves to next task
   d. Debug: user inspects logs and state
```

**Recovery strategies:**

| Error Type | Auto-Recovery | Manual |
|---|---|---|
| Agent crash | Retry 1x, then fail | Inspect logs |
| Timeout | Retry with fresh context | Adjust timeout |
| Context limit | Split task automatically | Manual split |
| Git conflict | Auto-resolve if simple | Manual resolve |
| Network error | Retry with backoff | Check connectivity |

### 3.3 Scenario: Progress Monitoring

**Desktop Dashboard:**
```
┌──────────────────────────────────────────────────┐
│ Innate Capture - Agent Dashboard                 │
├──────────────────────────────────────────────────┤
│ Agents                                           │
│  🟢 Claude (idle)     0/3 tasks                  │
│  🟡 Codex (running)   1/2 tasks  [Task #005]    │
│  ⚪ Kimi (offline)     0/2 tasks                  │
│                                                  │
│ Task Pipeline                                    │
│  ■■■■■■□□□□  5/10 completed                      │
│                                                  │
│  #001 Setup monorepo      ✅ done     12m        │
│  #002 Create web app       ✅ done     8m         │
│  #003 Category feature    ✅ done     23m        │
│  #004 Long running spec   🔄 running  Claude     │
│  #005 Integration tests   ⏳ pending             │
│  ...                                            │
│                                                  │
│ Notifications                                    │
│  14:32 ✅ Task #003 completed (23m)              │
│  14:10 🔄 Task #004 started on Claude            │
│  13:55 ✅ Task #002 completed (8m)               │
└──────────────────────────────────────────────────┘
```

**Feishu Notifications:**
```
🤖 Innate Capture Bot

✅ Task Completed
Task: #003 Category Feature
Agent: Claude (claude-sonnet-4)
Duration: 23m 14s
Commit: abc1234 "add category management UI"
PR: #6

Next: #004 Long running session spec (Claude)
Queue: 3 remaining

Reply "status" for details, "pause" to stop.
```

---

## 4. Workable Planning

### Phase 1: Local Daemon + Single Agent (2 weeks)

**Goal:** One machine, one agent type, batch execution.

| Task | Description |
|------|-------------|
| D-01 | Go daemon skeleton: start/stop/status CLI commands |
| D-02 | SQLite task queue: create/poll/claim/update |
| D-03 | Claude Code adapter: spawn subprocess, capture output |
| D-04 | Task execution loop: claim → execute → report |
| D-05 | Basic error handling: retry once, log failures |
| D-06 | Health endpoint: HTTP `/health` |

```bash
# Usage in Phase 1
capture daemon start
capture task queue tasks/mindstorm/features/*.md
capture daemon status
```

### Phase 2: Feishu Notifications (1 week)

**Goal:** Get notified on phone/desktop via Feishu.

| Task | Description |
|------|-------------|
| F-01 | Feishu Bot message templates (start/done/fail/progress) |
| F-02 | Feishu CLI integration (use lark CLI or Python SDK) |
| F-03 | Notification rules: configurable per task priority |
| F-04 | Remote control: reply "pause"/"resume"/"status" via Feishu |

### Phase 3: Desktop Dashboard (2 weeks)

**Goal:** Visual monitoring in the Tauri app.

| Task | Description |
|------|-------------|
| UI-01 | Dashboard page: agent status cards |
| UI-02 | Task pipeline view: kanban-style progress |
| UI-03 | Agent log viewer: tail agent output in real-time |
| UI-04 | Task submission: queue tasks from UI |
| UI-05 | Notification panel: Feishu message history |

### Phase 4: Multi-Agent + Error Recovery (2 weeks)

**Goal:** Run multiple agent types, handle failures gracefully.

| Task | Description |
|------|-------------|
| MA-01 | Agent adapter registry: Codex, Kimi backends |
| MA-02 | Concurrent task execution with semaphore |
| MA-03 | Session resume: recover from agent crash |
| MA-04 | Task dependency graph resolution |
| MA-05 | Auto-split: break oversized tasks on context limit |

### Phase 5: Multi-Machine + Web Monitoring (3 weeks)

**Goal:** Distributed execution across machines, web-based monitoring.

| Task | Description |
|------|-------------|
| MM-01 | Machine registration protocol |
| MM-02 | Task dispatch to remote machines via Feishu |
| MM-03 | PostgreSQL centralized state (optional) |
| MM-04 | Web dashboard with real-time updates |
| MM-05 | Remote log streaming

---

## 5. Detail Features and Tasks

### Self-Made Tools Inventory

| Tool | Language | Status | Purpose |
|------|----------|--------|---------|
| `capture daemon` | Go | New | Background task orchestrator |
| `capture task queue` | Go | New | Batch queue .md files |
| `capture agent list` | Go | New | Show registered agents |
| `capture notify` | Python | New | Send Feishu notifications |
| `agent-runner` | Go | New | Adapter to spawn/manage agent processes |
| `agent-monitor` | Go | New | Health checks, heartbeat tracking |
| `agent-recover` | Go | New | Session resume, retry logic |
| Desktop dashboard | TypeScript | Scaffolded | Monitor UI in Tauri app |
| Web dashboard | TypeScript | Scaffolded | Monitor UI in browser |

### Skills to Develop

| Skill | Purpose |
|-------|---------|
| `batch-execution-skill` | Read task directory, generate execution plan |
| `agent-assignment-skill` | Match tasks to best agent based on type/complexity |
| `error-recovery-skill` | Analyze failures, suggest recovery actions |
| `progress-report-skill` | Generate human-readable progress summaries |
| `feishu-notify-skill` | Format and send Feishu notifications |

---

## 6. Pros and Cons

### Pros
- **Leverages existing work:** innate-capture has daemon spec, Feishu bot, and task model already
- **Local-first:** No cloud dependency, runs entirely on your machines
- **Incremental:** Each phase delivers working value
- **Multi-agent:** Not locked to one AI provider
- **Feishu ecosystem:** Natural fit with existing Feishu Bot + Bitable integration
- **Git-native:** Tasks and results live in git repos, versioned and auditable

### Cons
- **Complexity:** Multi-machine orchestration is inherently complex
- **Agent instability:** Long-running agent sessions can crash or hallucinate
- **Context limits:** Large tasks may exceed agent context windows
- **Feishu dependency:** Heavy reliance on Feishu API availability
- **No standard agent protocol:** Each agent (Claude, Codex, Kimi) has different CLI/API interface
- **Monitoring overhead:** Real-time log streaming across processes adds latency

---

## 7. How to Start?

### Immediate Next Steps (This Week)

1. **Create the daemon skeleton** in `innate-capture/projects/capture/`:
   ```bash
   # Add daemon command to Cobra CLI
   capture daemon start [--foreground]
   capture daemon status
   ```

2. **Implement simplest task queue** using SQLite:
   ```sql
   CREATE TABLE task_queue (
     id TEXT PRIMARY KEY,
     title TEXT,
     prompt TEXT,
     status TEXT DEFAULT 'pending',  -- pending, running, done, failed
     agent_id TEXT,
     created_at DATETIME,
     started_at DATETIME,
     completed_at DATETIME,
     result TEXT
   );
   ```

3. **Build Claude Code adapter** (simplest agent):
   ```go
   func runClaude(prompt string, workDir string) (result, error) {
     cmd := exec.Command("claude", "--print", "--output-format", "json")
     cmd.Stdin = strings.NewReader(prompt)
     cmd.Dir = workDir
     output, err := cmd.CombinedOutput()
     return string(output), err
   }
   ```

4. **Test end-to-end**: Queue 2-3 tasks → daemon picks them up → Claude executes → results logged

5. **Add Feishu notification** on task completion (reuse existing bot code from innate-capture)

### Where to Put Code

```
innate-capture/projects/capture/
├── cmd/daemon.go           # Daemon CLI commands
├── internal/daemon/        # Daemon core logic
│   ├── daemon.go           # Main loop
│   ├── scheduler.go        # Task scheduling
│   └── health.go           # Health endpoint
├── internal/agent/         # Agent backends
│   ├── backend.go          # Interface
│   ├── claude.go           # Claude Code adapter
│   ├── codex.go            # Codex adapter
│   └── kimi.go             # Kimi adapter
└── internal/notify/        # Notifications
    └── feishu.go           # Feishu notifier

innate-way/client/           # Desktop/Web dashboard
├── apps/desktop/src/app/
│   ├── dashboard/          # Agent monitoring page
│   └── notifications/      # Feishu message viewer
```

### Priority Order

1. **Daemon + Claude adapter** (can run batch tasks immediately)
2. **Feishu notifications** (get notified on phone)
3. **Desktop dashboard** (visual monitoring)
4. **Multi-agent** (Codex, Kimi support)
5. **Multi-machine** (distributed execution)
