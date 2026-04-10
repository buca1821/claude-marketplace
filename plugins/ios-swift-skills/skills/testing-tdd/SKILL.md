---
name: testing-tdd
description: TDD workflows for Swift Testing — red-green-refactor for new features, reproduce-first bug fixes, and test data factories. Use when building features test-first, fixing bugs with regression tests, or setting up test infrastructure.
---

# Testing & TDD Skill

## When to Use

| Situation | Workflow |
|-----------|----------|
| Building a new feature test-first | `references/tdd-feature.md` |
| Fixing a bug and preventing regression | `references/tdd-bug-fix.md` |
| Reducing boilerplate test setup | `references/test-data-factory.md` |

## Project Context

- **Framework**: Swift Testing (`import Testing`, `@Suite`, `@Test`, `#expect`) — preferred for all new tests
- **XCTest**: Only for UI tests (`XCUITest`) — Swift Testing does not support UI automation
- **Test location**: `YourAppTests/`
- **UI test location**: `YourAppUITests/` (Page Object Model)
- **Mocks**: `MockDataSource` (or your project's mock) for data dependency injection
- **Coverage thresholds** (configure per project):
  - ViewModels ≥ 85%
  - Utilities ≥ 80%
  - Views and Services excluded
- **Locale-dependent tests**: MUST inject explicit `Locale` — never rely on `Locale.current`
  - Use `Locale(identifier: "es_ES")` for metric
  - Use `Locale(identifier: "en_US")` for imperial

## Process

### 1. Identify the Workflow

- **New feature**: Use TDD red-green-refactor → `references/tdd-feature.md`
- **Bug fix**: Reproduce first, then fix → `references/tdd-bug-fix.md`
- **Test boilerplate**: Create fixture factories → `references/test-data-factory.md`

### 2. Write Tests Using Swift Testing

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

### 3. Run Tests

```bash
# Using xcodebuild
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 16'

# Run specific suite
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 16' -only-testing YourAppTests/FormattersTests

# Using XcodeBuildMCP
# Call build_sim or test_sim with default scheme YourApp
```

### 4. Verify Coverage

Check test coverage using Xcode's built-in coverage report or your project's coverage tool.

## Cross-References

- `.agent/rules/testing-standards.md` — coverage thresholds, framework choice, locale rules
- `.agent/rules/ui-testing.md` — UI test patterns, Page Object Model, AccessibilityID
- `docs/TESTING.md` — full testing documentation
