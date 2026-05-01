# Biometric Authentication

Face ID and Touch ID let your app gate access to sensitive features and protect Keychain items so they can only be retrieved when the user actively authenticates. The two parts of this — "ask the user to authenticate" and "store something only unlockable with biometrics" — use different APIs and serve different threat models. Mixing them up is the most common source of security holes.

## Two distinct things

| Goal | API | What it actually verifies |
|---|---|---|
| "Is there a real user here right now?" | `LocalAuthentication` (`LAContext`) | A live biometric match against the enrolled template, in this app, just now |
| "This Keychain item should only be readable with biometrics" | `SecAccessControl` on the Keychain item | The keychain enforces it at retrieval time, regardless of the calling app's logic |

`LocalAuthentication` alone is **not** secure storage. The app can be patched, the policy decision can be subverted, and an attacker who can run code in your process can simply skip the call. Use it for UX gating ("show me the secret notes screen") backed by a Keychain item with `SecAccessControl` for actual security.

The reverse — Keychain with biometric ACL — is enforced by the OS. The keychain daemon itself prompts for biometrics; your code cannot bypass it because your code never sees the data without successful auth.

**Rule:** if the threat is "an attacker has unsupervised access to an unlocked device," only `SecAccessControl` helps. If the threat is "the user wants confirmation before this action," `LAContext` is fine.

## LAContext — policy decisions

```swift
import LocalAuthentication

func authenticateUser() async throws {
    let context = LAContext()
    var error: NSError?

    guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
        throw error ?? AuthError.biometricsUnavailable
    }

    do {
        let success = try await context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: "Sign in to your account"
        )
        guard success else { throw AuthError.biometricsFailed }
    } catch let error as LAError {
        throw mapLAError(error)
    }
}
```

Two policies:

| Policy | Behavior |
|---|---|
| `.deviceOwnerAuthenticationWithBiometrics` | Biometrics only. Fails if biometrics unavailable, lockout, or user cancels |
| `.deviceOwnerAuthentication` | Biometrics with passcode fallback. Fails only if device passcode is also unset |

Pick `.deviceOwnerAuthentication` for most app-level gates — users with a forgotten/lockout state shouldn't be locked out of your app. Pick `.deviceOwnerAuthenticationWithBiometrics` only when biometrics-or-nothing matches the threat model (e.g., a banking app that explicitly wants to refuse passcode fallback).

The `localizedReason` is shown in the system biometric prompt. Make it actionable: "Sign in to your account" beats "Authenticate."

## SecAccessControl — biometric-protected Keychain items

```swift
import Security

func saveSecret(_ data: Data, for account: String) throws {
    var error: Unmanaged<CFError>?
    guard let access = SecAccessControlCreateWithFlags(
        nil,
        kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
        .biometryCurrentSet,
        &error
    ) else {
        throw KeychainError.acl(error?.takeRetainedValue())
    }

    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: account,
        kSecAttrService as String: "com.acme.app",
        kSecAttrAccessControl as String: access,
        kSecValueData as String: data,
    ]

    SecItemDelete(query as CFDictionary)
    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else { throw KeychainError.save(status) }
}

func loadSecret(for account: String) async throws -> Data {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: account,
        kSecAttrService as String: "com.acme.app",
        kSecReturnData as String: true,
        kSecUseOperationPrompt as String: "Unlock your saved data",
    ]

    var item: CFTypeRef?
    let status = SecItemCopyMatching(query as CFDictionary, &item)
    guard status == errSecSuccess, let data = item as? Data else {
        throw KeychainError.load(status)
    }
    return data
}
```

The keychain prompts the user automatically on `SecItemCopyMatching` when an ACL requires biometrics. You don't need to wrap the call in `LAContext.evaluatePolicy` — the keychain handles it. The `kSecUseOperationPrompt` value is shown in the prompt, same role as `localizedReason`.

## ACL flag choice

```
.biometryAny        — any enrolled biometric works
.biometryCurrentSet — only the currently enrolled set; invalidates on enrollment change
.userPresence       — biometrics OR passcode
.devicePasscode     — passcode only (no biometrics)
```

The most security-relevant decision is `.biometryAny` vs `.biometryCurrentSet`:

- **`.biometryAny`** — the keychain item remains accessible after the user adds a new fingerprint or rescans Face ID. Convenient. Slightly weaker: an attacker who has the device unlocked momentarily and adds their own biometric can later access the item.
- **`.biometryCurrentSet`** — the keychain item is **deleted automatically** when biometrics enrollment changes. The user must re-authenticate (e.g., re-enter their account password) to re-create the item. More secure; more annoying.

Pick `.biometryCurrentSet` for high-value secrets (auth tokens, payment credentials). Pick `.biometryAny` for less sensitive convenience (saved password for a non-critical service).

## Accessibility levels — the second axis

`SecAccessControlCreateWithFlags` takes both an accessibility constant and a flag set. The accessibility decides *when* the OS allows access independent of the ACL:

| Constant | Available when |
|---|---|
| `kSecAttrAccessibleWhenUnlocked` | Device is unlocked |
| `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` | Device is unlocked AND not on a backup |
| `kSecAttrAccessibleAfterFirstUnlock` | After first unlock since boot (background access OK) |
| `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` | Device passcode is set; if user removes passcode, item is deleted |

For biometric-protected items, **always pair with `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly`**. It enforces the device has a passcode (a precondition for biometrics) and prevents the item from being restored to a different device via iCloud Keychain backup — biometric ACLs on a different device's enrollment is a meaningless concept.

## Error handling

`LAError` codes you must distinguish:

| Code | Meaning | UX response |
|---|---|---|
| `.userCancel` | User tapped "Cancel" | Silent — they explicitly opted out |
| `.userFallback` | User tapped "Enter Password" / "Use Passcode" | Switch flow to fallback path |
| `.systemCancel` | System interrupted (call, lock screen, app backgrounded) | Allow retry; do not treat as user denial |
| `.biometryNotEnrolled` | Device has no enrolled biometrics | Prompt user to set up Face ID/Touch ID |
| `.biometryNotAvailable` | Hardware missing or disabled | Fall back to password / disable feature |
| `.biometryLockout` | Too many failed attempts; passcode required to unlock | Show explanatory message; offer passcode fallback |
| `.passcodeNotSet` | Device has no passcode | Cannot use biometrics; prompt setup |
| `.appCancel` | Your app cancelled the operation programmatically | Internal state issue |

Most apps need two distinct messages: one for `.userCancel` (don't show error UI) and one bucket for everything else (show "Authentication failed, try again or use password"). Don't surface technical error codes — users don't care.

```swift
func mapLAError(_ error: LAError) -> AuthError {
    switch error.code {
    case .userCancel, .systemCancel, .appCancel:
        return .cancelled
    case .userFallback:
        return .needsFallback
    case .biometryNotEnrolled, .biometryNotAvailable, .passcodeNotSet:
        return .unavailable
    case .biometryLockout:
        return .lockedOut
    default:
        return .failed
    }
}
```

## Detecting biometry type for UI

Show a Face ID icon vs a Touch ID icon based on what the device has:

```swift
func biometryType() -> LABiometryType {
    let context = LAContext()
    _ = context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: nil)
    return context.biometryType
}
```

`canEvaluatePolicy` must be called first — `biometryType` is `.none` until then. Possible values: `.none`, `.touchID`, `.faceID`, `.opticID` (Vision Pro).

For accessibility, also offer a path that doesn't require biometrics — some users disable them or have hardware issues. A "Use password instead" button covers `.userFallback` and accessibility cases simultaneously.

## What biometrics doesn't protect against

A list to be honest with yourself about:

- **Jailbroken devices** — biometric checks can be patched. Combine with App Attest if the threat is high-value (see `app-attest.md` in a future skill).
- **Coerced unlock** — physical compulsion. Biometrics make this trivially fast for an attacker with the user.
- **Sleeping/unconscious user** — biometric auth can succeed against an unconscious user, particularly Touch ID. iOS mitigates partially with attention detection on Face ID.
- **Cloned biometrics** — rare in practice for Face ID/Touch ID generation 2+, but documented vulnerabilities exist.
- **Replay/MITM at the OS layer** — modulo OS-level vulnerabilities, your app doesn't see the biometric data; the OS attests success. Trust that boundary.

For most apps, the threat model is "lost or stolen device," and biometrics + passcode is sufficient. For a banking, medical, or government app, layer App Attest, server-side risk scoring, and additional auth steps for high-value operations.

## Migration from `LAContext`-only flows

A common legacy pattern: store a token in plain Keychain (no ACL), gate access via `LAContext` in code. This is insecure — anyone reading the binary or jailbreaking can extract the token directly.

The migration:

1. On next successful login, save the token *with* `SecAccessControl(.biometryCurrentSet)`.
2. Delete the unprotected item.
3. Subsequent reads use `SecItemCopyMatching` with `kSecUseOperationPrompt`. The OS prompts; no `LAContext` needed.

The user perceives the change as "now I have to use Face ID." The actual security level moves from "trust the app's code" to "trust the OS's enforcement."

## Rules

- `LAContext` for UX confirmation; `SecAccessControl` for actual security.
- Pair biometric ACL with `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly`.
- Use `.biometryCurrentSet` for high-value secrets; `.biometryAny` for convenience-only data.
- Always offer a password fallback for accessibility and for `.userFallback` paths.
- Distinguish `.userCancel` from real errors — don't show error UI when the user just tapped Cancel.
- Show the right icon (Face ID / Touch ID / Optic ID) based on `biometryType` after `canEvaluatePolicy`.
- Don't trust `LAContext.evaluatePolicy` alone for stored secrets — always back with a Keychain ACL.
- For sensitive apps, add App Attest and server-side risk scoring on top.
- Migrate plain-Keychain-plus-LAContext setups to ACL-enforced storage.
