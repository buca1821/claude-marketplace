# run-audits

Run the **bundled** ios-audit-agents auditors in parallel for a codebase audit. Each agent emits a **paired Markdown + JSON** record under the audited repository’s **`.claude-marketplace-audits/`** directory, per **`docs/AUDIT_OUTPUT_SPEC.md`**.

**Quality model (dimensions, severities P0–P3, AI risks):** `docs/QUALITY_FRAMEWORK.md` — use **Section 2** for severity, **Section 3** for dimension definitions, **Section 7.2** for which agent/skill operationalizes each dimension.

**Skills (consultative + CI):** `skills/quality-model`, `skills/ai-risk-catalog`, `skills/audit-output-format`, `skills/ci-cd-checklist` (invoke or read each `SKILL.md` before or during orchestration as needed).

## Bundled agents today

| Agent | Dimensions (primary) |
|---|---|
| `code-health-auditor` | 3.16, partial 3.4 |
| `architecture-auditor` | 3.2, 3.3 |
| `api-freshness-auditor` | 3.15 |
| `ux-accessibility-auditor` | 3.12, 3.13 |

There is **no** `performance-auditor` agent in this plugin bundle yet (dimension **3.14** remains `agent: performance-auditor` in the model). For ad-hoc performance heuristics, use **`/performance-audit`** with `$ARGUMENTS`.

## Input

Scope: `$ARGUMENTS` (optional — `full`, `health`, `architecture`, `api`, `ux`, `cicd`, or empty for `full`)

## Process

### If scope is `full` or empty — run four agents in parallel

Launch these agents **simultaneously** using the Agent tool:

1. **code-health-auditor**
2. **architecture-auditor**
3. **api-freshness-auditor**
4. **ux-accessibility-auditor**

For **`full` + CI/CD**, also execute the **`ci-cd-checklist` skill** (dimension **3.9**): treat the skill as the auditor — load `skills/ci-cd-checklist/SKILL.md`, run its checks, and emit the **same** paired `.md` + `.json` under `.claude-marketplace-audits/` (one additional timestamped pair).

### If scope is specific — run only that agent (or skill)

| Argument | Who runs |
|----------|-----------|
| `health` | `code-health-auditor` |
| `architecture` | `architecture-auditor` |
| `api` | `api-freshness-auditor` |
| `ux` | `ux-accessibility-auditor` |
| `cicd` | **`ci-cd-checklist` skill** only (dimension 3.9; paired audit output per `AUDIT_OUTPUT_SPEC.md`) |

### After agents complete

1. **Discover outputs** — List the newest files in `<repo>/.claude-marketplace-audits/` matching `*__*.json` (and their `.md` siblings). Each agent run should add **one** timestamped pair.
2. **Optional unified summary** — If the user wants a single Markdown digest, read the JSON files and produce one executive summary (counts by severity, top `ai_risk_id` values, dimensions covered). Do **not** delete per-agent JSON; the JSON is the canonical telemetry.
3. **Escalation** — If any **P0–P1** findings exist, suggest filing issues or blocking the release until addressed.

## Related

- **Performance heuristics (not a bundled agent):** `/performance-audit` with `$ARGUMENTS`.
