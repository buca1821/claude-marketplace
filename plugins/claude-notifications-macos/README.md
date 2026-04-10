# claude-notifications-macos

macOS notifications when Claude needs your attention — fires on task completion and permission requests.

## What it does

- **Stop** — sends a notification when Claude finishes a task, showing a preview of the final response
- **PermissionRequest** — sends a notification when Claude is waiting for you to approve a tool call, showing the tool name and relevant detail (command, file path, etc.)

## Requirements

- **python3** — pre-installed on any Mac with Xcode Command Line Tools (`xcode-select --install`)
- **[terminal-notifier](https://github.com/julienXX/terminal-notifier)** — install via Homebrew:

```bash
brew install terminal-notifier
```

## Installation

```
/plugin marketplace add <marketplace-url>
/plugin add claude-notifications-macos
```

## Notifications

| Event | Title | Message |
|---|---|---|
| Task complete | Claude Code — Done | Preview of Claude's last response |
| Permission required | Claude Code — Permission Required | Tool name and command/file path |

Clicking a notification brings Terminal to the foreground.
