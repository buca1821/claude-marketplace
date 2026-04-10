# macOS Views

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Quick Lookup

| Component | macOS | iOS Equivalent |
|-----------|-------|----------------|
| `HSplitView` | Side-by-side panes | `NavigationSplitView` |
| `Table` | Multi-column sortable | `List` |
| `PasteButton` | Paste from clipboard | Manual pasteboard |
| `CopyButton` | Copy to clipboard (macOS 15+) | Manual pasteboard |
| `ShareLink` | Share sheet | Same |

## Table (macOS)

Tables on macOS get full column headers, sorting, and selection:

```swift
@State private var selection = Set<Item.ID>()
@State private var sortOrder = [KeyPathComparator(\Item.name)]

Table(items, selection: $selection, sortOrder: $sortOrder) {
    TableColumn("Name", value: \.name)
    TableColumn("Date") { item in
        Text(item.date, format: .dateTime)
    }
    TableColumn("Size") { item in
        Text(item.size, format: .byteCount(style: .file))
    }
}
.onChange(of: sortOrder) { _, newOrder in
    items.sort(using: newOrder)
}
```

## File Operations

```swift
// Import
.fileImporter(
    isPresented: $showImporter,
    allowedContentTypes: [.json, .plainText]
) { result in
    // handle result
}

// Export
.fileExporter(
    isPresented: $showExporter,
    document: myDocument,
    contentType: .json,
    defaultFilename: "export.json"
) { result in
    // handle result
}

// Drag and Drop
.dropDestination(for: URL.self) { urls, location in
    handleDrop(urls)
    return true
}
```

## AppKit Interop

```swift
struct WrappedNSView: NSViewRepresentable {
    func makeNSView(context: Context) -> NSTextField {
        let field = NSTextField()
        field.delegate = context.coordinator
        return field
    }

    func updateNSView(_ nsView: NSTextField, context: Context) {
        // Update when SwiftUI state changes
    }

    func makeCoordinator() -> Coordinator { Coordinator() }

    class Coordinator: NSObject, NSTextFieldDelegate { }
}
```

## Commands and Keyboard Shortcuts

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .commands {
            CommandGroup(after: .newItem) {
                Button("Import...") { importAction() }
                    .keyboardShortcut("i", modifiers: [.command, .shift])
            }
            CommandMenu("Tools") {
                Button("Run Analysis") { analyze() }
                    .keyboardShortcut("r", modifiers: .command)
            }
        }
    }
}
```

## Best Practices

- Use `Table` on macOS, fall back to `List` on iOS
- Provide keyboard shortcuts for common actions
- Use `NSViewRepresentable` only when SwiftUI doesn't have an equivalent
- Test with keyboard navigation (Tab, arrow keys)
