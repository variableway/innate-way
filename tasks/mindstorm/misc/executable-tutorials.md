# Executable Tutorial: Run OpenClaw on Anthropic After April 2026 Restrictions

> **Source**: [thehype.news](https://thehype.news/how-to-run-openclaw-on-anthropic-after-the-april-2026-restrictions/)
> **Estimated time**: 5-7 minutes

---

## What Changed (April 4, 2026)

Anthropic now requires **Extra Usage** billing for OpenClaw calls. Max/Pro plans still work for claude.ai and Claude Code, but OpenClaw routes separately. Old OAuth tokens also started timing out (60s), so a migration to **Claude CLI backend** is needed.

---

## One-Stop Script

Everything below is automated in a single script:

```bash
# Run this (after enabling Extra Usage in claude.ai > Settings > Billing):
./setup-openclaw-anthropic.sh
```

The script is at `setup-openclaw-anthropic.sh` in the same directory as this file.

---

## Manual Steps (if you prefer)

### 0. Enable Extra Usage (1 min)

Go to **claude.ai > Settings > Billing** and activate Extra Usage. Without it, every request fails silently.

### 1. Verify Claude CLI (30 sec)

```bash
which claude && claude --version
# If not authenticated:
claude auth login
```

### 2. Migrate OpenClaw to CLI Backend (30 sec)

```bash
openclaw models auth login --provider anthropic --method cli --set-default
```

This changes model paths from `anthropic/claude-sonnet-4-6` to `claude-cli/claude-sonnet-4-6`.

### 3. Generate Fresh Token (1 min)

```bash
openclaw models auth setup-token --provider anthropic
```

When prompted, open a second terminal and run the same command. Copy the generated token, paste it back, give it a name.

### 4. Patch CLI Backend Config (2 min)

Add `cliBackends` to `~/.openclaw/openclaw.json`. Find your claude path with `which claude`, then:

```json
{
  "cliBackends": {
    "claude-cli": {
      "command": "/home/YOUR_USER/.local/bin/claude",
      "args": [
        "-p",
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--permission-mode", "bypassPermissions"
      ],
      "resumeArgs": [
        "-p",
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--permission-mode", "bypassPermissions",
        "--resume", "{sessionId}"
      ],
      "output": "jsonl",
      "input": "stdin",
      "modelArg": "--model",
      "systemPromptArg": "--append-system-prompt",
      "sessionArg": "--session-id",
      "systemPromptWhen": "first",
      "sessionMode": "always"
    }
  }
}
```

**Parameter reference:**

| Flag | Purpose |
|---|---|
| `-p` | Pipe mode (non-interactive) |
| `--output-format stream-json` | JSONL streaming output |
| `--include-partial-messages` | Send response fragments as generated |
| `--verbose` | Detailed logging |
| `--permission-mode bypassPermissions` | Skip interactive prompts |
| `--resume {sessionId}` | Session continuation |

### 5. Verify (30 sec)

```bash
openclaw agent --local --agent main -m "hello, what model are you?"
```

You should get a response confirming the model.

---

## Post-Migration Monitoring

- **Extra Usage balance**: check claude.ai > Settings > Billing regularly
- **CLI session expiry**: re-run `claude auth login` if it expires
- **Rollback**: backup saved at `openclaw.json.bak`
