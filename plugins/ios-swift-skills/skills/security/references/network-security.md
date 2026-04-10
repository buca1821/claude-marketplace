# Network Security

## App Transport Security (ATS)

ATS is enabled by default — all connections must use HTTPS with TLS 1.2+. **Keep it enabled.**

### Checking ATS Configuration

```xml
<!-- Info.plist — GOOD: no ATS exceptions needed -->
<!-- Simply don't add NSAppTransportSecurity -->

<!-- BAD — disables ATS globally -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

<!-- ACCEPTABLE — exception for a specific domain with justification -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>legacy-api.example.com</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSExceptionMinimumTLSVersion</key>
            <string>TLSv1.2</string>
        </dict>
    </dict>
</dict>
```

### ATS Rules

- Never use `NSAllowsArbitraryLoads: true` — Apple may reject
- If an exception is needed, use per-domain exceptions
- Document WHY the exception is necessary
- Plan migration to HTTPS for excepted domains

## Certificate Pinning

Pin the **SPKI hash** (Subject Public Key Info), not the full certificate — survives certificate renewal.

### URLSession Delegate Approach

```swift
final class PinnedSessionDelegate: NSObject, URLSessionDelegate {
    // SHA-256 hash of the server's SPKI
    private let pinnedHashes: Set<String> = [
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", // Primary
        "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=", // Backup
    ]

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge
    ) async -> (URLSession.AuthChallengeDisposition, URLCredential?) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            return (.cancelAuthenticationChallenge, nil)
        }

        // Evaluate trust
        var error: CFError?
        guard SecTrustEvaluateWithError(serverTrust, &error) else {
            return (.cancelAuthenticationChallenge, nil)
        }

        // Check pinned hashes
        let serverCertCount = SecTrustGetCertificateCount(serverTrust)
        for index in 0..<serverCertCount {
            guard let certificate = SecTrustCopyCertificateChain(serverTrust)?[index] else {
                continue
            }
            let publicKey = SecCertificateCopyKey(certificate as! SecCertificate)
            if let publicKeyData = SecKeyCopyExternalRepresentation(publicKey!, nil) as Data? {
                let hash = SHA256.hash(data: publicKeyData)
                let hashString = Data(hash).base64EncodedString()
                if pinnedHashes.contains(hashString) {
                    return (.useCredential, URLCredential(trust: serverTrust))
                }
            }
        }

        return (.cancelAuthenticationChallenge, nil)
    }
}
```

### Getting SPKI Hash

```bash
# From a live server
openssl s_client -connect api.example.com:443 2>/dev/null | \
    openssl x509 -pubkey -noout | \
    openssl pkey -pubin -outform DER | \
    openssl dgst -sha256 -binary | \
    base64
```

### Pinning Best Practices

- Pin at least 2 hashes (primary + backup key)
- Pin SPKI hashes, not full certificates
- Have a rotation plan before pins expire
- Consider pinning the intermediate CA instead of leaf for easier rotation
- Implement a fallback mechanism (e.g., remote config to update pins)

## Secure URLSession Configuration

```swift
let configuration = URLSessionConfiguration.default
configuration.tlsMinimumSupportedProtocolVersion = .TLSv12
configuration.httpShouldSetCookies = false // Unless needed
configuration.urlCache = nil // For sensitive endpoints

let session = URLSession(
    configuration: configuration,
    delegate: PinnedSessionDelegate(),
    delegateQueue: nil
)
```

## Request Security

```swift
// Always validate URLs
guard let url = URL(string: endpoint),
      url.scheme == "https" else {
    throw NetworkError.invalidURL
}

// Sanitize headers — never include sensitive data in URLs
var request = URLRequest(url: url)
request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
// NOT: URL(string: "https://api.example.com?token=\(token)")
```

## Rules

- ATS must remain enabled — no global exceptions
- Pin SPKI hashes with at least one backup
- Auth tokens go in headers, never in URLs
- Disable cookies for API sessions unless required
- Validate URL scheme is `https` before making requests
