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

**Cause**: CI doesn't have signing certificates.

**Fix**: Always use `CODE_SIGNING_ALLOWED=NO` for CI builds. Signing is only needed for archive/distribution.

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
