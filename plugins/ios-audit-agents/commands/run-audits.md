# run-audits

Run all 4 auditor agents in parallel for a comprehensive codebase audit.

## Input

Scope: `$ARGUMENTS` (optional — `full`, `health`, `architecture`, `api`, `ux`, or empty for full)

## Process

### If scope is `full` or empty — run all 4 in parallel:

Launch these agents simultaneously using the Agent tool:

1. **code-health** — structural health, file sizes, tech debt, clean code
2. **architecture** — MVVM, DI, concurrency, localization, feature structure
3. **api-freshness** — deprecated APIs, Apple docs updates, skills freshness
4. **ux-accessibility** — VoiceOver, Dynamic Type, UI states, user feedback

### If scope is specific — run only that agent.

### After all agents complete:

1. Collect all individual reports from `docs/audits/`
2. Produce a unified summary:

```markdown
# Full Automated Audit — {{PROJECT_NAME}}

**Date**: YYYY-MM-DD
**Branch**: `main` (`<commit-hash>`)

## Summary

| Category | P1 | P2 | P3 | Total |
|----------|----|----|-----|-------|
| Code Health | N | N | N | N |
| Architecture | N | N | N | N |
| API Freshness | N | N | N | N |
| UX & Accessibility | N | N | N | N |
| **Total** | **N** | **N** | **N** | **N** |

## P1 Findings (Action Required)
[List all P1 findings from all agents]

## Recommendations
[Top 5 highest-impact improvements across all categories]
```

3. Save unified report to `docs/audits/YYYY-MM-DD-full-automated-audit.md`
4. If any P1 findings, suggest creating GitHub issues for them
