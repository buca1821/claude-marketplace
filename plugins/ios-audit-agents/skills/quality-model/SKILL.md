---
name: quality-model
description: The ios-audit-agents quality model v0.1 — engineering quality model for AI-assisted iOS apps, organized in 16 dimensions (3.1–3.16) with a P0–P3 severity scale. Use when an audit needs to decide which dimension a finding belongs to, what severity to assign, which AI-typical risks apply, or whether an area is in-scope vs out-of-plugin-scope. Always paired with the ai-risk-catalog skill (to assign AI risk IDs to ai_typical findings) and the audit-output-format skill (to emit reports).
---

# Quality model — v0.1

This skill is the consultative lens over the plugin's quality model. It tells an agent **which dimension** a candidate finding belongs to, **which severity** to use, and **how the model is operationalized today**. It does not duplicate the model — the canonical source is `../../docs/QUALITY_FRAMEWORK.md` (English) and `../../docs/QUALITY_FRAMEWORK.es.md` (Spanish).

## Operating rules

- Read the canonical document **once per audit run** and reuse the loaded context for every finding in that run.
- Every finding emitted by an audit MUST reference exactly one dimension from Section 3 (3.1–3.16).
- Two dimensions are explicitly **out-of-plugin-scope (manual)** in Section 7.2: `3.1 Product fit & boundaries` and `3.10 Developer experience`. If a candidate finding only belongs to one of these, the agent MUST drop it; it is not auditable by this plugin.
- Severity uses the **P0–P3** scale defined in Section 2. Do not use other levels (no `critical`, `high`, `medium`, `low`). Do not invent a `confidence` field — the model does not define one.
- An AI-typical risk MUST be flagged with `ai_typical: true` AND carry a stable risk ID from `AI_RISK_CATALOG.md` (resolved through the `ai-risk-catalog` skill).
- Every finding MUST cite at least one **backing reference** from Section 6 (Apple HIG, App Review Guidelines, OWASP MASVS, Paul Hudson, Sundell, Wals, van der Lee, ISO/IEC 25010:2023, WCAG 2.2). The reference points to the source, not to the dimension itself.

## Topic router

| You need to know… | Section in `QUALITY_FRAMEWORK.md` |
|---|---|
| What this specification is and is not, and the AI dimension | Section 1 (Foundations: 1.1, 1.2, 1.3) |
| The severity scale (P0–P3) with examples per level | Section 2 (Severity scale) |
| The 16 dimensions, their signals and checks | Section 3 (Quality dimensions) — one subsection per `3.X` |
| What the plugin must emit per audit and per finding | Section 4 (What this specification measures) |
| The human-readable finding template (ID, Dimension, Severity, Evidence, AI-typical, Remediation, References) | Section 5 (Recording findings) |
| The list of backing references findings must cite | Section 6 (References) |
| Which dimensions are in scope vs out-of-plugin-scope today | Section 7.2 (Coverage snapshot) |
| How accumulated audit evidence updates the model | Section 7.3 (Evidence flow) |

## Coverage snapshot (mirrors Section 7.2)

| 3.X | Dimension | Operationalized by |
|---|---|---|
| 3.1 | Product fit & boundaries | `out-of-plugin-scope (manual)` |
| 3.2 | Architecture & modularity | `agent: architecture-auditor` |
| 3.3 | Domain model integrity | `agent: architecture-auditor` (extension) |
| 3.4 | State, concurrency & data races | `planned: concurrency-auditor`, partially `agent: code-health-auditor` |
| 3.5 | Reliability & error handling | `planned: reliability-auditor` |
| 3.6 | Security & privacy | `planned: security-privacy-auditor` |
| 3.7 | Observability & telemetry | `planned: observability-auditor` |
| 3.8 | Testing strategy | `planned: testing-strategy-auditor` |
| 3.9 | CI/CD & release engineering | `agent: ci-cd-auditor` (`skill: ci-cd-checklist`) |
| 3.10 | Developer experience | `out-of-plugin-scope (manual)` |
| 3.11 | Localization & i18n | `planned: localization-auditor` |
| 3.12 | UX & UI quality | `agent: ux-accessibility-auditor` |
| 3.13 | Accessibility | `agent: ux-accessibility-auditor` |
| 3.14 | Performance & energy | `agent: performance-auditor` |
| 3.15 | API freshness & deprecations | `agent: api-freshness-auditor` |
| 3.16 | Code health & SOLID | `agent: code-health-auditor` |

When the coverage status changes, update Section 7.2 of the specification first, then this table.

## Severity quick reference (mirrors Section 2)

- **P0** — Ship-blocker. User harm, data loss, legal risk, store rejection, public outage.
- **P1** — Strongly recommended before release. Real damage to users, team or product if left unfixed.
- **P2** — Should fix soon. Quality, maintainability or risk debt that compounds.
- **P3** — Nice to have. Polish, consistency, future-proofing.

Severity is independent of effort.

## Emitting a finding

1. **Pick the dimension.** If none of `3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.11, 3.12, 3.13, 3.14, 3.15, 3.16` fits, do not emit. Never assign 3.1 or 3.10 — they are out-of-plugin-scope.
2. **Pick the severity** (P0–P3) per Section 2.
3. **Decide if it is AI-typical.** If yes, invoke the `ai-risk-catalog` skill, set `ai_typical: true` and attach the catalog ID (`AI-3.X-NNN`).
4. **Pick at least one backing reference** from Section 6 that supports the finding (e.g. Apple HIG section, OWASP MASVS control, Paul Hudson article, etc.).
5. **Hand off to the `audit-output-format` skill** to serialize the finding into the JSON envelope and the human-readable Markdown report.

## Versioning

The quality model has its own version (currently `v0.1`), independent of the plugin version. The version is declared in the banner of `QUALITY_FRAMEWORK.md` and again in Section 7.1. Always emit it as `model_version: "0.1"` in the JSON envelope (see the `audit-output-format` skill).

## Bilingual note

Both the English document (`QUALITY_FRAMEWORK.md`) and the Spanish document (`QUALITY_FRAMEWORK.es.md`) are authoritative and kept in sync. Section numbering is identical, so a router entry pointing to "Section 3.4" is valid in either file.
