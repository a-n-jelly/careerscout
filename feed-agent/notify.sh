#!/bin/bash
# Parse feed.md and fire a macOS notification with the count summary

FEED="$(cd "$(dirname "$0")/.." && pwd)/feed/feed.md"

if [[ ! -f "$FEED" ]]; then
    osascript -e 'display notification "Feed file not found — check run.log" with title "Job Feed"'
    exit 1
fi

# Extract the summary line: "[N worth a look] · [N skipped]"
SUMMARY=$(grep -m1 "recommended · " "$FEED" | tr -d '*' | xargs)

if [[ -z "$SUMMARY" ]]; then
    osascript -e 'display notification "Feed ran but could not parse counts — check feed.md" with title "Job Feed"'
    exit 0
fi

osascript -e "display notification \"$SUMMARY\" with title \"Job Feed\" subtitle \"feed/feed.md updated\""
