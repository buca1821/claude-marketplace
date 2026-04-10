# macOS Scenes

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Quick Lookup

| Scene | Purpose |
|-------|---------|
| `WindowGroup` | Main app windows (multiple instances) |
| `Window` | Single-instance utility window |
| `Settings` | Preferences window (⌘,) |
| `MenuBarExtra` | Menu bar item |
| `DocumentGroup` | Document-based apps |
| `UtilityWindow` | Floating tool panels (iOS 26+/macOS) |

## Settings

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        Settings {
            SettingsView()
        }
    }
}
```

## MenuBarExtra

```swift
@main
struct MyApp: App {
    var body: some Scene {
        MenuBarExtra("Status", systemImage: "circle.fill") {
            MenuBarView()
        }
        .menuBarExtraStyle(.window) // Or .menu for simple menu
    }
}
```

## WindowGroup (macOS)

```swift
WindowGroup(id: "detail", for: Item.ID.self) { $itemID in
    if let itemID {
        DetailView(itemID: itemID)
    }
}

// Open from another view:
@Environment(\.openWindow) private var openWindow
Button("Open Detail") {
    openWindow(id: "detail", value: item.id)
}
```

## Window (Single Instance)

```swift
Window("Activity Monitor", id: "activity") {
    ActivityView()
}
.defaultSize(width: 400, height: 300)
.defaultPosition(.center)
```

## Platform Conditionals

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        #if os(macOS)
        Settings {
            SettingsView()
        }
        MenuBarExtra("Status", systemImage: "circle") {
            QuickMenu()
        }
        #endif
    }
}
```

## Best Practices

- Use `WindowGroup` for multi-instance, `Window` for single-instance
- Settings scene auto-wires ⌘, keyboard shortcut
- `MenuBarExtra` with `.window` style for rich UI, `.menu` for simple items
- Use `@Environment(\.openWindow)` / `@Environment(\.dismissWindow)` for programmatic control
