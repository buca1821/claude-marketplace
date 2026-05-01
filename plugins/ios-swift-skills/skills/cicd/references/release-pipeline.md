# Release Pipeline — From Tag to TestFlight

A release pipeline takes the question "is this ready to ship?" and turns it into a series of automated steps that either succeed end-to-end or fail clearly. This reference describes the canonical iOS release flow, the decisions encoded at each step, and the credentials and configuration that make it work.

## The flow

```
Developer creates git tag (e.g., v1.4.0)
   ↓
Pipeline triggers on tag push
   ↓
Lint  →  Test  →  Build  ✅ same gates as a regular main push
   ↓
Read version from tag, write to project (CFBundleShortVersionString, CFBundleVersion)
   ↓
Archive (signed .xcarchive)
   ↓
Export IPA + dSYMs
   ↓
Upload to App Store Connect via ASC API
   ↓
TestFlight processes (5-30 min, Apple-side)
   ↓
Notify (Slack/email): "Build N available on TestFlight"
   ↓
[Manual] Promote to External Testing or App Store Review
```

Everything up to the notification is automated. Promotion to external testing or to the App Store is a deliberate human action — there is no scenario where a CI commit should auto-publish to end users.

## Versioning policy

Two values to manage:

| Field | Plist key | Visible to user | What it means |
|---|---|---|---|
| Marketing version | `CFBundleShortVersionString` | Yes (in App Store) | Semantic version: `1.4.0` |
| Build number | `CFBundleVersion` | No | Monotonic integer, unique per upload to ASC |

App Store Connect rejects duplicate `(marketing version, build number)` pairs. The build number must increase for every upload, even if the marketing version stays the same.

**Recommended pattern:**

- Marketing version: derived from the git tag. `v1.4.0` → `1.4.0`. Patch and minor bumps follow [semver](https://semver.org/).
- Build number: CI run number, or `git rev-list --count HEAD`. Both are monotonic and reproducible.

```bash
# In CI, before archive:
MARKETING_VERSION="${GIT_TAG#v}"   # strip leading 'v'
BUILD_NUMBER="$(git rev-list --count HEAD)"

agvtool new-marketing-version "$MARKETING_VERSION"
agvtool new-version -all "$BUILD_NUMBER"
```

`agvtool` updates the Info.plist of all targets in one call. Don't try to edit plists with `sed` — there are XML and binary plist variants and you'll catch the wrong one.

## Trigger rules

| Event | What runs | Where it lands |
|---|---|---|
| Push to `main` | Lint + Test + Build + Archive + Distribute (TestFlight Internal) | Internal testing only — your own team |
| Push tag matching `v*.*.*` | Full release flow | TestFlight External (auto-detected from tag) |
| Push tag matching `v*.*.*-rc.*` | Release flow but mark as RC | TestFlight External, beta channel |
| Manual workflow run | Configurable | Wherever you say |

The auto-deploy to **TestFlight Internal** on every `main` push is what makes the team dogfood every change. Internal testing is unlimited, free, and does not require Apple review — there is no excuse not to have it.

External testing (real beta users outside your team) and App Store submission gate on tags. The semantic separation (push = internal, tag = external) is explicit and hard to confuse.

## Credentials: App Store Connect API key

The modern way to authenticate CI to App Store Connect is the **API key**. Don't use App-Specific Passwords; they're deprecated for this purpose.

Generate the key once:

1. App Store Connect → Users and Access → Integrations → App Store Connect API.
2. Generate API Key. Role: at minimum **App Manager** for upload; **Admin** if you also want to manage TestFlight groups via API.
3. Download the `.p8` file (it can only be downloaded once — store it immediately).
4. Note the **Key ID** and the **Issuer ID** shown on the page.

Store three secrets in CI:

| Secret name | Value |
|---|---|
| `ASC_KEY_ID` | The 10-character Key ID |
| `ASC_ISSUER_ID` | UUID-format Issuer ID |
| `ASC_KEY_BASE64` | Base64-encoded contents of the `.p8` file |

In the job, decode and use:

```bash
mkdir -p ~/.appstoreconnect/private_keys
echo "$ASC_KEY_BASE64" | base64 --decode > ~/.appstoreconnect/private_keys/AuthKey_${ASC_KEY_ID}.p8
chmod 600 ~/.appstoreconnect/private_keys/AuthKey_${ASC_KEY_ID}.p8

xcrun altool --upload-app \
    -f "$IPA_PATH" \
    -t ios \
    --apiKey "$ASC_KEY_ID" \
    --apiIssuer "$ASC_ISSUER_ID"
```

The `xcrun altool` invocation reads the `.p8` from `~/.appstoreconnect/private_keys/AuthKey_<KEY_ID>.p8` automatically. No password file, no Apple ID 2FA dance.

For more control (modify TestFlight metadata, manage testers programmatically), use `xcrun notarytool` for macOS or call the App Store Connect REST API directly with a JWT signed by the same key. See `code-signing.md` for the JWT flow.

## Code signing

Code signing must be set up before this pipeline runs. See **`code-signing.md`** for the full setup. In summary:

- Distribution certificate (`.p12`) and provisioning profile (`.mobileprovision`) stored as base64 secrets.
- A pre-archive step that imports them into a CI keychain.
- `xcodebuild archive` configured for manual signing with the provisioning profile name as input.

Skipping that setup means Archive will fail with `"No signing certificate \"iOS Distribution\" found"` and you'll spend an afternoon on it. Read that reference first if you've never done it.

## Archive and export

Two `xcodebuild` invocations:

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

xcodebuild -exportArchive \
    -archivePath build/YourApp.xcarchive \
    -exportPath build/export \
    -exportOptionsPlist scripts/ExportOptions.plist
```

**Do not pass `-allowProvisioningUpdates` in CI.** That flag tells Xcode it may contact Apple's portal to update the profile, which requires an interactive Apple ID login and fails non-interactively on a runner. With manual signing pre-configured per `code-signing.md`, the cert and profile are already imported — Xcode does not need to update anything. The explicit `CODE_SIGN_STYLE=Manual` and `PROVISIONING_PROFILE_SPECIFIER` make this unambiguous and match the example in `code-signing.md`.

`ExportOptions.plist` describes the distribution method:

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
    <key>uploadSymbols</key>
    <true/>
</dict>
</plist>
```

`uploadSymbols=true` sends dSYMs to Apple as part of the upload, which is what gives you symbolicated crash reports in Xcode Organizer for free.

After export, the IPA is at `build/export/YourApp.ipa` and dSYMs at `build/YourApp.xcarchive/dSYMs/`.

## Release notes from changelog

The `.ipa` upload itself doesn't carry release notes — those go via the App Store Connect API after the build finishes processing. A standard pattern: read from `CHANGELOG.md` (or git tag annotation) and post via the API.

```bash
# Extract release notes for the version being released
RELEASE_NOTES="$(awk "/^## $MARKETING_VERSION/,/^## /" CHANGELOG.md | head -n -1)"

# After upload completes and Apple finishes processing,
# update TestFlight build with the notes via the API.
```

For the first release on a project, skip this and add notes manually in App Store Connect. Once the project has multiple releases, automating beats remembering.

## Notification

Once the build is uploaded:

- Slack: post to a `#releases` channel with the build number, version, and a link to App Store Connect.
- Email: send to the QA list with the same.
- GitHub release: create a release object on the tag with the changelog excerpt.

Pseudo-code for a Slack post via webhook:

```bash
curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"📱 *YourApp $MARKETING_VERSION ($BUILD_NUMBER)* uploaded to TestFlight. Available in 5-30 min.\"}" \
    "$SLACK_WEBHOOK_URL"
```

Skip notification automation for solo projects — you know when you pushed the tag. For team projects, it removes the "is the build ready yet?" question from chat.

## TestFlight Internal vs External

| Feature | Internal | External |
|---|---|---|
| Tester count | Up to 100 | Up to 10,000 |
| Tester audience | Your team (must have ASC role) | Anyone with an email |
| Apple review | None | First build per version requires Beta App Review (24-48h) |
| Latency from upload to install | 5-15 min | 1-3 days for first build, then minutes |
| Use case | Continuous dogfooding | Pre-release validation with real users |

The auto-deploy on `main` should target Internal. External requires a deliberate decision (and Apple-side processing time), so it gates on a release tag.

## App Store submission

App Store submission is a separate manual step. The pipeline can prepare everything (build uploaded, metadata uploaded, screenshots uploaded), but the "Submit for Review" button is a human gate.

Why manual: App Store rejection has consequences. Apple reviewers are the last set of eyes — submitting on every release tag is reckless if you haven't verified screenshots, descriptions, and TestFlight crash reports.

## Failure modes

| Failure | Cause | Fix |
|---|---|---|
| `ITMS-90186 Invalid Pre-Release Train Version Number` | Build number not greater than the last upload | Increase build number; check ASC for the last value |
| `Provisioning profile doesn't include the currently signed device` | Wrong profile for distribution method | Use a Distribution profile, not Development |
| `Invalid Info.plist value` | Asset catalog or plist key with an unexpected type | Read Apple's exact rejection message; usually one key |
| `notarytool error` (macOS) | Wrong API key or expired team agreement | Re-check ASC roles; sign and renew agreements |
| TestFlight stuck "Processing" > 1h | Apple-side issue | Wait. If > 4h, contact Apple support — there is no client-side fix |

## Rules

- Build number must be unique per upload, monotonically increasing. Use git commit count or CI run number.
- Marketing version comes from the git tag — never manually edited in CI.
- Use App Store Connect API keys, not Apple ID + 2FA.
- Auto-deploy `main` to TestFlight Internal; gate External on tag push.
- Always upload dSYMs (`uploadSymbols=true` in ExportOptions.plist).
- Keep App Store submission as a manual step. Don't automate the green button.
- Notify on completion to a channel humans read.
- Never re-use a build number to "fix" a failed upload — bump it.
- Tag format `v*.*.*` is convention; document and enforce it in pipeline scripts.
