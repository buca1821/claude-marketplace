# performance-audit

Audit SwiftUI performance for a specific view, feature, or the entire app.

## Input

Target scope: `$ARGUMENTS`

Examples:
- `WorkoutListView` — audit a specific view
- `scrolling` — audit scroll performance
- `launch` — audit app launch time
- `memory` — audit memory usage
- (empty) — full app audit

## Process

### 1. Load performance skill

Load the performance skill for the decision tree and profiling guidance.

Based on the target, the skill will provide the appropriate reference for:
- SwiftUI view debugging
- CLI profiling with xctrace
- Memory, energy, and launch diagnostics

### 2. Code-first review

Read the target files and check for known anti-patterns:

- [ ] Object creation in `body` (DateFormatter, NumberFormatter)
- [ ] Heavy computation in `body` (sorting, filtering)
- [ ] Large `ForEach` inside eager `VStack` (should be `LazyVStack`)
- [ ] Broad `@Observable` dependencies
- [ ] Unstable `.id()` values
- [ ] Images decoded on main thread
- [ ] Missing `[weak self]` in escaping closures

### 3. Report findings

For each issue found:

```
**[Priority]: [File.swift:line]** — [description]
// Current: [problematic code]
// Suggested: [fix]
// Impact: [what improves]
```

### 4. Suggest profiling (if needed)

If code review is inconclusive, guide the user to profile with Instruments:

1. Build for Release (Cmd+I)
2. Select template (SwiftUI, Time Profiler, Allocations, etc.)
3. Reproduce the problematic interaction
4. Capture and analyze

Or use CLI:
```bash
xcrun xctrace record --template 'Time Profiler' --time-limit 60s --output /tmp/YourApp.trace --attach $(pgrep -x YourApp)
```

### 5. Summary

Provide:
- Top issues ordered by impact
- Quick wins (easy fixes)
- Recommendations for deeper investigation
