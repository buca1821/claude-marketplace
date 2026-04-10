---
name: security
description: iOS app security best practices — Keychain, App Transport Security, certificate pinning, secrets management, data protection, and OWASP MASVS compliance. Use when storing sensitive data, configuring network security, handling authentication, or auditing security posture.
---

# iOS Security Skill

## Operating Rules

- Never store sensitive data in UserDefaults, plist files, or plain text
- Always use Keychain Services for tokens, passwords, and cryptographic keys
- Keep App Transport Security (ATS) enabled — exceptions require justification
- Never hardcode API keys, secrets, or credentials in source code
- Follow OWASP MASVS (Mobile Application Security Verification Standard)
- Use CryptoKit for cryptographic operations (not CommonCrypto)

## Task Workflow

### Audit security posture
1. Scan for hardcoded secrets (API keys, tokens, passwords)
2. Check data storage (Keychain vs UserDefaults for sensitive data)
3. Verify ATS configuration in Info.plist
4. Review authentication flows
5. Check data protection levels on files
6. Verify third-party SDK data handling

### Implement secure storage
- Consult `references/keychain.md` for Keychain patterns
- Use appropriate access control and accessibility levels
- Consider biometric protection for high-value data

### Configure network security
- Consult `references/network-security.md` for ATS and pinning
- Implement certificate pinning for sensitive API endpoints
- Validate server certificates in URLSessionDelegate

### Manage secrets
- Consult `references/secrets-management.md` for build-time and runtime patterns
- Use .xcconfig files excluded from git for build-time secrets
- Inject secrets via CI/CD environment variables

### Topic Router

| Topic | Reference |
|-------|-----------|
| Keychain storage | `references/keychain.md` |
| Network security (ATS, pinning) | `references/network-security.md` |
| Secrets management | `references/secrets-management.md` |

## Security Checklist

- [ ] No hardcoded API keys or secrets in source code
- [ ] Sensitive data stored in Keychain (not UserDefaults)
- [ ] ATS enabled with no unnecessary exceptions
- [ ] Certificate pinning on sensitive API endpoints
- [ ] .xcconfig and .env files in .gitignore
- [ ] Data protection level set on sensitive files
- [ ] Biometric auth uses LocalAuthentication correctly
- [ ] No sensitive data in logs (print/NSLog/os_log)
- [ ] Privacy-sensitive APIs have usage descriptions in Info.plist
- [ ] Third-party SDKs reviewed for data collection
