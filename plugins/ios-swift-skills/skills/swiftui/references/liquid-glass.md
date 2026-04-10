# Liquid Glass (iOS 26+)

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Overview

Liquid Glass is iOS 26's new material effect. Only adopt when explicitly requested — it requires `#available(iOS 26, *)` gating with fallbacks.

## Core API

```swift
if #available(iOS 26, *) {
    content
        .glassEffect(.regular)
}
```

### Glass Effect Styles

| Style | Use Case |
|-------|----------|
| `.regular` | Standard glass panel |
| `.clear` | Subtle, more transparent |

## GlassEffectContainer

Group glass elements to share a unified backdrop:

```swift
if #available(iOS 26, *) {
    GlassEffectContainer {
        HStack {
            Button("Action 1") { }
                .glassEffect(.regular)
            Button("Action 2") { }
                .glassEffect(.regular)
        }
    }
}
```

## Glass Button Styles

```swift
if #available(iOS 26, *) {
    Button("Save") { save() }
        .buttonStyle(.glass)

    // Bordered glass
    Button("Cancel") { cancel() }
        .buttonStyle(.borderedGlass)
}
```

## Morphing Transitions

Smooth transition between glass elements during navigation:

```swift
if #available(iOS 26, *) {
    NavigationLink(value: item) {
        ItemRow(item: item)
    }
    .navigationTransition(.zoom(sourceID: item.id, in: namespace))
}
```

## Modifier Order

Glass effect should be applied after sizing but before positioning:

```swift
content
    .frame(width: 200, height: 50)  // 1. Size
    .glassEffect(.regular)           // 2. Glass
    .padding()                       // 3. Position
```

## Fallback Strategy

```swift
struct AdaptiveCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        Group {
            if #available(iOS 26, *) {
                content.glassEffect(.regular)
            } else {
                content
                    .background(.regularMaterial)
                    .clipShape(.rect(cornerRadius: 12))
            }
        }
    }
}
```

## Tab Bar (Automatic)

iOS 26 automatically applies Liquid Glass to tab bars — no code changes needed. Custom tab bar appearances may conflict.

## Design Notes

- Liquid Glass works best on vibrant, image-rich backgrounds
- Avoid nesting glass effects (glass inside glass)
- Keep glass areas focused — not full-screen panels
- Test with both light and dark mode

## Checklist

- [ ] All Liquid Glass APIs gated with `#available(iOS 26, *)`
- [ ] Fallback provided using `.regularMaterial` or `.ultraThinMaterial`
- [ ] `GlassEffectContainer` used when grouping glass elements
- [ ] Modifier order: size → glass → position
- [ ] Not nesting glass inside glass
