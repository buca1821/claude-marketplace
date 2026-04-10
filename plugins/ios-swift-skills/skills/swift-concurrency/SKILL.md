---
name: swift-concurrency
description: Swift 6.2 concurrency patterns — actors, @concurrent, isolated conformances, structured concurrency, and legacy API bridging. Use when fixing data race errors, migrating to Swift 6, or reviewing async code.
---

# Swift Concurrency Skill

## Decision Tree

```
What concurrency problem are you solving?
│
├─ Swift 6 compiler errors / migration
│  └─ Read references/swift62-features.md
│
├─ Swift 6.2 new features (@concurrent, isolated conformances)
│  └─ Read references/swift62-features.md
│
├─ Running work in parallel (async let, TaskGroup)
│  └─ Read references/structured-concurrency.md
│
├─ Thread safety for shared mutable state
│  └─ Read references/swift62-features.md (Actors section)
│
├─ Bridging old APIs (delegates, callbacks, etc.) to async/await
│  └─ Read references/continuations-bridging.md
│
└─ General async/await patterns
   └─ Read references/structured-concurrency.md
```

## Quick Reference

| Pattern | When to Use | Reference |
|---------|-------------|-----------|
| `async let` | Fixed number of parallel operations | structured-concurrency.md |
| `withTaskGroup` | Dynamic number of parallel operations | structured-concurrency.md |
| `.task { }` modifier | Load data when view appears | structured-concurrency.md |
| `.task(id:)` modifier | Re-load when a value changes | structured-concurrency.md |
| `actor` | Shared mutable state protection | swift62-features.md |
| `@MainActor` | UI-bound state and updates | swift62-features.md |
| `@concurrent` | Explicitly offload to background (6.2) | swift62-features.md |
| Isolated conformances | `@MainActor` type conforming to protocol (6.2) | swift62-features.md |
| `withCheckedContinuation` | Bridge callback API to async | continuations-bridging.md |
| `AsyncStream` | Bridge delegate/notification to async sequence | continuations-bridging.md |

## Process

### 1. Identify the Problem

- Is this a compiler error (strict concurrency) or runtime issue (data race, crash)?
- What Swift version and concurrency checking level?
- Migrating existing code or writing new code?

### 2. Load Relevant Reference

Based on the problem, read the appropriate reference file.

### 3. Apply Fix

Prefer the smallest safe fix that preserves existing behavior.

### 4. Review

Run through the checklist below.

## Review Checklist

- [ ] No blocking calls on `@MainActor` (use `await` for long operations)
- [ ] Shared mutable state protected by an actor (not locks or DispatchQueue)
- [ ] `Sendable` conformance correct for types crossing isolation boundaries
- [ ] Task cancellation handled (`Task.isCancelled` or `Task.checkCancellation()`)
- [ ] No unstructured `Task {}` where structured concurrency (`.task`, `TaskGroup`) would work
- [ ] Actor reentrancy considered at suspension points
- [ ] `withCheckedContinuation` called exactly once (not zero, not twice)
- [ ] `.task(id:)` used instead of manual `onChange` + cancel patterns

## Common Project Patterns

- ViewModels use `@MainActor` + `@Observable` — all UI state updates are main-actor-isolated
- Legacy callback APIs (e.g., HealthKit, CoreData, network) use `withCheckedContinuation` bridging — see `continuations-bridging.md`
- `DispatchQueue.main.async` is legacy — prefer `@MainActor` and `async/await`
- Data fetchers orchestrate async queries with structured concurrency
