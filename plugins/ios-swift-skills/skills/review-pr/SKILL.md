---
name: review-pr
description: Review Swift/SwiftUI code for quality, correctness, and project conventions. Use before opening a PR, after implementing a feature, or any time you want to audit existing code for problems. Checks MVVM patterns, @Observable usage, SwiftUI best practices, deprecated APIs, localization, design tokens, accessibility, performance, and concurrency. Can review a branch diff or specific files.
---

# Code Review — Pre-PR

Review code on the current branch, detecting common problems before opening a PR. Focus on Swift/SwiftUI best practices, project conventions, and accessibility.

## Step 1: Get the changes

```bash
BASE_BRANCH=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}')
[ -z "$BASE_BRANCH" ] && BASE_BRANCH="main"
echo "Base branch: $BASE_BRANCH"
git diff $BASE_BRANCH...HEAD --name-only --diff-filter=ACMR
git diff $BASE_BRANCH...HEAD
```

Read each modified file with the Read tool for full context. If there are more than 15 files, prioritize those with the most changes.

## Step 2: Apply checks

**Only report problems you actually find.** If a category is clean, skip it entirely.

---

### Critical

**State management violations**
- `@State` without `private` — must always be `private`.
- `@Published` or `ObservableObject` in new code — use `@Observable` (Observation framework).
- `@Observable` class without `@MainActor` annotation.
- ViewModel not owned via `@State private var viewModel:` in the view.
- `@StateObject` or `@ObservedObject` in new code — use `@State` with `@Observable`.
- Values passed into `@State` as parameters (only accepts initial values).

**Hardcoded user-facing strings**
- Text literals in views without `String(localized:)` or `Text("key.name")`.
- If the project has multiple languages, remind about adding translations for all of them.

**Business logic in views**
- Logic, computation, or side effects directly in a view `body`. Must be in the ViewModel.
- Button actions with inline logic instead of referencing a method.
- Sorting, filtering, or formatting inside `body` or `ForEach`.

**Data access without protocol**
- Direct access to data sources (e.g. HealthKit, CoreData, network API) without going through a protocol abstraction.

**Force unwraps**
- `!` for force unwrap where `guard let`, `if let`, or nil-coalescing would work.

---

### Medium

**Deprecated SwiftUI APIs**
- Check changed files against `references/deprecated-apis.md` for deprecated modifiers and patterns.
- Common offenders: `foregroundColor` -> `foregroundStyle`, `.cornerRadius` -> `.clipShape`, `.animation()` without `value:`.

**View composition**
- Computed properties or methods returning `some View` — extract to separate `View` structs.
- Multiple top-level type definitions in a single file — each type should have its own file.
- Excessively long `body` properties — break into extracted subviews.

**Accessibility**
- `onTapGesture` where `Button` should be used (VoiceOver cannot detect tap gestures).
- Missing `accessibilityLabel` on icon-only buttons or images.
- Custom numeric values that should use `@ScaledMetric` for Dynamic Type.

**Performance**
- `ForEach` using `.indices` for dynamic content — use stable `Identifiable` identity.
- `AnyView` in list rows — kills diffing performance.
- Eager stacks (`VStack`/`HStack`) with many children where `LazyVStack`/`LazyHStack` would be better.
- Object creation inside `body`.

**Tests**
- New logic without corresponding tests.
- `@Test` without a descriptive title in natural language.
  - Correct: `@Test("Distance formats correctly for metric units")`
  - Incorrect: `@Test func testDistanceFormats()`
- New tests using XCTest (`XCTestCase`) instead of Swift Testing (`@Test`, `#expect`).

**Weak references**
- Closures capturing `self` without `[weak self]` where a retain cycle is possible.

**Concurrency**
- UI updates from a context that doesn't guarantee the main thread without `@MainActor`.
- `DispatchQueue` usage in new code — prefer `async/await` with actors.
- `Task.sleep(nanoseconds:)` instead of `Task.sleep(for:)`.

---

### Minor

**Dead code**
- Unused methods, properties, types, or protocol conformances after refactoring.

**Naming**
- Variables, functions, or types with generic or ambiguous names.
- Types representing a specific standard should include it in the name.

**Stale comments**
- Comments that no longer reflect the current code.

**Redundant `return`**
- In single-expression functions (Swift 5.9+), `return` is unnecessary.

**Swift style**
- `String(format: "%.2f", value)` — use `FormatStyle` APIs instead.
- `Date()` — prefer `Date.now`.
- `if let value = value` — prefer `if let value` shorthand.

---

### Project-specific checks

If the project defines conventions in its `CLAUDE.md`, `AGENTS.md`, or documentation, also verify:

**Design system compliance**
- Raw `Button` instead of a project-specific button component (e.g. `AppButton`).
- Inline styles instead of design tokens (spacing, typography, colors).
- System colors (`.systemBlue`, `.label`) instead of project semantic colors.
- Corner radius via raw numbers instead of project tokens (e.g. `.radiusMedium`).
- Missing `EmptyStateView` for empty, error, or loading states (custom inline implementations).

**Formatting**
- Inline formatting of distance, duration, pace, or dates instead of using project formatters (e.g. `Formatters`).

**Localization completeness**
- New string keys without translations in all supported languages.

**Data access patterns**
- Raw callback-based queries (e.g., HealthKit, CoreData) instead of `async/await` with `withCheckedContinuation`.
- `DispatchQueue` usage in new data access code — must use structured concurrency.
- Missing authorization/permission check before accessing protected data.

**Security**
- Sensitive data (health data, tokens) logged via `print()` or `os_log` without redaction.

---

## Step 3: Report format

```
## Code Review — [branch name]

### Critical
[If any]

### Medium
[If any]

### Minor
[If any]

### PR Reminders
[Only if relevant to the change]

---
Ready for PR / Needs fixes before PR
```

For each issue, use before/after format:

```
**[File:line]** — Rule name.

// Before
problematic code

// After
corrected code
```

- Line numbers refer to the full file (from Read), not the diff.
- If a line range, use `File:12-18`. If line is unclear, use just the file name.
- If no issues found, report: `No issues detected — ready for PR`.
