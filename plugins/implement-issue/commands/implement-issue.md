# implement-issue

Implements a GitHub issue end-to-end: read → plan → code → build → PR → review replies.

## Input

Issue number: `$ARGUMENTS`

If no arguments provided, ask the user which issue to implement.

## Steps

### 1. Detect project context

Determine the GitHub repo from the current git remote:
```bash
git remote get-url origin
```
Extract `owner/repo` from the URL. Read `CLAUDE.md` for project conventions.

### 2. Read the issue

Use `gh issue view $ARGUMENTS` to fetch the issue title, body, and labels.
Read any referenced files in CLAUDE.md or docs/ relevant to the task.

### 3. Outline the plan

In 2–3 sentences, describe what files will change and why.
**Wait for user confirmation before writing any code.**

### 4. Implement

Follow the project's conventions from CLAUDE.md and `.claude/rules/`:
- Architecture patterns (MVVM, state management, DI)
- Localization (never hardcode user-facing strings)
- New tests with Swift Testing (`import Testing`, `#expect`)
- Use `async/await` over callbacks

### 5. Build and test

Use XcodeBuildMCP: `session_show_defaults` → `build_sim`.
Fix all compiler errors before proceeding.
Run tests and fix any failures.

### 6. Self-review

Review the changed files for:
- Architectural compliance with project conventions
- Missing tests for new logic
- Hardcoded strings or magic numbers
Fix any Critical or Medium issues before proceeding.

### 7. Commit and push

- Create branch matching issue type: `feat/<name>-<N>`, `fix/<name>-<N>`, `docs/<name>-<N>`
- Commit message: Conventional Commits in English (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`)
- **Ask for confirmation before `git push`.**

### 8. Create PR

Use `gh pr create` with:
- Title following Conventional Commits
- Body with `Closes #<N>`
- Summary of changes and test plan

### 9. Respond to review comments

After the PR is created, check for automated review comments:
```bash
gh api repos/<owner>/<repo>/pulls/<PR>/comments
```

For each comment, evaluate critically and reply in its own thread.
Do not leave any comment unanswered.
