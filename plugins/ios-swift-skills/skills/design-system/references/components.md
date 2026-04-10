# Design System Components

## Component Architecture

Components follow Atomic Design principles:

```
Atoms (Button, Icon, Label, Badge)
    ↓
Molecules (SearchBar, CardHeader, MetricDisplay)
    ↓
Organisms (Card, Form, NavigationBar)
    ↓
Templates (ScreenLayout, ListLayout)
```

## Building a Component

Every component must:
1. Accept content via parameters or `@ViewBuilder`
2. Read tokens from Environment (never hardcode)
3. Support Dark Mode (via semantic colors)
4. Support Dynamic Type (via system fonts or `@ScaledMetric`)
5. Include accessibility labels
6. Have previews for all states

## Example: Primary Button

```swift
struct PrimaryButton: View {
    let title: String
    let action: () -> Void
    let isLoading: Bool

    @Environment(\.colorPalette) private var colors
    @Environment(\.isEnabled) private var isEnabled

    init(
        _ title: String,
        isLoading: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.isLoading = isLoading
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            Group {
                if isLoading {
                    ProgressView()
                        .tint(colors.onPrimary)
                } else {
                    Text(title)
                }
            }
            .frame(maxWidth: .infinity)
            .frame(minHeight: 44) // Tap target
            .font(.labelLarge) // From typography scale
        }
        .buttonStyle(.borderedProminent)
        .tint(colors.primary)
        .disabled(isLoading)
    }
}
```

## Example: Card Container

```swift
struct DSCard<Content: View>: View {
    let content: Content
    @Environment(\.colorPalette) private var colors

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding(Spacing.lg)
            .background(colors.surface)
            .clipShape(.rect(cornerRadius: Radius.md))
            .elevation(Elevation.low)
    }
}
```

## Example: Badge

```swift
struct DSBadge: View {
    let text: String
    let style: BadgeStyle

    @Environment(\.colorPalette) private var colors

    enum BadgeStyle {
        case info, success, warning, error
    }

    var body: some View {
        Text(text)
            .font(.labelSmall)
            .padding(.horizontal, Spacing.sm)
            .padding(.vertical, Spacing.xxs)
            .foregroundStyle(foregroundColor)
            .background(backgroundColor)
            .clipShape(.capsule)
    }

    private var backgroundColor: Color {
        switch style {
        case .info: colors.primary.opacity(0.15)
        case .success: colors.success.opacity(0.15)
        case .warning: colors.warning.opacity(0.15)
        case .error: colors.error.opacity(0.15)
        }
    }

    private var foregroundColor: Color {
        switch style {
        case .info: colors.primary
        case .success: colors.success
        case .warning: colors.warning
        case .error: colors.error
        }
    }
}
```

## ViewModifier Components

For styling patterns that apply to any view:

```swift
struct CardModifier: ViewModifier {
    @Environment(\.colorPalette) private var colors

    func body(content: Content) -> some View {
        content
            .padding(Spacing.lg)
            .background(colors.surface)
            .clipShape(.rect(cornerRadius: Radius.md))
            .elevation(Elevation.low)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}

// Usage
VStack { ... }
    .cardStyle()
```

## Naming Convention

| Prefix | Type | Example |
|--------|------|---------|
| `DS` | Design System component | `DSCard`, `DSBadge`, `DSTextField` |
| No prefix | App-specific view | `WorkoutCard`, `ProfileHeader` |
| `*Modifier` | ViewModifier | `CardModifier`, `SectionModifier` |
| `*Style` | ButtonStyle/etc. | `PrimaryButtonStyle` |

Use `DS` prefix for design system components to distinguish them from app views.

## Component Composition

Build complex components from simpler ones:

```swift
struct DSMetricCard: View {
    let title: String
    let value: String
    let icon: String
    let trend: Trend?

    @Environment(\.colorPalette) private var colors

    var body: some View {
        DSCard {
            HStack {
                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(title)
                        .font(.labelMedium)
                        .foregroundStyle(colors.onSurfaceVariant)
                    Text(value)
                        .font(.headlineLarge)
                        .foregroundStyle(colors.onSurface)
                }
                Spacer()
                Image(systemName: icon)
                    .font(.title)
                    .foregroundStyle(colors.primary)
            }
        }
    }
}
```

## Rules

- Components ALWAYS read tokens from Environment
- Components NEVER import specific themes — they're theme-agnostic
- Use `DS` prefix for design system components
- Minimum 44pt tap targets for interactive elements
- `@ViewBuilder` for content slots, closures for actions
