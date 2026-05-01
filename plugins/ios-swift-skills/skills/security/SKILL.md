---
name: security
description: iOS app security — Keychain (with access groups and biometric ACLs), App Transport Security, certificate pinning, secrets management, biometric authentication, and privacy manifests. Use when storing sensitive data, configuring network security, handling authentication, or preparing for App Store submission.
---

# iOS Security Skill

## Operating Rules

- Never store sensitive data in `UserDefaults`, plist files, or plain text. Keychain only.
- Always pair high-value Keychain items with `SecAccessControl` (biometric) and `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` accessibility — biometry without access control is convenience, not security.
- Keep App Transport Security enabled. Exceptions require justification documented per-domain.
- Never hardcode API keys, secrets, or credentials in source code. Build-time secrets via `.xcconfig` (gitignored); runtime secrets via Keychain.
- `LocalAuthentication` is for UX confirmation. Storage security comes from `SecAccessControl` on the Keychain item — not from gating reads with `LAContext.evaluatePolicy`.
- `PrivacyInfo.xcprivacy` is mandatory for App Store submission. Treat it as compulsory, not optional. Audit it in every PR that touches the data path.
- Use CryptoKit for cryptographic operations; CommonCrypto only when bridging legacy.
- Follow OWASP MASVS for the threat model and a baseline checklist.

## Topic Router

| Topic | Reference |
|-------|-----------|
| Keychain CRUD, accessibility levels, biometric ACLs, access groups, app↔extension sharing | `references/keychain.md` |
| Biometric authentication (`LocalAuthentication` + Keychain ACLs, error handling) | `references/biometric.md` |
| App Transport Security and certificate pinning | `references/network-security.md` |
| Build-time and runtime secrets management | `references/secrets-management.md` |
| Privacy manifests (`PrivacyInfo.xcprivacy`, Required Reason APIs, third-party SDKs) | `references/privacy-manifests.md` |

## Task Workflow

### Audit security posture

1. Scan for hardcoded secrets (API keys, tokens, passwords).
2. Check storage: Keychain vs UserDefaults for every sensitive item; verify accessibility levels and ACLs.
3. Verify ATS configuration in Info.plist; document each exception.
4. Review authentication flows; check biometric items use `SecAccessControl`, not just `LAContext`.
5. Verify `PrivacyInfo.xcprivacy` covers every Required Reason API and every data category collected.
6. Check third-party SDKs ship their own privacy manifests and are signed.
7. Verify nothing logs sensitive data — see the `logging` skill (`privacy-redaction` reference).

### Implement secure storage

- Default to Keychain for any user-bound data.
- Pair high-value items with biometric ACL using `.biometryCurrentSet` and `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly`.
- For app-extension sharing, use access groups (see `references/keychain.md`).
- Wrap Keychain access in a `Sendable` protocol for testability.

### Configure network security

- Implement certificate pinning via SPKI hashing for sensitive endpoints.
- Validate server certificates in `URLSessionDelegate`.
- Treat ATS exceptions as a conscious decision per-domain, not a global toggle.

### Manage secrets

- Build-time secrets in `.xcconfig` files, gitignored.
- CI injects secrets via environment variables, never via committed files.
- Runtime secrets in Keychain, never in `UserDefaults` or files.

### Prepare a release

- Validate `PrivacyInfo.xcprivacy` matches actual app behavior — no undeclared collection, no missing API reasons.
- Confirm App Store Connect privacy nutrition label matches the manifest.
- Confirm all third-party SDKs include their manifests.

## Security Checklist

- [ ] No hardcoded API keys or secrets in source code (`grep` for common patterns).
- [ ] Sensitive data stored in Keychain with `kSecAttrAccessible*ThisDeviceOnly`.
- [ ] High-value Keychain items pair with `SecAccessControl(.biometryCurrentSet)`.
- [ ] App-extension keychain sharing uses explicit `kSecAttrAccessGroup`.
- [ ] ATS enabled; each exception is documented with a justification.
- [ ] Certificate pinning on sensitive API endpoints (SPKI hash).
- [ ] `.xcconfig` and `.env` files in `.gitignore`.
- [ ] Biometric flows distinguish `.userCancel` from real errors.
- [ ] `LAContext.evaluatePolicy` not relied on alone for stored secrets.
- [ ] `PrivacyInfo.xcprivacy` exists and includes `UserDefaults` (`CA92.1`).
- [ ] Every data category collected is declared in `NSPrivacyCollectedDataTypes`.
- [ ] Third-party SDKs have their own privacy manifests and are signed.
- [ ] No sensitive data in logs (`%{public}@` not used for tokens).
- [ ] Privacy-sensitive APIs have usage descriptions in Info.plist.
