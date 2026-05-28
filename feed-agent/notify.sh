#!/bin/bash
# Parse feed.md and fire a macOS notification with count + top role + why it fits

FEED="$(cd "$(dirname "$0")/.." && pwd)/feed/feed.md"

if [[ ! -f "$FEED" ]]; then
    osascript -e 'display notification "Feed file not found — check run.log" with title "Job Feed"'
    exit 1
fi

# Count summary line e.g. "3 recommended · 0 stretch · 98 skipped"
SUMMARY=$(grep -m1 "recommended · " "$FEED" | tr -d '*' | xargs)

if [[ -z "$SUMMARY" ]]; then
    osascript -e 'display notification "Feed ran but could not parse counts — check feed.md" with title "Job Feed"'
    exit 0
fi

# Extract recommended count
REC_COUNT=$(echo "$SUMMARY" | grep -oE "^[0-9]+")

if [[ "$REC_COUNT" == "0" ]]; then
    osascript -e "display notification \"No recommended roles today. $SUMMARY\" with title \"Job Feed\""
    exit 0
fi

# Top recommended role: first ### heading after "## Recommended"
TOP_ROLE=$(awk '/^## Recommended/{found=1; next} found && /^### /{print; exit}' "$FEED" \
    | sed 's/^### //' \
    | sed 's/ \[TARGET\]//g' \
    | sed 's/ \[REPOST\]//g' \
    | sed 's/ \[ABOVE LEVEL\]//g')

# "Why this is yours" for the top role
WHY=$(awk '/^## Recommended/{found=1} found && /\*\*Why this is yours:\*\*/{print; exit}' "$FEED" \
    | sed 's/.*\*\*Why this is yours:\*\* //')

# Trim WHY to ~100 chars so it fits in a macOS banner without truncating
if [[ ${#WHY} -gt 100 ]]; then
    WHY="${WHY:0:97}..."
fi

# Compose notification
TITLE="Job Feed — $SUMMARY"

if [[ -n "$TOP_ROLE" && -n "$WHY" ]]; then
    SUBTITLE="$TOP_ROLE"
    BODY="$WHY"
    osascript -e "display notification \"$BODY\" with title \"$TITLE\" subtitle \"$SUBTITLE\""
elif [[ -n "$TOP_ROLE" ]]; then
    osascript -e "display notification \"$TOP_ROLE\" with title \"$TITLE\""
else
    osascript -e "display notification \"$SUMMARY\" with title \"Job Feed\" subtitle \"feed/feed.md updated\""
fi
