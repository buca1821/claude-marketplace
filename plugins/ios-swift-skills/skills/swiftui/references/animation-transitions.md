# Animation Transitions

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Property Animations vs Transitions

- **Property animations**: animate changes to existing views (opacity, scale, offset)
- **Transitions**: animate views being inserted or removed from the hierarchy

## Basic Transitions

```swift
if showDetail {
    DetailView()
        .transition(.slide)
}
```

Built-in transitions: `.opacity`, `.slide`, `.scale`, `.move(edge:)`, `.push(from:)`

## Asymmetric Transitions

Different animations for insert and removal:

```swift
.transition(.asymmetric(
    insertion: .move(edge: .trailing).combined(with: .opacity),
    removal: .move(edge: .leading).combined(with: .opacity)
))
```

## Combining Transitions

```swift
.transition(.scale.combined(with: .opacity))
```

## Custom Transitions (iOS 17+)

```swift
struct RotateTransition: Transition {
    func body(content: Content, phase: TransitionPhase) -> some View {
        content
            .rotationEffect(.degrees(phase.isIdentity ? 0 : 90))
            .opacity(phase.isIdentity ? 1 : 0)
    }
}

// Usage
.transition(RotateTransition())
```

## Identity and Transitions

Transitions only fire when a view's **identity** changes (inserted/removed). Conditional content with `if/else` creates different identities — use this intentionally:

```swift
// TRIGGERS transition — different views
if isActive {
    ActiveView().transition(.slide)
} else {
    InactiveView().transition(.slide)
}

// NO transition — same view, different modifier
ActiveView()
    .opacity(isActive ? 1 : 0.5) // Animates as property change
```

## The Animatable Protocol

For animating custom values (paths, numbers):

```swift
struct AnimatableArc: Shape {
    var endAngle: Double
    var animatableData: Double {
        get { endAngle }
        set { endAngle = newValue }
    }
    func path(in rect: CGRect) -> Path { /* ... */ }
}
```

## matchedGeometryEffect

Hero transitions between views:

```swift
@Namespace private var animation

// Source
Image(item.image)
    .matchedGeometryEffect(id: item.id, in: animation)

// Destination (when navigated)
Image(item.image)
    .matchedGeometryEffect(id: item.id, in: animation)
```

## Checklist

- [ ] Transitions applied to views that are conditionally inserted/removed
- [ ] Asymmetric transitions used when insert ≠ removal animation
- [ ] `matchedGeometryEffect` IDs are stable and unique
- [ ] Custom transitions use `TransitionPhase` (iOS 17+)
