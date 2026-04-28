# Claude Marketplace

Personal Claude Code plugin marketplace by [@buca1821](https://github.com/buca1821).

## Installation

```bash
claude plugin marketplace add buca1821/claude-marketplace
```

Then install plugins with:

```bash
claude plugin install <plugin-name>@buca1821-marketplace
```

## Plugins

### iOS Development

| Plugin | Description |
|--------|-------------|
| **ios-swift-skills** | 12 skills: SwiftUI, design-system, swift-concurrency, security, networking, testing, performance, logging, cicd, app-store, review-pr, xcode-qa |
| **ios-audit-agents** | 6 audit agents (architecture, code health, API freshness, UX/accessibility, performance, CI/CD) + `/run-audits` and `/performance-audit` |
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

These plugins are designed to work with [claude-code-ios-template](https://github.com/buca1821/claude-code-ios-template). The template's `setup.sh` registers the marketplace and installs these plugins automatically.

## Updating plugins

```bash
claude plugin update ios-swift-skills@buca1821-marketplace
claude plugin update ios-audit-agents@buca1821-marketplace
claude plugin update ios-git-hooks@buca1821-marketplace
claude plugin update implement-issue@buca1821-marketplace
claude plugin update claude-notifications-macos@buca1821-marketplace
```

## License

MIT
