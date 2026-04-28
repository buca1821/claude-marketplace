# Merging multiple audit JSON files

After `/run-audits` **full**, you may have **six** (or more) JSON files in the audited repository:

```text
<repo>/.claude-marketplace-audits/<UTC>__<audit-id>.json
```

Each file is self-contained (`schema_version`, `findings`, `metrics`, …). There is **no** required merge step; this guide is for dashboards or one-off summaries.

## English

### 1. List recent runs

```bash
cd /path/to/audited-repo
ls -1t .claude-marketplace-audits/*.json | head
```

### 2. Per-run executive one-liner (`jq`)

```bash
jq '{audit_id, timestamp, agent: .scope.agents_used, dims: .scope.dimensions_audited, total: .metrics.total_findings, by_severity: .metrics.by_severity, ai_typical: .metrics.ai_typical_count}' \
  .claude-marketplace-audits/<pick-one>.json
```

### 3. Concatenate all `findings` from every JSON in the directory

Requires [jq](https://jqlang.github.io/jq/) 1.6+.

```bash
shopt -s nullglob
files=(.claude-marketplace-audits/*.json)
jq -s '[.[] | .findings[]?]' "${files[@]}" > /tmp/all-findings.json
jq '{count: length}' /tmp/all-findings.json
```

### 4. Top `ai_risk_id` across merged findings

```bash
jq '[group_by(.ai_risk_id)[] | {id: .[0].ai_risk_id, n: length}] | sort_by(-.n)' /tmp/all-findings.json
```

Filter out null IDs if needed:

```bash
jq '[.[] | select(.ai_risk_id != null)] | group_by(.ai_risk_id) | map({id: .[0].ai_risk_id, n: length}) | sort_by(-.n)' /tmp/all-findings.json
```

### 5. Integrity

- Never edit canonical per-run JSON in place for aggregation; write derived files to `/tmp` or a `derived/` folder.
- Respect **privacy** rules in `AUDIT_OUTPUT_SPEC.md` Section 4 when re-publishing merged data.

---

## Español (resumen)

Los pasos anteriores sirven para:

1. Ver las auditorías recientes.
2. Inspeccionar una corrida concreta.
3. **Concatenar** todos los `findings` de varios `.json` en un solo array (útil para contar o agrupar `ai_risk_id`).
4. Calcular frecuencias de riesgos IA típicos.

Si no tienes `jq`, puedes hacer lo mismo con Python (`json` + un bucle) manteniendo el mismo contrato de campos definido en `AUDIT_OUTPUT_SPEC.md`.
