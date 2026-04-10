---
name: cicd
description: CI/CD for iOS projects with GitHub Actions — build, test, and lint on PRs. Use when setting up continuous integration, automating builds, configuring test pipelines, or troubleshooting CI failures.
---

# CI/CD Skill

## Operating Rules

- GitHub Actions is the default CI platform for this template
- Workflows run on macOS runners with Xcode pre-installed
- Cache SPM dependencies and DerivedData to speed up builds
- Keep workflows simple — one job for build+test, separate for release
- Never store secrets in workflow files — use GitHub Secrets

## Task Workflow

### Set up CI for a new project
1. Create `.github/workflows/ci.yml` from the template in `references/github-actions.md`
2. Configure scheme and simulator names to match the project
3. Add secrets in GitHub repo settings if needed
4. Test with a PR

### Troubleshoot CI failures
1. Check build logs in the GitHub Actions tab
2. Common issues: Xcode version mismatch, missing simulator, SPM resolution
3. Consult `references/troubleshooting.md`

### Topic Router

| Topic | Reference |
|-------|-----------|
| GitHub Actions workflow | `references/github-actions.md` |
| CI troubleshooting | `references/troubleshooting.md` |

## CI Checklist

- [ ] Workflow triggers on PR to main and push to main
- [ ] Xcode version pinned via `maxim-lobanov/setup-xcode`
- [ ] SPM dependencies cached
- [ ] Build succeeds in Release configuration
- [ ] All tests pass
- [ ] Concurrency group cancels redundant runs
- [ ] Secrets injected via GitHub Secrets (not hardcoded)
