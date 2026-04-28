# ios-audit-agents

Claude Code plugin: **six auditors**, **`/run-audits`**, and **`/performance-audit`**, backed by a versioned **quality model**, **AI risk catalog**, and **audit output spec** (Markdown + JSON under `.claude-marketplace-audits/` in the audited repo).

## Agents

| Agent | Dimensions |
|-------|------------|
| `architecture-auditor` | 3.2, 3.3 |
| `code-health-auditor` | 3.16, partial 3.4 |
| `api-freshness-auditor` | 3.15 |
| `ux-accessibility-auditor` | 3.12, 3.13 |
| `performance-auditor` | 3.14 |
| `ci-cd-auditor` | 3.9 (loads `skills/ci-cd-checklist/SKILL.md`) |

## Commands

- **`/run-audits`** — Launches agents in parallel (`full` = all six). See `commands/run-audits.md`.
- **`/performance-audit`** — Scoped SwiftUI performance pass; complements `performance-auditor`. See `commands/performance-audit.md`.

## Skills

| Skill | Role |
|-------|------|
| `quality-model` | Dimensions, severities (P0–P3), scope |
| `ai-risk-catalog` | Stable `AI-3.X-NNN` risk IDs |
| `audit-output-format` | JSON schema v1.0 + Markdown report contract |
| `ci-cd-checklist` | Operational checklist applied by **`ci-cd-auditor`** |

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
