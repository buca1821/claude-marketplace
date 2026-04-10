# List and ForEach Patterns

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## ForEach Identity and Stability

```swift
// GOOD — stable Identifiable conformance
ForEach(items) { item in
    ItemRow(item: item)
}

// GOOD — stable key path
ForEach(items, id: \.stableID) { item in
    ItemRow(item: item)
}

// BAD — indices change on insert/delete, causes bugs
ForEach(items.indices, id: \.self) { index in
    ItemRow(item: items[index])
}

// BAD — unstable ID, recreates views every update
ForEach(items, id: \.hashValue) { item in ... }
```

## Enumerated Sequences

When you need both index and element:

```swift
// GOOD — use element's stable ID
ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
    Text("\(index + 1). \(item.name)")
}
```

## Pull-to-Refresh

```swift
List {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
.refreshable {
    await viewModel.loadItems()
}
```

## Empty States with ContentUnavailableView (iOS 17+)

```swift
if items.isEmpty {
    ContentUnavailableView(
        String(localized: "empty.title"),
        systemImage: "tray",
        description: Text(String(localized: "empty.description"))
    )
} else {
    List(items) { item in
        ItemRow(item: item)
    }
}

// Search empty state
ContentUnavailableView.search(text: searchText)
```

## Swipe Actions

```swift
List {
    ForEach(items) { item in
        ItemRow(item: item)
            .swipeActions(edge: .trailing) {
                Button(role: .destructive) {
                    viewModel.delete(item)
                } label: {
                    Label(String(localized: "action.delete"), systemImage: "trash")
                }
            }
            .swipeActions(edge: .leading) {
                Button {
                    viewModel.toggleFavorite(item)
                } label: {
                    Label(String(localized: "action.favorite"), systemImage: "star")
                }
                .tint(.yellow)
            }
    }
}
```

## Custom List Styling

```swift
List {
    // ...
}
.listStyle(.plain)
.scrollContentBackground(.hidden) // iOS 16+ — remove default background
.background(Color.customBackground)
```

## Table (iOS 16+)

```swift
Table(items) {
    TableColumn(String(localized: "column.name"), value: \.name)
    TableColumn(String(localized: "column.date")) { item in
        Text(item.date, format: .dateTime)
    }
}

// Sortable
Table(items, sortOrder: $sortOrder) {
    TableColumn(String(localized: "column.name"), value: \.name)
}
.onChange(of: sortOrder) { _, newOrder in
    items.sort(using: newOrder)
}
```

## Checklist

- [ ] `ForEach` always uses stable identity (Identifiable or stable key path)
- [ ] Never use `.indices` for dynamic content
- [ ] Empty states handled with `ContentUnavailableView` (iOS 17+)
- [ ] Destructive swipe actions use `role: .destructive`
- [ ] Pull-to-refresh uses `async` function
