#!/usr/bin/env bash
# PreToolUse hook: block commits on main unless docs-only.
# Exit 2 = block tool use with message.

input=$(cat)
tool_input=$(echo "$input" | jq -r '.tool_input.command // ""')

# Only care about git commit commands
echo "$tool_input" | grep -qE 'git commit' || exit 0

# Check current branch
branch=$(git symbolic-ref --short HEAD 2>/dev/null)
[ "$branch" != "main" ] && [ "$branch" != "master" ] && exit 0

# On main — check if only docs/config changed (no .swift files)
staged_swift=$(git diff --cached --name-only --diff-filter=ACMR | grep -c '\.swift$' || true)

if [ "$staged_swift" -gt 0 ]; then
  echo "BLOCKED: Cannot commit .swift files to main. Create a feature branch first."
  echo "  git checkout -b feat/<name>-<issue>"
  exit 2
fi

# Docs-only commit on main is allowed
exit 0
