# Claude Marketplace

Personal Claude Code plugin marketplace by [@buca1821](https://github.com/buca1821).

## Installation

Register this marketplace in `~/.claude/plugins/known_marketplaces.json`:

```json
{
  "claude-marketplace": {
    "source": {
      "source": "github",
      "repo": "buca1821/claude-marketplace"
    },
    "installLocation": "<your-home>/.claude/plugins/marketplaces/claude-marketplace"
  }
}
```

Then install plugins with:

```bash
claude plugin install <plugin-name>@claude-marketplace
```

## Plugins

### iOS Development

| Plugin | Description |
|--------|-------------|
| **ios-swift-skills** | 12 skills: SwiftUI, design-system, swift-concurrency, security, networking, testing, performance, logging, cicd, app-store, review-pr, xcode-qa |
| **ios-audit-agents** | 4 audit agents (architecture, code health, API freshness, UX/accessibility) + `/run-audits` and `/performance-audit` |
| **ios-git-hooks** | Guard main branch from .swift commits + pre-commit quality checks (hardcoded strings, SwiftLint) |

### Workflow

| Plugin | Description |
|--------|-------------|
| **implement-issue** | End-to-end GitHub issue workflow: read → plan → implement → build → PR → review replies |

### Utilities

| Plugin | Description |
|--------|-------------|
| **claude-notifications-macos** | macOS notifications on task completion and permission requests |

## Usage with claude-code-ios-template

These plugins are designed to work with [claude-code-ios-template](https://github.com/buca1821/claude-code-ios-template). The template's `setup.sh` installs these plugins automatically and adds project-specific config (CLAUDE.md, rules, commands).

## Updating plugins

```bash
claude plugin update ios-swift-skills@claude-marketplace
claude plugin update ios-audit-agents@claude-marketplace
claude plugin update ios-git-hooks@claude-marketplace
claude plugin update implement-issue@claude-marketplace
```

## License

MIT
