# SwiftUI Performance Debugging

## Self._printChanges() and Self._logChanges()

Add to any view body to see what triggered re-evaluation:

```swift
var body: some View {
    #if DEBUG
    let _ = Self._logChanges()  // iOS 17+: logs to com.apple.SwiftUI subsystem
    #endif
    // ... view content
}
```

### Interpreting Output

| Output | Meaning |
|--------|---------|
| `@self` | The view's value itself changed (struct was recreated) |
| `@identity` | The view's persistent data was recycled (identity changed) |
| `_propertyName changed` | A specific `@State`/`@Observable` property triggered the update |

- `Self._printChanges()`: Prints to standard output (available iOS 15+)
- `Self._logChanges()`: Logs to `com.apple.SwiftUI` subsystem with `os_log` (iOS 17+)

## Top 5 SwiftUI Performance Mistakes

### 1. Large ForEach Inside Eager VStack

```swift
// BAD — creates ALL views upfront
ScrollView {
    VStack {
        ForEach(items) { item in
            ExpensiveRow(item: item)
        }
    }
}

// GOOD — creates views on demand
ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ExpensiveRow(item: item)
        }
    }
}
```

Use `LazyVStack`/`LazyHStack` for 50+ items. iOS 26+ nested scroll views automatically defer loading in lazy stacks.

> Source: "What's new in SwiftUI" (WWDC25, session 256)

### 2. AnyView Type Erasure

```swift
// BAD — defeats SwiftUI's diffing algorithm
func makeView() -> AnyView {
    if condition {
        return AnyView(ViewA())
    } else {
        return AnyView(ViewB())
    }
}

// GOOD — preserves type information
@ViewBuilder
func makeView() -> some View {
    if condition {
        ViewA()
    } else {
        ViewB()
    }
}
```

### 3. Creating Objects in Body

```swift
// BAD — allocates on every render
var body: some View {
    let formatter = DateFormatter()
    formatter.dateStyle = .long
    return Text(formatter.string(from: date))
}

// GOOD — static shared instance
private static let dateFormatter: DateFormatter = {
    let f = DateFormatter()
    f.dateStyle = .long
    return f
}()

var body: some View {
    Text(Self.dateFormatter.string(from: date))
}
```

### 4. Observing Entire Model When Only One Property Needed

```swift
// BAD — row re-evaluates when ANY property on model changes
struct ItemRow: View {
    @Environment(AppModel.self) private var model
    let item: Item
    var body: some View {
        Text(item.name).foregroundStyle(model.theme.primaryColor)
    }
}

// GOOD — narrow dependency
struct ItemRow: View {
    let item: Item
    let themeColor: Color
    var body: some View {
        Text(item.name).foregroundStyle(themeColor)
    }
}
```

> Source: "Optimize SwiftUI performance with Instruments" (WWDC25, session 306)

### 5. Unstable .id() Values

```swift
// BAD — UUID() generates new ID every render → full view recreation
ForEach(items) { item in
    Row(item: item)
        .id(UUID())  // Never do this
}

// GOOD — stable identifier from model
ForEach(items) { item in
    Row(item: item)
        .id(item.stableID)
}
```

Never use array indices, `UUID()`, or `Date()` as identity for dynamic content.

## Instruments SwiftUI Template

1. **Xcode → Product → Profile** (Cmd+I)
2. Choose **SwiftUI** template (includes View Body, View Properties, Core Animation Commits)
3. Record, reproduce the slow interaction, stop
4. **View Body** lane: which views had body evaluated and how often
5. **View Properties** lane: which properties changed
6. Look for views with high body evaluation counts relative to actual state changes

## os_signpost for Custom Measurement

```swift
import os

private let perfLog = OSLog(subsystem: Bundle.main.bundleIdentifier!, category: "Performance")

// Mark a point in time
os_signpost(.event, log: perfLog, name: "WorkoutList.body")

// Measure a range
let id = OSSignpostID(log: perfLog)
os_signpost(.begin, log: perfLog, name: "FetchWorkouts", signpostID: id)
let workouts = try await fetchWorkouts()
os_signpost(.end, log: perfLog, name: "FetchWorkouts", signpostID: id)
```

View in Instruments with the **os_signpost** instrument.

## Checklist

### View Identity
- [ ] No unstable `.id()` values (random, Date(), array index on mutable arrays)
- [ ] Conditional branches (`if`/`else`) do not cause unnecessary view destruction
- [ ] `ForEach` uses stable, unique identifiers from the model

### Body Re-evaluation
- [ ] Views observe only the properties they actually use
- [ ] `@Observable` classes preferred over `ObservableObject`
- [ ] Large views split into smaller subviews to narrow observation scope
- [ ] `Self._logChanges()` used to identify unexpected updates during development

### Lazy Loading
- [ ] Large collections use `LazyVStack` / `LazyHStack`
- [ ] No `.frame(maxHeight: .infinity)` on children inside lazy containers (defeats laziness)

### Common Pitfalls
- [ ] No `AnyView` type erasure (use `@ViewBuilder` or `Group`)
- [ ] No object allocation in `body`
- [ ] Expensive computations moved to ViewModel or `.task { }`
- [ ] Images use `AsyncImage` or `.resizable()` with proper sizing
