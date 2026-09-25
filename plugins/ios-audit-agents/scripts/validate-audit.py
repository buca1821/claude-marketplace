#!/usr/bin/env python3
"""Validate ios-audit-agents output pairs against AUDIT_OUTPUT_SPEC.md v1.0.

Usage: validate-audit.py <stem>.json [<stem>.json ...]

Prints one ERROR/WARNING line per problem and a final OK/FAILED line per file.
Exits 1 if any file has errors. Standard library only.
"""

import json
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CATALOG = PLUGIN_ROOT / "docs" / "AI_RISK_CATALOG.md"

STEM_RE = re.compile(r"^(\d{8}T\d{6}Z)__([a-z0-9]{8})$")
TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
RISK_ID_RE = re.compile(r"^AI-(3\.\d+)-\d{3}$")
SEVERITIES = ("P0", "P1", "P2", "P3")
AUDITABLE = {f"3.{n}" for n in range(2, 17)} - {"3.10"}
OUT_OF_SCOPE = ["3.1", "3.10"]
OUT_OF_SCOPE_RISKS = {"AI-3.1-001", "AI-3.10-001"}
ID_PREFIXES = {
    "api-freshness-auditor": "api-fresh-",
    "architecture-auditor": "arch-",
    "ci-cd-auditor": "cicd-",
    "code-health-auditor": "code-health-",
    "performance-auditor": "perf-",
    "security-privacy-auditor": "sec-",
    "ux-accessibility-auditor": "ux-",
}
MARKDOWN_HEADINGS = (
    "# Audit report",
    "## Executive summary",
    "## Findings by dimension",
    "## Suggested remediation tasks",
    "## Methodology notes",
)
PASSED_CHECK_TITLE_RE = re.compile(r"^(no|zero)\b.*\b(found|detected)\b", re.IGNORECASE)


def load_catalog():
    """Map each catalog risk ID to its status (lowercase), or None if unreadable."""
    try:
        text = CATALOG.read_text(encoding="utf-8")
    except OSError:
        return None
    catalog = {}
    current = None
    for line in text.splitlines():
        heading = re.match(r"^###\s+(AI-3\.\d+-\d{3})\b", line)
        if heading:
            current = heading.group(1)
            catalog[current] = ""
            continue
        status = re.match(r"^- \*\*Status:\*\*\s*(.+)$", line)
        if current and status and not catalog[current]:
            catalog[current] = status.group(1).strip().rstrip(".").lower()
    return catalog


def is_str(value):
    return isinstance(value, str) and value.strip() != ""


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def is_dimension(value):
    return isinstance(value, str) and value in AUDITABLE


def is_line(value):
    return is_int(value) or (isinstance(value, str) and re.fullmatch(r"\d+(-\d+)?", value) is not None)


def validate(json_path, catalog):
    errors, warnings = [], []
    err, warn = errors.append, warnings.append

    stem_match = STEM_RE.match(json_path.stem)
    if not stem_match:
        err(f"file name '{json_path.name}' is not <YYYYMMDDTHHMMSSZ>__<[a-z0-9]{{8}}>.json (spec 1.2)")
    md_path = json_path.with_suffix(".md")
    if not md_path.is_file():
        err(f"Markdown sibling '{md_path.name}' is missing (spec 1.2)")

    try:
        record = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        err(f"cannot read JSON: {exc}")
        return errors, warnings
    if not isinstance(record, dict):
        err("top level is not a JSON object")
        return errors, warnings

    # Envelope (spec 3.1, 3.2)
    schema_version = record.get("schema_version")
    if not is_str(schema_version):
        err("schema_version is missing")
    elif not schema_version.startswith("1."):
        err(f"schema_version '{schema_version}' is not a 1.x version this validator understands")

    audit_id = record.get("audit_id")
    if not (is_str(audit_id) and re.fullmatch(r"[a-z0-9]{8}", audit_id)):
        err("audit_id is missing or not [a-z0-9]{8}")
    elif stem_match and stem_match.group(2) != audit_id:
        err(f"audit_id '{audit_id}' does not match the file name id '{stem_match.group(2)}'")

    timestamp = record.get("timestamp")
    if not (is_str(timestamp) and TIMESTAMP_RE.match(timestamp)):
        err("timestamp is missing or not ISO 8601 UTC with a Z suffix")
    elif stem_match:
        compact = re.sub(r"[-:]", "", timestamp.split(".")[0].rstrip("Z")) + "Z"
        if compact != stem_match.group(1):
            warn(f"timestamp '{timestamp}' differs from the file name timestamp '{stem_match.group(1)}'")

    model_version = record.get("model_version")
    if not is_str(model_version):
        err("model_version is missing")
    plugin_version = record.get("plugin_version")
    if not is_str(plugin_version):
        err("plugin_version is missing")
    elif plugin_version == "unknown":
        warn("plugin_version is 'unknown'; read it from ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json")

    project = record.get("project")
    if not isinstance(project, dict):
        err("project is missing")
        project = {}
    if not is_str(project.get("name")):
        err("project.name is missing")
    if not is_str(project.get("git_sha")):
        err("project.git_sha is missing (use \"uncommitted\" outside git)")

    scope = record.get("scope")
    if not isinstance(scope, dict):
        err("scope is missing")
        scope = {}
    dimensions_audited = scope.get("dimensions_audited")
    if not (isinstance(dimensions_audited, list) and dimensions_audited):
        err("scope.dimensions_audited is missing or empty")
        dimensions_audited = []
    for dimension in dimensions_audited:
        if not is_dimension(dimension):
            err(f"scope.dimensions_audited contains '{dimension}', which is not an auditable dimension")
    agents_used = scope.get("agents_used")
    if not (isinstance(agents_used, list) and agents_used and all(is_str(a) for a in agents_used)):
        err("scope.agents_used is missing or empty")
        agents_used = []

    findings = record.get("findings")
    if not isinstance(findings, list):
        err("findings is missing (use [] when there are none)")
        findings = []

    # Findings (spec 3.3)
    expected_prefix = ID_PREFIXES.get(agents_used[0]) if len(agents_used) == 1 else None
    seen_ids = set()
    for index, finding in enumerate(findings):
        where = f"findings[{index}]"
        if not isinstance(finding, dict):
            err(f"{where} is not an object")
            continue
        finding_id = finding.get("id")
        if not is_str(finding_id):
            err(f"{where}.id is missing" + (" (found 'finding_id')" if "finding_id" in finding else ""))
        else:
            where = f"finding '{finding_id}'"
            if finding_id in seen_ids:
                err(f"{where} is duplicated")
            seen_ids.add(finding_id)
            if expected_prefix and not finding_id.startswith(expected_prefix):
                warn(f"{where} does not use the '{expected_prefix}' prefix of {agents_used[0]}")

        dimension = finding.get("dimension")
        if not is_dimension(dimension):
            err(f"{where}.dimension '{dimension}' is not an auditable dimension")
        elif dimension not in dimensions_audited:
            err(f"{where}.dimension '{dimension}' is not listed in scope.dimensions_audited")

        severity = finding.get("severity")
        if severity not in SEVERITIES:
            err(f"{where}.severity '{severity}' is not one of P0-P3")

        title = finding.get("title")
        if not is_str(title) or "\n" in title:
            err(f"{where}.title is missing or spans several lines")
        elif PASSED_CHECK_TITLE_RE.match(title):
            warn(f"{where}.title reads like a passing check ('{title}'); a check that passed is not a finding")

        ai_typical = finding.get("ai_typical")
        risk_id = finding.get("ai_risk_id")
        if not isinstance(ai_typical, bool):
            err(f"{where}.ai_typical is missing or not a boolean")
        elif ai_typical and risk_id is None:
            warn(f"{where} is ai_typical without ai_risk_id; allowed only when no catalog entry matches, "
                 "and the gap must be noted in the report")
        elif not ai_typical and risk_id is not None:
            err(f"{where} has ai_risk_id but ai_typical is false")
        if risk_id is not None:
            risk_match = RISK_ID_RE.match(risk_id) if isinstance(risk_id, str) else None
            if not risk_match:
                err(f"{where}.ai_risk_id '{risk_id}' is not AI-3.X-NNN")
            elif risk_id in OUT_OF_SCOPE_RISKS:
                err(f"{where}.ai_risk_id '{risk_id}' belongs to an out-of-plugin-scope dimension")
            else:
                if catalog is not None and risk_id not in catalog:
                    err(f"{where}.ai_risk_id '{risk_id}' is not in AI_RISK_CATALOG.md")
                elif catalog is not None and catalog[risk_id].startswith("retired"):
                    err(f"{where}.ai_risk_id '{risk_id}' is retired")
                if is_dimension(dimension) and risk_match.group(1) != dimension:
                    warn(f"{where}.ai_risk_id '{risk_id}' belongs to dimension {risk_match.group(1)}, "
                         f"not {dimension}")

        if not is_str(finding.get("remediation")):
            err(f"{where}.remediation is missing")
        references = finding.get("references")
        if not (isinstance(references, list) and references and all(is_str(r) for r in references)):
            err(f"{where}.references must list at least one identifier")

        evidence = finding.get("evidence")
        if evidence is not None:
            files = evidence.get("files", []) if isinstance(evidence, dict) else None
            if not isinstance(files, list):
                err(f"{where}.evidence.files is not a list")
                files = []
            for entry in files:
                path = entry.get("path") if isinstance(entry, dict) else None
                if not is_str(path):
                    err(f"{where}.evidence.files has an entry without a path")
                elif path.startswith(("/", "~")):
                    err(f"{where}.evidence path '{path}' is absolute; use a path relative to the repository root")
                lines = entry.get("lines", []) if isinstance(entry, dict) else []
                if not (isinstance(lines, list) and all(is_line(n) for n in lines)):
                    err(f"{where}.evidence lines for '{path}' must be a list of line numbers or 'N-M' ranges")

    # Metrics (spec 3.2): must agree with findings
    metrics = record.get("metrics")
    if not isinstance(metrics, dict):
        err("metrics is missing")
        metrics = {}
    valid_findings = [f for f in findings if isinstance(f, dict)]
    total = len(valid_findings)
    if metrics.get("total_findings") != total:
        err(f"metrics.total_findings is {metrics.get('total_findings')!r}, findings has {total}")
    by_severity = metrics.get("by_severity")
    if not (isinstance(by_severity, dict) and set(by_severity) == set(SEVERITIES)):
        err("metrics.by_severity must have exactly the keys P0, P1, P2, P3")
    else:
        for severity in SEVERITIES:
            actual = sum(1 for f in valid_findings if f.get("severity") == severity)
            if by_severity[severity] != actual:
                err(f"metrics.by_severity.{severity} is {by_severity[severity]!r}, findings has {actual}")
    by_dimension = metrics.get("by_dimension")
    if not isinstance(by_dimension, dict):
        err("metrics.by_dimension is missing")
    else:
        dimensions = {f.get("dimension") for f in valid_findings if isinstance(f.get("dimension"), str)}
        for dimension in sorted(dimensions | set(by_dimension)):
            actual = sum(1 for f in valid_findings if f.get("dimension") == dimension)
            if by_dimension.get(dimension, 0) != actual:
                err(f"metrics.by_dimension['{dimension}'] is {by_dimension.get(dimension, 0)!r}, findings has {actual}")
    ai_count = sum(1 for f in valid_findings if f.get("ai_typical") is True)
    if metrics.get("ai_typical_count") != ai_count:
        err(f"metrics.ai_typical_count is {metrics.get('ai_typical_count')!r}, findings has {ai_count}")
    ratio = metrics.get("ai_typical_ratio")
    expected_ratio = ai_count / total if total else 0.0
    if not (isinstance(ratio, (int, float)) and not isinstance(ratio, bool) and abs(ratio - expected_ratio) < 0.01):
        err(f"metrics.ai_typical_ratio is {ratio!r}, expected {expected_ratio:.2f} (0.0, not null, with no findings)")
    duration = metrics.get("duration_seconds")
    if not (is_int(duration) and duration >= 0):
        err("metrics.duration_seconds is missing or not a non-negative integer")

    # Notes (spec 3.2)
    notes = record.get("notes")
    if not isinstance(notes, dict):
        err("notes is missing")
        notes = {}
    zero = notes.get("dimensions_in_scope_with_zero_findings")
    if not isinstance(zero, list):
        err("notes.dimensions_in_scope_with_zero_findings is missing (use [] when empty)")
    else:
        for dimension in zero:
            if dimension not in dimensions_audited:
                err(f"notes lists '{dimension}' with zero findings, but it is not in scope.dimensions_audited")
            elif any(f.get("dimension") == dimension for f in valid_findings):
                err(f"notes lists '{dimension}' with zero findings, but findings has entries for it")
    if model_version == "0.1":
        if notes.get("dimensions_out_of_plugin_scope") != OUT_OF_SCOPE:
            err(f"notes.dimensions_out_of_plugin_scope must be {OUT_OF_SCOPE} for quality model 0.1")
    elif is_str(model_version):
        warn(f"quality model '{model_version}' is unknown to this validator; "
             "notes.dimensions_out_of_plugin_scope was not checked")

    # Markdown projection (spec 2.1)
    if md_path.is_file():
        markdown = md_path.read_text(encoding="utf-8")
        for heading in MARKDOWN_HEADINGS:
            if not re.search(rf"^{re.escape(heading)}\b", markdown, re.MULTILINE):
                err(f"Markdown lacks the '{heading}' heading (spec 2.1)")
        if is_str(audit_id) and audit_id not in markdown:
            err("Markdown does not mention the audit_id")
        for finding_id in sorted(seen_ids):
            if not re.search(rf"(?<![\w-]){re.escape(finding_id)}(?![\w-])", markdown):
                err(f"Markdown does not mention finding '{finding_id}'")

    return errors, warnings


def main(argv):
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    catalog = load_catalog()
    if catalog is None:
        print(f"WARNING: cannot read {CATALOG}; ai_risk_id values are not checked against the catalog")
    failed = False
    for argument in argv:
        json_path = Path(argument)
        errors, warnings = validate(json_path, catalog)
        for message in errors:
            print(f"ERROR: {json_path.name}: {message}")
        for message in warnings:
            print(f"WARNING: {json_path.name}: {message}")
        verdict = "FAILED" if errors else "OK"
        print(f"{verdict}: {json_path.name} ({len(errors)} errors, {len(warnings)} warnings)")
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
