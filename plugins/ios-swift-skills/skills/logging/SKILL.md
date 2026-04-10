---
name: logging
description: Native iOS logging and diagnostics — OSLog with structured logging, MetricKit for production performance and crash reporting, diagnostics without third-party dependencies. Use when adding logging, setting up crash reporting, monitoring app performance, or replacing print statements.
---

# Logging & Diagnostics Skill

## Operating Rules

- Use `os.Logger` for all logging — never `print()` or `NSLog()` in production code
- Organize loggers by subsystem (bundle ID) and category (feature area)
- Never log sensitive data (tokens, passwords, PII)
- Use MetricKit for production diagnostics — no third-party crash reporters needed
- Log levels have meaning — use them correctly

## Task Workflow

### Replace print statements with OSLog
1. Identify all `print()` and `NSLog()` calls
2. Create loggers per feature area (see `references/oslog.md`)
3. Replace with appropriate log levels
4. Remove any sensitive data from log messages

### Set up production diagnostics
1. Implement MetricKit subscriber (see `references/metrickit.md`)
2. Handle crash reports and performance payloads
3. Forward to your analytics if needed

### Topic Router

| Topic | Reference |
|-------|-----------|
| OSLog structured logging | `references/oslog.md` |
| MetricKit diagnostics | `references/metrickit.md` |

## Logging Checklist

- [ ] No `print()` or `NSLog()` in production code
- [ ] Loggers organized by subsystem and category
- [ ] Log levels used correctly (debug, info, notice, error, fault)
- [ ] No sensitive data in log messages
- [ ] MetricKit subscriber implemented for production diagnostics
- [ ] Crash and hang diagnostics forwarded or stored
