# ios-audit-agents

Claude Code plugin: **seven auditors**, **`/run-audits`**, and **`/performance-audit`**, backed by a versioned **quality model**, **AI risk catalog**, and **audit output spec** (Markdown + JSON under `.claude-marketplace-audits/` in the audited repo).

## Agents

| Agent | Dimensions |
|-------|------------|
| `architecture-auditor` | 3.2, 3.3 |
| `code-health-auditor` | 3.16, partial 3.4 |
| `api-freshness-auditor` | 3.15 |
| `ux-accessibility-auditor` | 3.12, 3.13 |
| `performance-auditor` | 3.14 |
| `ci-cd-auditor` | 3.9 (loads `skills/ci-cd-checklist/SKILL.md`) |
| `security-privacy-auditor` | 3.6 |

## Commands

- **`/run-audits`** — Launches agents in parallel (`full` = all seven). See `commands/run-audits.md`.
- **`/performance-audit`** — Scoped SwiftUI performance pass; complements `performance-auditor`. See `commands/performance-audit.md`.

## Skills

| Skill | Role |
|-------|------|
| `quality-model` | Dimensions, severities (P0–P3), scope |
| `ai-risk-catalog` | Stable `AI-3.X-NNN` risk IDs |
| `audit-output-format` | JSON schema v1.0 + Markdown report contract |
| `ci-cd-checklist` | Operational checklist applied by **`ci-cd-auditor`** |
| `audit-run-protocol` | Rules every run shares: plugin paths, tracked-file enumeration, the audited project's rules, accepted exceptions, output validation. Preloaded by every agent |

Every agent preloads its skills through the `skills` field of its frontmatter, so it does not depend on finding them on disk.

## Scripts

- **`scripts/validate-audit.py`** — validates a Markdown + JSON pair against `AUDIT_OUTPUT_SPEC.md` (file name, required fields, metrics consistent with findings). Agents run it before finishing; `/run-audits` runs it again on every new pair.

## Accepted exceptions

A team can record findings it has decided to accept in `<audited-repo>/.claude-marketplace-audits/ACCEPTED.md`. Agents read the file, skip matching findings while their revisit condition does not hold, and list them in the report's Methodology notes. Format: `skills/audit-run-protocol/SKILL.md`, section 5.

## Documentation

| File | Content |
|------|---------|
| `docs/QUALITY_FRAMEWORK.md` | Quality model (English) |
| `docs/QUALITY_FRAMEWORK.es.md` | Same (Spanish) |
| `docs/AUDIT_OUTPUT_SPEC.md` | Output contract (English) |
| `docs/AUDIT_OUTPUT_SPEC.es.md` | Same (Spanish) |
| `docs/AI_RISK_CATALOG.md` | AI-typical risks (English) |
| `docs/AI_RISK_CATALOG.es.md` | Same (Spanish) |
| `docs/MERGE_AUDITS.md` | Optional: combine multiple audit JSON files |

## Install

From the marketplace root (see repository `README.md`):

```bash
claude plugin install ios-audit-agents@<marketplace-ref>
```

---

## Nota (ES)

Los documentos normativos del modelo y del contrato de salida están en **inglés y español** (`*.md` / `*.es.md`). Las skills de agente están en **inglés**; el checklist de CI/CD es el mismo cuerpo operativo que ejecuta **`ci-cd-auditor`**. Para unir varias salidas JSON en un solo resumen, véase **`docs/MERGE_AUDITS.md`**.
