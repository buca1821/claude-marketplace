# CI Troubleshooting

## Common Failures

### "No matching destination found"

**Cause**: Simulator name doesn't match what's available on the runner.

**Fix**: List available simulators and use an exact match:
```yaml
- name: List simulators
  run: xcrun simctl list devices available
```

### "xcodebuild: error: unable to find scheme"

**Cause**: Scheme not shared or workspace not specified.

**Fix**:
1. In Xcode: Product → Scheme → Manage Schemes → check "Shared"
2. Commit `.xcodeproj/xcshareddata/xcschemes/`
3. If using workspace: add `-workspace MyApp.xcworkspace`

### SPM resolution fails

**Cause**: Package.resolved out of sync or network issues.

**Fix**:
```yaml
- name: Resolve packages
  run: xcodebuild -resolvePackageDependencies -scheme MyApp
```

### Code signing errors

For Test and Build jobs (no archive needed), the simplest fix is to disable signing entirely:

```bash
xcodebuild build -configuration Debug CODE_SIGNING_ALLOWED=NO
```

For Archive and Distribute jobs, signing must succeed — see `code-signing.md` for the full setup. The most common archive-time failures and their fixes:

| Symptom | Cause | Fix |
|---|---|---|
| `No signing certificate "iOS Distribution" found` | Cert not imported, wrong keychain, or keychain locked | Verify `security find-identity -v` shows the cert in the active keychain. Run `security unlock-keychain` and `security set-key-partition-list` |
| `User interaction is not allowed` | Keychain partition list not set; `codesign` prompts non-interactively | Run `security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k <password>` after import |
| `Provisioning profile doesn't include the currently signed device` | Distribution profile doesn't match build destination, or you're using a Development profile | Use `-destination 'generic/platform=iOS'` for archives. Confirm the profile is "Distribution" not "Development" |
| `Provisioning profile doesn't match the entitlements` | Profile is for a different bundle ID, or app added a capability the profile doesn't include | Regenerate the profile in Apple Developer portal after capability changes |
| `Could not locate installed application` | Wrong destination — building for a specific simulator that doesn't exist on the runner | Use `generic/platform=iOS` for archives, not a Simulator destination |
| `iCloud entitlement missing` | Capability added in Xcode, profile not regenerated | Profile must be regenerated whenever entitlements change |
| `errSecAuthFailed` (-25293) during import | Wrong `.p12` password | Verify `DISTRIBUTION_CERT_PASSWORD` matches the password set during export |

**Debug routine** for signing failures:

```bash
# 1. List identities visible to codesign
security find-identity -v -p codesigning

# 2. List provisioning profiles installed
ls -la "$HOME/Library/MobileDevice/Provisioning Profiles/"

# 3. Show the profile's bundle ID and team
security cms -D -i "$HOME/Library/MobileDevice/Provisioning Profiles/profile.mobileprovision" \
    | plutil -extract Entitlements xml1 -o - -

# 4. Confirm Xcode picked the right profile
xcodebuild archive ... 2>&1 | grep -i "provision\|sign"
```

If the identity is missing from step 1, the cert was never imported into the active keychain or the keychain is wrong (see `security list-keychains -d user`). If the profile in step 2 is missing or has the wrong bundle ID, the per-run setup script didn't install it correctly. Step 4 confirms which provisioning profile `xcodebuild` actually selected.

### Build succeeds locally but fails on CI

Common causes:
- **Xcode version mismatch**: Pin version with `setup-xcode`
- **macOS version**: Check runner image (`macos-14` vs `macos-15`)
- **Implicit dependencies**: CI starts clean — no cached state
- **Environment differences**: Check locale, timezone settings

### Tests pass locally but fail on CI

Common causes:
- **Locale-dependent tests**: Always inject explicit `Locale` (see testing-standards rule)
- **Timing-dependent tests**: CI runners are slower — increase timeouts
- **File system paths**: Don't use absolute paths in tests
- **Order-dependent tests**: CI may run tests in different order

### "Operation timed out"

**Cause**: Simulator boot or test execution too slow.

**Fix**:
```yaml
# Increase timeout
timeout-minutes: 45

# Or boot simulator first
- name: Boot simulator
  run: |
    DEVICE_ID=$(xcrun simctl list devices available -j | jq -r '.devices | to_entries[] | .value[] | select(.name == "iPhone 16") | .udid' | head -1)
    xcrun simctl boot "$DEVICE_ID" || true
```

### Cache not working

**Cause**: Cache key doesn't match, or paths are wrong.

**Fix**: Verify paths exist:
```yaml
- name: Debug cache paths
  run: |
    ls -la ~/Library/Caches/org.swift.swiftpm/ || echo "SPM cache not found"
    ls -la .build/ || echo ".build not found"
```

## Runner Images

| Runner | macOS | Pre-installed Xcode |
|--------|-------|-------------------|
| `macos-14` | Sonoma | Xcode 15.x, 16.x |
| `macos-15` | Sequoia | Xcode 16.x |

Check available versions: https://github.com/actions/runner-images

## Debugging Tips

1. **SSH into runner** (for debugging stuck builds):
   ```yaml
   - name: Debug via SSH
     uses: mxschmitt/action-tmate@v3
     if: failure()
   ```

2. **Save build logs**:
   ```yaml
   - name: Upload logs
     uses: actions/upload-artifact@v4
     if: failure()
     with:
       name: build-logs
       path: |
         ~/Library/Logs/DiagnosticReports/
         TestResults.xcresult
   ```

3. **Check Xcode version**:
   ```yaml
   - name: Xcode info
     run: xcodebuild -version && swift --version
   ```
