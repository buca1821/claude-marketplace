---
name: logging
description: Native iOS logging and diagnostics — OSLog with structured logging, privacy redaction, signposts, MetricKit for production performance and crash reporting. Use when adding logging, tuning what reaches release builds, setting up crash reporting, or replacing print statements.
---

# Logging & Diagnostics Skill

## Operating Rules

- Use `os.Logger` for all logging — never `print()` or `NSLog()` in production code.
- Annotate every dynamic interpolation with an explicit `privacy:` modifier (`%{public}@`, `%{private}@`, `.sensitive`). Don't rely on the default — `Logger` redacts dynamic strings to `<private>` in release.
- Organize loggers by subsystem (bundle ID) and category (feature area). Categories should follow feature lines, not architectural layers.
- Use `OSSignposter` for performance instrumentation — intervals around hot paths, named events at boundaries. Signposts cost nothing in release if no one is listening.
- Use MetricKit for production diagnostics — no third-party crash reporters needed.
- Log levels have meaning: `debug` (DEBUG-only), `info` (general flow), `notice` (significant events), `error` (recoverable failures), `fault` (unrecoverable).
- Never log sensitive data without `.sensitive` annotation. Tokens, passwords, and PII must be marked so even sysdiagnose strips them.

## Topic Router

| Topic | Reference |
|-------|-----------|
| `Logger` setup, levels, subsystems, categories | `references/oslog.md` |
| Privacy modifiers, redaction behavior, what to redact, Console.app filtering | `references/privacy-redaction.md` |
| `OSSignposter` for performance instrumentation, Instruments integration | `references/signposts.md` |
| MetricKit for crash and performance diagnostics in production | `references/metrickit.md` |

## Quick Decision

| You need to... | Reach for |
|---|---|
| Record what happened (event, error, decision) | `Logger` |
| Time a region of code (will profile later) | `OSSignposter` |
| Mark a moment for Instruments correlation | `OSSignposter.emitEvent` |
| Receive crash reports from production | `MetricKit` |
| Receive performance diagnostics from production | `MetricKit` |
| Tune what's visible in release vs debug | `privacy:` modifier on interpolations |

## Logging Checklist

- [ ] No `print()` or `NSLog()` in production code paths.
- [ ] Every `Logger` interpolation has an explicit `privacy:` argument.
- [ ] Tokens, passwords, credentials use `.sensitive` (also stripped from sysdiagnose).
- [ ] PII that needs correlation uses `.private(mask: .hash)` instead of `.public`.
- [ ] No interpolation of whole model objects — pick specific fields.
- [ ] Loggers organized by subsystem (bundle ID) and category (feature).
- [ ] Log levels chosen deliberately — `debug` not used for events that matter in release.
- [ ] `OSSignposter` markers around suspected hot paths and feature boundaries.
- [ ] MetricKit subscriber implemented; crash and hang diagnostics forwarded or stored.
- [ ] No `#if DEBUG` used as a privacy mechanism — privacy is per-interpolation, not per-build.
