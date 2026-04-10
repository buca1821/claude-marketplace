# TDD Bug Fix — Reproduce First

Fix bugs the right way: reproduce first, fix second, verify always.

```
Without TDD:   Bug → AI fix → hope it works → bug returns later
With TDD:      Bug → failing test → fix → test passes → regression prevented forever
```

## Process

### Phase 1: Understand the Bug

Identify:
- Expected vs actual behavior
- Steps to reproduce
- Which code is involved

### Phase 2: RED — Write Failing Test

Write a test that **fails because of the bug**:

```swift
import Testing
@testable import YourApp

@Suite("Bug Fix: brief description")
struct BugFix_DescriptionTests {

    @Test("should [expected] — was [actual]")
    func reproduceBug() {
        let result = SomeModule.operation(triggeringInput)
        #expect(result == expectedOutput)  // Fails with current bug
    }
}
```

**The test MUST fail.** If it passes, you haven't reproduced the bug.

### Phase 3: GREEN — Minimal Fix

- Change as little code as possible
- Don't refactor while fixing
- Don't fix other issues — file them separately
- Run ALL tests to check for regressions

### Phase 4: Verify

- [ ] Test fails before fix
- [ ] Test passes after fix
- [ ] All existing tests still pass
- [ ] Edge cases covered
- [ ] Fix is minimal — no unrelated changes

## Output Format

```
Bug Fix: [description]
- Expected: [what should happen]
- Actual: [what was happening]
- Root cause: [why]
- Fix: [file:line — what changed]
- Test: [test file — what it verifies]
```

## Pitfalls

| Pitfall | Solution |
|---------|----------|
| Test passes before fix | Make assertions more specific |
| Fix breaks other tests | Revert, use smaller targeted change |
| Skipping the red step | Always verify test fails first |
| Fixing multiple bugs at once | One bug = one test + one fix |
