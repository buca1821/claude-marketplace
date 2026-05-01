# Swift Testing Patterns

Swift Testing replaces XCTest for unit tests. Macros (`@Suite`, `@Test`), expressive expectations (`#expect`, `#require`), parametrized tests, and traits make most test code shorter and more readable. This reference covers the patterns that pay off in real projects: organization, parametrization, traits, async, time control, and where XCTest still matters.

## Suite organization

Group related tests in a `@Suite`. The suite's name is the human-readable label that appears in the test navigator and CI reports:

```swift
import Testing
@testable import YourApp

@Suite("Distance formatter")
struct DistanceFormatterTests {

    @Test("formats meters in metric locale")
    func metric() {
        let result = DistanceFormatter.string(meters: 5_000, locale: .init(identifier: "es_ES"))
        #expect(result == "5 km")
    }

    @Test("formats meters in imperial locale")
    func imperial() {
        let result = DistanceFormatter.string(meters: 5_000, locale: .init(identifier: "en_US"))
        #expect(result == "3.11 mi")
    }
}
```

Two organization rules that scale:

- **One suite per type under test.** `DistanceFormatterTests`, not `FormattersTests` lumping multiple formatters together. Test failures point you at one type immediately.
- **Suite names match the type they test, not the file.** A test navigator listing 30 suites with descriptive names beats one giant `Tests` suite.

Suites can be `struct`, `final class`, or `actor`. Use `struct` unless you need shared mutable setup (rare with parametrized tests), in which case `actor` keeps it `Sendable`.

## `#expect` vs `#require`

```swift
#expect(value == expected)        // recorded as failure, test continues
let unwrapped = try #require(opt) // recorded as failure AND throws — test stops
```

Use `#require` when subsequent assertions depend on the value:

```swift
@Test("Parsed feed has at least one post")
func feedHasContent() throws {
    let posts = try #require(parser.parse(json), "Parser returned nil")
    let first = try #require(posts.first)
    #expect(first.id == "expected-id")
}
```

Without `#require`, a `nil` `posts` would crash on `.first`. The test would still fail, but the error message would point at the wrong line.

## Parametrized tests — `arguments:`

Tables of cases live in the test signature, not as ten copy-pasted methods:

```swift
@Test(
    "Pace calculation",
    arguments: [
        (duration: 1800.0, distance: 5000.0, expected: "6:00 /km"),
        (duration: 3600.0, distance: 10_000.0, expected: "6:00 /km"),
        (duration: 1500.0, distance: 5000.0, expected: "5:00 /km"),
    ]
)
func pace(duration: TimeInterval, distance: Double, expected: String) {
    let result = PaceFormatter.string(
        duration: .init(value: duration, unit: .seconds),
        distance: .init(value: distance, unit: .meters),
        locale: .init(identifier: "es_ES")
    )
    #expect(result == expected)
}
```

Each tuple becomes a separate test case visible in the navigator. A failure in case 2 reports the exact arguments — no `// case 2:` comments needed.

For the cross product of two dimensions:

```swift
@Test(
    "Distance formatting per locale and unit",
    arguments: [1_000.0, 5_000.0, 42_195.0],
    [Locale(identifier: "es_ES"), Locale(identifier: "en_US")]
)
func distancePerLocale(meters: Double, locale: Locale) {
    let result = DistanceFormatter.string(meters: meters, locale: locale)
    #expect(!result.isEmpty)
}
```

Two `arguments:` arrays produce 3×2 = 6 cases.

For `zip` (paired arguments without cross product):

```swift
@Test(arguments: zip([1, 2, 3], ["one", "two", "three"]))
func numberToWord(number: Int, word: String) {
    #expect(NumberSpeller.word(for: number) == word)
}
```

## Traits — `.tags`, `.serialized`, `.disabled`, `.bug`

Traits attach metadata or behavior to suites and tests:

```swift
@Suite("Network layer", .tags(.network, .integration))
struct NetworkTests {

    @Test(.serialized)
    func uploadOrderingMatters() async throws {
        // forced sequential within this suite
    }

    @Test(.disabled("Flaky on CI — see #4321"))
    func flakyDownload() {}

    @Test(.bug("https://github.com/acme/app/issues/4321", "Crashes on iOS 17.0.1"))
    func bugRepro() {}
}
```

- **`.tags(...)`** lets you filter at run time: `swift test --filter '.tags(.network)'`. Define tags as `extension Tag` once in a shared file.
- **`.serialized`** disables parallelism within the suite. Use only when state is shared across tests; the default (parallel) is what you want most of the time.
- **`.disabled(reason)`** records skip with a reason in the report. Always pass a reason.
- **`.bug(url, comment)`** ties a test to an issue tracker. The link surfaces in test reports.

Define tags once:

```swift
extension Tag {
    @Tag static var network: Self
    @Tag static var integration: Self
    @Tag static var slow: Self
}
```

Then filter on the command line or in Xcode's test plan to run only fast tests during development.

## `confirmation()` — for callback-shaped expectations

When the code under test fires a callback (or sends a notification, or calls a closure), `confirmation()` lets the test wait for that signal:

```swift
@Test("Authenticator notifies on success")
func authNotifies() async throws {
    let auth = Authenticator()

    await confirmation { confirmed in
        auth.onSuccess = { confirmed() }
        try await auth.signIn(token: "valid")
    }
}
```

The test fails if `confirmed()` is not called within the suite's timeout. `confirmation(expectedCount: 3)` waits for exactly three calls.

## `withKnownIssue` — for known-failing tests you don't want to delete

When a test exposes a real bug you can't fix yet, mark the failure as expected:

```swift
@Test
func handlesEmptyResponse() throws {
    withKnownIssue("Parser crashes on empty array — #5123") {
        let result = try parser.parse(Data())
        #expect(result.isEmpty)
    }
}
```

If the assertion *passes* (i.e., the bug is silently fixed), `withKnownIssue` flags the test so you remember to remove the marker. This is better than `.disabled` because the test still runs and tells you when reality changes.

## Async tests

`@Test` functions can be `async throws`. No setup needed — concurrent tests run in parallel by default:

```swift
@Test
func loadFetchesFromAPI() async throws {
    let api = StubWorkoutAPI(workouts: [.fixture()])
    let sut = WorkoutListViewModel(api: api)

    await sut.load()

    #expect(sut.workouts.count == 1)
}
```

For tests that touch `@MainActor` types, mark the test:

```swift
@MainActor
@Test
func viewModelMutationsAreMainActor() async {
    let sut = WorkoutListViewModel(api: .mock([]))
    sut.workouts = [.fixture()]
    #expect(sut.workouts.count == 1)
}
```

You can also annotate the entire suite with `@MainActor` — every test inside inherits the isolation. This is convenient for view-model-heavy test files where every `init` and property access needs main actor.

## Time control — inject `Clock`

Code that uses `Task.sleep`, `Date.now`, or `Timer` is hard to test deterministically. The fix is dependency injection for time:

```swift
public protocol TimeSource: Sendable {
    var now: Date { get }
    func sleep(for: Duration) async throws
}

struct LiveTimeSource: TimeSource {
    var now: Date { .now }
    func sleep(for duration: Duration) async throws {
        try await Task.sleep(for: duration)
    }
}

actor MockTimeSource: TimeSource {
    var now: Date
    init(now: Date) { self.now = now }
    func sleep(for: Duration) async throws { /* no-op */ }
    func advance(by interval: TimeInterval) { now.addTimeInterval(interval) }
}
```

The view model takes `TimeSource`; tests pass a `MockTimeSource` and call `advance(by:)` to step time forward without waiting in real time. This is the difference between a 0.05s test and a 5s test.

## Tests that depend on `Locale`

A test that asserts `"5 km"` will pass on your machine and fail on a CI runner with `en_US`. Inject the locale always:

```swift
@Test
func formatsKilometers() {
    let result = DistanceFormatter.string(meters: 5_000, locale: .init(identifier: "es_ES"))
    #expect(result == "5 km")
}
```

The same applies to `Calendar`, `TimeZone`, `Currency`. If your formatter takes them as parameters at the call site, the test stays deterministic across machines.

## When XCTest is still the answer

- **UI tests with XCUITest.** Swift Testing does not support `XCUIApplication`. Keep UI tests in their own target with XCTest.
- **Performance regression baselines (`measure { }`).** Swift Testing has no equivalent yet. Performance assertions live in XCTest until that gap closes.
- **Bridging Objective-C-only test harnesses.** Some legacy frameworks expect `XCTestCase` subclasses.

You can mix targets: unit tests in Swift Testing, UI tests in XCTest, both shipping with the same app. Don't mix them in the same target — pick one per target.

## Migrating from XCTest

The mechanical translation:

| XCTest | Swift Testing |
|---|---|
| `class FooTests: XCTestCase` | `struct FooTests` (or `@Suite struct FooTests`) |
| `func testBar()` | `@Test func bar()` |
| `XCTAssertEqual(a, b)` | `#expect(a == b)` |
| `XCTAssertTrue(p)` | `#expect(p)` |
| `XCTAssertNil(x)` | `#expect(x == nil)` |
| `XCTAssertThrowsError { try x() }` | `#expect(throws: SomeError.self) { try x() }` |
| `XCTUnwrap(opt)` | `try #require(opt)` |
| `setUp() / tearDown()` | `init() / deinit` (struct stored properties) |
| `expectation(description:)` | `confirmation { confirmed in ... }` |
| `XCTSkip` | `withKnownIssue` or `.disabled(reason:)` |

Migrate file by file. Both frameworks coexist in the same target until the migration completes — Swift Testing tests run alongside XCTest tests under `xcodebuild test`.

## Rules

- One `@Suite` per type under test; descriptive suite names that read in CI reports.
- Use `@Test` parametrized over `arguments:` for tables of cases — never copy-paste 10 method bodies.
- `try #require` for any value subsequent assertions depend on.
- Inject `Locale`, `Calendar`, `TimeSource` — never assert against ambient values.
- Tag tests so you can filter; define tags once in a shared file.
- Keep `@MainActor` at the suite level for view-model tests; per-test for outliers.
- Use `withKnownIssue` for known bugs; `.disabled` only when a test cannot run at all.
- Keep XCUITest in its own target with XCTest; do not try to mix in the same target.
