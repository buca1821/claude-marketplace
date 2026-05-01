# Pipeline Jobs — The Five iOS CI Stages

Every iOS project's CI pipeline boils down to five jobs, in order: **Lint → Test → Build → Archive → Distribute**. The runner platform (GitHub Actions, Xcode Cloud, GitLab CI, Bitrise, self-hosted) is implementation detail. The jobs and their gates are not.

This reference defines what each job verifies, what it fails on, and what artifacts it produces. Use it as the contract between the project and whichever CI platform runs it.

## Why this order

Each stage is faster and cheaper than the next. Failing fast on a SwiftLint violation costs seconds; failing on a code-signing issue at archive time costs minutes plus a slot on a macOS runner. Keep the cheap stages early so the expensive ones only run on changes that have already cleared the floor.

The order is also a dependency chain: Test depends on Lint passing (lint is so cheap there's no reason to test broken code), Build depends on Test, etc. A break at any stage stops the pipeline.

## Stage 1: Lint

**Purpose:** Catch style violations and formatting drift before they enter `main`.

**Tools:**
- `swiftlint` — zero-violations policy. Configure via `.swiftlint.yml` at the repo root.
- `swiftformat --lint` — checks formatting without modifying. Configure via `.swiftformat`.

**Runs on:** Linux runner (Ubuntu). Both tools are available natively without Xcode. This is the only stage that should not need a macOS runner — exploit that.

**Trigger:** Every push, every PR.

**Fails when:** Any rule violation. There is no "warning" tier — drift is binary.

**Outputs:**
- A list of violations in the build log.
- Optionally a SARIF file for code scanning integration.

**Typical duration:** 30–60 seconds.

**Common pitfalls:**
- Running on a macOS runner — wastes a slot 10× more expensive than Linux.
- `swiftlint --fix` in CI — never. CI lints; it does not modify code.
- Different SwiftLint versions locally vs CI — pin the version (`mint`, Homebrew bottle pin, or a Docker image).

## Stage 2: Test

**Purpose:** Run the test suites and enforce coverage thresholds.

**Tool:** `xcodebuild test` (or `swift test` for SPM-only projects).

**Runs on:** macOS runner (required — depends on Xcode + Simulator).

**Trigger:** Every PR. On `main`, also on every push.

**Fails when:**
- Any test fails.
- Coverage drops below the project's threshold (e.g., ViewModels < 85%, Utilities < 80%). Use `xccov` to extract per-target coverage from the `.xcresult` bundle.
- Tests pass individually but emit warnings about Sendable, MainActor isolation, or other concurrency drift — promote those to errors with `-warnings-as-errors` if the project enforces a clean concurrency build.

**Outputs:**
- Test report (`.xcresult`) uploaded as an artifact.
- Coverage summary in the job log.
- Optional: JUnit XML for test reporting integrations.

**Typical duration:** 3–10 minutes for a healthy project.

**UI tests:** Skip by default in PR runs (`-skip-testing:YourAppUITests`). They are slow and flaky. Schedule them on `main` only, or on a `--with-ui` flag for explicit pre-release runs.

**Common pitfalls:**
- Running tests on a Simulator that doesn't exist on the runner. Use `name=iPhone SE (3rd generation),OS=latest` or pin a specific OS the runner image guarantees.
- Locale-dependent tests asserting `"5 km"` while the runner is `en_US`. Inject `Locale` explicitly in the tests — see `swift-testing-patterns.md` and project testing-standards rules.
- Skipping coverage check in CI but enforcing it locally. Either both or neither — divergence rots quickly.

## Stage 3: Build

**Purpose:** Compile the app for Release configuration with all targets.

**Tool:** `xcodebuild build` with `-configuration Release`.

**Runs on:** macOS runner.

**Trigger:** Every PR (after Test passes). On `main`, also on every push.

**Fails when:**
- Compilation error in any target (app, extensions, frameworks, tests).
- Warning treated as error per the project's policy.
- Asset catalog issues (missing image set sizes for required idioms).

**Outputs:**
- Built `.app` bundle (often discarded — Archive will rebuild).
- Build settings dump if requested for debugging.

**Typical duration:** 2–5 minutes (mostly cached after the first run).

**Why a separate job:** Test runs in Debug. Release-only compilation issues (optimizer crashes, conditional `#if DEBUG` paths) only surface in Build. Catching them before Archive shortens the feedback loop.

**Skip for PRs against feature branches** if the project is small and Test already exercises Release-style asserts. For the typical project, keep it — the cost is low.

## Stage 4: Archive

**Purpose:** Produce a signed `.xcarchive` ready for distribution.

**Tool:** `xcodebuild archive`.

**Runs on:** macOS runner with code-signing credentials available.

**Trigger:** On tag push, on merge to `main`, or manually.

**Fails when:**
- Code signing fails (missing certificate, expired profile, wrong team ID). See `code-signing.md`.
- Bitcode requirement issues (rare on modern projects).
- Required device family missing assets (e.g., iPad icons missing for a universal app).
- Privacy manifest validation fails — `PrivacyInfo.xcprivacy` is required, missing required reasons trigger errors.

**Outputs:**
- `.xcarchive` bundle (must be uploaded as an artifact — re-archiving for distribution is wasteful).
- dSYM bundles (must be preserved — symbolication of crash reports depends on them).

**Typical duration:** 5–15 minutes including signing.

**Common pitfalls:**
- Running Archive on every PR. Don't — it's expensive and you have nothing to do with the result. Archive only when you intend to distribute.
- Throwing away the dSYMs. They are the only path back from a stack trace to a line number for users in the field. Upload them as artifacts and forward to whatever crash reporter you use (or store them yourself for Xcode's Organizer).

## Stage 5: Distribute

**Purpose:** Upload the archive somewhere users (or testers) can install it.

**Tools:**
- TestFlight / App Store (iOS and macOS): `xcrun altool --upload-app`, or the App Store Connect API directly.
- Notarization (macOS apps distributed outside the App Store): `xcrun notarytool submit` followed by `xcrun stapler staple`. Notarization is unrelated to TestFlight — don't conflate them.
- Ad-hoc: `xcodebuild -exportArchive -exportOptionsPlist`.
- App Store submission: TestFlight first, then promote via App Store Connect.

**Runs on:** macOS runner with App Store Connect API key configured.

**Trigger:** On `main` push (auto-deploy to TestFlight Internal), on tag push (TestFlight External or App Store), or manually.

**Fails when:**
- Authentication to App Store Connect fails (expired API key, wrong issuer ID).
- App Store metadata invalid (missing screenshots, description too short — only relevant for App Store, not TestFlight).
- `ITMS-XXXXX` server-side rejection (binary integrity, missing capability, version conflict).
- TestFlight processing times out (flaky; Apple-side).

**Outputs:**
- A build ID in App Store Connect.
- Optionally a Slack or email notification with download instructions.

**Typical duration:** 1–3 minutes for upload; TestFlight processing time is on top (5–30 min, Apple-side).

**Versioning policy:** The pipeline must produce a unique build number per archive. Either bump in the project before tagging, or compute from CI run number / git commit count. App Store Connect rejects duplicate (version, build) pairs.

**See `release-pipeline.md`** for the full automated flow from tag to TestFlight.

## Gating: which jobs block what

```
PR opened   →  Lint  →  Test  →  Build  ✅ ready to merge
                                  ↓ (skip Archive/Distribute on PRs)

main push   →  Lint  →  Test  →  Build  →  Archive  →  Distribute (TestFlight Internal)

tag push    →  Lint  →  Test  →  Build  →  Archive  →  Distribute (TestFlight External / App Store)
```

For PRs, only the first three are gates. Archive and Distribute do not run on PRs — they cost too much and the value is zero (the change isn't merged yet).

## Job parallelism

Lint and Test can run in parallel — Test does not depend on Lint passing semantically; you only fail the pipeline if either fails. This shaves the wall-clock time for the gating set:

```
parallel:
  - Lint  (60s)
  - Test  (5min)
serial after both pass:
  - Build (3min)
  - Archive (10min, only on release events)
  - Distribute (3min, only on release events)
```

A PR's blocking time is `max(Lint, Test) + Build` ≈ 8 minutes for a healthy project. If your numbers are 2× that, the bottleneck is usually Test — split slow integration tests into a separate job and run them on `main` only.

## Caching

Cache the right things, not everything:

| What | Cache key | Why |
|---|---|---|
| `~/Library/Developer/Xcode/DerivedData` | Xcode version + Package.resolved hash | Massive build speedup; safe to invalidate aggressively |
| `~/Library/Caches/org.swift.swiftpm` | Package.resolved hash | SPM downloads are slow; hits should be near-100% |
| Homebrew bottles for `swiftlint`, `swiftformat` | Tool versions | Avoid re-installing on every run |
| Ruby gems / Bundler (if you use `fastlane`) | Gemfile.lock | `bundle install` is slow |

**Never cache:**
- Provisioning profiles or certificates — security risk and they change.
- The `.xcarchive` itself — it must be reproducible from source.
- Test results (`.xcresult`) — these are artifacts, not cache.

## Job environment requirements

Each job declares what it needs. The CI platform's job to honor it.

| Job | Runner OS | Xcode | Tools | Secrets |
|---|---|---|---|---|
| Lint | Linux | — | swiftlint, swiftformat | none |
| Test | macOS | required | Xcode + Simulator | none |
| Build | macOS | required | Xcode | none |
| Archive | macOS | required | Xcode | code-signing cert + provisioning profile |
| Distribute | macOS | required | xcrun altool / notarytool | ASC API key |

The Lint job's "Linux" assumption is the most commonly violated. Fix it — Linux runners are ~10× cheaper per minute on hosted CI.

## Rules

- Five jobs: Lint, Test, Build, Archive, Distribute. Order matters.
- Lint runs on Linux. Everything else needs macOS + Xcode.
- PRs gate on Lint + Test + Build. Archive and Distribute run only on `main` push or tags.
- Run Lint and Test in parallel; run Build serially after both pass.
- Skip UI tests on PR runs by default; gate them on `main` or an explicit flag.
- Always upload `.xcresult`, `.xcarchive`, and dSYMs as artifacts. Never cache them.
- Cache DerivedData and SPM downloads; never cache certificates or build artifacts.
- Each job must produce a unique build number — never let App Store Connect reject for duplicates.
- A test job that passes on PR but breaks on `main` indicates flaky tests; investigate, don't retry.
