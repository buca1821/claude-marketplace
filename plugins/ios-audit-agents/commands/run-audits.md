# run-audits

Run the **bundled** ios-audit-agents auditors in parallel for a codebase audit. Each agent emits a **paired Markdown + JSON** record under the audited repository’s **`.claude-marketplace-audits/`** directory, per **`${CLAUDE_PLUGIN_ROOT}/docs/AUDIT_OUTPUT_SPEC.md`**. The run ends with one readable report built from those pairs (step 6).

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

Before launching, give each agent that will run its own stem and working directory (`audit-run-protocol` §7.1). Create them in one Bash call. Replace `<base>` with your scratchpad directory when your environment names one, else `${TMPDIR:-/tmp}`. Replace `<agents>` with the names of the agents that will run, without the plugin prefix: all seven for `full`, one for a specific scope.

```bash
run="$(mktemp -d "<base>/ios-audit.XXXXXX")"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
for agent in <agents>; do
  mkdir "$run/$agent"
  echo "$agent ${ts}__$(openssl rand -hex 4) $run/$agent"
done
```

Keep the printed table: step 3 checks every pair against it. Assigning the values here is what gives step 3 that table, and with it an assigned stem without a pair, or a new pair under a stem nobody was given, shows up. On 2026-09-25, with no table, one agent wrote its JSON under the stem another agent had generated and then moved it to a new name of its own; counting one pair per agent could not tell. The table does not catch a pair that another agent overwrites and then regenerates, because the regenerated pair names its owner again; the exclusive first write of `audit-run-protocol` §7.2 is what prevents that case.

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

- **Machine-side merge** — For `jq` recipes that concatenate `findings` across runs or count the most frequent `ai_risk_id` values, see **`${CLAUDE_PLUGIN_ROOT}/docs/MERGE_AUDITS.md`**. The document for a person to read is the report of step 6; it replaces the hand-written digest this step used to offer. Do **not** delete per-agent JSON; the JSON is the canonical telemetry.
- **Escalation** — If any **P0–P1** findings exist, suggest filing issues or blocking the release until addressed.

### 6. Publish the readable report

Every run ends with one document a person can read without knowing the audit: what each finding is, how serious it is, and what to do about it. Write it after steps 1 to 5, never before: it reads the pairs that step 3 validated. It does not replace the chat summary of step 5, which keeps the validation results, the comparison with the previous run and the accepted exceptions. Write it in the language of the conversation, headings and column names included, from this run's pairs only (the stems of step 2). The JSON stays the canonical record; the report is a reading of it.

**Content rules**

- One row per finding of this run. Add nothing, drop nothing, merge nothing, and keep each finding's severity as the JSON gives it.
- Write each row from the finding's `title`, `remediation` and evidence, and from its section in the agent's Markdown. Read the cited file only when the finding does not say who is affected. Never state an effect the finding does not support.
- Plain words. No finding IDs, no `ai_risk_id`, no dimension numbers. A technical term the reader may not know gets a one-line definition under the section heading, the first time a section needs it (for example contrast, the main thread, a deprecated API).
- When the finding cites an issue or pull request that already tracks it, name it in "What to do". When the evidence says nothing was measured, the row says so.

**Structure**

1. Title `<project> audit <YYYY-MM-DD>: findings`, then the date.
2. A **Summary** section: one sentence with the commit, the date and the count per severity, then a table of the four severities with their meaning in plain words (`QUALITY_FRAMEWORK.md` Section 2), then one line naming that scale as the source. Two cases change that sentence:
   - When step 1 audited the working tree as it is, the sentence says so: "on commit `<sha>` plus uncommitted changes in `<N>` files". The JSON does not record this; take it from step 1.
   - When an agent that was launched produced no valid pair (step 3), the sentence names the areas that were not audited, and the counts cover only the agents that reported.
3. One section per agent that ran, numbered, titled with its area and its number of findings, for example `2. UX and accessibility (13)`, in this order: security and privacy, UX and accessibility, CI/CD, performance, API freshness, code health, architecture. An agent that produced no valid pair keeps its section, titled `(not audited)`, with one sentence saying so instead of a table. An agent with a valid pair and no findings keeps its section too, with one sentence saying nothing was found.
4. In each section, one table with a row per finding, most severe first, and these five columns:

| Column | Holds |
|---|---|
| Severity | P0–P3, in bold for P0 and P1 |
| What happens | the defect, in one or two sentences |
| What breaks / who is affected | the consequence for a user, the team or the release |
| Where | one file name, the most telling one; "and N more" when there are several |
| What to do | the fix in one or two sentences, with the issue or PR that tracks it |

**Where it goes**

- **When the session has the Claude Docs connector** (tools named `…Claude_Docs__batch`, `…Claude_Docs__update`), create a document with it. Use the connector's calls as its guide describes them: the outline first, with one pending block per section, then open it for the user, then fill one section per call. Two of its general rules give way to this command: the document is created here, at step 6, not with the first call of the turn; and the chat keeps step 5's summary, followed by one line with the document's link. Use no other document service.
- **Otherwise**, write it as Markdown to `<repo>/.claude-marketplace-audits/REPORT-<timestamp>.md`, with the timestamp of this run's stems, and give the user its path. That file is not an audit output: it has no JSON and does not follow the naming of `AUDIT_OUTPUT_SPEC.md` Section 1.2.

## Related

- **Ad-hoc / scoped performance review:** `/performance-audit` with `$ARGUMENTS` (complements dimension **3.14**; does not replace Instruments when you need measured proof).
