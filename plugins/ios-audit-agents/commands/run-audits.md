# run-audits

Run the **bundled** ios-audit-agents auditors in parallel for a codebase audit. Each agent emits a **paired Markdown + JSON** record under the audited repository’s **`.claude-marketplace-audits/`** directory, per **`docs/AUDIT_OUTPUT_SPEC.md`**.

**Quality model (dimensions, severities P0–P3, AI risks):** `docs/QUALITY_FRAMEWORK.md` — use **Section 2** for severity, **Section 3** for dimension definitions, **Section 7.2** for which agent/skill operationalizes each dimension.

**Skills:** `skills/quality-model`, `skills/ai-risk-catalog`, `skills/audit-output-format` (consultative; each agent loads these per its prompt). Dimension **3.9** is executed by **`ci-cd-auditor`**, which in turn loads **`skills/ci-cd-checklist/SKILL.md`** — there is no separate “headless” CI run outside that agent.

## Bundled agents today

| Agent | Dimensions (primary) |
|---|---|
| `code-health-auditor` | 3.16, partial 3.4 |
| `architecture-auditor` | 3.2, 3.3 |
| `api-freshness-auditor` | 3.15 |
| `ux-accessibility-auditor` | 3.12, 3.13 |
| `performance-auditor` | 3.14 |
| `ci-cd-auditor` | 3.9 (applies `ci-cd-checklist` skill) |

For a **narrow, view-scoped** performance pass (arguments like a single view name), **`/performance-audit`** is still useful alongside or instead of the full `performance-auditor` run.

## Input

Scope: `$ARGUMENTS` (optional — `full`, `health`, `architecture`, `api`, `ux`, `performance`, `cicd`, or empty for `full`)

## Process

### If scope is `full` or empty — run six agents in parallel

Launch these agents **simultaneously** using the Agent tool:

1. **code-health-auditor**
2. **architecture-auditor**
3. **api-freshness-auditor**
4. **ux-accessibility-auditor**
5. **performance-auditor**
6. **ci-cd-auditor**

### If scope is specific — run only that agent

| Argument | Who runs |
|----------|-----------|
| `health` | `code-health-auditor` |
| `architecture` | `architecture-auditor` |
| `api` | `api-freshness-auditor` |
| `ux` | `ux-accessibility-auditor` |
| `performance` | `performance-auditor` |
| `cicd` | `ci-cd-auditor` |

### After agents complete

1. **Discover outputs** — List the newest files in `<repo>/.claude-marketplace-audits/` matching `*__*.json` (and their `.md` siblings). Each agent run should add **one** timestamped pair.
2. **Optional unified summary** — If the user wants a single Markdown digest, read the JSON files and produce one executive summary (counts by severity, top `ai_risk_id` values, dimensions covered). For **machine-side merge** recipes (`jq`, concatenating `findings`), see **`docs/MERGE_AUDITS.md`**. Do **not** delete per-agent JSON; the JSON is the canonical telemetry.
3. **Escalation** — If any **P0–P1** findings exist, suggest filing issues or blocking the release until addressed.

## Related

- **Ad-hoc / scoped performance review:** `/performance-audit` with `$ARGUMENTS` (complements dimension **3.14**; does not replace Instruments when you need measured proof).
