# macOS Window Styling

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Toolbar Styles

```swift
WindowGroup {
    ContentView()
}
.windowToolbarStyle(.unified)        // Compact, title in toolbar
// .windowToolbarStyle(.unifiedCompact) // Even more compact
// .windowToolbarStyle(.expanded)       // Separate title bar
```

## Window Sizing

```swift
WindowGroup {
    ContentView()
}
.defaultSize(width: 800, height: 600)
.defaultPosition(.center)
.windowResizability(.contentSize)       // Fit to content
// .windowResizability(.contentMinSize)  // Minimum = content size
// .windowResizability(.automatic)       // System default
```

## Window Style

```swift
WindowGroup {
    ContentView()
}
.windowStyle(.hiddenTitleBar) // Borderless look
```

## Navigation Layout

```swift
NavigationSplitView(columnVisibility: $columnVisibility) {
    Sidebar()
        .navigationSplitViewColumnWidth(min: 200, ideal: 250, max: 300)
} content: {
    ContentList()
        .navigationSplitViewColumnWidth(min: 300, ideal: 400)
} detail: {
    DetailView()
}
.navigationSplitViewStyle(.balanced)
```

## Inspector (macOS 14+)

```swift
ContentView()
    .inspector(isPresented: $showInspector) {
        InspectorView()
            .inspectorColumnWidth(min: 200, ideal: 300, max: 400)
    }
```

## MenuBarExtra Styles

```swift
// Rich window-style menu bar extra
MenuBarExtra("Status", systemImage: "circle.fill") {
    RichMenuView()
}
.menuBarExtraStyle(.window)

// Simple menu-style
MenuBarExtra("Quick", systemImage: "bolt") {
    Button("Action") { }
    Divider()
    Button("Quit") { NSApp.terminate(nil) }
}
.menuBarExtraStyle(.menu)
```

## Best Practices

- Use `.unified` toolbar for most apps
- Set sensible `defaultSize` — don't rely on auto-sizing
- Provide `.windowResizability(.contentMinSize)` to prevent too-small windows
- Use `Inspector` for contextual panels instead of custom split views
