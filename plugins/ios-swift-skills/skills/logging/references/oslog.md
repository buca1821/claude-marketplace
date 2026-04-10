# OSLog — Structured Logging

## Logger Setup

```swift
import os

extension Logger {
    /// Subsystem = Bundle ID (identifies the app)
    private static let subsystem = Bundle.main.bundleIdentifier ?? "com.app"

    // One logger per feature area
    static let network = Logger(subsystem: subsystem, category: "Network")
    static let auth = Logger(subsystem: subsystem, category: "Auth")
    static let sync = Logger(subsystem: subsystem, category: "Sync")
    static let ui = Logger(subsystem: subsystem, category: "UI")
    static let storage = Logger(subsystem: subsystem, category: "Storage")
}
```

## Log Levels

| Level | When to Use | Persisted | Performance |
|-------|------------|-----------|-------------|
| `.debug` | Development-only tracing | No (streaming only) | Negligible |
| `.info` | Helpful but not critical | No (unless collected) | Low |
| `.notice` | Important events (default) | Yes | Low |
| `.error` | Recoverable errors | Yes | Low |
| `.fault` | Critical failures, bugs | Yes + stack | Low |

## Usage

```swift
// Debug — development only, not persisted
Logger.network.debug("Fetching items from \(endpoint)")

// Info — useful context, not always persisted
Logger.auth.info("User login attempt for \(userID, privacy: .private)")

// Notice — default level, important events
Logger.sync.notice("Sync completed: \(itemCount) items updated")

// Error — something went wrong but recoverable
Logger.network.error("Request failed: \(error.localizedDescription)")

// Fault — critical bug, should never happen
Logger.storage.fault("Database corruption detected in \(tableName)")
```

## Privacy

OSLog redacts dynamic data by default in production. Control with `privacy`:

```swift
// Public — visible in production logs
Logger.network.info("Status code: \(statusCode, privacy: .public)")

// Private — redacted in production (default for strings/objects)
Logger.auth.info("User email: \(email, privacy: .private)")

// Auto — public for numeric types, private for strings (default)
Logger.network.debug("Response size: \(byteCount)") // Auto = public (numeric)
Logger.auth.debug("Token: \(token)")                 // Auto = private (string)

// Hashed — shows consistent hash, useful for correlation
Logger.auth.info("Session: \(sessionID, privacy: .private(mask: .hash))")
```

## Formatting

```swift
// Alignment and padding
Logger.network.debug("Size: \(byteCount, align: .right(columns: 10))")

// Hex
Logger.storage.debug("Flags: \(flags, format: .hex)")

// Boolean
Logger.ui.debug("Dark mode: \(isDarkMode, format: .answer)") // "yes"/"no"
```

## Signpost Integration

For performance measurement:

```swift
let signposter = OSSignposter(logger: Logger.network)

func fetchItems() async throws -> [Item] {
    let signpostID = signposter.makeSignpostID()
    let state = signposter.beginInterval("FetchItems", id: signpostID)

    defer {
        signposter.endInterval("FetchItems", state)
    }

    return try await apiClient.request(.get("/items"))
}
```

## Viewing Logs

### Console.app
- Filter by subsystem: `subsystem:com.yourapp`
- Filter by category: `category:Network`
- Filter by level: `type:error`

### Terminal
```bash
# Stream logs from simulator
log stream --predicate 'subsystem == "com.yourapp"' --level debug

# Collect from device
log collect --device --last 1h --output app.logarchive
```

### In Xcode
Debug console shows OSLog output during debugging.

## Migration from print()

```swift
// BEFORE
print("Loading items...")                    // ❌
print("Error: \(error)")                     // ❌
NSLog("User tapped button")                  // ❌

// AFTER
Logger.storage.debug("Loading items...")      // ✅
Logger.network.error("Request failed: \(error.localizedDescription)") // ✅
Logger.ui.info("User tapped \(buttonName, privacy: .public)")        // ✅
```

## Rules

- One `Logger` extension per app — static properties per category
- Use appropriate log level — don't default everything to `.error`
- Never log sensitive data as `.public`
- Use `privacy: .private(mask: .hash)` for correlating private data
- Use signposts for performance measurement, not log timestamps
- Remove all `print()` and `NSLog()` from production code
