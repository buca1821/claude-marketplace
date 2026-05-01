# Code Signing in CI

Code signing is the most common reason iOS pipelines fail at Archive time, and the most frustrating to debug. This reference covers the full setup: certificates, profiles, keychain, secrets, and the explicit `xcodebuild` configuration that survives across runners.

## Concepts in 60 seconds

| Term | What it is | Where it lives |
|---|---|---|
| **Distribution certificate** | Public/private keypair Apple uses to verify you signed the binary | `.p12` file (private + public + chain) |
| **Provisioning profile** | A signed document tying a certificate, an app ID, capabilities, and (for ad-hoc) device UDIDs | `.mobileprovision` file |
| **Team ID** | A 10-char Apple Developer team identifier | Visible in Apple Developer portal |
| **Bundle ID** | Your app's reverse-DNS identifier | Set in Xcode and matches the provisioning profile |

To sign at archive time, the runner needs the `.p12` imported into a keychain it can unlock and a `.mobileprovision` placed where Xcode expects it. The rest is configuration glue.

## Automatic vs manual signing — pick manual for CI

Xcode's "Automatically manage signing" works locally because Xcode logs you into your Apple ID and creates ephemeral profiles as needed. CI cannot do that — there is no Apple ID logged in, and you don't want one.

**Manual signing in CI:**

- You generate a single distribution certificate and provisioning profile.
- You commit them (encrypted as base64 secrets) to your CI provider.
- Xcode is told exactly which profile to use; no auto-discovery.

In Xcode, set the target's Signing tab to "Manually manage signing" for the **Release** configuration only. Debug can stay automatic for local development.

## One-time setup: generate certs and profiles

You only do this when bootstrapping a project or rotating credentials. The output gets committed to CI secrets.

### 1. Distribution certificate

If you don't already have one:

1. Apple Developer → Certificates, Identifiers & Profiles → Certificates → `+`.
2. Choose **Apple Distribution** (works for both App Store and Ad Hoc).
3. Generate a CSR locally (Keychain Access → Certificate Assistant → Request a Certificate from a Certificate Authority).
4. Upload the CSR; download the resulting `.cer`.
5. Open the `.cer` in Keychain Access. It pairs with the private key from the CSR.
6. Export the pair as `.p12` (right-click in Keychain Access → Export). Set a password — store it in CI as `CERT_PASSWORD`.

You now have `Distribution.p12` and `CERT_PASSWORD`.

### 2. Provisioning profile

1. Apple Developer → Profiles → `+`.
2. Choose **App Store** for App Store distribution, or **Ad Hoc** for off-store builds.
3. Pick the App ID, the Distribution certificate from above, and (for ad hoc) the device UDIDs.
4. Download the `.mobileprovision`.

You now have `YourApp_AppStore.mobileprovision`.

### 3. Encode for CI secrets

```bash
base64 -i Distribution.p12 -o Distribution.p12.base64
base64 -i YourApp_AppStore.mobileprovision -o profile.base64
```

Copy the contents of those `.base64` files into CI secrets:

| Secret name | Value |
|---|---|
| `DISTRIBUTION_CERT_BASE64` | base64 of `.p12` |
| `DISTRIBUTION_CERT_PASSWORD` | password set during export |
| `PROVISIONING_PROFILE_BASE64` | base64 of `.mobileprovision` |
| `KEYCHAIN_PASSWORD` | a random string (you generate, you keep) |

The keychain password is for the *temporary* keychain CI creates per run — not Apple's. Generate any random value.

## Per-run setup: import to keychain

At the start of any job that needs to sign (Archive, Distribute), run:

```bash
#!/bin/bash
set -euo pipefail

# Decode the certificate
echo "$DISTRIBUTION_CERT_BASE64" | base64 --decode > /tmp/cert.p12

# Create a temporary keychain
KEYCHAIN_PATH="$RUNNER_TEMP/build.keychain"
security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH"   # 6h timeout
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

# Import the cert into the keychain
security import /tmp/cert.p12 \
    -k "$KEYCHAIN_PATH" \
    -P "$DISTRIBUTION_CERT_PASSWORD" \
    -T /usr/bin/codesign \
    -T /usr/bin/security

# Allow codesign to access the key without a password prompt
security set-key-partition-list \
    -S apple-tool:,apple:,codesign: \
    -s -k "$KEYCHAIN_PASSWORD" \
    "$KEYCHAIN_PATH"

# Make this the default keychain for the session
security list-keychains -d user -s "$KEYCHAIN_PATH" $(security list-keychains -d user | sed 's/"//g')

# Install the provisioning profile
mkdir -p "$HOME/Library/MobileDevice/Provisioning Profiles"
echo "$PROVISIONING_PROFILE_BASE64" | base64 --decode \
    > "$HOME/Library/MobileDevice/Provisioning Profiles/profile.mobileprovision"

# Cleanup
rm /tmp/cert.p12
```

Three things this does that fix the most common CI signing errors:

- **Creates a fresh keychain per run** (not reusing the system keychain). No leftover state, no conflicts with other workflows.
- **`set-key-partition-list`** — the line that makes 90% of "User interaction not allowed" errors go away. Without it, `codesign` prompts for a password and fails non-interactively.
- **Sets the new keychain as default** — without this, `xcodebuild` looks in the wrong keychain and reports "no signing certificate."

Wrap this in a reusable shell script (`scripts/ci-setup-signing.sh`) — every signing job invokes it, identical, no copy-paste in YAML.

## Archive with manual signing

```bash
xcodebuild archive \
    -workspace YourApp.xcworkspace \
    -scheme YourApp \
    -configuration Release \
    -archivePath build/YourApp.xcarchive \
    -destination 'generic/platform=iOS' \
    DEVELOPMENT_TEAM=ABCDE12345 \
    CODE_SIGN_STYLE=Manual \
    PROVISIONING_PROFILE_SPECIFIER="YourApp App Store"
```

The four explicit settings are the contract:

- `DEVELOPMENT_TEAM` — your 10-char team ID.
- `CODE_SIGN_STYLE=Manual` — overrides any project-level "automatic" leftover.
- `PROVISIONING_PROFILE_SPECIFIER` — the *name* of the profile (visible in Apple Developer portal), not its UUID. Easier to read in errors.
- `-destination 'generic/platform=iOS'` — required for archives. A specific simulator destination archives a simulator binary, which TestFlight rejects.

## Export for distribution

```bash
xcodebuild -exportArchive \
    -archivePath build/YourApp.xcarchive \
    -exportPath build/export \
    -exportOptionsPlist scripts/ExportOptions.plist
```

The `ExportOptions.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store-connect</string>
    <key>signingStyle</key>
    <string>manual</string>
    <key>teamID</key>
    <string>ABCDE12345</string>
    <key>provisioningProfiles</key>
    <dict>
        <key>com.acme.YourApp</key>
        <string>YourApp App Store</string>
    </dict>
    <key>uploadSymbols</key>
    <true/>
</dict>
</plist>
```

Match the bundle ID key to the app's actual bundle ID, and the value to the profile name. For apps with extensions, list each bundle ID (main app + each extension) with its respective profile.

## fastlane match — when to use it

`fastlane match` automates the bootstrapping by storing certs and profiles in a private git repo, encrypted. You run `match appstore` once per developer or CI runner; it pulls the encrypted secrets, decrypts them with a passphrase, and installs them.

**When match is worth it:**

- Multi-developer team where everyone needs distribution certs.
- Multiple apps under the same team — match centralizes credentials.
- Projects that already use fastlane for other things.

**When it's overkill:**

- Solo project with one CI workflow. Direct base64 secrets are simpler and have fewer moving parts.
- Single app, infrequent cert rotation. The bootstrap cost beats the maintenance cost.

If you adopt match, the `xcodebuild` invocation stays similar — match just replaces the keychain-import step. The secrets still live somewhere; they're just managed differently.

## Notarization (macOS only)

For macOS apps distributed outside the App Store (DMG, signed installer, or non-MAS distribution), notarization is required. The flow:

```bash
xcrun notarytool submit YourApp.zip \
    --key ~/.appstoreconnect/private_keys/AuthKey_XXX.p8 \
    --key-id "$ASC_KEY_ID" \
    --issuer "$ASC_ISSUER_ID" \
    --wait

xcrun stapler staple YourApp.app
```

`--wait` blocks until Apple's servers respond. Typical: 1-5 minutes. After approval, `stapler staple` attaches the notarization ticket so the app runs offline.

iOS apps and Mac App Store apps go through TestFlight/ASC instead; notarization does not apply.

## Common failures

| Error | Cause | Fix |
|---|---|---|
| `User interaction is not allowed` | Keychain not unlocked, or partition list not set | Run `set-key-partition-list` after import |
| `No signing certificate "iOS Distribution" found` | Cert not imported, or wrong keychain | Verify `security find-identity -v` shows the cert |
| `Provisioning profile doesn't match the entitlements file's value for the application-identifier entitlement` | Profile is for a different bundle ID | Generate a profile that matches; check the profile name in `xcodebuild` matches `provisioningProfiles` in ExportOptions |
| `Could not locate installed application` | Wrong destination for archive | Use `-destination 'generic/platform=iOS'`, not a specific simulator |
| `iCloud entitlement missing from provisioning profile` | Capabilities added in Xcode but not regenerated in the portal | Regenerate the profile after adding capabilities |
| `IDEDistribution: -[IDEDistributionLogging _addPackageInfo:]` cryptic error | Often a network issue or wrong API key | Check ASC API key validity; retry |

For "User interaction not allowed", the fix is always `security set-key-partition-list`. If that doesn't fix it, the import succeeded but to the wrong keychain — check `security list-keychains` output.

## Rotation

Distribution certificates expire annually. Provisioning profiles expire annually (App Store) or with the certificate (Ad Hoc). When they expire:

1. Generate the new cert / profile.
2. Update the CI secrets (overwrite `DISTRIBUTION_CERT_BASE64`, `PROVISIONING_PROFILE_BASE64`).
3. Test on a non-release branch first — sign, archive, export. Verify before tagging a release.

Calendar a reminder 60 days before expiry. Apps that fail to sign on the day of expiry are not a fun situation.

## Rules

- Manual signing for CI; automatic signing for local Debug only.
- Store certs and profiles as base64 secrets; never commit them in plaintext.
- Create a fresh keychain per CI run; tear it down after.
- Always run `set-key-partition-list` after importing — fixes "User interaction not allowed".
- Match bundle IDs to provisioning profile names exactly in `ExportOptions.plist`.
- Use `-destination 'generic/platform=iOS'` for archives, never a simulator destination.
- Wrap signing setup in a reusable shell script — never copy-paste in YAML.
- Rotate certs and profiles 30-60 days before expiry, not after.
- Use the App Store Connect API key (`.p8`) for upload, not Apple ID + 2FA.
- For multi-developer teams, evaluate `fastlane match`; for solo projects, direct secrets are simpler.
