# Scroll Patterns

> Source: Adapted from [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) (MIT License)

## ScrollViewReader

```swift
ScrollViewReader { proxy in
    ScrollView {
        ForEach(messages) { message in
            MessageRow(message: message)
                .id(message.id)
        }
    }
    .onChange(of: messages.count) { _, _ in
        withAnimation {
            proxy.scrollTo(messages.last?.id, anchor: .bottom)
        }
    }
}
```

## Scroll Position (iOS 17+)

```swift
@State private var scrollPosition: ScrollPosition = .init(idType: Item.ID.self)

ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
    .scrollTargetLayout()
}
.scrollPosition($scrollPosition)

// Programmatic scroll
scrollPosition.scrollTo(id: targetItem.id)
```

## Header Visibility on Scroll

```swift
ScrollView {
    LazyVStack(pinnedViews: [.sectionHeaders]) {
        Section {
            ForEach(items) { item in
                ItemRow(item: item)
            }
        } header: {
            Text(String(localized: "section.header"))
                .font(.headline)
        }
    }
}
```

## Scroll Transitions (iOS 17+)

```swift
ScrollView(.horizontal) {
    LazyHStack(spacing: 16) {
        ForEach(items) { item in
            CardView(item: item)
                .scrollTransition { content, phase in
                    content
                        .opacity(phase.isIdentity ? 1 : 0.5)
                        .scaleEffect(phase.isIdentity ? 1 : 0.9)
                }
        }
    }
    .scrollTargetLayout()
}
.scrollTargetBehavior(.viewAligned) // Snap to cards
```

## Paging

```swift
ScrollView(.horizontal) {
    LazyHStack(spacing: 0) {
        ForEach(pages) { page in
            PageView(page: page)
                .containerRelativeFrame(.horizontal)
        }
    }
}
.scrollTargetBehavior(.paging)
```

## Content Margins

```swift
ScrollView {
    // content
}
.contentMargins(.horizontal, 16, for: .scrollContent)
.contentMargins(.vertical, 8, for: .scrollIndicators)
```

## Checklist

- [ ] `scrollTargetLayout()` applied when using scroll target behaviors
- [ ] `LazyVStack`/`LazyHStack` used for large scrollable content
- [ ] Programmatic scrolling uses `ScrollPosition` (iOS 17+) or `ScrollViewReader`
- [ ] Paging uses `.scrollTargetBehavior(.paging)` not `TabView` with page style
