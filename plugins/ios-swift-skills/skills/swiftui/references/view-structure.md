# View Structure

## Principles

- Views should be small, focused, and context-agnostic
- Extract subviews when body exceeds ~40 lines or a logical group emerges
- Prefer modifiers over conditional views to preserve view identity
- Use `@ViewBuilder` functions only for simple conditional logic — extract to subviews for complex cases

## Prefer Modifiers Over Conditional Views

```swift
// BAD — destroys identity, loses state and animations
if isHighlighted {
    Text(title).bold().foregroundStyle(.yellow)
} else {
    Text(title)
}

// GOOD — preserves identity
Text(title)
    .bold(isHighlighted)
    .foregroundStyle(isHighlighted ? .yellow : .primary)
```

## Extract Subviews, Not Computed Properties

```swift
// BAD — computed property, not a view; no identity or lifecycle
var header: some View {
    HStack { ... }
}

// GOOD — separate struct with its own identity
struct HeaderView: View {
    let title: String
    var body: some View {
        HStack { ... }
    }
}
```

## When @ViewBuilder Functions Are Acceptable

Short, conditional logic that doesn't warrant a full struct:

```swift
@ViewBuilder
private func badge(for status: Status) -> some View {
    switch status {
    case .active: Image(systemName: "checkmark.circle.fill")
    case .inactive: Image(systemName: "xmark.circle")
    }
}
```

## Container View Pattern

```swift
struct CardContainer<Content: View>: View {
    let content: Content
    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }
    var body: some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(.rect(cornerRadius: 12))
    }
}
```

## ZStack vs overlay/background

- Use `overlay` / `background` when layering decorations on a primary view
- Use `ZStack` when views are peers with no clear primary

```swift
// GOOD — icon is decoration on the image
image
    .overlay(alignment: .bottomTrailing) { badge }

// GOOD — peers
ZStack {
    mapView
    controlPanel
}
```

## Compositing Group Before Clipping

Apply visual effects to a group, then clip:

```swift
HStack { ... }
    .compositingGroup()
    .shadow(radius: 4)
    .clipShape(.rect(cornerRadius: 12))
```

## Reusable Styling with ViewModifier

```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(.rect(cornerRadius: 12))
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}
```

## Skeleton Loading with Redacted Views

```swift
VStack {
    Text("Placeholder title")
    Text("Longer placeholder description text")
}
.redacted(reason: viewModel.isLoading ? .placeholder : [])
```

## UIViewRepresentable Essentials

```swift
struct WrappedUIView: UIViewRepresentable {
    func makeUIView(context: Context) -> UIViewType {
        // Create and configure once
    }
    func updateUIView(_ uiView: UIViewType, context: Context) {
        // Update when SwiftUI state changes — keep lightweight
    }
    // Use Coordinator for delegates
}
```

## Checklist

- [ ] No view body exceeds ~40 lines
- [ ] Subviews are separate structs, not computed properties
- [ ] Modifiers preferred over conditional view swaps
- [ ] `@ViewBuilder` used only for short conditional logic
- [ ] Container views use generic `@ViewBuilder` content
- [ ] `overlay`/`background` for decoration, `ZStack` for peers
