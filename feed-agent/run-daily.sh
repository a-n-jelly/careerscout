#!/bin/bash
# Daily job feed runner — called by launchd at 8am (fires on wake if missed)
# Logs to feed-agent/run.log

AGENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$AGENT_DIR/feed-agent/run.log"

# Log the start timestamp first — so any failure below is traceable
echo "--- $(date '+%Y-%m-%d %H:%M:%S') ---" >> "$LOG"

# ── Resolve paths ─────────────────────────────────────────────────────────────

# 1. User config (copy config.sh.template → config.sh and set your paths)
CONFIG="$AGENT_DIR/feed-agent/config.sh"
[[ -f "$CONFIG" ]] && source "$CONFIG"

# 2. Fallback: search common install locations for claude
if [[ -z "${CLAUDE_BIN:-}" ]]; then
    for candidate in \
        /usr/local/bin/claude \
        /opt/homebrew/bin/claude \
        "$HOME/.local/bin/claude" \
        "$HOME/.npm/bin/claude" \
        "$HOME/node_modules/.bin/claude"
    do
        if [[ -x "$candidate" ]]; then
            CLAUDE_BIN="$candidate"
            break
        fi
    done
fi

# 3. Python: prefer venv, fall back to system
PYTHON="${PYTHON_BIN:-$AGENT_DIR/feed-agent/.venv/bin/python3}"
if [[ ! -x "$PYTHON" ]]; then
    PYTHON="$(which python3 2>/dev/null || true)"
fi

# Validate
if [[ -z "${CLAUDE_BIN:-}" ]]; then
    echo "ERROR: claude not found. Copy feed-agent/config.sh.template to feed-agent/config.sh and set CLAUDE_BIN." >> "$LOG"
    osascript -e "display notification \"Feed failed — claude not found. Check run.log\" with title \"Job Feed\"" 2>/dev/null
    exit 1
fi
if [[ -z "${PYTHON:-}" ]]; then
    echo "ERROR: python3 not found." >> "$LOG"
    exit 1
fi

# ── Run ───────────────────────────────────────────────────────────────────────

set -euo pipefail
trap 'osascript -e "display notification \"Feed failed — check run.log\" with title \"Job Feed\" subtitle \"$(date +%H:%M)\"" 2>/dev/null' ERR

cd "$AGENT_DIR"

echo "Fetching roles..." >> "$LOG"
"$PYTHON" feed-agent/fetch.py >> "$LOG" 2>&1

echo "Filtering dismissed roles..." >> "$LOG"
"$PYTHON" feed-agent/filter_dismissed.py >> "$LOG" 2>&1

echo "Enriching descriptions..." >> "$LOG"
"$PYTHON" feed-agent/enrich.py >> "$LOG" 2>&1

echo "Scoring feed..." >> "$LOG"
"$CLAUDE_BIN" --model claude-sonnet-4-5 --dangerously-skip-permissions -p "/feed" >> "$LOG" 2>&1

echo "Notifying..." >> "$LOG"
bash feed-agent/notify.sh

echo "Done." >> "$LOG"
