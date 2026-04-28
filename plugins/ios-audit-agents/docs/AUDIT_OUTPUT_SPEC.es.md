# Especificación de salida de auditoría

> **Spec v1.0.** Contrato de salida de cada auditoría producida por el
> plugin `ios-audit-agents`: reporte Markdown legible por humanos y
> registro JSON legible por máquina.

Este documento es el contrato bajo el que los agentes y comandos
emiten sus hallazgos. Está referenciado desde el modelo de calidad
[`QUALITY_FRAMEWORK.md`](./QUALITY_FRAMEWORK.md) Sección 4.

Toda ejecución de auditoría **debe** producir ambos:

- Un reporte Markdown pensado para humanos (developers, leads,
  revisores).
- Un registro JSON pensado para máquinas (scripts de agregación,
  dashboards, análisis longitudinales).

Ambos archivos cubren los mismos hallazgos. El Markdown es una
proyección humana del JSON.

---

## 1. Ubicación y nomenclatura

Las salidas de auditoría viven dentro del repositorio auditado, nunca
en el plugin ni en carpetas del usuario, de forma que el historial de
auditorías viaje con el proyecto bajo control de versiones si el equipo
así lo decide.

### 1.1 Directorio

```
<repo-auditado>/.claude-marketplace-audits/
```

El directorio lo crea el plugin si no existe. Los equipos pueden
decidir ignorarlo vía `.gitignore` (uso privado) o comitearlo
(historial auditable). El plugin no fuerza ninguna de las dos
opciones.

### 1.2 Nomenclatura de archivo

Cada ejecución de auditoría produce dos archivos con el mismo nombre
base:

```
<UTC-timestamp>__<audit-id>.md
<UTC-timestamp>__<audit-id>.json
```

- `<UTC-timestamp>`: ISO 8601 en formato básico sin dos puntos, en UTC,
  p. ej. `20260427T134205Z`.
- `<audit-id>`: identificador estable corto de la ejecución, formato
  `[a-z0-9]{8}` (p. ej. `9f3c1a72`). Generado por el plugin.

Pareja de ejemplo:

```
20260427T134205Z__9f3c1a72.md
20260427T134205Z__9f3c1a72.json
```

### 1.3 Índice opcional

Cuando hay más de una auditoría en el directorio, el plugin puede
mantener un `index.json` que liste todas las ejecuciones en orden.
Es opcional y aditivo; no sustituye los archivos por ejecución.

---

## 2. Reporte Markdown

El reporte Markdown es la proyección humana de la auditoría. Debe
servir a un developer que nunca haya visto el JSON.

### 2.1 Estructura obligatoria

```markdown
# Reporte de auditoría — <nombre del proyecto>

- Audit ID: <audit-id>
- Timestamp: <ISO 8601 UTC>
- Versión del modelo de calidad: <p. ej. 0.1>
- Versión del plugin: <p. ej. 1.3.2>
- Alcance: <lista de dimensiones auditadas, p. ej. 3.2, 3.12, 3.13, 3.14, 3.15, 3.16>
- Commit del proyecto: <git sha o "uncommitted">

## Resumen ejecutivo

- Total de hallazgos: <N>
- Por severidad: P0 <a>, P1 <b>, P2 <c>, P3 <d>
- IA típicos: <X> de <N> (<ratio>%)
- Top de IDs de riesgo IA recurrentes: <top-3 si aplica>
- Hallazgos de mayor severidad que requieren atención: <conteo>

## Hallazgos por dimensión

### 3.X — <Nombre de la dimensión>

#### <severidad> — <título del hallazgo>

- ID: <auditor>-<slug-corto>
- Severidad: P0 | P1 | P2 | P3
- IA típico: sí (<AI-3.X-NNN>) | no
- Evidencia:
  - <archivo>:<línea(s)>
  - <referencia a métrica o log>
- Remediación: <qué, quién, para cuándo>
- Referencias: <referencia(s) de respaldo>

(repetir por hallazgo)

(repetir por dimensión que produzca hallazgos)

## Tareas de remediación sugeridas

Lista plana, ordenada por severidad, lista para copiar a un tracker.
Cada entrada incluye el ID del hallazgo y una acción en una línea.

- [P0] <tarea> (hallazgo: <id>)
- [P1] <tarea> (hallazgo: <id>)
- ...

## Notas de metodología

- Agentes ejecutados: <nombres>
- Skills consultadas: <nombres>
- Dimensiones en alcance pero con cero hallazgos: <lista>
- Dimensiones fuera de alcance del plugin: 3.1, 3.10
```

### 2.2 Reglas de estilo

- Un archivo de reporte por ejecución. No se añade a un archivo
  anterior.
- El Markdown debe ser autocontenido: el lector no debería tener que
  abrir el JSON para actuar.
- Los fragmentos de código respetan la política de privacidad de la
  Sección 4.
- Orden de severidad dentro de una dimensión: P0, P1, P2, P3.
- Orden de dimensiones: numérico (3.2 antes que 3.12).

---

## 3. Esquema JSON (v1.0)

El registro JSON es la forma canónica de los datos. El Markdown se
deriva de él. La agregación, los dashboards y el análisis longitudinal
consumen el JSON, nunca el Markdown.

### 3.1 Forma de nivel superior

```json
{
  "schema_version": "1.0",
  "audit_id": "9f3c1a72",
  "timestamp": "2026-04-27T13:42:05Z",
  "model_version": "0.1",
  "plugin_version": "1.3.2",
  "project": {
    "name": "ExampleApp",
    "git_sha": "abc1234",
    "ios_deployment_target": "16.0"
  },
  "scope": {
    "dimensions_audited": ["3.2", "3.12", "3.15"],
    "agents_used": ["architecture-auditor", "ux-accessibility-auditor", "api-freshness-auditor"],
    "skills_used": ["quality-model", "ai-risk-catalog"]
  },
  "findings": [],
  "metrics": {
    "total_findings": 0,
    "by_severity": { "P0": 0, "P1": 0, "P2": 0, "P3": 0 },
    "by_dimension": {},
    "ai_typical_count": 0,
    "ai_typical_ratio": 0.0,
    "duration_seconds": 0
  },
  "notes": {
    "dimensions_in_scope_with_zero_findings": [],
    "dimensions_out_of_plugin_scope": ["3.1", "3.10"]
  }
}
```

### 3.2 Referencia de campos

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `schema_version` | string | sí | Semver de este spec. v1.0 hoy. |
| `audit_id` | string | sí | `[a-z0-9]{8}`, estable por ejecución. |
| `timestamp` | string | sí | ISO 8601 UTC con sufijo `Z`. |
| `model_version` | string | sí | Versión del modelo de calidad (`QUALITY_FRAMEWORK.md`), p. ej. `0.1`. |
| `plugin_version` | string | sí | Versión de `plugin.json`. |
| `project.name` | string | sí | Nombre del proyecto. |
| `project.git_sha` | string | sí | SHA corto o completo, o `"uncommitted"`. |
| `project.ios_deployment_target` | string | opcional | p. ej. `"16.0"`. |
| `scope.dimensions_audited` | string[] | sí | IDs de dimensión como `"3.X"`. |
| `scope.agents_used` | string[] | sí | Nombres de agentes. |
| `scope.skills_used` | string[] | opcional | Nombres de skills. |
| `findings` | object[] | sí | Ver 3.3. Puede estar vacío. |
| `metrics.total_findings` | integer | sí | Conteo de `findings`. |
| `metrics.by_severity` | object | sí | Conteo por `P0`/`P1`/`P2`/`P3`. |
| `metrics.by_dimension` | object | sí | Mapa dimensión → conteo. |
| `metrics.ai_typical_count` | integer | sí | Conteo de `ai_typical: true`. |
| `metrics.ai_typical_ratio` | number | sí | `ai_typical_count / total_findings`, 0.0 si no hay hallazgos. |
| `metrics.duration_seconds` | integer | sí | Duración en pared de la ejecución. |
| `notes.dimensions_in_scope_with_zero_findings` | string[] | sí | Dimensiones auditadas sin hallazgos. Útil para detectar agentes flojos. |
| `notes.dimensions_out_of_plugin_scope` | string[] | sí | En la v0.1 del modelo de calidad siempre `["3.1", "3.10"]`. |

### 3.3 Objeto `finding`

```json
{
  "id": "arch-001",
  "dimension": "3.15",
  "severity": "P2",
  "title": "NavigationView used in 4 views",
  "evidence": {
    "files": [
      { "path": "Views/Home.swift", "lines": [42, 87] },
      { "path": "Views/Detail.swift", "lines": [15] }
    ],
    "metrics": [],
    "logs": []
  },
  "ai_typical": true,
  "ai_risk_id": "AI-3.15-001",
  "remediation": "Migrate NavigationView usages to NavigationStack.",
  "references": ["hudson:281"]
}
```

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | string | sí | Estable por ejecución, formato `<prefijo-auditor>-<slug>`. |
| `dimension` | string | sí | `"3.X"` del modelo de calidad. |
| `severity` | enum | sí | `"P0" \| "P1" \| "P2" \| "P3"`. |
| `title` | string | sí | Título humano de una línea. |
| `evidence.files` | object[] | opcional | `{ path, lines[] }`. |
| `evidence.metrics` | object[] | opcional | Referencias libres a métricas. |
| `evidence.logs` | object[] | opcional | Referencias libres a logs. |
| `ai_typical` | boolean | sí | Si encaja con una entrada del catálogo. |
| `ai_risk_id` | string | obligatorio si `ai_typical: true` | ID estable `AI-3.X-NNN` del `AI_RISK_CATALOG.md`. |
| `remediation` | string | sí | Frase orientada a la acción. |
| `references` | string[] | sí | Referencias de respaldo. Ver 3.4. |

### 3.4 Identificadores de referencia

Para mantener referencias estables entre auditorías, este spec define
un esquema corto que se usa en el array `references`:

| Prefijo | Fuente |
|---|---|
| `apple:hig` | Apple Human Interface Guidelines |
| `apple:review` | Apple App Review Guidelines |
| `apple:a11y` | Documentación de accesibilidad de Apple |
| `apple:concurrency` | Documentación oficial de Swift Concurrency |
| `apple:testing` | Documentación oficial de Swift Testing |
| `apple:oslog` | Documentación oficial de OSLog |
| `apple:metrickit` | Documentación oficial de MetricKit |
| `apple:localization` | Documentación oficial de localización de Apple |
| `masvs:<grupo>` | OWASP MASVS v2.1 + grupo de control (p. ej. `masvs:storage`) |
| `iso:25010` | ISO/IEC 25010:2023 |
| `wcag:2.2` | WCAG 2.2 |
| `hudson:<art>` | Paul Hudson, Hacking with Swift, número de artículo |
| `sundell:<topic>` | Swift by Sundell, slug del tema |
| `wals:<topic>` | Donny Wals, slug del tema |
| `vanderlee:<topic>` | Antoine van der Lee, slug del tema |

Las referencias que no encajen en esta lista usan un string libre y
podrán normalizarse en una versión futura del spec.

---

## 4. Política de privacidad

El JSON está diseñado para que pueda comitearse al repositorio o
compartirse en agregación con seguridad. Las siguientes reglas son
innegociables.

### 4.1 Nunca incluir en evidencia

- **Fragmentos verbatim de código fuente** más largos de lo
  estrictamente necesario para identificar un hallazgo. Usa
  `path:line` en lugar de pegar código.
- **Secretos en claro**. Cuando se detecta un secreto, el hallazgo
  registra su ubicación y tipo, nunca su valor.
- **Información personal identificable** de los commits (email del
  autor, nombres completos, mensajes completos de commit). Usar solo
  el SHA.
- **Datos de cliente** de cualquier tipo, incluyendo datos en
  fixtures o archivos de test cuando su origen sean usuarios reales.
- **URLs internas, hostnames internos o variables de entorno** cuya
  divulgación revelaría infraestructura.

### 4.2 Recomendado para evidencia

- Rutas de archivo relativas a la raíz del repositorio.
- Números y rangos de línea.
- Nombres de símbolos (función, clase, tipo) cuando hagan falta para
  la claridad.
- Valores de métrica (sin identificar usuarios).
- Niveles y categorías de log (sin contenido del log).

### 4.3 Expectativas de redacción

En caso de duda, el agente que produce el hallazgo **debe redactar**.
La redacción toma forma de placeholder, p. ej.:

```
"path": "Sources/Auth/Token.swift",
"lines": [42],
```

nunca:

```
"snippet": "let apiKey = \"sk_live_abc123...\""
```

---

## 5. Versionado del esquema

Este spec sigue versionado semántico a nivel de esquema:

- **Mayor (`2.0`, `3.0`, ...)**: cambio incompatible de la forma JSON
  (campos obligatorios renombrados/eliminados, cambios de tipo). Los
  logs antiguos no pueden leerse con el tooling nuevo sin migración.
- **Menor (`1.1`, `1.2`, ...)**: añadidos compatibles hacia atrás
  (campos opcionales nuevos, valores enum nuevos en campos no
  obligatorios).
- **Parche**: solo aclaraciones, sin cambios de campos.

El tooling que consume el JSON debe verificar `schema_version` y
negarse a operar sobre una versión mayor más nueva de la que entiende.

---

## 6. Pistas de agregación

El JSON está pensado para que la agregación simple sea posible sin
infraestructura. Estas preguntas se pueden contestar iterando los
archivos JSON de `.claude-marketplace-audits/`:

- *¿Qué riesgos IA recurren más?*
  Contar `ai_risk_id` en todos los hallazgos con `ai_typical: true`.
- *¿Qué dimensiones están en silencio?*
  Comparar `scope.dimensions_audited` con `metrics.by_dimension`; las
  dimensiones silenciosas aparecen en la primera y no en la segunda,
  o están listadas en
  `notes.dimensions_in_scope_with_zero_findings`.
- *¿Está derivando la severidad con el tiempo?*
  Ordenar las ejecuciones por `timestamp`; trazar la serie
  `metrics.by_severity`.
- *¿Sube o baja el `ai_typical_ratio`?*
  Trazar la serie de `metrics.ai_typical_ratio`.

Estas son las entradas que alimentan la Sección 7.3 del modelo de
calidad.

---

## 7. Ejemplos

### 7.1 Auditoría mínima (sin hallazgos)

```json
{
  "schema_version": "1.0",
  "audit_id": "01abcdef",
  "timestamp": "2026-04-27T10:00:00Z",
  "model_version": "0.1",
  "plugin_version": "1.3.2",
  "project": {
    "name": "TinyApp",
    "git_sha": "deadbee",
    "ios_deployment_target": "17.0"
  },
  "scope": {
    "dimensions_audited": ["3.15"],
    "agents_used": ["api-freshness-auditor"],
    "skills_used": ["quality-model"]
  },
  "findings": [],
  "metrics": {
    "total_findings": 0,
    "by_severity": { "P0": 0, "P1": 0, "P2": 0, "P3": 0 },
    "by_dimension": {},
    "ai_typical_count": 0,
    "ai_typical_ratio": 0.0,
    "duration_seconds": 12
  },
  "notes": {
    "dimensions_in_scope_with_zero_findings": ["3.15"],
    "dimensions_out_of_plugin_scope": ["3.1", "3.10"]
  }
}
```

### 7.2 Auditoría con un hallazgo IA típico

```json
{
  "schema_version": "1.0",
  "audit_id": "9f3c1a72",
  "timestamp": "2026-04-27T13:42:05Z",
  "model_version": "0.1",
  "plugin_version": "1.3.2",
  "project": {
    "name": "ExampleApp",
    "git_sha": "abc1234",
    "ios_deployment_target": "16.0"
  },
  "scope": {
    "dimensions_audited": ["3.15"],
    "agents_used": ["api-freshness-auditor"],
    "skills_used": ["quality-model", "ai-risk-catalog"]
  },
  "findings": [
    {
      "id": "apifresh-001",
      "dimension": "3.15",
      "severity": "P2",
      "title": "NavigationView used in 4 views",
      "evidence": {
        "files": [
          { "path": "Views/Home.swift", "lines": [42, 87] },
          { "path": "Views/Detail.swift", "lines": [15] },
          { "path": "Views/Settings.swift", "lines": [9] }
        ],
        "metrics": [],
        "logs": []
      },
      "ai_typical": true,
      "ai_risk_id": "AI-3.15-001",
      "remediation": "Migrate NavigationView usages to NavigationStack.",
      "references": ["hudson:281"]
    }
  ],
  "metrics": {
    "total_findings": 1,
    "by_severity": { "P0": 0, "P1": 0, "P2": 1, "P3": 0 },
    "by_dimension": { "3.15": 1 },
    "ai_typical_count": 1,
    "ai_typical_ratio": 1.0,
    "duration_seconds": 18
  },
  "notes": {
    "dimensions_in_scope_with_zero_findings": [],
    "dimensions_out_of_plugin_scope": ["3.1", "3.10"]
  }
}
```
