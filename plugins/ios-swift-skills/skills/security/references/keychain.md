# Keychain Storage

## When to Use Keychain

| Data Type | Storage | Why |
|-----------|---------|-----|
| Auth tokens | Keychain | Encrypted, persists across reinstalls |
| Passwords | Keychain | Hardware-backed encryption |
| API keys (runtime) | Keychain | Not visible in binary |
| User preferences | UserDefaults | Not sensitive |
| Cached data | FileManager | Not sensitive, purgeable |
| Feature flags | UserDefaults / Remote config | Not sensitive |

## Basic Keychain Operations

### Save

```swift
func saveToKeychain(data: Data, for key: String) throws {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
    ]

    // Delete existing item first
    SecItemDelete(query as CFDictionary)

    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else {
        throw KeychainError.saveFailed(status)
    }
}
```

### Read

```swift
func readFromKeychain(for key: String) throws -> Data {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecReturnData as String: true,
        kSecMatchLimit as String: kSecMatchLimitOne
    ]

    var result: AnyObject?
    let status = SecItemCopyMatching(query as CFDictionary, &result)

    guard status == errSecSuccess, let data = result as? Data else {
        throw KeychainError.readFailed(status)
    }
    return data
}
```

### Delete

```swift
func deleteFromKeychain(for key: String) throws {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key
    ]

    let status = SecItemDelete(query as CFDictionary)
    guard status == errSecSuccess || status == errSecItemNotFound else {
        throw KeychainError.deleteFailed(status)
    }
}
```

## Accessibility Levels

| Level | When Available | Migrates to New Device |
|-------|---------------|----------------------|
| `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | When unlocked | No — **recommended default** |
| `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` | After first unlock | No — background access |
| `kSecAttrAccessibleWhenUnlocked` | When unlocked | Yes |
| `kSecAttrAccessibleAfterFirstUnlock` | After first unlock | Yes |

**Default recommendation**: `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` — most secure, prevents backup extraction.

## Access Groups — Sharing Items Across Targets

Keychain items default to being scoped per-app (per bundle ID + team prefix). To share an item between an app and its extension, between two apps from the same team, or among the targets in an app group, use `kSecAttrAccessGroup`.

### App ↔ extension / widget

This is the most common case. The app saves an auth token; the widget needs to read it to show authenticated state.

**1. Add an App Group entitlement.** In each target (app, extension, widget), Signing & Capabilities → `+ Capability` → App Groups → `+ group.com.acme.app`. The same group ID must be added to every target that needs to share.

**2. Add a Keychain Sharing entitlement.** Same panel → `+ Capability` → Keychain Sharing → `+ com.acme.app` (the keychain group name; conventionally the same as the bundle ID prefix). Apple writes this into the entitlements file as `keychain-access-groups`.

**3. Save and read with the group:**

```swift
let group = "ABCDE12345.com.acme.app"   // Team ID prefix + group name

func saveToSharedKeychain(_ data: Data, for key: String) throws {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecAttrService as String: "com.acme.app",
        kSecAttrAccessGroup as String: group,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlock,
    ]
    SecItemDelete(query as CFDictionary)
    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else { throw KeychainError.saveFailed(status) }
}

func readFromSharedKeychain(for key: String) throws -> Data {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecAttrService as String: "com.acme.app",
        kSecAttrAccessGroup as String: group,
        kSecReturnData as String: true,
        kSecMatchLimit as String: kSecMatchLimitOne,
    ]
    var result: AnyObject?
    let status = SecItemCopyMatching(query as CFDictionary, &result)
    guard status == errSecSuccess, let data = result as? Data else {
        throw KeychainError.readFailed(status)
    }
    return data
}
```

The `Team ID + .` prefix is mandatory — without it, the keychain returns `errSecMissingEntitlement` (-34018). Get the team prefix from `$(AppIdentifierPrefix)` in build settings, or hardcode the 10-char team ID.

### Background access from extensions

Extensions and widgets often run while the device is locked (e.g., a widget refreshing on the lock screen). Use `kSecAttrAccessibleAfterFirstUnlock` for shared items the extension needs in the background — `kSecAttrAccessibleWhenUnlocked` will fail to retrieve the item.

The trade-off: items accessible after first unlock are slightly less protected (the encryption key is in memory after first unlock). Use the most restrictive level the extension's behavior allows.

### Sharing between two apps from the same team

Less common, but supported: two completely separate apps under the same Apple Developer team can share keychain items by using the same access group. Each app declares the same `keychain-access-groups` entitlement, and uses the same `kSecAttrAccessGroup` in its queries.

For sign-on continuity between a free and a pro version of the same product, this is the cleanest approach — no server round-trip needed to detect "user has already signed in on the other app."

### Avoiding silent leaks across targets

Items written without specifying `kSecAttrAccessGroup` go to the *first* group in the `keychain-access-groups` list — usually the app's bundle ID. Reads behave the same way. Two consequences:

- An app with multiple groups can write to one and unintentionally read from another. Always set `kSecAttrAccessGroup` explicitly on every query, even within a single app, once you've added Keychain Sharing.
- Migrating a previously single-target app to use sharing requires re-saving items into the explicit group; old items remain in the default group invisible to other targets.

A migration helper:

```swift
func migrateLegacyItem(_ key: String) throws {
    let unscopedQuery: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecReturnData as String: true,
    ]
    var result: AnyObject?
    guard SecItemCopyMatching(unscopedQuery as CFDictionary, &result) == errSecSuccess,
          let data = result as? Data else { return }

    try saveToSharedKeychain(data, for: key)
    SecItemDelete(unscopedQuery as CFDictionary)
}
```

Run this on launch after introducing sharing; it's idempotent.

## Biometric-Protected Items

```swift
let access = SecAccessControlCreateWithFlags(
    nil,
    kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
    .biometryCurrentSet, // Invalidates if biometrics change
    nil
)

let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: key,
    kSecValueData as String: data,
    kSecAttrAccessControl as String: access as Any
]
```

## Protocol-Based Wrapper (for DI/testing)

```swift
protocol KeychainServiceProtocol: Sendable {
    func save(_ data: Data, for key: String) throws
    func read(for key: String) throws -> Data
    func delete(for key: String) throws
}

final class KeychainService: KeychainServiceProtocol {
    func save(_ data: Data, for key: String) throws { /* ... */ }
    func read(for key: String) throws -> Data { /* ... */ }
    func delete(for key: String) throws { /* ... */ }
}

// In tests
final class MockKeychainService: KeychainServiceProtocol {
    var storage: [String: Data] = [:]
    func save(_ data: Data, for key: String) throws { storage[key] = data }
    func read(for key: String) throws -> Data {
        guard let data = storage[key] else { throw KeychainError.readFailed(errSecItemNotFound) }
        return data
    }
    func delete(for key: String) throws { storage.removeValue(forKey: key) }
}
```

## Keychain Error Handling

```swift
enum KeychainError: Error, LocalizedError {
    case saveFailed(OSStatus)
    case readFailed(OSStatus)
    case deleteFailed(OSStatus)

    var errorDescription: String? {
        switch self {
        case .saveFailed(let status): "Keychain save failed: \(status)"
        case .readFailed(let status): "Keychain read failed: \(status)"
        case .deleteFailed(let status): "Keychain delete failed: \(status)"
        }
    }
}
```

## Rules

- Always use `ThisDeviceOnly` accessibility unless migration is required
- Delete before add to avoid `errSecDuplicateItem`
- Wrap Keychain in a protocol for dependency injection and testing
- Never log Keychain data or include it in crash reports
- Use `kSecAttrService` to namespace keys by app/feature
