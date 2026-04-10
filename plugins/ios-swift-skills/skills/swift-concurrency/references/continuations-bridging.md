# Bridging Legacy APIs to async/await

## withCheckedContinuation

Bridge a single callback to async:

```swift
func executeQuery(_ query: HKQuery) async -> [HKSample]? {
    await withCheckedContinuation { continuation in
        store.execute(query) { _, results, _ in
            continuation.resume(returning: results as? [HKSample])
        }
    }
}
```

### CRITICAL: Resume Exactly Once

- **Zero calls** → task hangs forever
- **Two calls** → runtime crash
- Always handle all callback paths (success AND error)
- Use `withChecked*` (not `withUnsafe*`) in development to catch violations

## withCheckedThrowingContinuation

For callbacks that can fail — resume with `.throwing` or `.returning`, never both.

## AsyncStream

Bridge delegate or repeated-callback patterns to an async sequence.

**Preferred**: `AsyncStream.makeStream(of:)` — returns `(stream, continuation)` pair.

| Legacy Pattern | Async Bridge |
|---------------|-------------|
| Single callback | `withCheckedContinuation` |
| Single callback + error | `withCheckedThrowingContinuation` |
| Delegate with repeated callbacks | `AsyncStream` |
| Delegate with errors | `AsyncThrowingStream` |
| NotificationCenter | `.notifications(named:)` (built-in, iOS 15+) |

## Gotchas

- **Retain the delegate/observer** — if deallocated, continuation may never resume
- **onTermination cleanup** — always stop queries/observers when stream terminates
- **Back-pressure** — use `.bufferingPolicy(.bufferingNewest(1))` for high-frequency updates
