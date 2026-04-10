# tdd-bug-fix

Fix a bug using the reproduce-first TDD workflow. Write a failing test, then fix, then verify.

## Input

Bug description or issue number: `$ARGUMENTS`

If an issue number is provided, fetch it:
```bash
gh issue view $ARGUMENTS -R owner/repo
```

## Process

### 1. Load TDD skill

Load the testing-tdd skill for the full bug fix workflow reference.

### 2. Understand the bug

Identify:
- Expected behavior vs actual behavior
- Steps to reproduce
- Which code is involved (grep/read the suspected files)

Present findings and wait for confirmation.

### 3. RED — Write failing test

Write a test using Swift Testing that **fails because of the bug**.

```bash
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 16' -only-testing YourAppTests
```

The test MUST fail. If it passes, the bug is not reproduced — make assertions more specific.

### 4. GREEN — Fix the bug

- Change as little code as possible
- Don't refactor while fixing
- Don't fix other issues — file them separately

Run BOTH:
```bash
# The bug fix test
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 16' -only-testing YourAppTests

# ALL tests for regressions
xcodebuild test -scheme YourApp -destination 'platform=iOS Simulator,name=iPhone 16'
```

### 5. Verify

- [ ] Failing test reproduced the bug
- [ ] Fix implemented — test passes
- [ ] All existing tests still pass
- [ ] Edge cases covered
- [ ] Fix is minimal — no unrelated changes

### 6. Build

Use XcodeBuildMCP: `session_show_defaults` → `build_sim`.

## Output

Summarize using this format:

```
Bug Fix: [description]
- Expected: [what should happen]
- Actual: [what was happening]  
- Root cause: [why it was broken]
- Fix: [file:line — what changed]
- Test: [test file — what it verifies]
```
