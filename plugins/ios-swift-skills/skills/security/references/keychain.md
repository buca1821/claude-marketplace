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
