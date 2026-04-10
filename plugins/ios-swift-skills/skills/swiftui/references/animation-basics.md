# Animation Basics

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Implicit Animations

Applied via `.animation(_:value:)` — animate when value changes:

```swift
Circle()
    .scaleEffect(isExpanded ? 1.5 : 1.0)
    .animation(.spring(duration: 0.3), value: isExpanded)
```

**Always include the `value` parameter.** The parameterless `.animation(_:)` is deprecated.

## Explicit Animations

Wrap state changes in `withAnimation`:

```swift
withAnimation(.easeInOut(duration: 0.3)) {
    isExpanded.toggle()
}
```

## When to Use Which

| Scenario | Use |
|----------|-----|
| Single property reacts to state | Implicit `.animation(_:value:)` |
| Multiple properties change together | Explicit `withAnimation` |
| Different animations per property | Multiple implicit `.animation` modifiers |

## Timing Curves

| Curve | When |
|-------|------|
| `.easeInOut` | General-purpose, natural feel |
| `.spring()` | Interactive, bouncy feedback |
| `.spring(duration:bounce:)` | Controlled spring (iOS 17+) |
| `.linear` | Progress indicators, constant motion |
| `.easeOut` | Elements entering the screen |
| `.easeIn` | Elements leaving the screen |

## Selective Animation

Exclude properties from animation:

```swift
withAnimation(.spring()) {
    isExpanded.toggle()
}
// This won't animate:
Text(title)
    .animation(nil, value: isExpanded)
```

## Performance

- Animate transforms (scale, offset, rotation, opacity) — they're GPU-composited
- Avoid animating layout-triggering properties (frame size, padding) in tight loops
- Use `.drawingGroup()` for complex animated layer trees

## Disabling Animations

```swift
// Respect Reduce Motion
@Environment(\.accessibilityReduceMotion) private var reduceMotion

.animation(reduceMotion ? nil : .spring(), value: isExpanded)

// Or globally disable:
var transaction = Transaction(animation: nil)
transaction.disablesAnimations = true
withTransaction(transaction) { /* ... */ }
```

## Checklist

- [ ] `.animation(_:value:)` always has `value` parameter
- [ ] `withAnimation` used when multiple state changes animate together
- [ ] Reduce Motion respected via `accessibilityReduceMotion`
- [ ] Only transforms and opacity animated in performance-critical paths
