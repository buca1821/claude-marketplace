# Secrets Management

## The Rules

1. **Never** hardcode secrets in source code
2. **Never** commit secrets to git
3. **Never** include secrets in the app bundle
4. Secrets in source = secrets in every user's device (trivially extractable)

## Build-Time Secrets (.xcconfig)

For API keys needed at compile time (e.g., analytics, maps):

### Setup

```
// Config/Debug.xcconfig (NOT committed to git)
API_KEY = your-debug-api-key-here
BASE_URL = https:$(/)$(/)api-staging.example.com

// Config/Release.xcconfig (NOT committed to git)
API_KEY = your-production-api-key-here
BASE_URL = https:$(/)$(/)api.example.com
```

### Info.plist Reference

```xml
<key>API_KEY</key>
<string>$(API_KEY)</string>
<key>BASE_URL</key>
<string>$(BASE_URL)</string>
```

### Access in Code

```swift
enum Configuration {
    static let apiKey: String = {
        guard let key = Bundle.main.infoDictionary?["API_KEY"] as? String,
              !key.isEmpty else {
            fatalError("API_KEY not configured — check .xcconfig files")
        }
        return key
    }()

    static let baseURL: URL = {
        guard let urlString = Bundle.main.infoDictionary?["BASE_URL"] as? String,
              let url = URL(string: urlString) else {
            fatalError("BASE_URL not configured — check .xcconfig files")
        }
        return url
    }()
}
```

### .gitignore

```gitignore
# Secrets
Config/Debug.xcconfig
Config/Release.xcconfig
*.xcconfig.local
```

### Template for Team Members

```
// Config/Debug.xcconfig.template (committed to git)
// Copy this file to Debug.xcconfig and fill in values
// DO NOT commit Debug.xcconfig
API_KEY = <your-api-key>
BASE_URL = https:$(/)$(/)api-staging.example.com
```

## CI/CD Secret Injection

### GitHub Actions

```yaml
# .github/workflows/build.yml
jobs:
  build:
    steps:
      - name: Create xcconfig from secrets
        run: |
          echo "API_KEY = ${{ secrets.API_KEY }}" > Config/Release.xcconfig
          echo "BASE_URL = ${{ secrets.BASE_URL }}" >> Config/Release.xcconfig
```

### Environment Variables in Xcode Cloud

Xcode Cloud supports secrets natively — add them in App Store Connect under CI/CD → Workflows → Environment Variables (mark as Secret).

## Runtime Secrets

For tokens received after authentication:

```swift
// Store in Keychain immediately after receiving
func handleLoginResponse(_ response: LoginResponse) async throws {
    let tokenData = Data(response.accessToken.utf8)
    try keychainService.save(tokenData, for: "access_token")

    // Never store in:
    // - UserDefaults ❌
    // - @AppStorage ❌
    // - In-memory singleton that logs ❌
    // - Files without data protection ❌
}
```

## What Goes Where

| Secret Type | Storage | Lifetime |
|-------------|---------|----------|
| API keys (build-time) | .xcconfig → Info.plist | Build |
| Auth tokens | Keychain | Session |
| Refresh tokens | Keychain (biometric) | Long-lived |
| Encryption keys | Keychain | Permanent |
| Feature flags | Remote config | Dynamic |
| User preferences | UserDefaults | Permanent |

## Detecting Hardcoded Secrets

Common patterns to scan for:

```swift
// BAD — hardcoded secrets
let apiKey = "sk-abc123..."           // ❌ String literal key
let secret = "Bearer eyJhbGciOiJ..."  // ❌ Hardcoded token
let password = "P@ssw0rd"             // ❌ Hardcoded password

// GOOD — from configuration or Keychain
let apiKey = Configuration.apiKey      // ✅ From xcconfig
let token = try keychainService.read(for: "access_token") // ✅ From Keychain
```

## @AppStorage Security

`@AppStorage` uses UserDefaults — **never** store sensitive data:

```swift
// GOOD — non-sensitive preferences
@AppStorage("hasCompletedOnboarding") private var hasCompletedOnboarding = false
@AppStorage("selectedTheme") private var selectedTheme = "default"

// BAD — sensitive data
@AppStorage("authToken") private var authToken = ""     // ❌ Use Keychain
@AppStorage("userPassword") private var password = ""   // ❌ Use Keychain
```

## Rules

- .xcconfig files for build-time secrets, Keychain for runtime secrets
- .xcconfig files must be in .gitignore with .template committed
- CI/CD injects secrets into .xcconfig at build time
- @AppStorage is UserDefaults — never for sensitive data
- Audit for hardcoded strings matching key/token/secret/password patterns
