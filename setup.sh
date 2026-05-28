#!/bin/bash
# CareerScout setup — wires .claude/ so Claude Code picks up commands and skills

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$SCRIPT_DIR/.claude"

mkdir -p "$CLAUDE_DIR"

# Commands
if [ -L "$CLAUDE_DIR/commands" ]; then
    echo "  .claude/commands symlink already exists — skipping"
elif [ -e "$CLAUDE_DIR/commands" ]; then
    echo "  Warning: .claude/commands exists but is not a symlink — leaving it alone"
else
    ln -s ../commands "$CLAUDE_DIR/commands"
    echo "  Created .claude/commands → commands/"
fi

# Skills
if [ -L "$CLAUDE_DIR/skills" ]; then
    echo "  .claude/skills symlink already exists — skipping"
elif [ -e "$CLAUDE_DIR/skills" ]; then
    echo "  Warning: .claude/skills exists but is not a symlink — leaving it alone"
else
    ln -s ../skills "$CLAUDE_DIR/skills"
    echo "  Created .claude/skills → skills/"
fi

echo ""
echo "Done. Open Claude Code in this directory and run /feed-setup to get started."
