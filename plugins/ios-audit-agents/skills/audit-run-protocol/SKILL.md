---
name: audit-run-protocol
description: How every ios-audit-agents auditor prepares and closes a run — locating the plugin's canonical documents, identifying the audited tree and commit, enumerating tracked sources, applying the audited project's own rules and accepted exceptions, naming the output pair and the working directory, and validating the Markdown + JSON pair before finishing. Preloaded by every auditor agent; also followed by /run-audits.
---

# Audit run protocol

Every auditor agent follows these steps around its own checks. The checks are only as good as the file list they run over, the project context they read, and the output they leave behind; each section below exists because a real run got one of those wrong.

Section 7.1 applies from your first command: it fixes the name of your output pair and the directory for your intermediate files before you create any file.

## 1. Plugin documents

The plugin is installed at `${CLAUDE_PLUGIN_ROOT}`. Its canonical documents are:

- `${CLAUDE_PLUGIN_ROOT}/docs/QUALITY_FRAMEWORK.md` — dimensions and severities.
- `${CLAUDE_PLUGIN_ROOT}/docs/AI_RISK_CATALOG.md` — AI risk IDs.
- `${CLAUDE_PLUGIN_ROOT}/docs/AUDIT_OUTPUT_SPEC.md` — output contract.
- `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` — the `version` to write as `plugin_version`.

A path such as `docs/QUALITY_FRAMEWORK.md` without that prefix resolves against the audited repository, where these files do not exist. Always use the prefixed path.

## 2. The audited tree

Run from the audited repository:

```bash
git rev-parse --show-toplevel     # repository root; every evidence path is relative to it
git rev-parse --short HEAD        # project.git_sha
git status --porcelain -- . ':(exclude).claude-marketplace-audits'
```

- **Not a git repository** — `project.git_sha` is `"uncommitted"`; enumerate with the fallback in section 3.
- **Uncommitted changes** — the audit then describes code that the SHA does not. Keep `project.git_sha` as the SHA, write `- Project commit: <sha> plus uncommitted changes in <N> files` in the Markdown header, and repeat it in Methodology notes. Never stash, commit, reset or check out anything.

## 3. Source enumeration

In a git repository, the file list is the set of tracked files:

```bash
git ls-files '*.swift'
git ls-files -z '*.swift' | xargs -0 wc -l | sort -rn     # line counts
git ls-files '*Info.plist' '*.strings' '*.entitlements' '*.xcprivacy' '*.xcconfig' '*.pbxproj' '*Package.resolved'
```

Do not enumerate or count lines with `find`, `ls -R` or a `**/*.swift` Glob in a git repository. They also return untracked trees that are not the project: build products (`build/`, `DerivedData/`), SwiftPM checkouts (`SourcePackages/`, `.build/`) and nested git worktrees (`.claude/worktrees/`, `.worktrees/`). In one measured repository, `git ls-files` listed 349 Swift files and `find` returned 4,786: 2,569 from two nested worktrees and 1,865 from third-party package checkouts.

The same applies to search results: discard any Grep hit whose path is not in the `git ls-files` output.

Apply the agent's own exclusions (tests, generated code, vendored code) to that list afterwards.

**Fallback outside git:** Glob `**/*.swift` and exclude `Pods/`, `Carthage/`, `.build/`, `build/`, `DerivedData/`, `SourcePackages/`, `.claude/worktrees/`, `.worktrees/` and `*.generated.swift`.

## 4. Project rules

Read, when present: `CLAUDE.md` and `AGENTS.md` at the repository root, and every file under `.claude/rules/`. They record decisions the team made on purpose, often after measuring something.

- When code follows a documented project rule and one of your checks would flag it, the rule wins: do not emit the finding. List the check and the rule's path under Methodology notes, in a subsection named "Checks adjusted by project rules".
- When code contradicts its own project's rule, that is a finding. Cite the rule in `references` as a free string, for example `project:.claude/rules/swift-concurrency.md`.
- A project rule never raises a finding above the severity the quality model assigns.

## 5. Accepted exceptions

The audited repository may contain `.claude-marketplace-audits/ACCEPTED.md`. The team writes it; an agent never creates or edits it. Each entry is a `###` section with these fields:

```markdown
### <short title>

- Match: <checklist item such as C6, a finding id slug, or a description of the finding>
- Dimension: <3.X>
- Reason: <why the team accepts it>
- Accepted on: <YYYY-MM-DD>
- Revisit when: <the condition under which the finding should be reported again>
```

- A candidate finding that matches an entry is not emitted while the entry's "Revisit when" condition does not hold. List it under Methodology notes, in a subsection named "Accepted exceptions (not re-reported)", with the entry's title.
- When the condition holds, or the evidence is materially worse than the entry describes, emit the finding normally and name the entry in `remediation`.
- An accepted exception is not a finding: it appears in neither `findings` nor `metrics`.

## 6. What is not a finding

- **A check that passed.** "No force unwraps found" belongs in Methodology notes. It never goes in `findings` and never carries a severity.
- **Code documented as intentional** — by a project rule (section 4), an accepted exception (section 5), or a comment next to the code that states the reason (for example an `@unchecked Sendable` with its justification).

## 7. Writing and validating the output

### 7.1 Output name and working directory

Two values identify your run. The **stem** names your Markdown + JSON pair. The **working directory** holds every intermediate file: file lists, scripts that assemble the report, drafts.

- **Launched by `/run-audits`** — your prompt gives both values. Use them exactly as given.
- **Launched on your own**, with neither value in your prompt — create both with your first command, replacing `<agent>` with your agent name and `<base>` with your scratchpad directory when your environment names one, else `${TMPDIR:-/tmp}`:

  ```bash
  stem="$(date -u +%Y%m%dT%H%M%SZ)__$(openssl rand -hex 4)"
  work="$(mktemp -d "<base>/<agent>.XXXXXX")"
  echo "stem=$stem work=$work"
  ```

Then, in both cases:

- Each Bash call starts a new shell, so a shell variable does not survive to the next call. Write the stem and the working directory as literal text in every later command. Never save either value to a file to read it back.
- Keep every intermediate file under the working directory. Write nothing from this run directly in the scratchpad directory or in `/tmp`.
- The stem's timestamp is also the JSON `timestamp`, and `metrics.duration_seconds` counts from it to the moment you write the pair. No start time needs to be stored anywhere else.

Every agent a session launches shares that session's scratchpad directory. On 2026-09-25, seven auditors ran in parallel and kept their stems in files with generic names there (`stem.txt`, `start.txt`, `gen.py`). One agent read a `stem.txt` that another had just overwritten, and wrote its JSON over the other agent's pair.

### 7.2 Writing the pair

Write both files with Bash as `<repo>/.claude-marketplace-audits/<stem>.md` and `<stem>.json`.

- Create each file in place and exclusively, so that the write fails instead of replacing an existing file: `open(path, "x")` in Python, or a `>` redirection after `set -o noclobber` in shell. To place a draft from your working directory, use `cat <draft> > <path>` under `noclobber`. `cp` and `mv` ignore `noclobber`, so never use them to place the files.
- If the creation fails because the file exists, the stem belongs to another run. Stop and report the stem to the caller. Never write, rename, delete or regenerate another run's pair, not even to restore it.
- Once you have created your pair, rewriting it to fix validation errors is an ordinary overwrite of your own files.

### 7.3 Validating the pair

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-audit.py" --agent <agent> "<repo>/.claude-marketplace-audits/<stem>.json"
```

The script checks the file name, the Markdown sibling, every required field of `AUDIT_OUTPUT_SPEC.md` Section 3, and that `metrics` agrees with `findings`. With `--agent`, it also checks that `scope.agents_used` names that agent and no other. Fix every error it reports and rewrite both files until it exits 0. Warnings may remain; list them in Methodology notes. End your answer to the caller with the stem and the validator's last line.
