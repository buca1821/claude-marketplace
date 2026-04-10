# Accessibility Patterns

## Core Principle

Every interactive element must be usable with VoiceOver, Switch Control, and Voice Control. Use `Button` for all tappable elements — never bare `onTapGesture`.

## Dynamic Type and @ScaledMetric

```swift
// System fonts scale automatically
Text("Title").font(.headline)

// Custom sizes — use @ScaledMetric
@ScaledMetric(relativeTo: .body) private var iconSize: CGFloat = 24

Image(systemName: "star")
    .frame(width: iconSize, height: iconSize)
```

Always test with the largest accessibility text size.

## Accessibility Traits

```swift
// Announce as a button
Text("Delete")
    .accessibilityAddTraits(.isButton)

// Header for VoiceOver navigation
Text("Settings")
    .accessibilityAddTraits(.isHeader)

// Mark decorative images
Image("background")
    .accessibilityHidden(true)
```

## Decorative Images

```swift
// Informational — needs label
Image(systemName: "heart.fill")
    .accessibilityLabel(String(localized: "accessibility.favorites"))

// Decorative — hide from VoiceOver
Image("divider")
    .accessibilityHidden(true)
```

## Element Grouping

### Combine — merge children into single element
```swift
HStack {
    Image(systemName: "clock")
    Text("5 min ago")
}
.accessibilityElement(children: .combine) // Reads: "clock, 5 min ago"
```

### Ignore children — provide custom label
```swift
HStack {
    Image(systemName: "star.fill")
    Text("4.5")
    Text("(128 reviews)")
}
.accessibilityElement(children: .ignore)
.accessibilityLabel(String(localized: "accessibility.rating \("4.5") \("128")"))
```

### Contain — keep children separate but group
```swift
VStack {
    Text("Section Title").accessibilityAddTraits(.isHeader)
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
.accessibilityElement(children: .contain)
```

## Custom Adjustable Controls

```swift
struct RatingControl: View {
    @Binding var rating: Int

    var body: some View {
        HStack { /* stars */ }
            .accessibilityElement()
            .accessibilityLabel(String(localized: "accessibility.rating"))
            .accessibilityValue("\(rating) stars")
            .accessibilityAdjustableAction { direction in
                switch direction {
                case .increment: rating = min(rating + 1, 5)
                case .decrement: rating = max(rating - 1, 1)
                @unknown default: break
                }
            }
    }
}
```

## Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

.animation(reduceMotion ? nil : .spring(), value: isExpanded)
```

## Checklist

- [ ] All interactive elements use `Button` (not `onTapGesture`)
- [ ] Decorative images hidden with `.accessibilityHidden(true)`
- [ ] Informational images have `.accessibilityLabel`
- [ ] Complex groups use `.accessibilityElement(children:)`
- [ ] Custom controls support `.accessibilityAdjustableAction`
- [ ] Animations respect `accessibilityReduceMotion`
- [ ] Headers marked with `.isHeader` trait
- [ ] Tested with largest Dynamic Type size
