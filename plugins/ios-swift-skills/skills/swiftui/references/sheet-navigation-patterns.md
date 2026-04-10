# Sheet and Navigation Patterns

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## Sheet Patterns

### Item-Driven Sheets (Preferred)

```swift
@State private var selectedItem: Item?

.sheet(item: $selectedItem) { item in
    DetailView(item: item)
}
```

### Enum-Based Multiple Sheets

```swift
enum SheetType: Identifiable {
    case edit(Item)
    case create
    case settings

    var id: String {
        switch self {
        case .edit(let item): "edit-\(item.id)"
        case .create: "create"
        case .settings: "settings"
        }
    }
}

@State private var activeSheet: SheetType?

.sheet(item: $activeSheet) { sheet in
    switch sheet {
    case .edit(let item): EditView(item: item)
    case .create: CreateView()
    case .settings: SettingsView()
    }
}
```

### Sheets Own Dismiss Actions

```swift
struct EditView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            Form { /* ... */ }
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button(String(localized: "action.cancel")) { dismiss() }
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        Button(String(localized: "action.save")) {
                            save()
                            dismiss()
                        }
                    }
                }
        }
    }
}
```

## NavigationStack (Type-Safe)

```swift
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationDestination(for: Item.self) { item in
        DetailView(item: item)
    }
    .navigationDestination(for: Category.self) { category in
        CategoryView(category: category)
    }
}

// Programmatic navigation
path.append(someItem)
path.removeLast()    // Pop
path = NavigationPath() // Pop to root
```

## NavigationSplitView

```swift
NavigationSplitView {
    List(categories, selection: $selectedCategory) { category in
        Label(category.name, systemImage: category.icon)
    }
} content: {
    if let category = selectedCategory {
        List(category.items, selection: $selectedItem) { item in
            ItemRow(item: item)
        }
    }
} detail: {
    if let item = selectedItem {
        DetailView(item: item)
    } else {
        ContentUnavailableView(
            String(localized: "detail.empty.title"),
            systemImage: "sidebar.left"
        )
    }
}
```

## Inspector (iOS 17+)

```swift
.inspector(isPresented: $showInspector) {
    InspectorView(item: selectedItem)
        .inspectorColumnWidth(min: 200, ideal: 300, max: 400)
}
```

## Presentation Modifiers

```swift
.sheet(item: $item) { item in
    DetailView(item: item)
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
        .presentationCornerRadius(20)
        .presentationBackground(.regularMaterial)
        .interactiveDismissDisabled(hasUnsavedChanges)
}
```

## Checklist

- [ ] Item-driven `.sheet(item:)` preferred over `.sheet(isPresented:)`
- [ ] Sheets wrap content in `NavigationStack` for toolbar
- [ ] `NavigationLink(value:)` + `.navigationDestination(for:)` for type-safe nav
- [ ] Multi-column uses `NavigationSplitView`
- [ ] Enum-based sheet selection for multiple sheet types
