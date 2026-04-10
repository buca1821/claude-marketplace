# Structured Concurrency

## async let — Fixed Parallel Operations

```swift
async let profile = fetchProfile()
async let posts = fetchPosts()
async let friends = fetchFriends()
let data = try await (profile, posts, friends)
```

Rules: child tasks auto-cancel if parent exits. Each `async let` must be awaited. If one throws, others cancel.

## withTaskGroup — Dynamic Parallel Operations

```swift
await withTaskGroup(of: (UUID, Data).self) { group in
    for item in items {
        group.addTask { (item.id, await fetch(item)) }
    }
    for await (id, data) in group {
        results[id] = data
    }
}
```

Variants: `withThrowingTaskGroup` (if tasks can fail), `withDiscardingTaskGroup` (fire-and-forget).

## .task { } Modifier

Loads data on appear, auto-cancels on disappear:

```swift
List(viewModel.items) { item in ItemRow(item: item) }
    .task { await viewModel.load() }
```

## .task(id:) — Re-load on Value Change

```swift
.task(id: selectedID) { await viewModel.load(id: selectedID) }
```

**Always prefer `.task(id:)` over manual `onChange` + Task cancel.**

## Task Cancellation

Use `try Task.checkCancellation()` (throws) or `Task.isCancelled` (bool) in long-running loops.

## Structured vs Unstructured

| | Structured (.task, TaskGroup) | Unstructured (Task { }) |
|---|---|---|
| Cancellation | Automatic | Manual |
| Lifetime | Tied to scope | Independent |
| Use when | Default choice | Button taps, fire-and-forget |

## Patterns to Avoid

- `onChange` + manual Task cancel → use `.task(id:)` instead
- `onAppear { Task { } }` → use `.task { }` instead
- `Task.detached` without clear reason → usually `@concurrent` is better
