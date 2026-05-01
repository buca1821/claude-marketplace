# Privacy Redaction in OSLog

`Logger` redacts dynamic values to `<private>` in release builds by default. The vast majority of "missing" log output in production is this — not a logging bug. Knowing how redaction works (and how to opt out where it is safe) is the difference between logs that help you debug and logs that waste storage with `<private>` placeholders.

## The default

For any string interpolation, `Logger` decides at runtime whether the value is shown verbatim or redacted to `<private>`. The decision is per-build-configuration:

| Build configuration | Default for dynamic values | Default for static literals |
|---|---|---|
| DEBUG | shown verbatim | shown verbatim |
| RELEASE | redacted to `<private>` | shown verbatim |

A "static literal" is a string the compiler knows at build time:

```swift
logger.info("User signed in")          // visible in release
logger.info("User \(email)")           // <private> in release — `email` is dynamic
```

To override the default, annotate the interpolation explicitly:

```swift
logger.info("User \(email, privacy: .public)")    // visible in release
logger.info("User \(email, privacy: .private)")   // redacted in release (same as default)
```

The `.private` annotation is not just cosmetic: it documents intent. A future reader knows you considered the privacy implication and chose redaction deliberately.

## The four privacy options

```swift
public enum OSLogPrivacy {
    case auto      // default
    case `public`  // never redact
    case `private` // always redact
    case sensitive // redact AND mark for system-level handling (iOS 15+)
}
```

`.auto` matches the table above (debug verbatim, release redacted). `.public` and `.private` force the behavior. `.sensitive` is `.private` plus a hint to the system that this value is so sensitive that even sysdiagnose collection should redact it; use it for credentials and tokens.

```swift
logger.error("Auth failed for \(userID, privacy: .public): token=\(token, privacy: .sensitive)")
```

In a release build that line emits `Auth failed for u_42: token=<private>`. In a sysdiagnose, the user ID is captured (debugging an outage) but the token is not (no exfiltration risk).

## Hashing for correlation

For values that are PII but where you still need to correlate sessions across log lines, the privacy modifier supports a `mask: .hash` option:

```swift
logger.info("Request from \(userEmail, privacy: .private(mask: .hash))")
```

Output in release: `Request from <mask.hash: 'd4f7…'>`. The hash is stable within the boot session, so you can grep for the same user across many lines, but the actual email never appears. Use this whenever you need correlation but the literal value is sensitive.

## Common PII categories — what to do with each

| Category | Default policy | Annotation |
|---|---|---|
| Auth tokens, refresh tokens, API keys | redact always, even in DEBUG | `.sensitive` |
| Passwords | never log | omit entirely |
| Email addresses | redact in release | `.private(mask: .hash)` if correlation needed |
| Phone numbers | redact in release | `.private(mask: .hash)` |
| User IDs (your own opaque identifiers) | safe to show | `.public` |
| Health data (HealthKit values) | redact always | `.private` or `.sensitive` |
| Location (lat/long) | redact always; consider not logging at all | `.private` |
| Device identifiers (IDFV, vendor ID) | safe within team; redact for external builds | `.public` or `.private` per policy |
| URLs | path is usually safe; query string and fragments can leak | log path only, redact full URL |
| File paths | safe up to user home; below `~/Documents` may be PII | redact full path or log relative path |
| Backend response bodies | redact always — mixed PII | `.private` or do not log body |
| Error messages from third-party SDKs | unpredictable; redact by default | `.private` |

## Anti-patterns

### Logging entire objects

```swift
logger.info("Fetched workout: \(workout)")  // BAD
```

`workout` interpolates via `String(describing:)`, which dumps every property — likely including health data, location, timestamps that combine to identify the user. Even with `.private`, you've now committed to a pattern where any property added to `Workout` later silently flows into logs. Log only the minimum field you actually need.

```swift
logger.info("Fetched workout id=\(workout.id, privacy: .public)")  // GOOD
```

### Trusting `description`

If a type implements `CustomStringConvertible`, you've moved the privacy decision from the call site to the type's description. The next reader has to know that. Avoid relying on `description` for log output — interpolate the specific fields you care about.

### Concatenating before passing in

```swift
let msg = "User \(email) failed login"
logger.info("\(msg)")  // BAD — `msg` is a fully dynamic string
```

The whole interpolation collapses into one dynamic value, redacted as a unit. You lose the ability to mark literal portions as `.public`. Always pass the structured interpolation directly to the logger:

```swift
logger.info("User \(email, privacy: .private) failed login")
```

### Treating `.public` as "safe by default"

`.public` is opt-in for a reason. Adding it to a value that later changes type or scope (e.g., a "user ID" that becomes "session token" in v2) silently turns a logging change into a privacy regression. Reserve `.public` for values that are inherently non-PII (numbers, enum cases, your own opaque identifiers).

## The DEBUG/RELEASE escape hatch

A common mistake is adding `#if DEBUG` around verbose loggers and assuming production gets only the `release` lines:

```swift
#if DEBUG
logger.info("Fetched: \(item)")
#endif
```

This hides the call entirely in release — fine — but it does not change anything about how `Logger` redacts other lines. Don't use `#if DEBUG` as a privacy mechanism. Use `privacy:` modifiers on every dynamic interpolation regardless of configuration. The `#if` adds a maintenance liability (production diverges from development) without solving the actual problem.

## Subsystem and category — for filtering, not privacy

Subsystems and categories control filtering in Console.app and `log stream`, not privacy:

```swift
private let auth = Logger(subsystem: "com.acme.app", category: "auth")
private let net  = Logger(subsystem: "com.acme.app", category: "network")
```

In Console.app, filter by `subsystem:com.acme.app category:auth` to see only one feature's logs. This is independent of redaction — a `.private` value remains redacted regardless of category.

Group categories along the lines of "what do I want to see together when debugging X" — usually feature areas (`auth`, `sync`, `storage`, `payments`) rather than layers (`network`, `parsing`).

## Reading redacted logs from a real device

Three sources, in order of preference:

1. **`log stream`** from a Mac connected via cable. Run `log stream --predicate 'subsystem == "com.acme.app"'`. Live, full output, redacted in release.
2. **`log show --last 1h`** to dump the buffer. Useful for failures that already happened.
3. **`sysdiagnose`** (Settings → Privacy & Security → Analytics → Privacy → Sysdiagnose Logs) for a full dump. `.sensitive` values are dropped here.

For production users, `MetricKit`'s diagnostic payloads forward a redacted slice of logs — see `metrickit.md`. You will not see `.private` content in those payloads either; design your redaction policy assuming you only ever see `.public` values from the field.

## Migrating from `print` and `NSLog`

`print` and `NSLog` have no concept of privacy — every value is `.public` by definition. A blind sed replacement to `Logger` will silently mark every value as redacted in release, which often looks like "logging stopped working." Plan the migration in two passes:

1. Replace the call site with `Logger.<level>(...)`. Compile.
2. For each interpolation, decide: is this safe to mark `.public`, or do I want it redacted?

Do not skip step 2. Defaulting everything to `.public` defeats the purpose of switching; defaulting everything to `.private` makes the logs useless.

## Rules

- Annotate every dynamic interpolation with an explicit `privacy:` argument — never rely on the default.
- Use `.sensitive` for tokens, passwords, and credentials so they are also stripped from sysdiagnose.
- Use `.private(mask: .hash)` when you need to correlate sessions on PII without exposing the value.
- Never interpolate whole model objects; pick specific fields.
- Subsystems and categories are for filtering, not privacy; keep them stable across releases.
- When migrating from `print`/`NSLog`, decide privacy per call site, not in bulk.
- If you cannot decide, redact and reconsider later — opting out of redaction later is safe; opting in after PII has shipped to logs is not.
