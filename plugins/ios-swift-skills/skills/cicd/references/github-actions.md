# GitHub Actions for iOS

## Standard CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build-and-test:
    name: Build & Test
    runs-on: macos-15
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Select Xcode
        uses: maxim-lobanov/setup-xcode@v1
        with:
          xcode-version: '16.4'  # Adjust to project needs

      - name: Cache SPM
        uses: actions/cache@v4
        with:
          path: |
            ~/Library/Caches/org.swift.swiftpm
            .build
          key: spm-${{ runner.os }}-${{ hashFiles('**/Package.resolved') }}
          restore-keys: |
            spm-${{ runner.os }}-

      - name: Build
        run: |
          xcodebuild build \
            -scheme "$SCHEME" \
            -destination "$DESTINATION" \
            -skipPackagePluginValidation \
            -skipMacroValidation \
            CODE_SIGNING_ALLOWED=NO \
            | xcpretty
        env:
          SCHEME: MyApp        # ← Replace with project scheme
          DESTINATION: 'platform=iOS Simulator,name=iPhone 16,OS=latest'

      - name: Test
        run: |
          xcodebuild test \
            -scheme "$SCHEME" \
            -destination "$DESTINATION" \
            -skipPackagePluginValidation \
            -skipMacroValidation \
            -resultBundlePath TestResults.xcresult \
            CODE_SIGNING_ALLOWED=NO \
            | xcpretty
        env:
          SCHEME: MyApp        # ← Replace with project scheme
          DESTINATION: 'platform=iOS Simulator,name=iPhone 16,OS=latest'

      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-results
          path: TestResults.xcresult
```

## With Secret Injection

```yaml
      - name: Create xcconfig
        run: |
          echo "API_KEY = ${{ secrets.API_KEY }}" > Config/Release.xcconfig
          echo "BASE_URL = ${{ secrets.BASE_URL }}" >> Config/Release.xcconfig
```

## Matrix Builds (Multiple Configurations)

```yaml
jobs:
  build-and-test:
    strategy:
      matrix:
        include:
          - scheme: MyApp
            destination: 'platform=iOS Simulator,name=iPhone 16,OS=latest'
          - scheme: MyAppMac
            destination: 'platform=macOS'
    runs-on: macos-15
    steps:
      # ... same steps with ${{ matrix.scheme }} and ${{ matrix.destination }}
```

## Release Workflow (Manual)

```yaml
# .github/workflows/release.yml
name: Release

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version number (e.g., 1.2.0)'
        required: true

jobs:
  archive:
    name: Archive & Upload
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        uses: maxim-lobanov/setup-xcode@v1
        with:
          xcode-version: '16.4'

      - name: Archive
        run: |
          xcodebuild archive \
            -scheme MyApp \
            -archivePath build/MyApp.xcarchive \
            -destination 'generic/platform=iOS' \
            CODE_SIGNING_ALLOWED=NO

      # For actual App Store upload, use Fastlane or xcrun altool
```

## SwiftLint Integration

```yaml
      - name: SwiftLint
        run: |
          if command -v swiftlint &> /dev/null; then
            swiftlint lint --strict --reporter github-actions-logging
          else
            echo "SwiftLint not installed, skipping"
          fi
```

## Key Settings

| Setting | Value | Why |
|---------|-------|-----|
| `CODE_SIGNING_ALLOWED=NO` | Disable signing | CI has no certificates |
| `-skipPackagePluginValidation` | Skip plugin prompts | No interactive input in CI |
| `-skipMacroValidation` | Skip macro trust | No interactive input in CI |
| `xcpretty` | Readable output | Cleaner logs |
| `timeout-minutes: 30` | Prevent hangs | Kill stuck builds |
| `cancel-in-progress: true` | Cancel old runs | Save CI minutes |

## Customization

Replace these values in the template:

| Placeholder | Example Value |
|------------|---------------|
| `MyApp` (scheme) | `SnapGPX` |
| `iPhone 16` (simulator) | `iPhone 17` |
| `16.4` (Xcode version) | `17.0` |
