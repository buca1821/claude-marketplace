# Design Tokens

## 3-Level Token Architecture

```
Primitive Tokens (raw values) — NEVER use directly in views
    ↓
Semantic Tokens (meaning) — USE in views and components
    ↓
Component Tokens (specific) — USE in component internals
```

### Why 3 levels?

- **Primitive**: `blue500`, `gray100` — raw palette. Changing these updates everything.
- **Semantic**: `primaryAction`, `surfaceBackground` — what the color *means*. Enables theming.
- **Component**: `buttonPrimaryBackground`, `cardBorder` — scoped to one component. Optional layer.

## Color Tokens

### Primitives (internal only)

```swift
// DesignSystem/Tokens/PrimitiveColors.swift
enum PrimitiveColor {
    static let blue500 = Color("Blue500")  // Asset Catalog
    static let blue600 = Color("Blue600")
    static let gray50 = Color("Gray50")
    static let gray100 = Color("Gray100")
    static let gray900 = Color("Gray900")
    // ... full palette in Asset Catalog with light/dark variants
}
```

### Semantic (public API)

```swift
// DesignSystem/Tokens/SemanticColors.swift
struct ColorPalette {
    // Surfaces
    let background: Color
    let surface: Color
    let surfaceVariant: Color

    // Content (text, icons on surfaces)
    let onBackground: Color
    let onSurface: Color
    let onSurfaceVariant: Color

    // Actions
    let primary: Color
    let onPrimary: Color
    let secondary: Color
    let onSecondary: Color

    // Feedback
    let error: Color
    let onError: Color
    let warning: Color
    let success: Color

    // Borders
    let outline: Color
    let outlineVariant: Color
}
```

### Accessing in views via Environment

```swift
// DesignSystem/Environment/ColorPaletteKey.swift
struct ColorPaletteKey: EnvironmentKey {
    static let defaultValue = ColorPalette.default
}

extension EnvironmentValues {
    var colorPalette: ColorPalette {
        get { self[ColorPaletteKey.self] }
        set { self[ColorPaletteKey.self] = newValue }
    }
}

// Usage in views
struct MyView: View {
    @Environment(\.colorPalette) private var colors

    var body: some View {
        Text("Hello")
            .foregroundStyle(colors.onBackground)
            .background(colors.background)
    }
}
```

## Typography Tokens

```swift
// DesignSystem/Tokens/Typography.swift
struct TypographyScale {
    // Display — hero content
    let displayLarge: Font   // 34pt bold
    let displayMedium: Font  // 28pt bold
    let displaySmall: Font   // 24pt bold

    // Headlines — section headers
    let headlineLarge: Font  // 22pt semibold
    let headlineMedium: Font // 20pt semibold
    let headlineSmall: Font  // 17pt semibold

    // Body — reading content
    let bodyLarge: Font      // 17pt regular
    let bodyMedium: Font     // 15pt regular
    let bodySmall: Font      // 13pt regular

    // Labels — UI elements
    let labelLarge: Font     // 15pt medium
    let labelMedium: Font    // 13pt medium
    let labelSmall: Font     // 11pt medium
}
```

All fonts should use `.system()` or custom fonts via `Font.custom()` — both scale with Dynamic Type automatically.

## Spacing Tokens (8pt Grid)

```swift
// DesignSystem/Tokens/Spacing.swift
enum Spacing {
    static let none: CGFloat = 0
    static let xxs: CGFloat = 2
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 12
    static let lg: CGFloat = 16
    static let xl: CGFloat = 24
    static let xxl: CGFloat = 32
    static let xxxl: CGFloat = 48
    static let xxxxl: CGFloat = 64
}

// Usage
.padding(.horizontal, Spacing.lg)
.spacing(Spacing.sm)
```

## Radius Tokens

```swift
enum Radius {
    static let none: CGFloat = 0
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 12
    static let lg: CGFloat = 16
    static let xl: CGFloat = 24
    static let full: CGFloat = 9999  // Capsule
}

// Usage
.clipShape(.rect(cornerRadius: Radius.md))
```

## Motion Tokens

```swift
enum Motion {
    static let quick = Animation.easeOut(duration: 0.15)
    static let normal = Animation.easeInOut(duration: 0.25)
    static let slow = Animation.easeInOut(duration: 0.4)
    static let spring = Animation.spring(duration: 0.3, bounce: 0.2)
    static let springBouncy = Animation.spring(duration: 0.5, bounce: 0.4)
}

// Respect Reduce Motion
extension Animation {
    static func adaptive(_ animation: Animation) -> Animation? {
        // Let SwiftUI handle this via .animation(_:value:)
        // and accessibilityReduceMotion environment
        animation
    }
}
```

## Elevation Tokens

```swift
enum Elevation {
    static let none = ShadowStyle(color: .clear, radius: 0, x: 0, y: 0)
    static let low = ShadowStyle(color: .black.opacity(0.08), radius: 2, x: 0, y: 1)
    static let medium = ShadowStyle(color: .black.opacity(0.12), radius: 8, x: 0, y: 4)
    static let high = ShadowStyle(color: .black.opacity(0.16), radius: 16, x: 0, y: 8)
}

struct ShadowStyle {
    let color: Color
    let radius: CGFloat
    let x: CGFloat
    let y: CGFloat
}

// ViewModifier for easy use
extension View {
    func elevation(_ style: ShadowStyle) -> some View {
        shadow(color: style.color, radius: style.radius, x: style.x, y: style.y)
    }
}
```

## Rules

- Primitive tokens live in Asset Catalogs (colors) and static enums (spacing, radius)
- Semantic tokens are structs injected via Environment
- Components reference semantic tokens, never primitives
- Spacing follows the 8pt grid — exceptions only for xxs (2pt) and xs (4pt)
- Typography uses system font scales that support Dynamic Type
