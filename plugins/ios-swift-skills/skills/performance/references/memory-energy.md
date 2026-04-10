# Memory, Launch, and Energy Diagnostics

## Memory Profiling

### Tools

| Tool | How | Use When |
|------|-----|----------|
| **Leaks** instrument | Cmd+I → Leaks template | Suspect retain cycles |
| **Memory Graph** | Debug → Debug Memory Graph (during session) | Find who retains what |
| **Allocations** | Cmd+I → Allocations, "Mark Generation" before/after action | Memory grows over time |

### Common Leak Patterns

- **Closures**: Missing `[weak self]` in escaping closures
- **Delegates**: `var delegate` instead of `weak var delegate`
- **Timers**: `Timer.scheduledTimer` holding strong reference to target
- **NotificationCenter**: Observer not removed (pre-iOS 15 `addObserver` pattern)

### autoreleasepool

Use in tight loops creating ObjC objects (images, Core Graphics):
```swift
for imageData in largeDataSet {
    autoreleasepool {
        let image = UIImage(data: imageData)
        processImage(image)
    }
}
```

## Launch Optimization

Profile with **App Launch** template. Phases: pre-main (dylib loading) + post-main (through first frame).

| Bottleneck | Fix |
|-----------|-----|
| Heavy `App.init()` | Defer non-essential setup with `.task { }` |
| Synchronous network at launch | Make async, show placeholder |
| Large asset loading | Load lazily, use thumbnails |
| Many dynamic frameworks | Prefer static linking |

## Energy Diagnostics

Profile with **Energy Log** template.

| Issue | Fix |
|-------|-----|
| Location always `.best` accuracy | Match accuracy to actual need |
| Timers without tolerance | Add `.tolerance` to allow coalescing |
| Frequent network requests | Batch requests, use background refresh |
| No thermal state handling | Monitor `ProcessInfo.thermalState` and reduce work |

## Production Monitoring

Use **MetricKit** (`MXMetricManagerSubscriber`) to collect launch time, hang rate, peak memory, and diagnostic payloads from real users.

## Xcode Diagnostics (Scheme → Run → Diagnostics)

| Setting | Catches |
|---------|---------|
| Main Thread Checker | UI work off main thread |
| Thread Sanitizer | Data races |
| Address Sanitizer | Buffer overflows, use-after-free |
| Zombie Objects | Messages to deallocated objects |
