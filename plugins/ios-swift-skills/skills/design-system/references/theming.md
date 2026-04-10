# Theming

## Theme Structure

A theme maps semantic tokens to specific values:

```swift
struct AppTheme {
    let colors: ColorPalette
    let typography: TypographyScale
    // Spacing, Radius, Motion are usually constant across themes
}
```

## Default Theme

```swift
extension ColorPalette {
    static let `default` = ColorPalette(
        // Surfaces
        background: Color("Background"),      // Asset Catalog, light/dark
        surface: Color("Surface"),
        surfaceVariant: Color("SurfaceVariant"),

        // Content
        onBackground: Color("OnBackground"),
        onSurface: Color("OnSurface"),
        onSurfaceVariant: Color("OnSurfaceVariant"),

        // Actions
        primary: Color("Primary"),
        onPrimary: Color("OnPrimary"),
        secondary: Color("Secondary"),
        onSecondary: Color("OnSecondary"),

        // Feedback
        error: Color("Error"),
        onError: Color("OnError"),
        warning: Color("Warning"),
        success: Color("Success"),

        // Borders
        outline: Color("Outline"),
        outlineVariant: Color("OutlineVariant")
    )
}
```

## Asset Catalog Setup

Each semantic color lives in the Asset Catalog with light and dark variants:

```
Assets.xcassets/
  Colors/
    Background.colorset/       — light: #FFFFFF, dark: #1C1C1E
    Surface.colorset/          — light: #F2F2F7, dark: #2C2C2E
    SurfaceVariant.colorset/   — light: #E5E5EA, dark: #3A3A3C
    OnBackground.colorset/     — light: #000000, dark: #FFFFFF
    OnSurface.colorset/        — light: #1C1C1E, dark: #F2F2F7
    Primary.colorset/          — light: #007AFF, dark: #0A84FF
    OnPrimary.colorset/        — light: #FFFFFF, dark: #FFFFFF
    Error.colorset/            — light: #FF3B30, dark: #FF453A
    ...
```

## Applying a Theme

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.colorPalette, .default)
        }
    }
}
```

## Multiple Themes

```swift
extension ColorPalette {
    static let ocean = ColorPalette(
        background: Color("OceanBackground"),
        surface: Color("OceanSurface"),
        // ...
    )

    static let forest = ColorPalette(
        background: Color("ForestBackground"),
        surface: Color("ForestSurface"),
        // ...
    )
}

// Theme picker
struct ThemeSettingsView: View {
    @AppStorage("selectedTheme") private var selectedTheme = "default"

    var body: some View {
        Picker(String(localized: "settings.theme"), selection: $selectedTheme) {
            Text(String(localized: "theme.default")).tag("default")
            Text(String(localized: "theme.ocean")).tag("ocean")
            Text(String(localized: "theme.forest")).tag("forest")
        }
    }
}
```

## High Contrast Theme

```swift
extension ColorPalette {
    static let highContrast = ColorPalette(
        background: .white,
        surface: Color(white: 0.95),
        onBackground: .black,
        onSurface: .black,
        primary: Color(red: 0, green: 0.4, blue: 0.9), // Higher contrast blue
        // ...
    )
}

// Automatic high contrast support via Asset Catalog:
// Each colorset has "High Contrast" variants in Appearances
```

## Per-Branch Theming

Apply different themes to different parts of the view hierarchy:

```swift
VStack {
    // Default theme
    HeaderView()

    // Custom theme for this section
    PromoSection()
        .environment(\.colorPalette, .ocean)
}
```

## Dark Mode

Dark Mode is handled automatically when:
1. Colors are defined in Asset Catalog with "Any, Dark" appearances
2. Components use semantic tokens via Environment
3. No hardcoded `Color.white` or `Color.black`

Test with:
```swift
#Preview("Dark Mode") {
    MyComponent()
        .preferredColorScheme(.dark)
}
```

## Rules

- Themes only change `ColorPalette` values — spacing, radius, motion stay constant
- Use Asset Catalog for colors to get automatic light/dark resolution
- High contrast support via Asset Catalog "High Contrast" appearance
- Theme applied via `.environment(\.colorPalette, theme)` at the root
- Components never reference a specific theme — they're always theme-agnostic
