#!/usr/bin/env bash
# OpenClaw on Anthropic - Post April 2026 Fix
# One-stop script to migrate OpenClaw to Claude CLI backend
# Usage: ./setup-openclaw-anthropic.sh
#
# Prerequisites:
#   - Anthropic account with Extra Usage enabled (https://claude.ai settings > billing)
#   - Claude CLI installed (https://docs.anthropic.com/en/docs/claude-code)
#
# Expected runtime: ~5 minutes

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# --- Step 0: Prerequisites Check ---
info "Checking prerequisites..."

if ! command -v openclaw &>/dev/null; then
  error "openclaw not found. Install it first: https://github.com/openclaw/openclaw"
fi

if ! command -v claude &>/dev/null; then
  error "claude CLI not found. Install it first: https://docs.anthropic.com/en/docs/claude-code"
fi

CLAUDE_PATH=$(command -v claude)
info "Found claude at: $CLAUDE_PATH"
info "Found openclaw at: $(command -v openclaw)"

# --- Step 1: Authenticate Claude CLI ---
info "Step 1/4: Verifying Claude CLI authentication..."

if claude --version &>/dev/null; then
  info "Claude CLI version: $(claude --version 2>&1 | head -1)"
else
  warn "Claude CLI not authenticated. Launching login..."
  claude auth login
fi

# --- Step 2: Migrate OpenClaw to Claude CLI backend ---
info "Step 2/4: Migrating OpenClaw models to claude-cli provider..."

openclaw models auth login --provider anthropic --method cli --set-default

info "Model paths migrated from anthropic/* to claude-cli/*"

# --- Step 3: Generate fresh token ---
info "Step 3/4: Setting up auth token..."
info "Run this in a SECOND terminal if prompted:"
info "  openclaw models auth setup-token --provider anthropic"

openclaw models auth setup-token --provider anthropic

# --- Step 4: Fix missing CLI backend in config ---
info "Step 4/4: Patching openclaw.json with CLI backend config..."

OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

if [ ! -f "$OPENCLAW_CONFIG" ]; then
  warn "No openclaw.json found at $OPENCLAW_CONFIG"
  warn "Creating a minimal config with CLI backend..."
  mkdir -p "$HOME/.openclaw"
  cat > "$OPENCLAW_CONFIG" <<JSONEOF
{
  "cliBackends": {
    "claude-cli": {
      "command": "$CLAUDE_PATH",
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
JSONEOF
  info "Created $OPENCLAW_CONFIG"
else
  # Backup existing config
  cp "$OPENCLAW_CONFIG" "${OPENCLAW_CONFIG}.bak"
  info "Backed up existing config to ${OPENCLAW_CONFIG}.bak"

  # Use python/jq to merge cliBackends if possible
  if command -v jq &>/dev/null; then
    # Read existing, merge cliBackends, write back
    TMP=$(mktemp)
    jq --arg path "$CLAUDE_PATH" '
      .cliBackends = (.cliBackends // {}) |
      .cliBackends["claude-cli"] = {
        "command": $path,
        "args": ["-p", "--output-format", "stream-json", "--include-partial-messages", "--verbose", "--permission-mode", "bypassPermissions"],
        "resumeArgs": ["-p", "--output-format", "stream-json", "--include-partial-messages", "--verbose", "--permission-mode", "bypassPermissions", "--resume", "{sessionId}"],
        "output": "jsonl",
        "input": "stdin",
        "modelArg": "--model",
        "systemPromptArg": "--append-system-prompt",
        "sessionArg": "--session-id",
        "systemPromptWhen": "first",
        "sessionMode": "always"
      }
    ' "$OPENCLAW_CONFIG" > "$TMP" && mv "$TMP" "$OPENCLAW_CONFIG"
    info "Merged cliBackends into existing config using jq"
  elif command -v python3 &>/dev/null; then
    python3 -c "
import json, sys
with open('$OPENCLAW_CONFIG') as f:
    cfg = json.load(f)
cfg.setdefault('cliBackends', {})
cfg['cliBackends']['claude-cli'] = {
    'command': '$CLAUDE_PATH',
    'args': ['-p', '--output-format', 'stream-json', '--include-partial-messages', '--verbose', '--permission-mode', 'bypassPermissions'],
    'resumeArgs': ['-p', '--output-format', 'stream-json', '--include-partial-messages', '--verbose', '--permission-mode', 'bypassPermissions', '--resume', '{sessionId}'],
    'output': 'jsonl', 'input': 'stdin',
    'modelArg': '--model',
    'systemPromptArg': '--append-system-prompt',
    'sessionArg': '--session-id',
    'systemPromptWhen': 'first',
    'sessionMode': 'always'
}
with open('$OPENCLAW_CONFIG', 'w') as f:
    json.dump(cfg, f, indent=2)
"
    info "Merged cliBackends into existing config using python3"
  else
    warn "Neither jq nor python3 found. Manually add the cliBackends section to $OPENCLAW_CONFIG"
    warn "See the tutorial markdown for the full JSON block."
  fi
fi

# --- Verification ---
info "Running verification test..."
echo ""

if openclaw agent --local --agent main -m "hello, what model are you?" 2>&1; then
  echo ""
  info "SUCCESS! OpenClaw agents are working."
else
  echo ""
  warn "Verification returned non-zero. Check the output above for errors."
  warn "Common fixes:"
  warn "  - Ensure Extra Usage is enabled at claude.ai > Settings > Billing"
  warn "  - Re-run: claude auth login"
  warn "  - Check: openclaw models auth status"
fi

echo ""
info "Post-migration checklist:"
info "  [ ] Monitor Extra Usage balance at claude.ai > Settings > Billing"
info "  [ ] If Claude CLI session expires, run: claude auth login"
info "  [ ] Backup saved at: ${OPENCLAW_CONFIG}.bak"
info "Done. Expected total time: ~5 minutes."
