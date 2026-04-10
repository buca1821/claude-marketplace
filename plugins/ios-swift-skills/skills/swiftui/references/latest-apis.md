# Deprecated → Modern API Quick Lookup

> Read this file at the start of every SwiftUI task.

## Always Use (iOS 15+)

| Deprecated | Recommended | Notes |
|-----------|-------------|-------|
| `.foregroundColor(_:)` | `.foregroundStyle(_:)` | Accepts `ShapeStyle` |
| `.cornerRadius(_:)` | `.clipShape(.rect(cornerRadius:))` | Or `UnevenRoundedRectangle` |
| `NavigationView` | `NavigationStack` / `NavigationSplitView` | Column behavior built in |
| `.navigationBarTitle(_:)` | `.navigationTitle(_:)` | — |
| `.navigationBarItems(...)` | `.toolbar { ... }` | — |
| `.navigationBarHidden(_:)` | `.toolbarVisibility(.hidden, for: .navigationBar)` | iOS 16+ |
| `.accentColor(_:)` | `.tint(_:)` | — |
| `.overlay(alignment:) { ... }` | `.overlay(content:)` form | Use trailing-closure form |
| `.background(alignment:) { ... }` | `.background(content:)` form | Use trailing-closure form |
| `GeometryReader` (for sizing) | `containerRelativeFrame(_:)` | iOS 17+ preferred |

## When Targeting iOS 16+

| Deprecated | Recommended | Notes |
|-----------|-------------|-------|
| `List { ForEach }` with `onDelete` | `List` with `.swipeActions` | More flexible |
| `.sheet(isPresented:)` with manual dismiss | `.sheet(item:)` with `@Binding` item | Cleaner lifecycle |
| `@AppStorage` for complex types | `@AppStorage` with `RawRepresentable` | Conform enums to `RawRepresentable` |
| `NavigationLink(destination:)` | `NavigationLink(value:)` + `.navigationDestination(for:)` | Type-safe |

## When Targeting iOS 17+

| Deprecated | Recommended | Notes |
|-----------|-------------|-------|
| `ObservableObject` + `@Published` | `@Observable` macro | Automatic dependency tracking |
| `@StateObject` | `@State` (with `@Observable`) | — |
| `@ObservedObject` | Direct property (with `@Observable`) | Use `@Bindable` for bindings |
| `@EnvironmentObject` | `@Environment` (with `@Observable`) | — |
| `.onChange(of:) { oldValue, newValue in }` | `.onChange(of:) { old, new in }` (two-param) | One-param deprecated |
| `.animation(_:)` (no value) | `.animation(_:value:)` | Always pass trigger value |
| `#if DEBUG` + `PreviewProvider` | `#Preview` macro | Simpler |
| `withAnimation { }` | `withAnimation(_:completionCriteria:_:completion:)` | Completion support |
| `.contentTransition(.identity)` | `.contentTransition(.numericText())` | For changing numbers |
| `.scrollPosition(id:)` | `.scrollPosition($position)` | iOS 18+ preferred |

## When Targeting iOS 18+

| Deprecated | Recommended | Notes |
|-----------|-------------|-------|
| `TabView { ... .tabItem { } }` | `TabView { Tab("...", image:) { } }` | New `Tab` type |
| `@Entry` macro in `EnvironmentValues` | Define custom environment keys with `@Entry` | Reduces boilerplate |
| `.sheet` for side content | `.inspector(isPresented:)` | Trailing panel |

## When Targeting iOS 26+

| Pattern | Modern API | Notes |
|---------|-----------|-------|
| Custom glass effects | `.glassEffect()` | See `liquid-glass.md` |
| Tab bar customization | Automatic Liquid Glass tabs | System-managed |
| SF Symbol animations | `.symbolEffect(.wiggle)` | Extended effects |
| Matched geometry | `.matchedGeometryEffect` + `.navigationTransition(.zoom)` | Hero transitions |
| WebView | `WebView(url:)` | Native SwiftUI (no WKWebView wrapping) |
