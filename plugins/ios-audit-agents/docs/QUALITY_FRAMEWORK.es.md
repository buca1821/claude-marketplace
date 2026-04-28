# ios-audit-agents — Modelo de calidad y especificación de auditoría

> **Especificación v0.1.** Modelo de calidad de ingeniería para apps
> iOS asistidas por IA, usada como base de auditoría del plugin
> `ios-audit-agents`.

Este documento define las dimensiones de calidad de ingeniería que el
plugin audita, los riesgos típicos de IA que vigila y el contrato bajo
el que se registran los hallazgos. No es un estándar externo, no es un
checklist de App Review y no es un envoltorio de ISO/IEC 25010.

Esta especificación está acompañada de dos documentos hermanos:

- [`AUDIT_OUTPUT_SPEC.md`](./AUDIT_OUTPUT_SPEC.md) — el contrato de
  salida humano (Markdown) y máquina (JSON) de cada auditoría.
- [`AI_RISK_CATALOG.md`](./AI_RISK_CATALOG.md) — el catálogo de riesgos
  típicos de IA con identificadores estables (`AI-3.X-NNN`)
  referenciados desde las dimensiones de abajo.

## Introducción

Las apps iOS modernas se escriben cada vez más con copilotos de IA. Eso
aporta velocidad, pero también una clase de desviaciones recurrentes:
APIs deprecadas, arquitecturas plausibles pero erróneas, errores
silenciados, regresiones de accesibilidad, fugas de secretos. Esta
especificación existe para que los agentes, skills y comandos del
plugin tengan una base compartida y explícita de qué buscar y cómo
reportarlo.

**Alcance.** Esta especificación cubre la **calidad de ingeniería**
de apps iOS (Swift, SwiftUI/UIKit, distribución por App Store). El
encaje de producto, las métricas de negocio y la experiencia de
desarrollo a nivel de equipo se reconocen como parte de la calidad
global de una app pero quedan explícitamente fuera del alcance del
plugin; aparecen en la Sección 3 solo para hacer visible la frontera.

**Identidad.** Esta especificación es operativa, no normativa. Es el
vocabulario que los agentes y skills del plugin usan, y el contrato
con el que su salida cumple. Cualquier aspiración a convertirse en
referencia pública depende de la evidencia acumulada vía Sección 4 —
no de las afirmaciones de este documento.

---

## 1. Fundamentos

### 1.1 Qué es y qué no es esta especificación

Esta especificación **es**:

- La base operativa compartida de `ios-audit-agents`: el vocabulario
  (dimensiones, severidades, riesgos típicos de IA) que todo agente,
  skill y comando del plugin consume.
- Un instrumento de medida: cada auditoría produce datos
  estructurados (`AUDIT_OUTPUT_SPEC.md`) que, en agregado, validan o
  refutan los supuestos de la propia especificación.

Esta especificación **no es**:

- Un estándar externo ni una publicación.
- Un sustituto de ISO/IEC 25010, OWASP MASVS, Apple HIG o App Review
  Guidelines. Los usa como referencias de respaldo donde aplican.
- Una cobertura completa de “calidad de app”. Las dimensiones de
  producto, negocio y equipo quedan fuera de alcance por diseño
  (ver Sección 3).

### 1.2 La dimensión IA

Cada dimensión declara uno o varios **riesgos típicos de IA** —
desviaciones que los agentes del plugin esperan encontrar con más
frecuencia en código escrito o asistido por copilotos de IA. Estos
riesgos tienen identificadores estables en
[`AI_RISK_CATALOG.md`](./AI_RISK_CATALOG.md), de forma que cuando el
plugin registra un hallazgo se puede agregar y trazar a lo largo del
tiempo.

Si los riesgos típicos de IA aparecen efectivamente con más frecuencia
en código asistido por IA que en código escrito a mano es una
hipótesis. El papel del plugin es **medir**, no afirmar. La Sección 4
define qué se mide; la Sección 7 describe cómo la evidencia acumulada
vuelve a esta especificación.

### 1.3 Cómo el plugin usa esta especificación

Un ciclo típico de auditoría:

1. El usuario invoca un comando (p. ej. `/run-audits`).
2. El comando selecciona qué dimensiones entran en alcance.
3. Para cada dimensión, un agente o skill realiza el análisis usando
   las **Señales y checks** de la dimensión y los IDs de riesgos IA
   del catálogo.
4. Los hallazgos se registran en el formato definido por
   `AUDIT_OUTPUT_SPEC.md`, tanto en Markdown legible como en JSON.
5. La salida JSON se añade al log de auditorías del proyecto
   (`.claude-marketplace-audits/` dentro del repositorio auditado).
6. Periódicamente, los logs acumulados se revisan y esta especificación
   se actualiza con la evidencia (Sección 7).

---

## 2. Escala de severidad

Los hallazgos usan una escala de cuatro niveles. La severidad es
independiente del esfuerzo.

| Nivel | Significado | Ejemplos |
|---|---|---|
| **P0** | Bloquea release. Daño al usuario, pérdida de datos, riesgo legal, rechazo en store, caída pública. | API key hardcodeada, ATS desactivado globalmente, crash en arranque en frío, falta de privacy manifest. |
| **P1** | Recomendado fuertemente antes de release. Daño real a usuarios, equipo o producto si no se corrige. | Sin accesibilidad en flujo principal, sin manejo offline en pantalla crítica, sin feedback de error en acción central. |
| **P2** | Corregir pronto. Deuda de calidad, mantenibilidad o riesgo que se acumula. | APIs deprecadas en código activo, cobertura de tests débil en lógica, logging ad-hoc sin categorías. |
| **P3** | Conviene. Pulido, consistencia, preparación a futuro. | Tokens de espaciado inconsistentes, deriva en nombrado, computed properties redundantes. |

---

## 3. Dimensiones de calidad

Cada dimensión sigue la misma estructura:

- **Qué auditamos** — alcance de la dimensión.
- **Por qué importa** — una frase con la consecuencia de hacerlo mal.
- **Riesgos IA típicos** — IDs estables del `AI_RISK_CATALOG.md`.
- **Señales y checks** — cosas concretas que mirar.
- **Operativizado por** — el agente, skill o estado dentro del plugin.
- **Referencias de respaldo** — fuentes del sector que apoyan la
  dimensión.

Leyenda de **Operativizado por**:

- `agent: <nombre>` — implementado hoy por un agente auditor existente.
- `skill: <nombre>` — implementado por una skill consultiva.
- `planned: <nombre>` — declarado pero todavía no implementado.
- `out-of-plugin-scope (manual)` — reconocido como parte de la calidad
  de la app pero no auditable por este plugin; requiere revisión humana.

### 3.1 Encaje de producto y límites

- **Qué auditamos** — declaración de alcance, usuario objetivo,
  propuesta de valor, alineación con la categoría de App Store, presencia
  de funcionalidad especulativa, código muerto de iteraciones anteriores.
- **Por qué importa** — una funcionalidad bonita pero irrelevante sigue
  siendo desperdicio, y la falta de alcance es causa común de rechazo
  en App Review.
- **Riesgos IA típicos** — `AI-3.1-001`.
- **Señales y checks** — declaración explícita de fuera-de-alcance;
  sin rutas de código para funcionalidades fuera del spec; feature flags
  documentados y con dueño; categoría y descripción en App Store
  coinciden con la app real.
- **Operativizado por** — `out-of-plugin-scope (manual)`.
- **Referencias de respaldo** — Apple App Review Guidelines (Business,
  Design).

### 3.2 Arquitectura y modularidad

- **Qué auditamos** — capas, fronteras de módulo, dirección de
  dependencias, superficies públicas, presencia de ciclos, separación
  UI/dominio/datos.
- **Por qué importa** — la arquitectura es lo que permite evolucionar
  a escala y que varias personas trabajen sin pisarse.
- **Riesgos IA típicos** — `AI-3.2-001`, `AI-3.2-002`.
- **Señales y checks** — las vistas no conocen persistencia ni red
  directamente; sin dependencias cíclicas; interfaces públicas mínimas
  y estables; aspectos transversales inyectados, no importados en
  todos lados.
- **Operativizado por** — `agent: architecture-auditor`.
- **Referencias de respaldo** — Swift by Sundell (arquitectura y
  modularización); ISO/IEC 25010:2023 — Maintainability.

### 3.3 Integridad del modelo de dominio

- **Qué auditamos** — tipos significativos, invariantes garantizados,
  semántica valor vs referencia, identificadores, corrección de
  `Codable`, tipos de error.
- **Por qué importa** — un modelo débil filtra complejidad a cada
  funcionalidad que lo toca.
- **Riesgos IA típicos** — `AI-3.3-001`.
- **Señales y checks** — identificadores tipados, no `String` plano;
  tipos valor donde corresponde; errores tipados en frontera; sin
  enums “stringly typed”.
- **Operativizado por** — `agent: architecture-auditor` (extensión).
- **Referencias de respaldo** — Swift by Sundell (diseño de modelos).

### 3.4 Estado, concurrencia y data races

- **Qué auditamos** — aislamiento de actores, ubicación de `@MainActor`,
  conformidad `Sendable`, ciclo de vida de tareas, cancelación,
  corrección de hilos.
- **Por qué importa** — los data races corrompen estado y crashean a
  los usuarios; son la clase de bugs más difícil de reproducir.
- **Riesgos IA típicos** — `AI-3.4-001`, `AI-3.4-002`.
- **Señales y checks** — modo Swift 6 considerado o planificado;
  avisos de data race limpios; tareas largas con cancelación
  explícita; sin parches `.main.async` que tapan un problema de
  aislamiento.
- **Operativizado por** — `planned: concurrency-auditor`. Hasta
  entonces, parcialmente cubierto por `agent: code-health-auditor`.
- **Referencias de respaldo** — Donny Wals, Antoine van der Lee
  (Swift Concurrency); documentación oficial de Swift Concurrency;
  ISO/IEC 25010:2023 — Reliability.

### 3.5 Fiabilidad y manejo de errores

- **Qué auditamos** — propagación de errores, reintentos, recuperación,
  comportamiento offline, casos límite, ratio crash-free, fronteras
  defensivas.
- **Por qué importa** — la realidad es poco fiable; los usuarios solo
  recuerdan el momento en que algo falló.
- **Riesgos IA típicos** — `AI-3.5-001`, `AI-3.5-002`.
- **Señales y checks** — los errores llegan al usuario con mensajes
  accionables; estrategia explícita de retry/offline en fallos de red;
  objetivo crash-free definido; sin errores tragados en rutas de
  producción.
- **Operativizado por** — `planned: reliability-auditor`.
- **Referencias de respaldo** — ISO/IEC 25010:2023 — Reliability.

### 3.6 Seguridad y privacidad

- **Qué auditamos** — almacenamiento de secretos, seguridad de
  transporte, autenticación, permisos, telemetría de datos sensibles,
  App Transport Security, privacy manifest, declaraciones de tracking.
- **Por qué importa** — la superficie legal y de confianza; los fallos
  aquí dañan al usuario directamente y pueden retirar la app de la store.
- **Riesgos IA típicos** — `AI-3.6-001`, `AI-3.6-002`, `AI-3.6-003`.
- **Señales y checks** — secretos en Keychain, nunca en `UserDefaults`
  ni en código; sin excepciones ATS globales; privacy manifest
  presente y exacto; dominios de tracking declarados; eventos de
  analítica revisados para PII; permisos pedidos en contexto con
  propósito claro.
- **Operativizado por** — `planned: security-privacy-auditor`.
- **Referencias de respaldo** — OWASP MASVS v2.1 (STORAGE, CRYPTO,
  AUTH, NETWORK, PLATFORM, PRIVACY); Apple App Review Guidelines
  (Safety, Legal); ISO/IEC 25010:2023 — Security.

### 3.7 Observabilidad y telemetría

- **Qué auditamos** — logging estructurado, categorías de log, reporte
  de crashes, métricas de rendimiento, trazabilidad de incidentes.
- **Por qué importa** — no se puede arreglar ni medir lo que no se ve;
  la observabilidad convierte un report de usuario en diagnóstico
  accionable.
- **Riesgos IA típicos** — `AI-3.7-001`, `AI-3.7-002`.
- **Señales y checks** — `OSLog` con subsistema y categoría, no
  `print`; MetricKit (o equivalente) integrado; niveles de log
  consistentes; sin PII en logs.
- **Operativizado por** — `planned: observability-auditor`.
- **Referencias de respaldo** — documentación oficial de OSLog y
  MetricKit.

### 3.8 Estrategia de testing

- **Qué auditamos** — equilibrio de la pirámide, cobertura de lógica
  vs UI, mocks/fixtures, snapshot tests, integración con CI,
  mantenibilidad.
- **Por qué importa** — los tests son el único mecanismo sostenible
  para evolucionar la app sin regresiones.
- **Riesgos IA típicos** — `AI-3.8-001`, `AI-3.8-002`.
- **Señales y checks** — cobertura unitaria significativa en código
  con lógica; UI tests con page-object o equivalente; baselines de
  snapshot revisadas al cambiar; tests en CI como gate.
- **Operativizado por** — `planned: testing-strategy-auditor`.
- **Referencias de respaldo** — documentación oficial de Swift Testing;
  ISO/IEC 25010:2023 — Functional Suitability.

### 3.9 CI/CD e ingeniería de release

- **Qué auditamos** — pipelines, gates, firma, entornos, rollouts,
  notas de release, ruta de hotfix, protección de ramas.
- **Por qué importa** — la ingeniería de release permite ir rápido
  con seguridad; sin ella cada release es un ejercicio manual heroico.
- **Riesgos IA típicos** — `AI-3.9-001`.
- **Señales y checks** — gates obligatorios marcados como obligatorios
  (gates de merge, no informativos); firma y provisioning automatizados
  y documentados; rutas de hotfix y rollback existen y se han probado;
  notas de release generadas o curadas.
- **Operativizado por** — `skill: ci-cd-checklist`.
- **Referencias de respaldo** — ISO/IEC 25010:2023 — Maintainability,
  Flexibility.

### 3.10 Experiencia de desarrollo (DX)

- **Qué auditamos** — tiempo de setup, herramientas, scripts,
  documentación interna, onboarding, señales de fricción reportadas
  por el equipo.
- **Por qué importa** — una mala DX es un asesino silencioso de
  calidad; aparece más tarde como atajos, falta de tests y estilo
  inconsistente.
- **Riesgos IA típicos** — `AI-3.10-001`.
- **Señales y checks** — comando único de bootstrap; README y
  `CONTRIBUTING` exactos; hooks pre-commit/pre-push presentes y útiles;
  artefactos generados o comiteados o reproducibles.
- **Operativizado por** — `out-of-plugin-scope (manual)`.
- **Referencias de respaldo** — Swift by Sundell (ergonomía del
  codebase); retrospectivas de equipo.

### 3.11 Localización e internacionalización

- **Qué auditamos** — string catalogs, plurales, formato consciente
  de locale, soporte RTL, claves faltantes/no usadas, datos de test
  mezclados.
- **Por qué importa** — la localización es corrección, no decoración;
  una mala localización se ve en cada usuario fuera del locale por
  defecto.
- **Riesgos IA típicos** — `AI-3.11-001`, `AI-3.11-002`.
- **Señales y checks** — todos los strings visibles vienen de un
  string catalog; reglas de plural definidas donde aplica; formatters
  conscientes de locale; lint/script reportando claves faltantes o no
  usadas.
- **Operativizado por** — `planned: localization-auditor`.
- **Referencias de respaldo** — documentación oficial de localización
  de Apple.

### 3.12 Calidad UX y UI

- **Qué auditamos** — navegación, layout, feedback, consistencia
  visual, uso de design tokens, alineación con Apple HIG.
- **Por qué importa** — este es el producto que el usuario realmente
  toca; calidad de UI es calidad percibida.
- **Riesgos IA típicos** — `AI-3.12-001`, `AI-3.12-002`.
- **Señales y checks** — cumplimiento HIG en navegación, modalidad,
  feedback; design system documentado y en uso; composición con
  subvistas reales, no solo computed properties; APIs SwiftUI
  modernas (`NavigationStack`, `foregroundStyle`, `.tab`).
- **Operativizado por** — `agent: ux-accessibility-auditor`.
- **Referencias de respaldo** — Apple Human Interface Guidelines;
  Paul Hudson — *What to fix in AI-generated Swift code*.

### 3.13 Accesibilidad

- **Qué auditamos** — VoiceOver, Dynamic Type, contraste, reduce
  motion, áreas táctiles, traits semánticos, alternativas a gestos.
- **Por qué importa** — requisito legal, mínimo ético y expansión
  medible de la audiencia.
- **Riesgos IA típicos** — `AI-3.13-001`, `AI-3.13-002`.
- **Señales y checks** — VoiceOver llega y describe cada elemento
  interactivo; Dynamic Type no rompe los flujos principales; contraste
  cumple WCAG 2.2 AA; los gestos tienen alternativa con botón o
  teclado.
- **Operativizado por** — `agent: ux-accessibility-auditor`.
- **Referencias de respaldo** — documentación de accesibilidad de
  Apple; WCAG 2.2; Paul Hudson sobre accesibilidad en SwiftUI.

### 3.14 Rendimiento y energía

- **Qué auditamos** — tiempo de arranque, suavidad de scroll, huella
  de memoria, eficiencia de red, impacto energético y de batería.
- **Por qué importa** — calidad percibida y retención; una app lenta
  se desinstala independientemente de su funcionalidad.
- **Riesgos IA típicos** — `AI-3.14-001`, `AI-3.14-002`.
- **Señales y checks** — presupuesto de cold launch definido; las
  listas perfilan limpio en Instruments; assets de imagen del tamaño
  del dispositivo; modos background y de energía usados
  apropiadamente.
- **Operativizado por** — `agent: performance-auditor`.
- **Referencias de respaldo** — documentación de rendimiento de Apple;
  MetricKit; ISO/IEC 25010:2023 — Performance Efficiency.

### 3.15 Frescura de APIs y deprecaciones

- **Qué auditamos** — alineación de deployment target, uso de APIs
  deprecadas, adopción de patrones modernos de Swift/SwiftUI.
- **Por qué importa** — deuda técnica, cumplimiento App Store y
  capacidad de publicar para nuevas versiones de iOS.
- **Riesgos IA típicos** — `AI-3.15-001`, `AI-3.15-002`, `AI-3.15-003`,
  `AI-3.15-004`.
- **Señales y checks** — cero warnings de deprecación en código
  activo; APIs SwiftUI modernas en archivos nuevos; deployment target
  consistente entre módulos; `@Observable`, `NavigationStack`,
  `foregroundStyle` por defecto.
- **Operativizado por** — `agent: api-freshness-auditor`.
- **Referencias de respaldo** — Paul Hudson — *What to fix in
  AI-generated Swift code* y *Teach your AI to write Swift the
  Hacking with Swift way*.

### 3.16 Salud del código y SOLID

- **Qué auditamos** — tamaño de funciones y tipos, nombrado, cohesión,
  acoplamiento, duplicación, código muerto, calidad de comentarios,
  cumplimiento de lint.
- **Por qué importa** — la salud del código es el coste corriente del
  codebase; se ve directamente en lead time y frecuencia de incidentes.
- **Riesgos IA típicos** — `AI-3.16-001`, `AI-3.16-002`.
- **Señales y checks** — SwiftLint/SwiftFormat aplicados en CI;
  distribuciones de longitud de funciones y tipos revisadas;
  violaciones SOLID detectadas; sin código comentado; sin comentarios
  narrativos que dupliquen el código.
- **Operativizado por** — `agent: code-health-auditor`.
- **Referencias de respaldo** — Swift by Sundell (organización de
  código); ISO/IEC 25010:2023 — Maintainability.

---

## 4. Qué mide esta especificación

Esta especificación es un instrumento de medida. Cada auditoría produce
datos estructurados para que los supuestos de la propia especificación
puedan validarse contra evidencia acumulada a lo largo del tiempo.

El contrato completo de salida — reporte Markdown y esquema JSON —
vive en [`AUDIT_OUTPUT_SPEC.md`](./AUDIT_OUTPUT_SPEC.md). El resumen
de abajo declara qué debe emitir el plugin, independientemente del
formato concreto.

### 4.1 Salida por auditoría

Para cada ejecución de auditoría el plugin emite ambos:

- **Un reporte Markdown legible por humanos** — resumen ejecutivo,
  hallazgos por dimensión, tareas de remediación sugeridas, ranking
  de severidad.
- **Un registro JSON legible por máquina** — los mismos hallazgos en
  forma estructurada, con IDs estables, referencias a dimensión, IDs
  de riesgos IA y localizadores de evidencia.

Ambos archivos se escriben en `.claude-marketplace-audits/` dentro
del repositorio auditado.

### 4.2 Campos por hallazgo

Cada hallazgo lleva como mínimo:

- Un identificador estable.
- La dimensión a la que pertenece (3.X).
- Severidad (P0–P3).
- Evidencia (archivos, líneas, métricas o logs).
- El flag `ai_typical` y, si es `true`, el `ai_risk_id` del catálogo.
- Sugerencia de remediación.
- Una o más referencias de respaldo de la Sección 6.

### 4.3 Métricas por auditoría

Cada auditoría emite al menos:

- Total de hallazgos.
- Hallazgos por severidad.
- Hallazgos por dimensión.
- Conteo y ratio de hallazgos `ai_typical: true`.
- Duración de la auditoría.

### 4.4 Señales agregadas (opcionales, sin infraestructura)

Cuando se acumulan varias auditorías de un proyecto (o entre proyectos,
a discreción del equipo), las siguientes señales quedan disponibles
sin infraestructura adicional:

- Top-N de riesgos IA por ocurrencia.
- Recurrencia de riesgos específicos a lo largo de auditorías.
- Dimensiones que sistemáticamente no producen hallazgos — señal de
  detección floja o de bajo riesgo real.
- Tendencia de distribución de severidad por dimensión a lo largo
  del tiempo.

Estas señales son la entrada de la Sección 7.3 y la base para
promocionar, degradar o reformular entradas de
`AI_RISK_CATALOG.md`.

---

## 5. Cómo registrar hallazgos

Los hallazgos se producen en dos formas pareadas (humano y máquina)
según `AUDIT_OUTPUT_SPEC.md`. La forma humana sigue esta plantilla:

```text
ID:           <auditor>-<slug-corto>
Dimensión:    3.X — <Nombre de la dimensión>
Severidad:    P0 | P1 | P2 | P3
Evidencia:    <archivos, líneas, capturas, métricas, logs>
IA típico:    sí (<AI-3.X-NNN>) | no
Remediación:  <qué hacer, quién, para cuándo>
Referencias:  <referencia(s) de respaldo de la Sección 6>
```

Notas:

- El campo `IA típico` es obligatorio. Cuando es `sí`, el ID del
  riesgo IA del catálogo es obligatorio. Eso es lo que permite la
  agregación y la validación.
- `Referencias` debe apuntar a la fuente concreta de la Sección 6,
  no a la dimensión.

---

## 6. Referencias

Agrupadas por lo que aportan a esta especificación.

### Apple — verdad de plataforma

- **Human Interface Guidelines** — UX, navegación, modalidad,
  movimiento, iconografía, primitivas de accesibilidad.
  https://developer.apple.com/design/human-interface-guidelines/
- **App Review Guidelines** — Safety, Performance, Business, Design,
  Legal.
  https://developer.apple.com/app-store/review/guidelines/
- **Documentación de accesibilidad** — VoiceOver, Dynamic Type,
  AccessibilityTraits, contenido semántico.
  https://developer.apple.com/accessibility/
- **Swift Concurrency, Swift Testing, OSLog, MetricKit** —
  documentación oficial de la cadena de herramientas moderna.

### Seguridad y privacidad móvil

- **OWASP MASVS v2.1** — Mobile Application Security Verification
  Standard. Ocho grupos de control: STORAGE, CRYPTO, AUTH, NETWORK,
  PLATFORM, CODE, RESILIENCE, PRIVACY.
  https://mas.owasp.org/MASVS/

### Referencias del sector iOS / Swift

- **Paul Hudson — Hacking with Swift**
  - *What to fix in AI-generated Swift code* — catálogo directo de
    desviaciones de la IA en Swift/SwiftUI.
    https://www.hackingwithswift.com/articles/281/what-to-fix-in-ai-generated-swift-code
  - *Teach your AI to write Swift the Hacking with Swift way* — receta
    para un `AGENTS.md` que oriente a las herramientas IA.
    https://www.hackingwithswift.com/articles/284/teach-your-ai-to-write-swift-the-hacking-with-swift-way
- **John Sundell — Swift by Sundell** — arquitectura, modularización,
  modelado de dominio, codebases sostenibles.
  https://www.swiftbysundell.com/
- **Donny Wals** — Swift 6, concurrencia, aislamiento, Sendable.
  https://www.donnywals.com/
- **Antoine van der Lee** — herramientas de migración a Swift 6,
  patrones y trampas de concurrencia.
  https://www.avanderlee.com/

### Calidad de software general (informativa)

- **ISO/IEC 25010:2023** — modelo de calidad de producto software.
  Aquí como referencia cruzada, no como estructura principal.
- **WCAG 2.2** — Web Content Accessibility Guidelines, usadas como
  respaldo cross-platform de los criterios de accesibilidad.

---

## 7. Estado y hoja de ruta

### 7.1 Estado actual (especificación v0.1)

- Esta especificación es la base operativa de `ios-audit-agents`.
  No está validada externamente y no reclama autoridad más allá del
  plugin.
- Solo alcance de ingeniería. Encaje de producto (3.1) y experiencia
  de desarrollo (3.10) aparecen como `out-of-plugin-scope (manual)`
  para hacer la frontera explícita pero no son auditables por este
  plugin.
- El catálogo de riesgos IA
  ([`AI_RISK_CATALOG.md`](./AI_RISK_CATALOG.md)) empieza
  deliberadamente pequeño con entradas citables primero; las
  heurísticas se marcan como tal hasta que la evidencia se acumule.

### 7.2 Foto de cobertura

| 3.X | Dimensión | Operativizado por |
|---|---|---|
| 3.1 | Encaje de producto y límites | `out-of-plugin-scope (manual)` |
| 3.2 | Arquitectura y modularidad | `agent: architecture-auditor` |
| 3.3 | Integridad del modelo de dominio | `agent: architecture-auditor` (extensión) |
| 3.4 | Estado, concurrencia y data races | `planned: concurrency-auditor`, parcialmente `agent: code-health-auditor` |
| 3.5 | Fiabilidad y manejo de errores | `planned: reliability-auditor` |
| 3.6 | Seguridad y privacidad | `planned: security-privacy-auditor` |
| 3.7 | Observabilidad y telemetría | `planned: observability-auditor` |
| 3.8 | Estrategia de testing | `planned: testing-strategy-auditor` |
| 3.9 | CI/CD e ingeniería de release | `skill: ci-cd-checklist` |
| 3.10 | Experiencia de desarrollo | `out-of-plugin-scope (manual)` |
| 3.11 | Localización e i18n | `planned: localization-auditor` |
| 3.12 | Calidad UX y UI | `agent: ux-accessibility-auditor` |
| 3.13 | Accesibilidad | `agent: ux-accessibility-auditor` |
| 3.14 | Rendimiento y energía | `agent: performance-auditor` |
| 3.15 | Frescura de APIs y deprecaciones | `agent: api-freshness-auditor` |
| 3.16 | Salud del código y SOLID | `agent: code-health-auditor` |

### 7.3 Cómo la evidencia vuelve a esta especificación

Esta especificación se actualiza solo cuando los datos acumulados de
auditoría lo justifican. Ciclo típico de actualización:

1. Agregar las salidas JSON de `.claude-marketplace-audits/` de uno
   o varios proyectos (Sección 4.4).
2. Revisar qué riesgos IA se han observado, con qué frecuencia y a
   qué severidades.
3. Actualizar `AI_RISK_CATALOG.md`:
   - Promocionar riesgos heurísticos a “conocimiento común” cuando
     se observen consistentemente entre proyectos.
   - Degradar o eliminar riesgos que nunca aparezcan, o reformularlos
     si su manifestación difiere de lo hipotetizado.
4. Ajustar dimensiones de esta especificación solo si los datos
   muestran un gap estructural (clase recurrente de hallazgo que no
   encaja en ninguna dimensión) o redundancia estructural (dos
   dimensiones que siempre co-ocurren).
5. Subir la versión de la especificación (Sección 7.1) y registrar el
   cambio en una entrada de changelog.

Esta especificación no cambia con opinión. Cambia con evidencia.

### 7.4 Camino a una referencia de comunidad (diferido)

Una promoción futura de esta especificación a referencia pública
requeriría:

- Una pasada de citas sobre cada riesgo IA del `AI_RISK_CATALOG.md`,
  separando citado / conocimiento común / heurística del marco.
- Un análisis comparativo explícito con ISO/IEC 25010, OWASP MASVS,
  Apple HIG y App Review Guidelines.
- Un protocolo empírico reproducible: ejecutar auditorías sobre un
  conjunto definido de muestras iOS asistidas y no asistidas por IA,
  midiendo si la hipótesis del riesgo IA se sostiene.

Esto queda diferido. Esta especificación aspira primero a ser un
instrumento útil; cualquier afirmación externa se sigue de los datos,
no de este documento.
