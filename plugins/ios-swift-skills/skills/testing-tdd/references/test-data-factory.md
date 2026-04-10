# Test Data Factories

Eliminate repetitive test setup with `.fixture()` factories.

```swift
// Without factory — 10 lines of setup per test
let item = Item(id: UUID(), title: "Test", status: .active, createdAt: Date(), ...)

// With factory — 1 line, override only what matters
let item = Item.fixture()
let special = Item.fixture(status: .archived)
```

## Pattern: Static Factory Extension

```swift
// YourAppTests/Factories/Item+Factory.swift
import Foundation
@testable import YourApp

extension Item {
    static func fixture(
        id: UUID = UUID(),
        title: String = "Test Item",
        status: Status = .active,
        createdAt: Date = Date(timeIntervalSince1970: 1_700_000_000)
    ) -> Item {
        Item(id: id, title: title, status: status, createdAt: createdAt)
    }

    static var sample: Item { .fixture() }
    static var sampleList: [Item] {
        [.fixture(title: "First"), .fixture(title: "Second"), .fixture(title: "Third")]
    }
    static func fixtures(count: Int) -> [Item] {
        (0..<count).map { .fixture(id: UUID(), title: "Item \($0 + 1)") }
    }
}
```

## Default Rules

| Property Type | Default |
|---|---|
| `UUID` | `UUID()` — unique per call |
| `String` | Descriptive placeholder |
| `Date` | **Fixed timestamp** (never `Date()`) |
| `Bool` | `false` — opt-in to special states |
| `Array` | Empty `[]` — opt-in to populated |
| `Optional` | `nil` — opt-in to value |
| `Enum` | Most common case |
| Nested model | That model's `.fixture()` |

## Naming

| Pattern | Use |
|---|---|
| `.fixture(prop: value)` | Customizable |
| `.sample` | Quick default |
| `.sampleList` | Collection |
| `.fixtures(count: N)` | N unique items |

Keep factories in the **test target only**.
