---
name: audit-output-format
description: The ios-audit-agents audit output contract — schema v1.0 covering the human-readable Markdown report and the machine-readable JSON record that every audit run must produce. Use when a command or agent has to write audit results to disk, validate that required fields are present, choose a `references` identifier (apple:hig, masvs:storage, hudson:281, ...), apply the privacy redaction policy, or decide where the output files go inside the audited repository. Always paired with the quality-model skill (for dimensions and severities) and the ai-risk-catalog skill (for `ai_risk_id`).
---

# Audit output format — schema v1.0

This skill is the consultative lens over the plugin's output contract. It tells an agent or command **where to write** the audit results, **what fields are required**, **which reference identifiers exist**, and **what must never be included** in the evidence. It does not duplicate the spec — the canonical source is `../../docs/AUDIT_OUTPUT_SPEC.md` (English) and `../../docs/AUDIT_OUTPUT_SPEC.es.md` (Spanish).

## Operating rules

- Every audit run MUST produce both files: a Markdown report (humans) and a JSON record (machines). They cover the same findings; the Markdown is a projection of the JSON.
- Both files MUST have the same base name and live in `<audited-repo>/.claude-marketplace-audits/`. Never write outputs anywhere else (not the plugin folder, not the user's home).
- The JSON `schema_version` is the version of THIS document (`"1.0"` today). The `model_version` is the version of the quality model (`"0.1"` today). They are independent and must not be confused.
- `model_version` and `schema_version` are mandatory in every JSON record; do not omit them even on a no-findings audit.
- All required fields must be present even when empty: `findings: []`, `metrics.by_severity: {"P0": 0, "P1": 0, "P2": 0, "P3": 0}`, `metrics.by_dimension: {}`, `metrics.ai_typical_ratio: 0.0` (not `null`).
- `notes.dimensions_out_of_plugin_scope` is `["3.1", "3.10"]` for quality model v0.1. If the model version changes, recheck this list against the new Section 7.2.
- The privacy rules in Section 4 are **non-negotiable**. When in doubt, redact.

## Topic router

| You need to know… | Section in `AUDIT_OUTPUT_SPEC.md` |
|---|---|
| Where the output files go and how they are named | Section 1 (1.1 directory, 1.2 file naming, 1.3 optional index) |
| The required structure of the Markdown report | Section 2.1 (template) and 2.2 (style rules) |
| The JSON top-level shape and an example | Section 3.1 |
| The full required/optional field reference for the envelope | Section 3.2 |
| What goes inside a single finding object | Section 3.3 |
| The catalog of `references` identifier prefixes | Section 3.4 |
| What must never appear in evidence | Section 4.1 |
| What is recommended in evidence | Section 4.2 |
| How redaction looks in practice | Section 4.3 |
| When to bump major / minor / patch of the schema | Section 5 |
| Aggregation queries the JSON shape supports | Section 6 |
| Worked examples (minimal audit, audit with finding) | Sections 7.1 and 7.2 |

## File output quick reference (mirrors Section 1)

Directory:

```text
<audited-repo>/.claude-marketplace-audits/
```

File naming (UTC ISO 8601 basic, no colons, plus an 8-char audit id):

```text
<UTC-timestamp>__<audit-id>.md
<UTC-timestamp>__<audit-id>.json
```

Example pair: `20260427T134205Z__9f3c1a72.md` / `20260427T134205Z__9f3c1a72.json`.

## JSON envelope required fields (mirrors Section 3.2)

These MUST be present in every record:

- `schema_version` — semver of this spec, `"1.0"` today.
- `audit_id` — `[a-z0-9]{8}`.
- `timestamp` — ISO 8601 UTC with `Z` suffix.
- `model_version` — version of the quality model.
- `plugin_version` — from `plugin.json`.
- `project.name`, `project.git_sha` (`"uncommitted"` when no commit).
- `scope.dimensions_audited` — list of `"3.X"` strings.
- `scope.agents_used` — list of agent names.
- `findings` — array of finding objects (may be empty).
- `metrics.total_findings`, `metrics.by_severity`, `metrics.by_dimension`, `metrics.ai_typical_count`, `metrics.ai_typical_ratio`, `metrics.duration_seconds`.
- `notes.dimensions_in_scope_with_zero_findings`, `notes.dimensions_out_of_plugin_scope`.

Optional but encouraged:

- `project.ios_deployment_target`.
- `scope.skills_used`.

## Finding required fields (mirrors Section 3.3)

Every finding object MUST have:

- `id` — `<auditor-prefix>-<slug>`, stable per run.
- `dimension` — `"3.X"` (never `"3.1"` or `"3.10"`; those are out-of-plugin-scope).
- `severity` — exactly one of `"P0" | "P1" | "P2" | "P3"`.
- `title` — single line.
- `ai_typical` — boolean. Required even when `false`.
- `ai_risk_id` — required IF AND ONLY IF `ai_typical: true`. Format `AI-3.X-NNN`. Resolve via the `ai-risk-catalog` skill.
- `remediation` — action-oriented sentence.
- `references` — array of at least one identifier from Section 3.4 (or a free string if none fits).

Optional:

- `evidence.files`, `evidence.metrics`, `evidence.logs`.

## Reference identifier prefixes (mirrors Section 3.4)

Use these prefixes in `references` so that aggregation across audits is stable:

| Prefix | Source |
|---|---|
| `apple:hig` | Apple Human Interface Guidelines |
| `apple:review` | Apple App Review Guidelines |
| `apple:a11y` | Apple Accessibility documentation |
| `apple:concurrency` | Apple Swift Concurrency documentation |
| `apple:testing` | Apple Swift Testing documentation |
| `apple:oslog` | Apple OSLog documentation |
| `apple:metrickit` | Apple MetricKit documentation |
| `apple:localization` | Apple Localization documentation |
| `masvs:<group>` | OWASP MASVS v2.1 + control group (e.g. `masvs:storage`, `masvs:network`) |
| `iso:25010` | ISO/IEC 25010:2023 |
| `wcag:2.2` | WCAG 2.2 |
| `hudson:<art>` | Paul Hudson, Hacking with Swift article number (e.g. `hudson:281`) |
| `sundell:<topic>` | Swift by Sundell, topic slug |
| `wals:<topic>` | Donny Wals, topic slug |
| `vanderlee:<topic>` | Antoine van der Lee, topic slug |

A reference that does not fit any prefix is allowed as a free string and may be normalized in a future spec version.

## Privacy quick reference (mirrors Section 4)

NEVER include in evidence:

- Verbatim source code excerpts beyond what is strictly needed to identify a finding (use `path:line` instead).
- Secrets in clear text (record location and type only, never the value).
- Personally identifiable information from commits (author email, full names, full commit messages); use only the SHA.
- Customer data of any kind.
- Internal URLs, hostnames, or environment variables.

Recommended in evidence:

- Repo-relative file paths.
- Line numbers and ranges.
- Symbol names when needed for clarity.
- Metric values without user identifiers.
- Log levels and categories without log content.

When in doubt, redact. Use a `path` + `lines` reference, never a `snippet` field.

## Schema versioning rules (mirrors Section 5)

- **Major** (`2.0`, ...): breaking change to the JSON shape. Old logs cannot be read by new tooling without migration.
- **Minor** (`1.1`, ...): backward-compatible additions (new optional fields, new enum values for non-required fields).
- **Patch**: clarification only, no field changes.

Consumers of the JSON MUST check `schema_version` and refuse to operate on a major newer than what they understand.

## Markdown report — what must always appear (mirrors Section 2.1)

The Markdown report MUST self-contain enough information that a reader does not need the JSON:

- Header block: project name, audit id, timestamp, quality model version, plugin version, scope, project commit.
- `## Executive summary` with totals, severity breakdown, AI-typical ratio, top recurring AI risk IDs.
- `## Findings by dimension` grouped under `### 3.X — <name>` and `#### <severity> — <title>` per finding, severity-ordered (P0 → P3), dimensions ordered numerically.
- `## Suggested remediation tasks` flattened severity-ordered list.
- `## Methodology notes` listing agents that ran, skills consulted, dimensions in scope with zero findings, dimensions out-of-plugin-scope.

One report file per audit run. Do not append to a previous report.

## Bilingual note

Both the English document (`AUDIT_OUTPUT_SPEC.md`) and the Spanish document (`AUDIT_OUTPUT_SPEC.es.md`) are authoritative and kept in sync. Section numbering is identical, so a router entry pointing to "Section 3.3" is valid in either file. The JSON schema and the file naming are language-agnostic.
