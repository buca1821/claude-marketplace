---
name: xcode-qa
description: Build, test, and QA specialist for iOS/macOS projects using XcodeBuildMCP. Use when you need to compile, run tests, launch the app on a simulator or device, navigate the UI, or diagnose build/test failures.
---

# Xcode QA — iOS/macOS

Procedural guidance for build, test, and QA workflows using XcodeBuildMCP.

## Initial Setup (always do this first)

1. Call `session_show_defaults` to check current configuration.
2. If no project is configured, use `discover_projs` with the project root directory.
3. Call `list_sims` to find available simulators.
4. Call `list_schemes` to confirm available schemes.
5. Set defaults with `session_set_defaults`:
   - `projectPath` or `workspacePath`
   - `scheme` (use the main app scheme)
   - `simulatorName` (prefer latest iPhone available)
   - `useLatestOS: true`
   - `suppressWarnings: true`

## Workflows

### Build
- Use `build_sim` for the current scheme.
- Analyze errors with file paths and line numbers.

### Unit Tests
- Use `test_sim` with the appropriate scheme.
- If the project has a test script (e.g. `./scripts/run-tests.sh`), mention it as an alternative.
- Default: skip UI tests unless explicitly requested (e.g. `--skip-testing ProjectUITests`).
- Report: total, passed, failed, skipped.

### Launch App
- Use `build_run_sim` to compile and launch.
- After launch, use `screenshot` to verify visual state.

### UI Inspection
- Always use `describe_ui` before interacting to get precise coordinates.
- Use `tap` / `swipe` / `type_text` based on `describe_ui` output.
- Use `screenshot` after actions for visual verification.

## Important Notes

### iCloud Drive projects
SourceKit may report false-positive errors when the project is on iCloud Drive. Trust `xcodebuild` output, not IDE diagnostics. If SourceKit shows errors but the build succeeds, the errors are false positives.

### Post-test verification
After running tests, check for:
- New concurrency warnings (Sendable, @MainActor isolation)
- Tests that pass individually but fail in batch (order-dependent state)

## Reporting Format

### Build
- **Status**: SUCCESS / FAILURE
- **Scheme**: [scheme] | **Simulator**: [name]
- **Errors**: [count] — list each with file and line
- **Warnings**: [count] (if relevant)

### Tests
- **Status**: PASSED / FAILED
- **Total**: [N] | **Passed**: [N] | **Failed**: [N] | **Skipped**: [N]
- List failed tests with reason

## Error Recovery
- **Simulator not found**: list with `list_sims`, suggest the closest match.
- **Build/test failure**: analyze logs, propose a fix before retrying.
- **Cache issues**: run `clean` and retry.
