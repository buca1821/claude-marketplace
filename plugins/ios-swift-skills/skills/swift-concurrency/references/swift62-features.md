# Swift 6.2 Concurrency Features

## Default Actor Isolation (Main-Actor-by-Default)

Swift 6.2 with approachable concurrency keeps code single-threaded by default. All code runs on the main actor unless you explicitly opt out.

```swift
// In Swift 6.2, this class is implicitly @MainActor
final class StickerModel {
    let photoProcessor = PhotoProcessor()

    func extractSticker(_ item: PhotosPickerItem) async throws -> Sticker? {
        guard let data = try await item.loadTransferable(type: Data.self) else {
            return nil
        }
        return await photoProcessor.extractSticker(data: data)
    }
}
```

When default actor isolation is enabled, explicit `@MainActor` annotations are redundant on most types.

## @concurrent — Explicit Background Work

Mark async functions with `@concurrent` to run them on the concurrent thread pool:

```swift
nonisolated struct ImageProcessor {
    @concurrent
    func resize(_ image: UIImage, to size: CGSize) async -> UIImage {
        // Runs on background thread — safe for heavy work
        let renderer = UIGraphicsImageRenderer(size: size)
        return renderer.image { _ in
            image.draw(in: CGRect(origin: .zero, size: size))
        }
    }
}

// Caller adds await
let resized = await ImageProcessor().resize(original, to: targetSize)
```

**Key rule**: Only use `@concurrent` when you intentionally need background execution. Default (main actor) is correct for most code.

## Isolated Conformances

Conformances that need main-actor state are now supported:

```swift
protocol Exportable {
    func export() -> Data
}

// Isolated conformance — compiler ensures it's only used on the main actor
extension WorkoutDetailViewModel: @MainActor Exportable {
    func export() -> Data {
        // Can safely access @MainActor properties
        gpxEncoder.encode(workout)
    }
}
```

The compiler prevents passing this conformance to contexts that aren't on the main actor.

## Protecting Global/Static State

```swift
// Protect singletons with @MainActor
@MainActor
final class HealthStoreManager {
    static let shared = HealthStoreManager()
}

// Or use an actor for thread-safe shared state
actor WorkoutCache {
    private var storage: [String: AnyWorkout] = [:]

    func get(_ key: String) -> AnyWorkout? {
        storage[key]
    }

    func set(_ key: String, value: AnyWorkout) {
        storage[key] = value
    }
}
```

## Actor Patterns

### When to Use actor vs @MainActor

| Use | Pattern |
|-----|---------|
| UI state, ViewModels | `@MainActor` class |
| Shared mutable state (caches, stores) | `actor` |
| Pure computation, no shared state | `nonisolated struct` |
| Background processing | `nonisolated` + `@concurrent` |

### Actor Reentrancy

Actors are reentrant — state can change at any `await` point:

```swift
actor DataStore {
    var items: [Item] = []

    func refreshItems() async {
        let oldCount = items.count
        let newItems = await fetchFromNetwork()  // Suspension point!
        // WARNING: items.count may differ from oldCount here
        items = newItems
    }
}
```

**Fix**: Don't make assumptions about state after `await`. Re-check conditions.

## Sendable

Types that cross actor boundaries must be `Sendable`:

```swift
// Value types are implicitly Sendable
struct WorkoutRoutePoint: Sendable {
    let latitude: Double
    let longitude: Double
    let timestamp: Date
}

// Classes need explicit conformance + constraints
final class WorkoutExporter: Sendable {
    let encoder: GPXEncoder  // All stored properties must be let + Sendable
}
```

**Prefer value types (structs, enums)** for data crossing actor boundaries.

## Build Settings

Enable in Xcode → Swift Compiler → Concurrency:
- `SWIFT_STRICT_CONCURRENCY` = `complete`
- Enable approachable concurrency features (Swift 6.2+)

Or in Package.swift:
```swift
swiftSettings: [
    .swiftLanguageMode(.v6)
]
```

## Migration Checklist

1. Set Swift language version to 6.2 in build settings
2. Enable strict concurrency checking (`complete`)
3. Fix `@MainActor` isolation errors on UI-bound types
4. Add `Sendable` conformance to types crossing boundaries
5. Replace `DispatchQueue` patterns with async/await
6. Use `@concurrent` for intentional background work
7. Test thoroughly — concurrency bugs may surface at runtime
