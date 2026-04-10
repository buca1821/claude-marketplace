#!/bin/bash
# Sends a macOS notification when Claude needs user attention.
# Used for Stop and PermissionRequest hook events.

if ! command -v python3 >/dev/null 2>&1; then
  echo "claude-notifications-macos: python3 not found; install Xcode Command Line Tools with: xcode-select --install" >&2
  exit 0
fi

TERMINAL_NOTIFIER="${TERMINAL_NOTIFIER:-terminal-notifier}"
if ! command -v "$TERMINAL_NOTIFIER" >/dev/null 2>&1; then
  echo "claude-notifications-macos: terminal-notifier not found; install with: brew install terminal-notifier" >&2
  exit 0
fi

input=$(cat)
event=$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('hook_event_name','unknown'))" "$input")

# Sanitize a string for use in an AppleScript string literal:
# strips backslashes and double-quotes, truncates to 120 chars.
sanitize() {
  echo "$1" | tr -d '\\"' | cut -c1-120
}

case "$event" in
  "Stop")
    title="Claude Code — Done"
    # Extract the last assistant message text from the transcript
    context=""
    transcript_path=$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('transcript_path',''))" "$input")
    if [ -n "$transcript_path" ] && [ -f "$transcript_path" ]; then
      sleep 0.5
      context=$(python3 - "$transcript_path" <<'PYEOF'
import json, sys

path = sys.argv[1]
last_text = ""
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") == "assistant":
            content = obj.get("message", {}).get("content", [])
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    last_text = block.get("text", "")
print(last_text, end="")
PYEOF
)
    fi
    if [ -n "$context" ] && [ "$context" != "null" ]; then
      message=$(sanitize "$context")
    else
      message="Claude has finished — check your terminal"
    fi
    ;;
  "PermissionRequest")
    title="Claude Code — Permission Required"
    tool=$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('tool_name','unknown tool'))" "$input")
    detail=$(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tool_input = d.get('tool_input', {})
if d.get('tool_name') == 'Bash':
    print(tool_input.get('command', ''))
elif tool_input.get('file_path'):
    print(tool_input.get('file_path', ''))
else:
    print('')
" "$input")
    if [ -n "$detail" ] && [ "$detail" != "null" ]; then
      message=$(sanitize "$tool: $detail")
    else
      message=$(sanitize "Permission needed for: $tool")
    fi
    ;;
  *)
    title="Claude Code"
    message="Claude needs your attention"
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$TERMINAL_NOTIFIER" \
  -title "$title" \
  -message "$message" \
  -sound Glass \
  -activate "com.apple.Terminal" \
  -contentImage "$SCRIPT_DIR/claude-icon.png"
