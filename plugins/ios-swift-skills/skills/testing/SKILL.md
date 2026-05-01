---
name: testing
description: Swift Testing patterns, protocol-based mocks, and test data factories. Use when writing tests, setting up test infrastructure, or reviewing test coverage.
---

# Testing Skill

## Operating Rules

- Use Swift Testing (`import Testing`, `@Suite`, `@Test`, `#expect`) for new tests; reserve XCTest for UI tests (`XCUITest`) and `measure { }` performance baselines.
- Inject every dependency on time, locale, calendar, and network — never assert against `Date.now`, `Locale.current`, or live URLSession.
- Mocks are protocol-based and constructor-injected; substitutes are `Sendable`.
- Parametrize over tables of cases with `arguments:` instead of duplicating test methods.
- Tests run in parallel by default; opt out with `.serialized` only when state is shared.
- Coverage thresholds are enforced in CI, not aspirational — see project `testing-standards` rules for project-specific numbers.

## Topic Router

| Topic | Reference |
|-------|-----------|
| Swift Testing patterns (suites, parametrization, traits, async, time injection) | `references/swift-testing-patterns.md` |
| Protocol-based mocks (Stub, Spy, Fake, URLSession, callback bridging) | `references/mock-protocols.md` |
| Reducing fixture boilerplate | `references/test-data-factory.md` |

## When to Write What

| Situation | Pattern |
|-----------|---------|
| One ViewModel, multiple dependencies | Protocol per dependency, inject mocks via initializer |
| Same scenario with different inputs | `@Test(arguments: [...])` parametrized over the table |
| Code touches the network or a callback API | Bridge in the live implementation, expose `async throws` protocol, stub in tests |
| Same fixture used across 10+ tests | `extension Workout { static func fixture(...) -> Self }` |
| Test depends on "now" | Inject a `TimeSource` protocol; mock advances time deterministically |
| Test asserts formatted output | Inject `Locale` explicitly; never trust `Locale.current` |

## Quick Example

```swift
import Testing
@testable import YourApp

@Suite("Distance formatter")
struct DistanceFormatterTests {

    @Test(
        "Formats meters per locale",
        arguments: [
            (5_000.0, "es_ES", "5 km"),
            (5_000.0, "en_US", "3.11 mi"),
        ]
    )
    func format(meters: Double, localeID: String, expected: String) {
        let result = DistanceFormatter.string(
            meters: meters,
            locale: Locale(identifier: localeID)
        )
        #expect(result == expected)
    }
}
```

## Running Tests

```bash
# xcodebuild
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 17'

# Specific suite
xcodebuild test -scheme YourApp -only-testing YourAppTests/FormattersTests

# XcodeBuildMCP (recommended in Claude Code sessions)
# Call test_sim with default scheme
```

## Cross-References

- Project `CLAUDE.md` and `.claude/rules/testing-standards.md` — coverage thresholds, framework choice, project-specific mocks.
- Project `.claude/rules/ui-testing.md` — XCUITest with Page Object Model. UI tests live in their own target with XCTest, not Swift Testing.
- `swiftui` skill (`accessibility-patterns` reference) — accessibility identifiers used by UI tests.
