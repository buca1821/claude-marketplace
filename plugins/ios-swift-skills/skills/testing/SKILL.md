---
name: testing
description: Swift Testing patterns, test data factories, and testing conventions. Use when writing tests, setting up test infrastructure, or reviewing test coverage.
---

# Testing Skill

## When to Use

| Situation | Reference |
|-----------|-----------|
| Reducing boilerplate test setup | `references/test-data-factory.md` |
| Writing new tests | See patterns below |
| Reviewing test coverage | Check project thresholds |

## Project Context

- **Framework**: Swift Testing (`import Testing`, `@Suite`, `@Test`, `#expect`) — preferred for all new tests
- **XCTest**: Only for UI tests (`XCUITest`) — Swift Testing does not support UI automation
- **Test location**: `YourAppTests/`
- **UI test location**: `YourAppUITests/`
- **Mocks**: Protocol-based mocks for dependency injection
- **Locale-dependent tests**: MUST inject explicit `Locale` — never rely on `Locale.current`
  - Use `Locale(identifier: "es_ES")` for metric
  - Use `Locale(identifier: "en_US")` for imperial

## Writing Tests with Swift Testing

```swift
import Testing
@testable import YourApp

@Suite("Formatters")
struct FormattersTests {

    @Test("formats distance in metric locale")
    func distanceMetric() {
        let result = Formatters.formatDistance(
            meters: 5000,
            locale: Locale(identifier: "es_ES")
        )
        #expect(result.contains("5"))
    }
}
```

## Running Tests

```bash
# Using xcodebuild
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 17'

# Run specific suite
xcodebuild test -scheme YourApp -only-testing YourAppTests/FormattersTests

# Using XcodeBuildMCP (recommended)
# Call test_sim with default scheme
```

## Cross-References

- Project CLAUDE.md — coverage thresholds, framework choice
- Project `.claude/rules/` — testing standards, UI test patterns
