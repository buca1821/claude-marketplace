# Protocol-Based Mocks

Mocks let you test code in isolation by replacing collaborators with controllable substitutes. The pattern that works best in Swift — for testability, for SwiftUI previews, and for Swift 6 concurrency — is **protocol-first**: define a protocol, inject it, swap the implementation per environment.

This reference covers four substitute types (Stub, Spy, Mock, Fake), the conventions for naming and locating them, how to make them `Sendable` for Swift 6, and concrete examples for `URLSession` and callback-bridged APIs.

## Why protocol-first

Concrete types lock you in. The moment a `WorkoutListViewModel` constructs `URLSession.shared` directly, you cannot test the view model without hitting the network. If instead the view model takes a `WorkoutAPI` protocol, you can pass `WorkoutAPI.live` in production, `WorkoutAPI.mock` in previews, and `WorkoutAPISpy()` in tests — without changing the view model.

The protocol does not need to be elaborate. One method is fine. The point is that the boundary between layers is named, replaceable, and visible at the type level.

## Substitute taxonomy

Names matter. Pick the type that matches your intent:

| Type | Purpose | When to reach for it |
|---|---|---|
| **Stub** | Returns canned responses | You only care about what comes back, not what was called |
| **Spy** | Records what was called | You want to assert against call counts or arguments |
| **Mock** | Pre-programmed expectations + verification | Strict behavior verification (rare in Swift, usually overkill) |
| **Fake** | Working implementation, simplified | You need real behavior but with no I/O (in-memory store) |

Most Swift tests use stubs and spies. Mocks (in the strict Mockito sense) are uncommon. Fakes are valuable when many tests need realistic behavior — e.g., an in-memory `KeychainStore` that actually stores and retrieves.

## Defining the protocol

Keep it small. One responsibility, one protocol:

```swift
public protocol WorkoutAPI: Sendable {
    func fetch(after date: Date) async throws -> [Workout]
    func upload(_ workout: Workout) async throws
}
```

Notes:

- `Sendable` constrains both implementations and any captured state — required if you cross actor boundaries (you will).
- `async throws` for all methods that touch I/O. The protocol should not leak callback shapes.
- Method names describe *what*, not *how*. `fetch` and `upload`, not `getViaURLSession`.

## Stub — minimal, returns canned data

```swift
struct StubWorkoutAPI: WorkoutAPI, Sendable {
    let workouts: [Workout]
    let uploadError: Error?

    init(workouts: [Workout] = [], uploadError: Error? = nil) {
        self.workouts = workouts
        self.uploadError = uploadError
    }

    func fetch(after date: Date) async throws -> [Workout] {
        workouts.filter { $0.date > date }
    }

    func upload(_ workout: Workout) async throws {
        if let uploadError { throw uploadError }
    }
}
```

Use it in a test:

```swift
@Test("ViewModel renders workouts in date order")
func sortedByDate() async {
    let api = StubWorkoutAPI(workouts: [.fixture(date: .yesterday), .fixture(date: .today)])
    let sut = WorkoutListViewModel(api: api)

    await sut.load()

    #expect(sut.workouts.map(\.date) == [.today, .yesterday])
}
```

A stub stays a `struct`. No mutable state, value semantics, no concurrency concerns.

## Spy — records calls

When you need to assert that a method was called, with what arguments, and how many times, use a spy. Spies need mutable state, so they become `actor` (or `class` with locking) to remain `Sendable`:

```swift
actor SpyWorkoutAPI: WorkoutAPI {
    private(set) var fetchCalls: [Date] = []
    private(set) var uploaded: [Workout] = []
    private var fetchResult: Result<[Workout], Error> = .success([])

    func setFetchResult(_ result: Result<[Workout], Error>) {
        fetchResult = result
    }

    func fetch(after date: Date) async throws -> [Workout] {
        fetchCalls.append(date)
        return try fetchResult.get()
    }

    func upload(_ workout: Workout) async throws {
        uploaded.append(workout)
    }
}
```

Then assert on the recorded calls:

```swift
@Test("Refresh fetches workouts since last sync")
func refreshUsesLastSyncDate() async throws {
    let spy = SpyWorkoutAPI()
    let sut = WorkoutListViewModel(api: spy, lastSync: .yesterday)

    await sut.refresh()

    let calls = await spy.fetchCalls
    #expect(calls == [.yesterday])
}
```

Two patterns to know:

- **`private(set)`** exposes read-only access for assertions while keeping mutation inside the actor.
- **Awaiting actor state** (`await spy.fetchCalls`) is required because actors isolate their state. Tests live in a non-isolated context by default.

## Fake — working substitute, no I/O

When tests need a collaborator that *behaves like* the real thing — round-trips data, observes ordering, fails on duplicates — but without real I/O, write a fake:

```swift
actor InMemoryKeychain: KeychainStore {
    private var storage: [String: Data] = [:]

    func save(_ data: Data, key: String) throws {
        storage[key] = data
    }

    func load(key: String) throws -> Data? {
        storage[key]
    }

    func delete(key: String) throws {
        storage.removeValue(forKey: key)
    }
}
```

Fakes are worth the effort when many tests share the same collaborator and you'd otherwise reimplement the same stub every time. A handful of `if`/`else` in 30 stubs becomes one fake with real logic.

## Inject via initializer

The view model takes the protocol, not the concrete type:

```swift
@Observable
@MainActor
final class WorkoutListViewModel {
    private let api: WorkoutAPI
    private(set) var workouts: [Workout] = []

    init(api: WorkoutAPI) {
        self.api = api
    }

    func load() async {
        do {
            workouts = try await api.fetch(after: .distantPast)
        } catch {
            workouts = []
        }
    }
}
```

In production, callers pass a real implementation; in tests, they pass a stub or spy. Avoid:

- **Default arguments with `URLSession.shared`** — defeats the purpose; tests can still construct the view model without injecting.
- **Service locator patterns** — global `Container.shared.resolve()` calls hide dependencies and need test-time mutation. Stick to constructor injection.

## Static factories: `.live`, `.mock`, `.preview`

A clean convention is static factory methods on the protocol or on a type that conforms to it:

```swift
extension WorkoutAPI where Self == LiveWorkoutAPI {
    static var live: Self { LiveWorkoutAPI() }
}

extension WorkoutAPI where Self == StubWorkoutAPI {
    static func mock(_ workouts: [Workout] = []) -> StubWorkoutAPI {
        StubWorkoutAPI(workouts: workouts)
    }
}
```

Call sites read cleanly:

```swift
WorkoutListViewModel(api: .live)
WorkoutListViewModel(api: .mock([.fixture()]))
```

Both factories keep the dependency type opaque — callers don't need to know which concrete type implements the protocol. SwiftUI previews use the same `mock` factories, so you get UI exploration without running real network calls.

## URLSession example

`URLSession` is the canonical thing to mock. The protocol abstracts the *call*, not the session itself:

```swift
public protocol HTTPClient: Sendable {
    func data(for request: URLRequest) async throws -> (Data, HTTPURLResponse)
}

struct LiveHTTPClient: HTTPClient {
    let session: URLSession = .shared

    func data(for request: URLRequest) async throws -> (Data, HTTPURLResponse) {
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        return (data, http)
    }
}

struct StubHTTPClient: HTTPClient {
    let response: Result<(Data, HTTPURLResponse), Error>

    func data(for request: URLRequest) async throws -> (Data, HTTPURLResponse) {
        try response.get()
    }
}
```

For a test that exercises the parser:

```swift
@Test("Decodes workouts from valid JSON")
func decodesValidJSON() async throws {
    let json = #"[{"id":"1","date":"2026-04-29T10:00:00Z"}]"#.data(using: .utf8)!
    let response = HTTPURLResponse(url: URL(string: "x")!, statusCode: 200, httpVersion: nil, headerFields: nil)!
    let client = StubHTTPClient(response: .success((json, response)))
    let api = LiveWorkoutAPI(client: client)

    let workouts = try await api.fetch(after: .distantPast)

    #expect(workouts.count == 1)
}
```

Avoid `URLProtocol` subclassing for new code. It works but it's an indirect, framework-coupled approach; a protocol-based stub is cleaner and gives you better error messages when assertions fail.

## Bridging callback APIs (HealthKit, AVFoundation, CoreLocation)

Many Apple frameworks still use callback APIs. The bridging happens behind the protocol, in the live implementation:

```swift
public protocol WorkoutDataSource: Sendable {
    func workouts(since date: Date) async throws -> [HKWorkout]
}

struct LiveWorkoutDataSource: WorkoutDataSource {
    let store: HKHealthStore

    func workouts(since date: Date) async throws -> [HKWorkout] {
        try await withCheckedThrowingContinuation { continuation in
            let predicate = HKQuery.predicateForSamples(withStart: date, end: nil)
            let query = HKSampleQuery(
                sampleType: .workoutType(),
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: nil
            ) { _, samples, error in
                if let error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume(returning: (samples as? [HKWorkout]) ?? [])
                }
            }
            store.execute(query)
        }
    }
}
```

The protocol stays clean (`async throws`); the callback mess is contained in `Live*`. Tests get a stub:

```swift
struct StubWorkoutDataSource: WorkoutDataSource {
    let workouts: [HKWorkout]

    func workouts(since date: Date) async throws -> [HKWorkout] {
        workouts.filter { $0.startDate >= date }
    }
}
```

Two rules for bridging:

1. **Resume the continuation exactly once.** A callback that fires twice (success then error, or error then cancellation) becomes a runtime trap. Use a guard or wrap the continuation in a state machine if the underlying API is loose.
2. **Use `withCheckedContinuation` in tests/dev, `withUnsafeContinuation` only after profiling.** Checked continuations cost a few percent and catch double-resume bugs early.

## Locating mock files

Project layout that scales:

```
YourAppTests/
├── Mocks/
│   ├── StubHTTPClient.swift
│   ├── SpyWorkoutAPI.swift
│   └── InMemoryKeychain.swift
└── WorkoutListViewModelTests.swift
```

One substitute per file when they get over 30 lines. Group by collaborator type, not by test file — the same `SpyWorkoutAPI` is reused across many test files.

If a mock is also useful in SwiftUI previews, move it to a shared target (e.g., a `WorkoutAPITestSupport` SPM module) so the main target can `#if DEBUG` import it for previews without taking a dependency on the test target.

## Rules

- One protocol per collaborator boundary; keep methods small and async-first.
- Use `Sendable` on every protocol that crosses isolation; default to `actor` for stateful spies.
- Inject through the initializer; avoid global containers and default `.shared` arguments.
- Prefer stubs and spies; reach for mocks (strict expectations) only when behavior verification is the test's purpose.
- Bridge callback APIs in the live implementation only; keep the protocol pure async/await.
- Resume continuations exactly once when bridging.
- Name substitutes after their role — `StubX`, `SpyX`, `FakeX` — never just `MockX` for everything.
- Use static factories (`.live`, `.mock`, `.preview`) so call sites stay readable and previews share fixtures with tests.
