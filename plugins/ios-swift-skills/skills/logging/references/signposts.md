# Signposts and `OSSignposter`

Signposts mark moments and intervals on the unified logging timeline. They cost almost nothing in release builds, and they show up as named regions in Instruments. Use them whenever you want to answer "how long did X take, and how does that change between releases?" — they give you durable, named instrumentation without spamming the log buffer.

## Signposts vs `Logger`

| Use case | Tool |
|---|---|
| Recording an event happened ("user signed in", "fetch failed") | `Logger` |
| Recording an event with surrounding context (request, feature toggle state) | `Logger` |
| Measuring how long something takes | `OSSignposter` |
| Marking a point on the Instruments timeline to correlate with CPU/memory | `OSSignposter` |
| Tracing concurrent work to see overlap | `OSSignposter` with explicit IDs |

`Logger` records what happened. `OSSignposter` records when, for how long, and lets Instruments line that up against everything else the system was doing.

## The API in one screen

```swift
import os.signpost

private let signposter = OSSignposter(
    subsystem: "com.acme.app",
    category: "performance"
)

func loadHomeFeed() async throws -> [Post] {
    let state = signposter.beginInterval("load-home-feed")
    defer { signposter.endInterval("load-home-feed", state) }

    let posts = try await api.fetchPosts()
    let sorted = posts.sorted { $0.createdAt > $1.createdAt }
    return sorted
}
```

`beginInterval` returns an opaque `OSSignpostIntervalState`. Pass it back to `endInterval` to close the interval. The `defer` pattern keeps the interval balanced even if the function throws.

For one-shot events (no duration), use `emitEvent`:

```swift
signposter.emitEvent("cache-miss", "key=\(key, privacy: .public)")
```

## Names — keep them stable

The interval name is what Instruments groups by. Keep it stable across releases so you can compare flame charts over time:

- ✅ `"load-home-feed"`, `"decode-response"`, `"render-frame"`
- ❌ `"loading 47 posts for user_42"` — high cardinality, useless in aggregate

Put dynamic context in the message string, not the name:

```swift
let state = signposter.beginInterval("decode-response", "endpoint=\(endpoint, privacy: .public)")
defer { signposter.endInterval("decode-response", state) }
```

The same privacy modifiers as `Logger` apply — see `privacy-redaction.md`.

## IDs — for concurrent work

When you have several intervals of the same name running concurrently, Instruments cannot tell them apart unless you assign each one an explicit ID:

```swift
let id = signposter.makeSignpostID()
let state = signposter.beginInterval("fetch", id: id, "url=\(url.path, privacy: .public)")

let data = try await session.data(from: url).0

signposter.endInterval("fetch", state)
```

Each ID is unique within the process. The same ID flows through all `begin`/`end` calls, so Instruments can render five overlapping `fetch` intervals as five distinct rows instead of one tangled bar.

You can also derive an ID from an object identity if you want intervals tied to a model:

```swift
let id = signposter.makeSignpostID(from: download)
```

Two `Download` instances get two IDs; the same instance always gets the same ID across calls.

## End-to-end example: a network request

```swift
final class ImageLoader {
    private let signposter = OSSignposter(
        subsystem: "com.acme.app",
        category: "image-loading"
    )

    func load(_ url: URL) async throws -> UIImage {
        let id = signposter.makeSignpostID()

        let downloadState = signposter.beginInterval(
            "download",
            id: id,
            "host=\(url.host ?? "?", privacy: .public)"
        )
        let (data, _) = try await URLSession.shared.data(from: url)
        signposter.endInterval("download", downloadState, "bytes=\(data.count)")

        let decodeState = signposter.beginInterval("decode", id: id)
        guard let image = UIImage(data: data) else {
            signposter.emitEvent("decode-failed", id: id)
            throw ImageError.invalidData
        }
        signposter.endInterval("decode", decodeState, "size=\(image.size.width)x\(image.size.height)")

        return image
    }
}
```

In Instruments → "os_signpost" template, this renders as two named intervals (`download`, `decode`) sharing one ID per request, so you can see how many requests overlapped, which decodes were slow, and which downloads timed out.

## Viewing in Instruments

1. Build for Profiling (Cmd-I).
2. Choose template **"Logging"** or any template plus add the **"os_signpost"** instrument from the library.
3. Set the subsystem filter to your app's subsystem.
4. Each `category` shows as a swim lane. Each interval name shows as a row. Hover for messages.

For an automation-friendly capture from the command line:

```bash
xcrun xctrace record --template 'os_signpost' \
    --time-limit 30s \
    --output /tmp/signposts.trace \
    --attach $(pgrep -x YourApp)
```

Open `signposts.trace` in Instruments after the recording finishes.

## Signposts in ranges that span async boundaries

Async functions can suspend many times. `beginInterval` and `endInterval` do not need to be in the same task — you just need the state object.

```swift
actor Uploader {
    private let signposter = OSSignposter(subsystem: "com.acme.app", category: "upload")
    private var inFlight: [URL: OSSignpostIntervalState] = [:]

    func start(_ url: URL) {
        inFlight[url] = signposter.beginInterval("upload", "url=\(url.path, privacy: .public)")
    }

    func finish(_ url: URL) {
        guard let state = inFlight.removeValue(forKey: url) else { return }
        signposter.endInterval("upload", state)
    }
}
```

The state is `Sendable`-safe to pass between isolation domains.

## Cost in release

`OSSignposter` checks at runtime whether anyone is listening (Instruments attached, `log stream` filter matching). If nothing is listening, the work is bounded by a single atomic load. You can leave signposts in shipping code without measurable overhead — that is the whole point.

What you should *not* do: build expensive message strings unconditionally:

```swift
signposter.endInterval(
    "decode",
    state,
    "result=\(generateExpensiveDescription())"   // BAD — runs even when no one listens
)
```

Wrap with `signposter.isEnabled` if the message itself is expensive to construct:

```swift
if signposter.isEnabled {
    signposter.endInterval("decode", state, "result=\(generateExpensiveDescription())")
} else {
    signposter.endInterval("decode", state)
}
```

For simple interpolations of values you already have, this guard is unnecessary.

## When to add signposts

- Around any operation you would consider profiling — even pre-emptively. They cost nothing if no one looks.
- Around boundaries between subsystems (network → parsing → rendering) so you can see where time is spent in aggregate.
- Around suspected hot paths before changing them, then around the same paths after — Instruments can compare two traces side by side.
- Inside actors, around critical sections, to see how long isolation is held.

Do not add signposts:

- Inside tight loops without meaningful aggregation — you'll generate millions of events and Instruments becomes slow.
- For events that are already covered by a system-provided instrument (network requests are visible in "Network" without you doing anything).
- As a substitute for `Logger`. Signposts are not searchable text logs.

## Rules

- Use stable, low-cardinality names; put variables in the message string.
- Always pair `beginInterval` / `endInterval` via `defer` — leaks unbalance Instruments charts.
- Assign explicit IDs to overlapping work of the same name.
- Apply the same privacy modifiers (`privacy: .public`/`.private`) to message strings as you would for `Logger`.
- Guard expensive message construction with `signposter.isEnabled`.
- Leave signposts in shipping builds; they pay for themselves the first time you profile a regression.
- Do not log per-iteration inside hot loops — sample or aggregate.
