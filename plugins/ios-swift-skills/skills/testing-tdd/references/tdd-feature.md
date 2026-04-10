# TDD Feature — Red-Green-Refactor

Build new features test-first. The test is your acceptance criteria in code form.

```
Traditional:     AI generates code → hope it's correct → find bugs later
TDD with AI:     Write tests (spec) → AI generates code to pass → proven correct
```

## Process

### Phase 1: Define the Feature

Before writing any code, identify:
1. Inputs, outputs, edge cases, dependencies
2. Sketch the public interface (protocol or class signature)

### Phase 2: RED — Write Failing Tests

Write tests in this order:

1. **Construction** — can you create the object?
2. **Happy path** — does the basic operation work?
3. **State verification** — does state update correctly?
4. **Edge cases** — empty, nil, boundaries
5. **Error handling** — what fails and how?

Use Swift Testing:

```swift
import Testing
@testable import YourApp

@Suite("FeatureName")
struct FeatureNameTests {

    @Test("happy path description")
    func happyPath() async throws {
        let sut = FeatureUnderTest()
        let result = try await sut.perform(input)
        #expect(result == expectedOutput)
    }

    @Test("edge case description")
    func edgeCase() async {
        await #expect(throws: FeatureError.invalidInput) {
            try await sut.perform(badInput)
        }
    }
}
```

**Run tests — they should ALL fail.**

### Phase 3: GREEN — Implement to Pass

- One test at a time — make the first pass, then the second
- Simplest code that satisfies each test
- Run tests after each change

### Phase 4: REFACTOR

With all tests green, clean up. Run tests after every change. If any test fails → revert.

## Rhythm

```
RED       → Write one failing test     (30s – 2 min)
GREEN     → Make it pass               (1 – 5 min)
REFACTOR  → Clean up, tests green      (1 – 3 min)
```

If GREEN takes > 5 minutes, the test is too big. Break it down.

## Test Categories

| Feature Type | Key Tests |
|---|---|
| **ViewModel** | Initial state, load success, load error, formatted output, user actions |
| **Formatter/Utility** | Happy path per format, locale variants, zero/nil/boundary inputs |
| **Service/Data Layer** | Fetch, empty result, filter, sort, error handling |

## Pitfalls

| Pitfall | Solution |
|---------|----------|
| Too many tests before implementing | Write 2-3, implement, repeat |
| Testing implementation details | Test behavior and outcomes only |
| Skipping refactor step | Refactor every 3-5 green cycles |
| AI implementing beyond tests | Only implement what tests require |
