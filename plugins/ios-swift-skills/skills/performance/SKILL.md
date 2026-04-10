---
name: performance
description: Diagnose and fix performance issues in SwiftUI apps — profiling with Instruments/xctrace, SwiftUI view debugging, memory leaks, launch optimization, and energy diagnostics. Use when the app feels slow, has janky scrolling, high memory, slow launch, or battery drain.
---

# Performance Skill

## Operating Rules

- Profile on **real hardware**, not Simulator (Simulator uses host CPU/memory)
- Use **Release** build configuration (optimizations change behavior)
- Profile with **representative data** (empty databases hide real performance issues)
- Close other apps to reduce noise
- Present optimizations as suggestions backed by measurement, not premature fixes

## Decision Tree

```
What performance problem are you investigating?
│
├─ App hangs / stutters / dropped frames / slow UI
│  └─ Read references/swiftui-debugging.md
│
├─ High memory / leaks / OOM crashes / growing footprint
│  └─ Read references/memory-energy.md (Memory section)
│
├─ Slow app launch / time to first frame
│  └─ Read references/memory-energy.md (Launch section)
│
├─ Battery drain / thermal throttling / background energy
│  └─ Read references/memory-energy.md (Energy section)
│
├─ Need CLI-based profiling without opening Instruments
│  └─ Read references/profiling-cli.md
│
├─ General "app feels slow" (unknown cause)
│  └─ Start with references/swiftui-debugging.md, then profile
│
└─ Pre-release performance audit
   └─ Read ALL reference files, use Review Checklist below
```

## Quick Reference

| Problem | Tool | Key Metric | Reference |
|---------|------|------------|-----------|
| UI hangs > 250ms | Time Profiler + Hangs | Hang duration, main thread stack | swiftui-debugging.md |
| Excessive view updates | SwiftUI Instruments template | Body evaluation count | swiftui-debugging.md |
| High CPU usage | Time Profiler | CPU % by function | profiling-cli.md |
| Memory leak | Leaks + Memory Graph | Leaked bytes, retain cycle paths | memory-energy.md |
| Memory growth | Allocations | Live bytes, generation analysis | memory-energy.md |
| Slow launch | App Launch template | Time to first frame | memory-energy.md |
| Battery drain | Energy Log | Energy Impact score | memory-energy.md |

## Workflow

### 1. Code-First Review

Before profiling, review the code for known anti-patterns:
- Object creation in `body` (DateFormatter, NumberFormatter)
- Heavy computation in `body` (sorting, filtering)
- Large `ForEach` inside eager `VStack` (should be `LazyVStack`)
- Broad `@Observable` dependencies (pass only needed values)
- Unstable `.id()` values causing full view recreation
- Images decoded on main thread

### 2. Profile

If code review is inconclusive, guide profiling:
1. Build for Release (Product → Build For → Profiling, or Cmd+I)
2. Select appropriate Instruments template
3. Reproduce the exact problematic interaction
4. Capture timeline data
5. Identify hotspots in call tree

### 3. Apply Targeted Fixes

- Fix one issue at a time
- Re-profile after each fix to confirm improvement
- Add `os_signpost` markers for ongoing monitoring

### 4. Verify

Compare before/after:
- CPU usage
- Frame drops
- Memory peak
- Launch time

## Review Checklist

### Responsiveness
- [ ] No synchronous work on main thread > 100ms
- [ ] No file I/O or network calls on main thread
- [ ] Images decoded off main thread (use `.preparingThumbnail` or async decoding)
- [ ] `@MainActor` only on code that truly needs UI access

### Memory
- [ ] No retain cycles (check delegate patterns, closures with `self`)
- [ ] Large resources freed when not visible
- [ ] Collections don't grow unbounded (capped caches, pagination)
- [ ] `autoreleasepool` used in tight loops creating ObjC objects

### Launch Time
- [ ] No heavy work in `init()` of `@main App` struct
- [ ] Deferred non-essential initialization (analytics, prefetch)
- [ ] No synchronous network calls at launch

### Energy
- [ ] Background tasks use `BGProcessingTaskRequest` appropriately
- [ ] Location accuracy matches actual need (not always `.best`)
- [ ] Timers use `tolerance` to allow coalescing
- [ ] Network requests batched where possible

## Cross-References

- `swiftui-expert-skill` → `references/performance-patterns.md` for SwiftUI-specific optimization
- `.agent/rules/coding-patterns.md` → Data access patterns (e.g., HealthKit, CoreData, network API)
- `.agent/rules/testing-standards.md` → Coverage thresholds for performance-sensitive code
