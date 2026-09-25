# run-audits

Run the **bundled** ios-audit-agents auditors in parallel for a codebase audit. Each agent emits a **paired Markdown + JSON** record under the audited repository’s **`.claude-marketplace-audits/`** directory, per **`${CLAUDE_PLUGIN_ROOT}/docs/AUDIT_OUTPUT_SPEC.md`**.

**Quality model (dimensions, severities P0–P3, AI risks):** `${CLAUDE_PLUGIN_ROOT}/docs/QUALITY_FRAMEWORK.md` — use **Section 2** for severity, **Section 3** for dimension definitions, **Section 7.2** for which agent/skill operationalizes each dimension.

**Skills:** every agent preloads `audit-run-protocol`, `quality-model`, `ai-risk-catalog` and `audit-output-format` through the `skills` field of its frontmatter. `audit-run-protocol` holds the rules all runs share: tracked-file enumeration, the audited project's own rules, accepted exceptions (`.claude-marketplace-audits/ACCEPTED.md`) and output validation. Dimension **3.9** is executed by **`ci-cd-auditor`**, which also preloads **`ci-cd-checklist`** — there is no separate “headless” CI run outside that agent.

The agents read files and run `git` and `grep`. They do not build the app, boot simulators or use CI minutes.

## Bundled agents today

| Agent | Dimensions (primary) |
|---|---|
| `code-health-auditor` | 3.16, partial 3.4 |
| `architecture-auditor` | 3.2, 3.3 |
| `api-freshness-auditor` | 3.15 |
| `ux-accessibility-auditor` | 3.12, 3.13 |
| `performance-auditor` | 3.14 |
| `ci-cd-auditor` | 3.9 (applies `ci-cd-checklist` skill) |
| `security-privacy-auditor` | 3.6 |

For a **narrow, view-scoped** performance pass (arguments like a single view name), **`/performance-audit`** is still useful alongside or instead of the full `performance-auditor` run.

## Input

Scope: `$ARGUMENTS` (optional — `full`, `health`, `architecture`, `api`, `ux`, `performance`, `cicd`, `security`, or empty for `full`)

## Process

### 1. Check the audited tree

From the repository to audit, before launching anything:

```bash
git rev-parse --show-toplevel
git rev-parse --short HEAD
git status --porcelain -- . ':(exclude).claude-marketplace-audits'
ls -1 .claude-marketplace-audits/ 2>/dev/null
```

Keep the directory listing: step 3 uses it to tell this run's files from older ones.

If `git status` lists changes, stop and tell the user that the agents would audit uncommitted code while every report names the commit. Offer two options and wait for the answer:

- **Audit a clean tree** — the user commits or stashes the changes, or runs `/run-audits` from a git worktree checked out at the commit to audit. The reports are then written in that worktree's `.claude-marketplace-audits/`.
- **Audit the working tree as it is** — every report then states `plus uncommitted changes in <N> files` in its header (`audit-run-protocol` §2).

Never stash, commit, reset or check out on the user's behalf.

### 2. Launch the agents

**If scope is `full` or empty**, launch these seven agents **simultaneously** with the Agent tool, using their full names:

1. `ios-audit-agents:code-health-auditor`
2. `ios-audit-agents:architecture-auditor`
3. `ios-audit-agents:api-freshness-auditor`
4. `ios-audit-agents:ux-accessibility-auditor`
5. `ios-audit-agents:performance-auditor`
6. `ios-audit-agents:ci-cd-auditor`
7. `ios-audit-agents:security-privacy-auditor`

**If scope is specific**, launch only that agent:

| Argument | Who runs |
|----------|-----------|
| `health` | `ios-audit-agents:code-health-auditor` |
| `architecture` | `ios-audit-agents:architecture-auditor` |
| `api` | `ios-audit-agents:api-freshness-auditor` |
| `ux` | `ios-audit-agents:ux-accessibility-auditor` |
| `performance` | `ios-audit-agents:performance-auditor` |
| `cicd` | `ios-audit-agents:ci-cd-auditor` |
| `security` | `ios-audit-agents:security-privacy-auditor` |

Before launching, give each agent that will run its own stem and working directory (`audit-run-protocol` §7.1). Create them in one Bash call, listing only the agents that will run. Replace `<base>` with your scratchpad directory when your environment names one, else `${TMPDIR:-/tmp}`:

```bash
run="$(mktemp -d "<base>/ios-audit.XXXXXX")"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
for agent in code-health-auditor architecture-auditor api-freshness-auditor ux-accessibility-auditor performance-auditor ci-cd-auditor security-privacy-auditor; do
  mkdir "$run/$agent"
  echo "$agent ${ts}__$(openssl rand -hex 4) $run/$agent"
done
```

Keep the printed table: step 3 checks every pair against it. The agents cannot pick these values themselves, because every agent this session launches shares its scratchpad directory, and names picked independently collide there.

Give each agent its own values in its prompt: `Audit the repository at <root> (commit <sha>) for your dimensions. Follow your mandatory prelude. Your output stem is <stem>. Your working directory is <directory>.`

### 3. Validate the outputs

Each agent validates its own pair before it finishes (`audit-run-protocol` §7.3). Validate again here, because an agent can stop before its last step. Run the validator once per agent, with the agent name and stem from the table of step 2:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-audit.py" --agent <agent> <repo>/.claude-marketplace-audits/<stem>.json
```

- Each agent that ran must have written the pair of its own stem. `--agent` fails when `scope.agents_used` names another agent, which is what a pair overwritten by another agent looks like.
- A new file that is neither in the listing kept in step 1 nor one of the assigned stems means an agent wrote under a name it was not given. Report it to the user and leave it in place.
- If an agent's pair is missing or fails validation, send the validator output back to that agent and ask it to fix and rewrite the pair. If it fails a second time, report that agent as failed in the summary.
- Never edit an agent's JSON or Markdown yourself.

### 4. Compare with the previous run

For each agent, the previous run is the newest older JSON whose `scope.agents_used` names the same agent. Finding IDs are only stable within one run, so match findings by dimension, title and evidence paths. Classify this run's findings:

- **New** — nothing in the previous run describes the same defect.
- **Persisting** — a previous finding describes the same defect. Note a severity change if there is one.
- **No longer reported** — a previous finding with no counterpart now. Say whether it was fixed, accepted in `ACCEPTED.md`, or is unexplained; do not assume a fix you have not seen in the code.

### 5. Summarize

Report to the user, per agent: the stem of its pair, the validation result, counts by severity, and the comparison from step 4. List the accepted exceptions the agents applied (from each report's Methodology notes).

- **Optional unified digest** — If the user wants a single Markdown digest, read the JSON files and produce one executive summary (counts by severity, top `ai_risk_id` values, dimensions covered). For **machine-side merge** recipes (`jq`, concatenating `findings`), see **`${CLAUDE_PLUGIN_ROOT}/docs/MERGE_AUDITS.md`**. Do **not** delete per-agent JSON; the JSON is the canonical telemetry.
- **Escalation** — If any **P0–P1** findings exist, suggest filing issues or blocking the release until addressed.

## Related

- **Ad-hoc / scoped performance review:** `/performance-audit` with `$ARGUMENTS` (complements dimension **3.14**; does not replace Instruments when you need measured proof).
