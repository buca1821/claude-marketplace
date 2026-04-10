# Preview Patterns

## Mandatory Previews

Every design system component must have these previews:

```swift
// 1. Default state
#Preview("Default") {
    DSBadge(text: "Active", style: .success)
}

// 2. Dark Mode
#Preview("Dark Mode") {
    DSBadge(text: "Active", style: .success)
        .preferredColorScheme(.dark)
}

// 3. Large Dynamic Type
#Preview("Large Text") {
    DSBadge(text: "Active", style: .success)
        .environment(\.dynamicTypeSize, .accessibility3)
}

// 4. All variants
#Preview("All Styles") {
    VStack(spacing: Spacing.md) {
        DSBadge(text: "Info", style: .info)
        DSBadge(text: "Success", style: .success)
        DSBadge(text: "Warning", style: .warning)
        DSBadge(text: "Error", style: .error)
    }
    .padding()
}

// 5. Edge cases
#Preview("Long Text") {
    DSBadge(text: "Very Long Badge Text That Might Overflow", style: .info)
        .frame(maxWidth: 200)
}
```

## Preview Container

Create a reusable container for consistent preview styling:

```swift
struct PreviewContainer<Content: View>: View {
    let title: String
    let content: Content

    init(_ title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.md) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
            content
        }
        .padding()
    }
}
```

## Multi-Theme Preview

```swift
#Preview("Themes") {
    HStack(spacing: Spacing.lg) {
        VStack {
            Text("Default").font(.caption)
            DSCard {
                Text("Content")
            }
        }
        .environment(\.colorPalette, .default)

        VStack {
            Text("Ocean").font(.caption)
            DSCard {
                Text("Content")
            }
        }
        .environment(\.colorPalette, .ocean)
    }
    .padding()
}
```

## Interactive Previews

```swift
#Preview("Interactive") {
    @Previewable @State var isLoading = false

    VStack(spacing: Spacing.lg) {
        PrimaryButton("Submit", isLoading: isLoading) {
            isLoading = true
        }
        Button("Reset") { isLoading = false }
    }
    .padding()
}
```

## Color Palette Preview

```swift
#Preview("Color Palette") {
    let colors = ColorPalette.default

    ScrollView {
        LazyVGrid(columns: [.init(), .init()], spacing: Spacing.sm) {
            ColorSwatch("Primary", color: colors.primary)
            ColorSwatch("Secondary", color: colors.secondary)
            ColorSwatch("Background", color: colors.background)
            ColorSwatch("Surface", color: colors.surface)
            ColorSwatch("Error", color: colors.error)
            ColorSwatch("Warning", color: colors.warning)
            ColorSwatch("Success", color: colors.success)
        }
        .padding()
    }
}

private struct ColorSwatch: View {
    let name: String
    let color: Color

    init(_ name: String, color: Color) {
        self.name = name
        self.color = color
    }

    var body: some View {
        VStack {
            RoundedRectangle(cornerRadius: Radius.sm)
                .fill(color)
                .frame(height: 60)
            Text(name).font(.caption)
        }
    }
}
```

## Typography Preview

```swift
#Preview("Typography Scale") {
    VStack(alignment: .leading, spacing: Spacing.sm) {
        Text("Display Large").font(.system(size: 34, weight: .bold))
        Text("Headline Large").font(.system(size: 22, weight: .semibold))
        Text("Body Large").font(.system(size: 17))
        Text("Body Medium").font(.system(size: 15))
        Text("Label Medium").font(.system(size: 13, weight: .medium))
        Text("Label Small").font(.system(size: 11, weight: .medium))
    }
    .padding()
}
```

## Spacing Preview

```swift
#Preview("Spacing Scale") {
    VStack(alignment: .leading, spacing: Spacing.sm) {
        SpacingRow("xxs", value: Spacing.xxs)
        SpacingRow("xs", value: Spacing.xs)
        SpacingRow("sm", value: Spacing.sm)
        SpacingRow("md", value: Spacing.md)
        SpacingRow("lg", value: Spacing.lg)
        SpacingRow("xl", value: Spacing.xl)
        SpacingRow("xxl", value: Spacing.xxl)
    }
    .padding()
}

private struct SpacingRow: View {
    let name: String
    let value: CGFloat

    init(_ name: String, value: CGFloat) {
        self.name = name
        self.value = value
    }

    var body: some View {
        HStack {
            Text("\(name) (\(Int(value))pt)")
                .font(.caption)
                .frame(width: 100, alignment: .leading)
            Rectangle()
                .fill(.blue)
                .frame(width: value, height: 20)
        }
    }
}
```

## Rules

- Every component has at least 4 previews: default, dark mode, large text, all variants
- Use `@Previewable @State` for interactive previews
- Include edge cases: long text, empty content, loading states
- Color/typography/spacing token previews live alongside token definitions
- Previews are documentation — name them clearly
