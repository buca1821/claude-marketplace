# Branch Protection — `main` is sacred

Branch protection rules are the gates that turn "we have CI" into "broken code cannot reach `main`." Without them, any contributor can push directly, bypass review, or merge a PR while CI is still red — and the value of the pipeline collapses.

This reference covers what to protect, what to require, and how to enforce it. The platform-specific syntax (GitHub rulesets, GitLab push rules, Bitbucket branch permissions) varies, but the policy does not.

## What `main` should mean

`main` is the source of truth for what is shippable, or close to it. Every commit on `main` should:

1. Pass the Lint, Test, and Build stages (see `pipeline-jobs.md`).
2. Have been reviewed by at least one other person (or, for solo projects, marked as reviewed by yourself with a clear gate).
3. Be reachable by following PR history — never a force-push, never a direct commit.
4. Be uniquely identifiable for rollback (linear history or merge commits, but not mixed).

Every protection rule below exists to enforce one of those four properties.

## Required status checks

The single most important rule: **PRs cannot merge until specified checks pass.**

```
Required checks:
  - lint
  - test
  - build
```

These are the names of the CI jobs (or workflows) that must report a green status before the merge button enables. The names must match exactly — a typo silently disables the check.

**"Strict" mode:** the PR must be up to date with `main` *and* the checks must have run on the merged version, not on a stale base. Without strict mode, a PR can pass CI on top of a stale `main`, get merged, and break `main` because the merged code was never tested as a unit.

Trade-off: strict mode means contributors must rebase or update branches more often, which can be friction on a busy repo. For low-traffic repos, enable it. For high-traffic ones, consider a merge queue (below) instead.

## Required reviews

```
Required reviews: 1 (or more)
Dismiss stale approvals: yes
Require review from code owners: yes (if CODEOWNERS exists)
```

- **At least 1 approving review.** For solo projects, you can drop to 0 but only if you compensate with a strict CI gate and a written discipline ("self-review every PR before merge").
- **Dismiss stale approvals when new commits are pushed.** Otherwise an approval at commit `abc` carries over to `xyz` even though `xyz` is a different change. This is the most commonly forgotten rule and the most important for catching scope creep mid-review.
- **CODEOWNERS** lets you require approval from specific people for specific paths. Works at any project size — even solo, it's useful for marking "this folder is delicate."

## Linear history vs merge commits

Pick one:

- **Linear history (rebase / squash only):** Every commit on `main` has exactly one parent. `git log --oneline main` reads as a clean changelog. Best for small teams and for projects where commits are atomic features.
- **Merge commits required:** Every PR creates a merge commit. The PR's individual commits are preserved. Best for teams that work on long-lived branches with intermediate commits worth keeping.

**Don't mix the two.** A repo that allows both becomes hard to read and bisect — `git bisect` skips merge commits inconsistently, and commit messages drift between styles.

For most iOS projects, **squash-merge** is the right default: one PR equals one commit on `main`, the commit message is the PR title (which the project already uses Conventional Commits for), and bisecting works perfectly.

## Disallowing direct pushes to `main`

```
Restrict who can push to matching branches: <empty list>
Allow force pushes: never
Allow deletions: never
```

Setting "restrict pushes" to an empty list means no one — not even admins — can push directly. Everything goes through PRs. Combined with required reviews and required checks, this is the airtight version.

If your team needs an emergency override (e.g., the build is broken and you need to push a hotfix at 3 AM), grant a temporary admin override rather than relaxing the rule globally. Most platforms support this with audit logs.

**Never allow force pushes.** Force-pushing rewrites history, breaks every clone, and there's no scenario where it's the right answer on `main` — if you need to undo a bad commit, do `git revert`, which is itself a regular commit and goes through the same PR + review flow.

## Signed commits (optional but recommended)

```
Require signed commits: yes
```

Forces every commit on `main` to be signed with a GPG key or SSH signing key registered to the author's account. Prevents impersonation — someone with write access to the repo cannot land a commit attributed to a different developer.

For solo projects this matters less, but it's free to enable once you've set up signing locally. For team projects, especially those that ship to production, it's a basic supply-chain hygiene step.

## Merge queues

For repos with > 5 PRs/day all gating on the same `main`, status checks can become a coordination problem: PR A passes CI, PR B passes CI, both merge, and the combined result fails. A merge queue solves this:

```
PR approved
   ↓
Joins queue
   ↓
Queue rebases the PR on the latest main (or on the previous queued change)
   ↓
Re-runs CI
   ↓
On green, merges to main
```

GitHub, GitLab, and Bitbucket all have native merge queue support. For small projects (a handful of PRs/week), don't bother — the overhead is bigger than the benefit. For active projects, it's the difference between "CI is reliable" and "CI is a coin flip."

## Rules that target specific paths

For monorepo-ish projects (app + extensions + a shared SPM module), you can require different reviewers per path via `CODEOWNERS`:

```
# .github/CODEOWNERS
/Sources/Network/   @network-team
/Sources/UI/        @ui-team
/CI/                @platform-team
/PrivacyInfo.xcprivacy  @platform-team @legal
```

The last line is one of the few "review required" rules worth setting at a tiny project size — privacy manifests are easy to get wrong, and a second pair of eyes prevents an App Store rejection.

## Configuration in version control

Both GitHub and GitLab support declarative branch protection (GitHub: `branch ruleset`, GitLab: `Protected Branches API`). Treat these as code: store them in a `.github/rulesets/` or equivalent and apply via Terraform or a CI job. Don't configure them via the UI and forget about it — that's how rules drift and silent gaps appear.

Minimal example (GitHub ruleset, JSON):

```json
{
  "name": "main protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": { "include": ["refs/heads/main"], "exclude": [] }
  },
  "rules": [
    { "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "lint" },
          { "context": "test" },
          { "context": "build" }
        ]
      }
    },
    { "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true
      }
    },
    { "type": "non_fast_forward" },
    { "type": "deletion" }
  ]
}
```

`non_fast_forward` blocks force pushes. `deletion` blocks branch deletion.

## What happens when force-push is attempted

A protected branch returns:

```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: Cannot force-push to a protected branch
```

The push is rejected; nothing on the remote changes. The local repo still has the rewritten history — the contributor must reconcile by merging or re-rebasing on the actual `main`.

**Never disable the protection to allow a one-off force-push.** If the situation truly requires it (you committed secrets, you need to expunge a file from history), use BFG or `git filter-repo` and coordinate the rewrite as a planned event with all collaborators, not a stealth push.

## Testing the protection rules

Before relying on them, verify they work:

1. From a clean clone, attempt a direct push to `main`. Confirm it's rejected.
2. Open a PR with a deliberately failing test. Confirm the merge button is disabled.
3. Approve a PR, then push a new commit. Confirm the approval is dismissed.
4. Attempt a force-push. Confirm rejection.

Five minutes of testing prevents months of "we thought CI was gating but it never was."

## Solo projects

If you're the only developer:

- Require status checks: yes (still — your own code can break).
- Require reviews: 0 (or 1 self-review with discipline).
- No direct pushes: yes — even your own pushes go through PRs. This forces the CI loop.
- Linear history with squash merge: yes.
- Signed commits: optional.

The "PR even when I'm alone" rule sounds excessive. It isn't. The PR is where CI runs, where you read the diff one more time, and where you create a written record that a future you (or your eventual collaborator) can read.

## Rules

- `main` is protected: required CI checks, no direct pushes, no force-pushes, no deletions.
- Required checks include at least Lint, Test, Build. Use exact job names.
- Enable strict mode (must be up to date with `main`) unless you use a merge queue.
- Require at least 1 approving review and dismiss stale approvals on new commits.
- Pick squash, rebase, or merge — never all three at once. Squash is the default for most projects.
- Store ruleset config in version control. Apply declaratively.
- For projects with > 5 PRs/day on the same branch, use a merge queue.
- Test the rules from a clean clone before depending on them.
- Require signed commits for production projects; nice-to-have otherwise.
