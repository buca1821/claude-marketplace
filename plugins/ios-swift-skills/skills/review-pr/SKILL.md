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
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo "Base branch:    $BASE_BRANCH"
echo "---"
git log --oneline $BASE_BRANCH..HEAD
echo "---"
git diff $BASE_BRANCH...HEAD --name-only --diff-filter=ACMR
git diff $BASE_BRANCH...HEAD
```

Print the current branch first and use it in the report header — do not rely on any branch name from earlier in the conversation, snapshot, or system context, since those may be stale if the user switched branches mid-session.

Read each modified file with the Read tool for full context. If there are more than 15 files, prioritize those with the most changes.

**Distinguish "added in this PR" from "pre-existing code".** The `git diff $BASE...HEAD` output is authoritative for *what changed*, but the `Read` step loads each modified file in full — so the context you have for any given file mixes new lines (in the diff hunks) with pre-existing lines (unchanged). Only flag issues for lines that actually live inside a diff hunk for this PR. If you are unsure whether a specific line is new (especially for "unused / dead / placeholder" findings), verify with:

```bash
git log -p $BASE_BRANCH..HEAD -- <file>   # commits in this PR that touch the file
git blame -L <start>,<end> -- <file>      # who added the specific line
```

**Distinguish branch-naming mismatch from scope mixing.** A branch named `chore/foo` that contains feature commits is a naming smell, resolvable by renaming or by an explicit PR-description note. It is **not** the same as a PR mixing scopes. Confirm scope mixing only by inspecting the actual commits (`git log --oneline $BASE..HEAD` plus the paths each one touches) — never by branch name alone.

### Step 1b — Optional scope context

Before listing minor issues, optionally ask the user: *"Is there a plan, spec, or scope context for this PR I should know about (e.g. things that are intentional placeholders, deferred to a later PR, or already covered by an earlier merge)?"*

If they answer, demote anything covered by that context from `Minor` issue to `PR Reminders` (or drop it entirely). Typical examples worth flagging as *signals of scope* rather than defects: stub destinations (`Text(verbatim: "Detail #...")`), single-device snapshot coverage, loose snapshot precision, unused localization keys that a later PR will consume. If you have no scope context and the placeholder looks deliberate, prefer asking over listing as a Minor issue.

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

**View composition (stylistic)**
- Computed properties or methods returning `some View`. With `@Observable`, change propagation tracks specific keyPaths read inside a view, not struct identity, so extracting to dedicated `View` structs does not reduce re-evaluations in small files. Promote to `Medium` only when at least one of the following applies:
  - (a) the subview owns its own `@State` that must survive parent rebuilds;
  - (b) the same subview is reused in more than one place;
  - (c) the body is hard to read (deep nesting, or roughly 40+ lines for a single subview);
  - (d) the file is large enough that explicit `View` struct boundaries materially help navigation.

  Otherwise list as `Minor` or skip. This mirrors the Apple guidance (composition is free; identity is structural) and Paul Hudson's rule of thumb ("extract when your code becomes hard to read, not to chase performance").

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
