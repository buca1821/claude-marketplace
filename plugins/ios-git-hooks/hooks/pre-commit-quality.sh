#!/usr/bin/env bash
# PreToolUse hook: run quality checks on staged .swift files before commit.
# Exit 2 = block tool use with message.

input=$(cat)
tool_input=$(echo "$input" | jq -r '.tool_input.command // ""')

# Only care about git commit commands
echo "$tool_input" | grep -qE 'git commit' || exit 0

# Get staged .swift files
staged_files=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.swift$' || true)
[ -z "$staged_files" ] && exit 0

issues=""

# --- Check 1: Hardcoded strings in SwiftUI views ---
for file in $staged_files; do
  [ ! -f "$file" ] && continue

  # Detect Text("literal") without localized: pattern
  # Matches: Text("Some string") but NOT Text("key.name") or Text(variable)
  # Heuristic: flag Text("...") where the string contains spaces (likely user-facing)
  hardcoded=$(git diff --cached -- "$file" | grep '^+' | grep -v '^+++' | \
    grep -E 'Text\("[^"]*[[:space:]][^"]*"\)' | \
    grep -v 'localized' | \
    grep -v 'String(localized' | \
    head -3)

  if [ -n "$hardcoded" ]; then
    issues="${issues}\n⚠️  Possible hardcoded string in $file:\n$hardcoded\n   Use String(localized: \"key.name\") instead.\n"
  fi
done

# --- Check 2: SwiftLint (if available) ---
if command -v swiftlint &>/dev/null; then
  lint_errors=""
  for file in $staged_files; do
    [ ! -f "$file" ] && continue
    result=$(swiftlint lint --quiet --path "$file" 2>/dev/null | grep "error:" | head -3)
    [ -n "$result" ] && lint_errors="${lint_errors}\n$result"
  done

  if [ -n "$lint_errors" ]; then
    issues="${issues}\n⚠️  SwiftLint errors:${lint_errors}\n"
  fi
fi

# --- Report ---
if [ -n "$issues" ]; then
  echo -e "Pre-commit quality issues found:\n${issues}"
  echo "Fix these before committing, or use --no-verify for docs-only commits."
  exit 2
fi

exit 0
