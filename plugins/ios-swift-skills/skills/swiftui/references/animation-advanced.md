# Advanced Animations

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Transactions

Override animation for specific state changes:

```swift
var transaction = Transaction(animation: .spring(duration: 0.5))
withTransaction(transaction) {
    isExpanded.toggle()
}
```

## Phase Animations (iOS 17+)

Cycle through a sequence of phases:

```swift
PhaseAnimator([false, true]) { phase in
    Image(systemName: "heart.fill")
        .scaleEffect(phase ? 1.2 : 1.0)
        .foregroundStyle(phase ? .red : .pink)
} animation: { phase in
    phase ? .spring(duration: 0.3) : .easeOut(duration: 0.5)
}
```

### Trigger-based Phase Animations

```swift
PhaseAnimator([0, 1, 2], trigger: triggerValue) { phase in
    content
        .offset(y: phase == 1 ? -20 : 0)
        .scaleEffect(phase == 2 ? 1.2 : 1.0)
}
```

## Keyframe Animations (iOS 17+)

Fine-grained multi-property animation with precise timing:

```swift
Text("Hello")
    .keyframeAnimator(initialValue: AnimationValues()) { content, value in
        content
            .scaleEffect(value.scale)
            .offset(y: value.verticalOffset)
    } keyframes: { _ in
        KeyframeTrack(\.scale) {
            SpringKeyframe(1.5, duration: 0.3)
            SpringKeyframe(1.0, duration: 0.2)
        }
        KeyframeTrack(\.verticalOffset) {
            LinearKeyframe(-20, duration: 0.2)
            SpringKeyframe(0, duration: 0.3)
        }
    }

struct AnimationValues {
    var scale: CGFloat = 1.0
    var verticalOffset: CGFloat = 0
}
```

## Animation Completion (iOS 17+)

```swift
withAnimation(.spring(duration: 0.5)) {
    isExpanded = true
} completion: {
    showContent = true
}
```

## Symbol Effects (iOS 17+)

```swift
Image(systemName: "heart.fill")
    .symbolEffect(.pulse, isActive: isAnimating)
    .symbolEffect(.bounce, value: bounceCount)

// iOS 26+ extended effects
Image(systemName: "bell.fill")
    .symbolEffect(.wiggle, value: notificationCount)
```

## @Animatable Macro (iOS 26+)

Simplifies `Animatable` conformance:

```swift
@Animatable
struct PulseEffect: ViewModifier {
    var progress: Double // Automatically animatable

    func body(content: Content) -> some View {
        content
            .scaleEffect(1 + progress * 0.2)
            .opacity(1 - progress * 0.3)
    }
}
```

## Checklist

- [ ] Phase animations used for multi-step sequences
- [ ] Keyframe animations used for precise multi-property timing
- [ ] `@Animatable` macro used instead of manual `animatableData` (iOS 26+)
- [ ] Animation completions used for sequenced state changes (iOS 17+)
- [ ] Symbol effects preferred over custom icon animations
