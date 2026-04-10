# Layout Best Practices

## Relative Layout Over Constants

```swift
// BAD — fixed values break on different screen sizes
.frame(width: 320, height: 200)

// GOOD — relative sizing
.containerRelativeFrame(.horizontal) { length, _ in
    length * 0.9
}

// GOOD — flexible frames
.frame(maxWidth: .infinity)
.frame(minHeight: 44) // Tap target minimum
```

## Context-Agnostic Views

Views should not assume their container. Avoid hardcoded widths; let the parent constrain.

```swift
// BAD — assumes screen width
.frame(width: UIScreen.main.bounds.width - 32)

// GOOD — adapts to any container
.padding(.horizontal)
.frame(maxWidth: .infinity)
```

## Own Your Container

When a view needs specific layout, embed it in its own container rather than pushing layout rules outward.

```swift
// GOOD — the view defines its own layout needs
struct MetricCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.headline)
            Text(value).font(.largeTitle)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
```

## Full-Width Views

```swift
// Standard pattern for full-width content
.frame(maxWidth: .infinity, alignment: .leading)
```

## Layout Performance

- Avoid `GeometryReader` when `containerRelativeFrame` (iOS 17+) works
- `GeometryReader` proposes the full available space to its child — always constrain
- Prefer `Layout` protocol for complex custom layouts over manual geometry

## ViewThatFits

Pick the first child that fits the available space:

```swift
ViewThatFits {
    HStack { labelA; labelB; labelC } // First try horizontal
    VStack { labelA; labelB; labelC } // Fall back to vertical
}
```

## Grid (iOS 16+)

```swift
Grid(alignment: .leading, horizontalSpacing: 12, verticalSpacing: 8) {
    GridRow {
        Text("Label").gridColumnAlignment(.trailing)
        Text("Value")
    }
    GridRow {
        Text("Other")
        Text("123")
    }
}
```

## Action Handlers

Pass closures, not view model references, to keep subviews context-agnostic:

```swift
// GOOD — subview doesn't know about the view model
struct ActionButton: View {
    let title: String
    let action: () -> Void
    var body: some View {
        Button(title, action: action)
    }
}
```

## Checklist

- [ ] No hardcoded frame sizes tied to screen dimensions
- [ ] Views adapt to any container size
- [ ] `containerRelativeFrame` preferred over `GeometryReader` (iOS 17+)
- [ ] Minimum 44pt tap targets
- [ ] Action handlers use closures, not direct view model references
