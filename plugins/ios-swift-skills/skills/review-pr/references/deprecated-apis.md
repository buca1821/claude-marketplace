# Deprecated SwiftUI APIs — Quick Lookup

Reference table for code reviews. Only flag these when found in **changed files**.

## Modifiers

| Deprecated | Replacement | Since |
|---|---|---|
| `.foregroundColor(_:)` | `.foregroundStyle(_:)` | iOS 15 |
| `.cornerRadius(_:)` | `.clipShape(.rect(cornerRadius:))` | iOS 13.0 (soft) |
| `.background(_:in:)` with `Color` | `.background(_:in:)` with `ShapeStyle` | iOS 15 |
| `.overlay(_:)` with `Color` | `.overlay { }` content builder | iOS 15 |
| `.animation(_:)` (no value) | `.animation(_:value:)` | iOS 15 |
| `.onChange(of:perform:)` (1 param) | `.onChange(of:) { oldValue, newValue in }` | iOS 17 |
| `.onAppear { async work }` | `.task { }` (auto-cancels) | iOS 15 |
| `.navigationBarTitle(_:)` | `.navigationTitle(_:)` | iOS 14 |
| `.navigationBarHidden(_:)` | `.toolbar(.hidden, for: .navigationBar)` | iOS 16 |
| `.navigationBarItems(trailing:)` | `.toolbar { ToolbarItem(placement:) { } }` | iOS 14 |
| `.navigationBarBackButtonHidden(_:)` | `.toolbar(.hidden, for: .navigationBar)` or `.navigationBarBackButtonHidden()` | iOS 16 |
| `.accentColor(_:)` | `.tint(_:)` | iOS 15 |
| `.ignoresSafeArea()` (no params) | `.ignoresSafeArea(.all)` | Clarity |

## Navigation

| Deprecated | Replacement | Since |
|---|---|---|
| `NavigationView` | `NavigationStack` / `NavigationSplitView` | iOS 16 |
| `NavigationLink(destination:)` | `NavigationLink(value:)` + `.navigationDestination(for:)` | iOS 16 |

## State Management

| Deprecated | Replacement | Since |
|---|---|---|
| `ObservableObject` + `@Published` | `@Observable` macro | iOS 17 |
| `@StateObject` | `@State` (with `@Observable` class) | iOS 17 |
| `@ObservedObject` | `@Bindable` or direct property | iOS 17 |
| `@EnvironmentObject` | `@Environment` (with `@Observable`) | iOS 17 |

## Previews

| Deprecated | Replacement | Since |
|---|---|---|
| `PreviewProvider` protocol | `#Preview` macro | iOS 17 |

## Lists & Containers

| Deprecated | Replacement | Since |
|---|---|---|
| `List { ForEach }` with manual delete | `.onDelete(perform:)` or `EditButton` | — |
| `Form` sections without `Section` | Wrap in explicit `Section` | — |

## Swift (not SwiftUI)

| Deprecated | Replacement | Since |
|---|---|---|
| `String(format: "%.2f", val)` | `Text(val, format: .number.precision(...))` | iOS 15 |
| `replacingOccurrences(of:with:)` | `replacing(_:with:)` | Swift 5.7 |
| `DispatchQueue.main.async` | `@MainActor` / `MainActor.run` / `Task { @MainActor in }` | Swift 5.5 |
| `Task.sleep(nanoseconds:)` | `Task.sleep(for: .seconds(N))` | Swift 5.7 |
| `Date()` | `Date.now` | Swift 5.7 |

## Animations

| Deprecated | Replacement | Since |
|---|---|---|
| Manual `animatableData` | `@Animatable` macro | iOS 26 |
| Sequential `withAnimation` + `DispatchQueue.asyncAfter` | `withAnimation { } completion: { }` | iOS 17 |
| `PhaseAnimator` manual implementation | `.phaseAnimator(values:)` | iOS 17 |
