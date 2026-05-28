#!/bin/bash
# Daily job feed runner — called by launchd at 8am
# Logs to feed-agent/run.log

set -euo pipefail

# Fire a macOS notification on any failure
trap 'osascript -e "display notification \"Feed failed — check run.log\" with title \"Job Feed\" subtitle \"$(date +%H:%M)\"" 2>/dev/null' ERR

AGENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$AGENT_DIR/feed-agent/run.log"
CLAUDE="$(which claude)"
PYTHON="$AGENT_DIR/feed-agent/.venv/bin/python3"

cd "$AGENT_DIR"

echo "--- $(date '+%Y-%m-%d %H:%M:%S') ---" >> "$LOG"

echo "Fetching roles..." >> "$LOG"
"$PYTHON" feed-agent/fetch.py >> "$LOG" 2>&1

echo "Enriching descriptions..." >> "$LOG"
"$PYTHON" feed-agent/enrich.py >> "$LOG" 2>&1

echo "Scoring feed..." >> "$LOG"
"$CLAUDE" --model claude-sonnet-4-5 --dangerously-skip-permissions -p "/feed" >> "$LOG" 2>&1

echo "Notifying..." >> "$LOG"
bash feed-agent/notify.sh

echo "Done." >> "$LOG"
