---
name: networking
description: Modern networking patterns for iOS — async/await URLSession, APIClient with protocol-based DI, retry with backoff, offline detection, and error handling. Use when building API clients, implementing network layers, or handling connectivity.
---

# Networking Skill

## Operating Rules

- Use native URLSession with async/await — no third-party networking libraries needed
- APIClient must be protocol-based for dependency injection and testing
- Retry only on transient errors (5xx, timeout, connection lost) — never on 4xx
- Use `NWPathMonitor` for connectivity, not Reachability
- Auth tokens in headers, never in URLs
- All networking code must be `Sendable`

## Task Workflow

### Build an API client
1. Define the protocol (see `references/api-client.md`)
2. Implement with URLSession async/await
3. Add retry logic for transient errors
4. Create mock implementation for tests
5. Inject via initializer in ViewModels

### Handle offline scenarios
- Consult `references/connectivity.md` for NWPathMonitor patterns
- Cache critical data locally (SwiftData, FileManager)
- Queue mutations for sync when connectivity returns

### Topic Router

| Topic | Reference |
|-------|-----------|
| API client architecture | `references/api-client.md` |
| Connectivity & offline | `references/connectivity.md` |

## Networking Checklist

- [ ] APIClient is protocol-based (injectable, testable)
- [ ] Uses async/await (not completion handlers)
- [ ] Retry logic on transient errors with exponential backoff
- [ ] Auth tokens in Authorization header (not URL params)
- [ ] Errors mapped to app-specific types
- [ ] Mock client available for tests and previews
- [ ] `NWPathMonitor` for connectivity (not Reachability)
- [ ] Request/response logging only in DEBUG
