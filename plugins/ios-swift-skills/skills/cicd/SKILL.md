---
name: cicd
description: CI/CD strategy for iOS projects — the canonical pipeline jobs (lint, test, build, archive, distribute), branch protection, release flow, and code signing. Use when setting up continuous integration, defining merge gates, automating releases, or troubleshooting CI failures.
---

# CI/CD Skill

## Operating Rules

- Every iOS pipeline runs the same five jobs in order: **Lint → Test → Build → Archive → Distribute**. Order matters; gates are absolute.
- `main` is protected: required CI checks (Lint + Test + Build), required reviews, no direct pushes, no force-pushes.
- Lint runs on Linux. Everything else needs macOS + Xcode.
- PRs gate on Lint + Test + Build only. Archive and Distribute run on `main` push or release tags — never on every PR.
- `main` push auto-deploys to TestFlight Internal. External testing and App Store gate on tag pushes.
- The choice of platform (GitHub Actions, Xcode Cloud, GitLab CI, Bitrise) is a project-level decision and an implementation detail — the jobs and gates above don't change.
- Build numbers are unique and monotonic per upload. Marketing version comes from the git tag, not edited by hand.
- Code signing uses manual signing in CI; automatic signing is for local Debug only. Certificates and provisioning profiles ship as base64 secrets, imported into a fresh per-run keychain.

## Topic Router

| Topic | Reference |
|-------|-----------|
| The five canonical pipeline jobs (Lint, Test, Build, Archive, Distribute) | `references/pipeline-jobs.md` |
| Protecting `main`: required checks, reviews, force-push rules, merge queues | `references/branch-protection.md` |
| Release flow: tag → archive → TestFlight, versioning, ASC API key | `references/release-pipeline.md` |
| Code signing: certs, profiles, keychain setup, common failures | `references/code-signing.md` |
| GitHub Actions implementation example (one platform's translation of the above) | `references/github-actions.md` |
| Troubleshooting CI failures (signing, scheme, simulator, cache) | `references/troubleshooting.md` |

## When You're Setting Up CI for the First Time

1. **Decide branch protection first.** Read `branch-protection.md`. Set the rules in the repo before writing any CI YAML — gates are useless if anyone can push around them.
2. **Implement Lint and Test as the gating jobs.** See `pipeline-jobs.md`. These two pass first; everything else builds on them.
3. **Add Build as a third gate.** Catches Release-only compile errors that Test (Debug) misses.
4. **Set up code signing once.** See `code-signing.md`. Bootstrap the certs and profile, store as secrets. Without this, Archive can't run.
5. **Wire up Archive and Distribute for release events.** See `release-pipeline.md`. Tag-driven, not PR-driven.
6. **Pick a platform.** GitHub Actions example in `references/github-actions.md`. Xcode Cloud, GitLab CI, Bitrise translate from the same job structure.

## CI Checklist

- [ ] Lint, Test, Build are required status checks on `main`.
- [ ] PRs cannot merge with red CI; stale approvals dismiss on new commits.
- [ ] No direct pushes to `main`; no force-pushes; no deletions.
- [ ] Linear history (squash/rebase) or merge commits — pick one, not both.
- [ ] Lint job runs on Linux runners.
- [ ] Test job uses a Simulator that exists on the runner image (named or `latest`).
- [ ] Coverage thresholds enforced from `.xcresult`, not just measured.
- [ ] UI tests skipped on PR runs; gated on `main` or explicit flag.
- [ ] Code signing setup uses a fresh per-run keychain with `set-key-partition-list`.
- [ ] Build numbers monotonically increase; marketing version comes from git tag.
- [ ] dSYMs uploaded as artifacts on every Archive.
- [ ] App Store Connect API key (`.p8`) used for upload, not Apple ID.
- [ ] Release notification posted to a humans-read channel.
- [ ] `PrivacyInfo.xcprivacy` validated on Archive (see the `security` skill, `privacy-manifests` reference, for content).
