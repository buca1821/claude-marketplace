# tdd-feature

Build a new feature using TDD red-green-refactor. Tests define the spec, implementation makes them pass.

## Input

Feature description: `$ARGUMENTS`

If no arguments provided, ask the user what feature they want to build.

## Process

### 1. Load TDD skill

Load the testing-tdd skill for the full TDD feature workflow reference.

### 2. Define the feature

From the description (or issue), identify:
- Inputs, outputs, edge cases, dependencies
- Which files/modules will be involved

Present a 2-3 sentence plan and wait for confirmation.

### 3. Design the API surface

Sketch the public interface (protocol or class signature). Share with user for feedback.

### 4. RED — Write failing tests

Write tests using Swift Testing (`import Testing`, `@Suite`, `@Test`, `#expect`) in `YourAppTests/`.

Follow the order: construction → happy path → state → edge cases → errors.

Run tests to confirm they fail:
```bash
# Use your project's test script, or:
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 16' -only-testing YourAppTests
```

### 5. GREEN — Implement

Make tests pass one at a time. Simplest code that satisfies each test.

### 6. REFACTOR

With all tests green, clean up. Run tests after each change.

### 7. Verify coverage

Check test coverage using your project's coverage tool or Xcode's built-in coverage report.

### 8. Build

Use XcodeBuildMCP: `session_show_defaults` → `build_sim` to confirm no compiler errors.

## Conventions

- Swift Testing for all new tests
- Locale-dependent tests must inject explicit `Locale`
- Use `MockDataSource` (or your project's mock) for data injection
- Follow MVVM: `@MainActor` + `@Observable` ViewModels
