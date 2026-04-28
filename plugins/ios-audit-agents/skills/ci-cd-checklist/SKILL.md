---
name: ci-cd-checklist
description: Operational checklist that audits dimension 3.9 (CI/CD & release engineering) of the ios-audit-agents quality model — pipelines, merge gates, signing, environments, rollouts, release notes, hotfix path and branch protection — and emits findings conforming to the audit output spec. Use when an audit covers CI/CD without a dedicated agent. Looks at GitHub Actions, GitLab CI, Bitrise, Xcode Cloud and Fastlane configurations, plus repository hosting settings (branch protection rules). Pairs with the quality-model, ai-risk-catalog and audit-output-format skills.
---

# CI/CD checklist — dimension 3.9

This skill is the operational lens for auditing **dimension 3.9 — CI/CD & release engineering** of the quality model. Unlike the consultative skills (`quality-model`, `ai-risk-catalog`, `audit-output-format`), this one runs the checks and emits findings. Every finding produced by this skill carries `dimension: "3.9"`.

The canonical sources are:

- Dimension definition: `../../docs/QUALITY_FRAMEWORK.md` Section 3.9.
- AI-typical risk: `../../docs/AI_RISK_CATALOG.md` entry `AI-3.9-001`.
- Output contract: `../../docs/AUDIT_OUTPUT_SPEC.md`.

## Scope

In scope (this skill audits all of these):

- CI workflows: build, test, lint, coverage, format, generate-mocks.
- **Merge gates**: which checks are *required* by branch protection vs merely visible.
- Code signing and provisioning automation.
- Release pipelines: TestFlight, App Store, internal/beta tracks.
- Environment separation (development/staging/production builds).
- Rollback and hotfix paths.
- Release notes generation or curation.
- Branch protection rules on the default branch and any release branches.

Out of scope (do not emit findings for these here):

- Build performance and runner cost — that belongs to `3.14 Performance & energy`.
- Internal developer scripts, bootstrap docs, README onboarding — that belongs to `3.10 Developer experience`, which is `out-of-plugin-scope (manual)`.
- Test strategy and coverage thresholds themselves — that belongs to `3.8 Testing strategy`. (The *enforcement* of those checks as merge gates does belong here.)
- Code signing key storage and secrets handling — that belongs to `3.6 Security & privacy`. (The *automation* of signing belongs here.)

When a candidate finding straddles a boundary, prefer the more specific dimension and let the dedicated agent (when it exists) own it.

## Operating rules

- Read all three companion skills (`quality-model`, `ai-risk-catalog`, `audit-output-format`) before producing findings.
- Detect the CI platform first; if more than one is present, audit all of them but de-duplicate findings (one finding per defect, not one per platform).
- Always emit `dimension: "3.9"` on findings produced by this skill.
- The single AI-typical risk in the catalog for this dimension today is `AI-3.9-001`. Use it whenever the finding matches "checks run but are not required to merge". Do not invent other AI risk IDs for 3.9.
- If a check fails for "no CI configuration found at all", emit a single P1 finding rather than one per missing capability — surface the absence, do not pretend each item is independent.
- Branch protection lives on the hosting platform (GitHub, GitLab, Bitbucket), not in the repo. If the agent cannot inspect the platform settings (no API token, no `gh`/`glab` CLI), record that limitation in the audit's `notes`, do not infer protection from the absence of evidence.
- Severity defaults below are *defaults*. Override when the project context warrants it (e.g. a side-project with no users may downgrade signing automation from P1 to P2). Document the override in the finding's `remediation` paragraph.

## Topic router

| You need to know… | Source |
|---|---|
| What "CI/CD & release engineering" formally covers | `QUALITY_FRAMEWORK.md` Section 3.9 |
| The AI-typical risk for this dimension and its manifestation | `AI_RISK_CATALOG.md` entry `AI-3.9-001` |
| How to encode a finding (fields, severities, references) | `audit-output-format` skill |
| How to map findings to the right dimension | `quality-model` skill |
| Whether 3.9 is in scope at all today | `quality-model` skill, coverage snapshot |

## The checklist

Each item has: what to check, where to look, severity default, AI-typical mapping, recommended `references`. Items map one-to-one onto findings when they fail.

### C1 — A CI configuration exists

- **Check**: at least one of `.github/workflows/*.yml`, `.gitlab-ci.yml`, `bitrise.yml`, `.xcode-cloud/`, `fastlane/Fastfile` is present and valid.
- **Severity default if missing**: P1.
- **AI-typical**: `false` (absence is not specifically AI-typical; AI usually scaffolds *something*).
- **References**: `iso:25010`.

### C2 — Build runs on every PR / merge request

- **Check**: the CI configuration triggers on PR/MR events and runs `xcodebuild` or `fastlane` build for the main schemes.
- **Severity default if missing**: P1.
- **AI-typical**: `false`.
- **References**: `iso:25010`.

### C3 — Tests run on every PR / merge request

- **Check**: unit tests and (where present) snapshot/UI tests run on PR/MR events.
- **Severity default if missing**: P1.
- **AI-typical**: `false`.
- **References**: `apple:testing`, `iso:25010`.

### C4 — Lint runs on every PR / merge request

- **Check**: SwiftLint, SwiftFormat or equivalent runs on PR/MR events.
- **Severity default if missing**: P2.
- **AI-typical**: `false`.
- **References**: `iso:25010`.

### C5 — CI checks are required by branch protection (the AI-typical gap)

- **Check**: on the hosting platform, the default branch protection rule lists the build/test/lint workflow status checks under "required status checks". This is the difference between "the check runs" and "the check blocks merge".
- **Severity default if missing**: **P1** when build or tests are not required; **P2** when only lint is not required.
- **AI-typical**: `true`. `ai_risk_id: "AI-3.9-001"`.
- **References**: `iso:25010`, `hudson:281` if relevant.
- **Notes**: this is the canonical "required gates not actually required" finding. Always check it explicitly even when C1–C4 pass.

### C6 — Default branch is protected against direct pushes and force pushes

- **Check**: branch protection requires a PR to merge into the default branch; force-push and direct push are forbidden; deletions are forbidden.
- **Severity default if missing**: P0 if force push allowed on default branch; P1 if direct pushes allowed without review.
- **AI-typical**: `false`.
- **References**: `iso:25010`.

### C7 — Code review is required before merge

- **Check**: branch protection requires at least one approving review; stale approvals are dismissed on new commits.
- **Severity default if missing**: P1 (P2 for very small teams, document in remediation).
- **AI-typical**: `false`.
- **References**: `iso:25010`.

### C8 — Code signing and provisioning are automated

- **Check**: signing is handled by `fastlane match`, `xcodebuild` automatic signing with a documented provisioning profile, or Xcode Cloud workflows. The README or a CI doc explains how a new developer obtains signing credentials.
- **Severity default if missing**: P1.
- **AI-typical**: `false`.
- **References**: `apple:review`, `iso:25010`.

### C9 — Build artifacts are environment-separated

- **Check**: distinct schemes/configurations exist for dev/staging/production (or the project's equivalents) and CI knows which is which. Production builds do not embed development endpoints or debug flags.
- **Severity default if missing**: P1 if production embeds debug flags; P2 if environments exist but are not wired to CI.
- **AI-typical**: `false`.
- **References**: `iso:25010`.

### C10 — Release pipeline to TestFlight / App Store is automated

- **Check**: a CI workflow uploads to TestFlight (and optionally App Store) on a release tag, release branch, or manual trigger. The workflow does not require a developer's local machine.
- **Severity default if missing**: P2 (P1 for products with user-facing release cadence).
- **AI-typical**: `false`.
- **References**: `apple:review`, `iso:25010`.

### C11 — Release notes are generated or curated as part of the pipeline

- **Check**: release notes are produced from commits/PRs (e.g. `release-please`, `git-cliff`, custom action) or curated in a `CHANGELOG.md` updated per release.
- **Severity default if missing**: P3 (P2 if the team has documented release notes as a requirement and is not producing them).
- **AI-typical**: `false`.
- **References**: `iso:25010`.

### C12 — A documented hotfix path exists and has been exercised

- **Check**: documentation describes how to ship a hotfix (branch from latest release tag, expedited review, separate release notes). Look for evidence the path has been used: at least one tag matching a hotfix pattern (`*-hotfix.*`, `*+hotfix*`) or a PR with a hotfix label.
- **Severity default if missing**: P2 (P1 for products in the App Store with active users).
- **AI-typical**: `false`.
- **References**: `iso:25010`.

### C13 — A rollback strategy exists

- **Check**: documentation describes how to roll back a release (revert via App Store Connect, kill-switch via remote config, server-side feature flags). For App Store distribution, document the "phased release pause" workflow.
- **Severity default if missing**: P2.
- **AI-typical**: `false`.
- **References**: `apple:review`, `iso:25010`.

### C14 — Secrets are not stored in CI configuration files

- **Check**: no plaintext API keys, signing keys or tokens in workflow files. Secrets come from the platform's secret store (`secrets.GITHUB_TOKEN`, GitLab CI variables, Xcode Cloud environment variables, etc.). This skill produces a *cross-reference* finding only when CI files contain secrets; deeper secret-handling audits belong to `3.6 Security & privacy`.
- **Severity default if missing**: P0.
- **AI-typical**: `false` for this dimension (the AI-typical risk for hardcoded secrets is `AI-3.6-001`, not 3.9).
- **References**: `masvs:storage`.
- **Notes**: when emitting this finding, set `dimension: "3.9"` (the configuration file is a CI artefact) and add a `remediation` line that mentions the related `AI-3.6-001` risk so the future security agent can connect both findings.

## Severity quick reference for this skill

| Default | Used for |
|---|---|
| **P0** | Force push allowed on default branch (C6); secrets in CI files (C14). |
| **P1** | No CI at all (C1); build/tests not running on PR (C2/C3); checks not enforced as merge gates for build/tests (C5); no signing automation (C8); production embeds debug flags (C9); direct push allowed without review (C6/C7). |
| **P2** | Lint not running (C4) or not required (C5); environments not wired to CI (C9); no automated release pipeline (C10); no documented hotfix path (C12); no rollback strategy (C13). |
| **P3** | No release notes generation (C11) when not declared as a requirement. |

Severities are defaults; override per project context and document the reason in `remediation`.

## Mapping a checklist failure to a finding

For each failed item, build a finding object as defined by `audit-output-format`:

```json
{
  "id": "cicd-<short-slug>",
  "dimension": "3.9",
  "severity": "<P0|P1|P2|P3>",
  "title": "<one-line title>",
  "evidence": {
    "files": [{ "path": "<ci-config-path>", "lines": [<line>] }],
    "metrics": [],
    "logs": []
  },
  "ai_typical": <true|false>,
  "ai_risk_id": "<AI-3.9-001 only when ai_typical: true>",
  "remediation": "<action-oriented sentence>",
  "references": ["<prefix:slug>", ...]
}
```

Conventions specific to this skill:

- Use `id` prefix `cicd-`.
- For C5 always set `ai_typical: true` and `ai_risk_id: "AI-3.9-001"`.
- For C14 (secrets in CI files), keep `dimension: "3.9"` but reference `AI-3.6-001` in the remediation text only — never set `ai_risk_id` to a non-3.9 ID.
- When inspection of the hosting platform is not possible, omit the relevant findings (do not guess) and add an entry to the audit's top-level `notes.dimensions_in_scope_with_zero_findings` only when no other 3.9 finding has been produced.

## Platform-specific hints

These hints help find the evidence; they do not change what is being audited.

- **GitHub Actions**: workflows under `.github/workflows/`. Branch protection via the `gh` CLI (`gh api repos/:owner/:repo/branches/<branch>/protection`) or repo settings. Required status checks under `required_status_checks.contexts`.
- **GitLab CI**: pipeline in `.gitlab-ci.yml`. Branch protection via `glab` CLI (`glab api projects/:id/protected_branches`) or repo settings. "Push rules" cover force-push and direct-push policies. Status checks not required for merge unless the project enforces "Pipelines must succeed".
- **Bitrise**: pipeline in `bitrise.yml`. Required for merge is configured in the hosting platform (still GitHub/GitLab), not in Bitrise.
- **Xcode Cloud**: workflows in App Store Connect; configuration may be referenced from `.xcode-cloud/` or `ci_scripts/`. Required-for-merge again lives on the hosting platform.
- **Fastlane**: `fastlane/Fastfile`. Look for `match`, `gym`, `pilot`, `deliver` lanes for signing, build, TestFlight, App Store. Lanes invoked from CI workflows are the link between the two.

## Bilingual note

The canonical sources are bilingual: `QUALITY_FRAMEWORK.md` / `.es.md`, `AI_RISK_CATALOG.md` / `.es.md`, `AUDIT_OUTPUT_SPEC.md` / `.es.md`. This skill is currently English-only; a Spanish counterpart can be added later under the same skill name in another language without breaking the contract, since the JSON output is language-agnostic.
