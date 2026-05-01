# Privacy Manifests (`PrivacyInfo.xcprivacy`)

Apple now requires a privacy manifest in every app and SDK that submits to the App Store. Missing manifests, missing required-reason declarations, or wrong reason codes block submission. This is enforcement, not advice — Apple's submission service rejects builds without it for any covered API.

This reference covers what to declare, the four manifest sections, the Required Reason API list, third-party SDK manifests, and how to keep the file accurate without manually auditing it on every release.

## Scope and applicability

The privacy manifest is required if **any** of the following is true:

- Your app collects data (anything tied to a user — even an anonymized device ID counts).
- Your app uses tracking (cross-app/cross-website data combined for ads or shared with data brokers).
- Your app calls any of Apple's Required Reason APIs (list below).
- Your app embeds any third-party SDK that itself requires a manifest.

In practice, every shipping iOS app needs one. Even a fully offline calculator app likely calls `UserDefaults` (a Required Reason API). Treat the manifest as mandatory.

The file lives at `PrivacyInfo.xcprivacy` in the bundle, alongside `Info.plist`. It's an XML plist. Xcode generates a starter when you add `New File... → App Privacy File`.

## The four sections

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>

    <key>NSPrivacyTrackingDomains</key>
    <array/>

    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <!-- Each data type collected -->
    </array>

    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <!-- Each Required Reason API + its reason codes -->
    </array>
</dict>
</plist>
```

### `NSPrivacyTracking`

`true` if the app combines user data across other companies' apps or websites for advertising or sharing with data brokers. Most non-advertising apps are `false`.

If you set `true`, you must also list `NSPrivacyTrackingDomains` (the domains your app contacts for tracking). Setting `true` also requires the App Tracking Transparency prompt (`ATTrackingManager.requestTrackingAuthorization`) before any tracking activity.

### `NSPrivacyTrackingDomains`

The list of fully-qualified domain names contacted for tracking purposes. Connections to listed domains are blocked unless ATT permission is granted. If you set tracking to `false`, this stays empty.

```xml
<key>NSPrivacyTrackingDomains</key>
<array>
    <string>analytics.example.com</string>
    <string>ads.example.com</string>
</array>
```

### `NSPrivacyCollectedDataTypes`

For each category of data your app collects, declare:
- The data type (`NSPrivacyCollectedDataType`)
- Whether it's linked to the user's identity (`NSPrivacyCollectedDataTypeLinked`)
- Whether it's used for tracking (`NSPrivacyCollectedDataTypeTracking`)
- The purposes (`NSPrivacyCollectedDataTypePurposes`)

```xml
<dict>
    <key>NSPrivacyCollectedDataType</key>
    <string>NSPrivacyCollectedDataTypeEmailAddress</string>
    <key>NSPrivacyCollectedDataTypeLinked</key>
    <true/>
    <key>NSPrivacyCollectedDataTypeTracking</key>
    <false/>
    <key>NSPrivacyCollectedDataTypePurposes</key>
    <array>
        <string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string>
        <string>NSPrivacyCollectedDataTypePurposeAccountManagement</string>
    </array>
</dict>
```

The full enum lists for each field are in Apple's documentation. The categories you'll most often declare:

| Type constant | Common cause |
|---|---|
| `NSPrivacyCollectedDataTypeEmailAddress` | Account sign-up |
| `NSPrivacyCollectedDataTypeName` | User profile |
| `NSPrivacyCollectedDataTypeUserID` | Custom IDs you assign |
| `NSPrivacyCollectedDataTypeDeviceID` | IDFV, vendor ID |
| `NSPrivacyCollectedDataTypeCrashData` | Sentry, Crashlytics |
| `NSPrivacyCollectedDataTypePerformanceData` | Performance/diagnostics SDKs |
| `NSPrivacyCollectedDataTypeProductInteraction` | In-app event tracking |
| `NSPrivacyCollectedDataTypePreciseLocation` | GPS-accurate |
| `NSPrivacyCollectedDataTypeCoarseLocation` | City-level |

The matrix of (type × linked × tracking × purposes) maps directly to App Store Connect's privacy nutrition label. If they don't match, App Store Connect flags inconsistencies during submission.

### `NSPrivacyAccessedAPITypes` — the Required Reason APIs

This is the section that catches everyone off-guard. Apple has a list of APIs that have legitimate privacy-relevant uses and a history of fingerprinting abuse. For each, you must declare *why* you call it, choosing from a fixed set of reason codes.

```xml
<dict>
    <key>NSPrivacyAccessedAPIType</key>
    <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
    <key>NSPrivacyAccessedAPITypeReasons</key>
    <array>
        <string>CA92.1</string>
    </array>
</dict>
```

Apple validates the reason codes — invalid codes block submission.

## Required Reason API categories

Five categories, each with its own list of valid reason codes:

### `NSPrivacyAccessedAPICategoryUserDefaults`

Every app calls `UserDefaults` somewhere. Reasons:

| Code | Description |
|---|---|
| `CA92.1` | Read/write to your own app's UserDefaults |
| `1C8F.1` | Reading values from other apps in your app group |
| `C56D.1` | Reading values written by your app's extensions |
| `AC6B.1` | App-managed device identifiers (only for some specific cases — read the docs first) |

For 99% of apps, declare `CA92.1`. If you use app groups (extension or widget sharing UserDefaults), add the relevant code.

### `NSPrivacyAccessedAPICategoryFileTimestamp`

If you call `creationDate`, `contentModificationDate`, or any file timestamp API on `URL` or `FileManager`. Reasons:

| Code | Description |
|---|---|
| `DDA9.1` | Display to the user |
| `C617.1` | Inside the app's container |
| `3B52.1` | When the user has explicitly consented to file access |
| `0A2A.1` | Calculating file age for purposes the user requested |

### `NSPrivacyAccessedAPICategorySystemBootTime`

`mach_absolute_time`, `kern.boottime`. Reasons:

| Code | Description |
|---|---|
| `35F9.1` | Measuring time elapsed within the app |
| `8FFB.1` | User-initiated bug-reporting |
| `3D61.1` | Implementing your own monotonic clock |

### `NSPrivacyAccessedAPICategoryDiskSpace`

`NSURL.volumeAvailableCapacityKey` and friends. Reasons:

| Code | Description |
|---|---|
| `E174.1` | Display to the user |
| `85F4.1` | Pre-flight a write to ensure success |
| `7D9E.1` | Verify disk space for user-initiated download |
| `B728.1` | Health/diagnostics for app's own disk usage |

### `NSPrivacyAccessedAPICategoryActiveKeyboards`

`UITextInputMode.activeInputModes`. Reasons:

| Code | Description |
|---|---|
| `3EC4.1` | Apps for users with custom keyboards |
| `54BD.1` | Provide localized text input help |

If you don't actively need the active keyboard list, **don't call the API at all** rather than declaring it. The list is short for a reason — Apple expects most apps to have no entry in this section.

## Manifest validation

Xcode validates the manifest at archive time:

- **Missing manifest while using a Required Reason API** → archive fails with "Missing privacy manifest entry."
- **Wrong reason code** → archive fails with "Invalid privacy manifest entry."
- **Reason code that doesn't match documented use** → no compile-time check; can be flagged in App Store Review.

When archive fails for a privacy reason, the error message points at the API and category. Add the entry, archive again. There is no `--ignore` flag; this is a hard gate.

## Third-party SDK manifests

Every iOS SDK shipped via SPM, CocoaPods, or XCFramework must include its own `PrivacyInfo.xcprivacy`. When you embed an SDK:

- Verify the SDK has a manifest. If not, the SDK is non-compliant and may block your submission.
- Apple maintains a list of "commonly used SDKs that require manifests" — embedding any of those without their manifest is an automatic rejection. The list grows; check it at integration time.

The combined manifest at submission is the union of your app's manifest and every SDK's manifest. App Store Connect aggregates them automatically — you don't write the combined version yourself. Each manifest stays with its source.

If an SDK's manifest declares more data collection than you actually trigger (e.g., a logger that *could* send crash dumps but you've configured it not to), your app is still credited with that collection in the privacy nutrition label. There's no way to reduce it via configuration. For privacy-sensitive apps, this is a strong reason to choose minimal SDKs.

## SDK signature requirement

Beyond the manifest, certain commonly used SDKs (the same list that requires manifests) must also be code-signed by their author. Embedding an unsigned commonly-used SDK fails submission even if you have your own valid manifest.

For SPM dependencies built from source, you typically don't need to worry — the build system signs them with your team's certificate during archive. For binary XCFrameworks shipped pre-built, the framework must be signed by the publisher; verify with `codesign -dv` before integrating.

## App Privacy Report

Once shipped, users can enable **Settings → Privacy & Security → App Privacy Report**. This shows them, per app, which data categories were accessed and which network domains were contacted. It's generated on-device and not sent to Apple.

There is no developer-facing equivalent to inspect the same data on a build. The closest substitute: enable the report on your own device, run the app through normal flows, then check the report. If it shows accesses you haven't declared, your manifest is incomplete — fix before submission.

## Deadlines and updates

Apple's enforcement deadline for the manifest passed in May 2024. Subsequent enforcement steps:

- New submissions: rejected immediately if the manifest is missing or invalid.
- Updates to existing apps: same gate.
- New Required Reason API additions: Apple announces new categories at WWDC. New required entries may take effect months later — track the changelog.

The manifest must accurately reflect the build being submitted. Updates that add new data collection require updating the manifest in the same release.

## Process for keeping the manifest accurate

A discipline that scales:

1. **Per-PR audit:** if a PR touches anything in the data-flow path (network, storage, telemetry), the reviewer checks whether `PrivacyInfo.xcprivacy` needs updating.
2. **Pre-release diff:** before tagging a release, run a script (or a manual audit) over the diff since the last release looking for: new SDKs, new `UserDefaults` usage, new file-system APIs, new tracking domains. Update the manifest if any are found.
3. **Ownership:** mark `PrivacyInfo.xcprivacy` in `CODEOWNERS` so a privacy-aware reviewer is required for every change.
4. **First-class doc:** keep a one-page summary of "what data we collect and why" alongside the manifest. Reviewers and auditors want this.

The audit is cheap if done per-PR. It's expensive if deferred until submission and an SDK update silently changed what's collected.

## Common rejections

| Symptom | Cause | Fix |
|---|---|---|
| `ITMS-91053: Missing API declaration` | Calling a Required Reason API without an entry | Add the API category and a valid reason code |
| `ITMS-91054: Invalid reason in API declaration` | Reason code doesn't exist in Apple's table | Replace with a valid code |
| `ITMS-91056: Invalid privacy manifest` | Plist syntax error or wrong structure | Validate the file with `plutil -lint`; check Xcode's "Open as → Source Code" view |
| `ITMS-91065: Missing signature` for a known SDK | Pre-built XCFramework not signed by publisher | Use a signed version or replace the SDK |
| Privacy nutrition label mismatch | Manifest declares X, ASC's label says Y | Update the manifest or the label so they agree |

## Quick checklist before tagging a release

```
[ ] PrivacyInfo.xcprivacy exists at the project root
[ ] NSPrivacyTracking matches actual app behavior
[ ] NSPrivacyTrackingDomains includes every domain contacted for tracking (or array is empty)
[ ] NSPrivacyCollectedDataTypes covers every data category collected
[ ] NSPrivacyAccessedAPITypes covers every Required Reason API call (UserDefaults always)
[ ] All third-party SDKs include their own PrivacyInfo.xcprivacy
[ ] No commonly-used SDKs lack signature
[ ] App Privacy Report on test device shows nothing undeclared
```

## Rules

- Treat the privacy manifest as mandatory for every iOS app, regardless of size.
- Declare `UserDefaults` (`CA92.1`) — almost every app uses it.
- Audit the manifest in every PR that touches data flow; don't defer to release time.
- Verify every third-party SDK has its own `PrivacyInfo.xcprivacy` before adding it.
- Match the manifest to App Store Connect's privacy nutrition label exactly.
- Include `PrivacyInfo.xcprivacy` in `CODEOWNERS` for required review.
- Use `plutil -lint PrivacyInfo.xcprivacy` to catch syntax errors before archive.
- Track Apple's WWDC announcements for new Required Reason API additions.
- Don't call `UITextInputMode.activeInputModes` unless you genuinely need it — saves a manifest entry and a possible rejection.
