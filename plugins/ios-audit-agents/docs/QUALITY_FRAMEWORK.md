# ios-audit-agents — Quality model and audit specification

> **Specification v0.1.** Engineering quality model for AI-assisted iOS
> apps, used as the audit basis of the `ios-audit-agents` plugin.

This document defines the dimensions of engineering quality the plugin
audits, the AI-typical risks it watches for, and the contract under
which findings are recorded. It is not an external standard, not an
App Review checklist, and not a wrapper for ISO/IEC 25010.

The specification is paired with two companion documents:

- [`AUDIT_OUTPUT_SPEC.md`](./AUDIT_OUTPUT_SPEC.md) — the human (Markdown) and
  machine (JSON) output contract for every audit run.
- [`AI_RISK_CATALOG.md`](./AI_RISK_CATALOG.md) — the catalog of AI-typical
  risks with stable identifiers (`AI-3.X-NNN`) referenced from the
  dimensions below.

## Introduction

Modern iOS apps are increasingly written with AI copilots. That brings
speed but also a class of recurring deviations: deprecated APIs,
plausible-looking architectures, silently swallowed errors, accessibility
regressions, leaked secrets. This specification exists so the plugin's
agents, skills and commands have a shared, explicit basis for what they
look for and how they report it.

**Scope.** This specification covers the **engineering quality** of iOS
apps (Swift, SwiftUI/UIKit, App Store distribution). Product fit,
business metrics and team-level developer experience are recognized as
part of overall app quality but are explicitly out of the plugin's
scope; they are listed in Section 3 only to make the boundary visible.

**Identity.** The specification is operational, not normative. It is
the vocabulary the plugin's agents and skills use, and the contract
their output complies with. Any aspiration to become a public reference
depends on evidence accumulated through Section 4 — not on this
document's claims.

---

## 1. Foundations

### 1.1 What this specification is and is not

This specification **is**:

- The shared operational basis of `ios-audit-agents`: the vocabulary
  (dimensions, severities, AI-typical risks) that every agent, skill
  and command in the plugin must consume.
- A measurement instrument: each audit produces structured data
  (`AUDIT_OUTPUT_SPEC.md`) that, in aggregate, validates or falsifies
  this document's own assumptions.

This specification **is not**:

- An external standard or a publication.
- A replacement for ISO/IEC 25010, OWASP MASVS, Apple HIG or App Review
  Guidelines. It uses them as backing references where they apply.
- Complete coverage of "app quality". Product, business and team
  dimensions are out of scope by design (see Section 3).

### 1.2 The AI dimension

Each dimension declares one or more **AI-typical risks** — deviations the
plugin's agents are expected to find more often in code that has been
written or assisted by AI copilots. These risks have stable identifiers
in [`AI_RISK_CATALOG.md`](./AI_RISK_CATALOG.md) so that, when the plugin
records a finding, it can be aggregated and tracked over time.

Whether AI-typical risks actually show up more frequently in AI-assisted
code than in handwritten code is a hypothesis. The plugin's role is to
**measure**, not to assert. Section 4 defines what is measured;
Section 7 describes how accumulated evidence flows back into this
specification.

### 1.3 How the specification is used by the plugin

A typical audit cycle:

1. A user invokes a command (e.g. `/run-audits`).
2. The command selects which dimensions are in scope.
3. For each dimension, an agent or skill performs the analysis, using
   the **Signals & checks** of the dimension and the AI-typical risk IDs
   from the catalog.
4. Findings are recorded in the format defined by `AUDIT_OUTPUT_SPEC.md`,
   both human-readable Markdown and machine-readable JSON.
5. The JSON output is appended to the project's audit log
   (`.claude-marketplace-audits/` inside the audited repository).
6. Periodically, accumulated logs across audits are reviewed and this
   specification is updated with evidence (Section 7).

---

## 2. Severity scale

Findings use a four-level scale. Severity is independent of effort.

| Level | Meaning | Examples |
|---|---|---|
| **P0** | Ship-blocker. User harm, data loss, legal risk, store rejection, public outage. | Hardcoded API key, ATS disabled globally, crash on cold launch, missing privacy manifest. |
| **P1** | Strongly recommended before release. Real damage to users, team or product if left unfixed. | No accessibility on primary flow, no offline handling on a critical screen, no error feedback on a core action. |
| **P2** | Should fix soon. Quality, maintainability or risk debt that compounds. | Deprecated APIs in active code, weak test coverage on logic, ad-hoc logging without categories. |
| **P3** | Nice to have. Polish, consistency, future-proofing. | Inconsistent spacing tokens, naming drift, redundant computed properties. |

---

## 3. Quality dimensions

Every dimension follows the same structure:

- **What we audit** — scope of the dimension.
- **Why it matters** — one sentence on the consequence of getting it wrong.
- **AI-typical risks** — stable IDs from `AI_RISK_CATALOG.md`.
- **Signals & checks** — concrete things to look for.
- **Operationalized by** — the agent, skill, or status in the plugin.
- **Backing references** — the industry sources that support this dimension.

Status legend for **Operationalized by**:

- `agent: <name>` — implemented today by an existing auditor agent.
- `skill: <name>` — implemented by a consultative skill.
- `planned: <name>` — declared but not yet implemented.
- `out-of-plugin-scope (manual)` — recognized as part of app quality but
  not auditable by this plugin; requires human review.

### 3.1 Product fit & boundaries

- **What we audit** — scope statement, target user, value proposition,
  alignment with the App Store category, presence of speculative features,
  dead code from earlier directions.
- **Why it matters** — a beautifully built irrelevant feature is still
  waste, and unscoped features are a common cause of App Review rejection.
- **AI-typical risks** — `AI-3.1-001`.
- **Signals & checks** — explicit out-of-scope statements; no code paths
  for features outside the spec; feature flags documented and owned;
  App Store category and description match the actual app.
- **Operationalized by** — `out-of-plugin-scope (manual)`.
- **Backing references** — Apple App Review Guidelines (Business, Design).

### 3.2 Architecture & modularity

- **What we audit** — layering, module boundaries, dependency direction,
  public surfaces, presence of cycles, separation of UI/domain/data.
- **Why it matters** — architecture is what lets the app evolve at scale
  and multiple people work on it without breaking each other.
- **AI-typical risks** — `AI-3.2-001`, `AI-3.2-002`.
- **Signals & checks** — views do not know about persistence or network
  directly; no cyclic dependencies; minimal stable public interfaces;
  cross-cutting concerns injected, not imported everywhere.
- **Operationalized by** — `agent: architecture-auditor`.
- **Backing references** — Swift by Sundell (architecture & modularization);
  ISO/IEC 25010:2023 — Maintainability.

### 3.3 Domain model integrity

- **What we audit** — meaningful types, enforced invariants, value vs
  reference semantics, identifiers, codable correctness, error types.
- **Why it matters** — a weak model leaks complexity into every feature
  that touches it.
- **AI-typical risks** — `AI-3.3-001`.
- **Signals & checks** — typed identifiers, not raw `String`; value types
  where appropriate; typed errors at boundaries; no "stringly typed" enums.
- **Operationalized by** — `agent: architecture-auditor` (extension).
- **Backing references** — Swift by Sundell (model design).

### 3.4 State, concurrency & data races

- **What we audit** — actor isolation, `@MainActor` placement, Sendable
  conformance, task lifecycle, cancellation, threading correctness.
- **Why it matters** — data races corrupt state and crash users; they are
  the hardest class of bugs to reproduce.
- **AI-typical risks** — `AI-3.4-001`, `AI-3.4-002`.
- **Signals & checks** — Swift 6 mode considered or planned; data race
  warnings clean; long-running tasks have explicit cancellation; no
  `.main.async` band-aids covering an isolation problem.
- **Operationalized by** — `planned: concurrency-auditor`.
  Until then, partially covered by `agent: code-health-auditor`.
- **Backing references** — Donny Wals, Antoine van der Lee
  (Swift Concurrency); Apple Swift Concurrency documentation;
  ISO/IEC 25010:2023 — Reliability.

### 3.5 Reliability & error handling

- **What we audit** — error propagation, retries, recovery, offline
  behavior, edge cases, crash-free rate, defensive boundaries.
- **Why it matters** — real-world conditions are unreliable; users only
  remember the moment things broke.
- **AI-typical risks** — `AI-3.5-001`, `AI-3.5-002`.
- **Signals & checks** — errors surface to the user with actionable
  messaging; explicit retry/offline strategy on network failures;
  crash-free target defined; no swallowed errors in production paths.
- **Operationalized by** — `planned: reliability-auditor`.
- **Backing references** — ISO/IEC 25010:2023 — Reliability.

### 3.6 Security & privacy

- **What we audit** — secret storage, transport security, authentication,
  permissions, telemetry of sensitive data, App Transport Security,
  privacy manifest, tracking declarations.
- **Why it matters** — the legal and trust surface; failures here harm
  users directly and can pull the app from the store.
- **AI-typical risks** — `AI-3.6-001`, `AI-3.6-002`, `AI-3.6-003`.
- **Signals & checks** — secrets in Keychain, never in `UserDefaults` or
  source; no global ATS exceptions; privacy manifest present and accurate;
  tracking domains declared; analytics events reviewed for PII;
  permissions requested in context with clear purpose strings.
- **Operationalized by** — `planned: security-privacy-auditor`.
- **Backing references** — OWASP MASVS v2.1 (STORAGE, CRYPTO, AUTH,
  NETWORK, PLATFORM, PRIVACY); Apple App Review Guidelines (Safety, Legal);
  ISO/IEC 25010:2023 — Security.

### 3.7 Observability & telemetry

- **What we audit** — structured logging, log categories, crash reporting,
  performance metrics, traceability of incidents.
- **Why it matters** — you cannot fix or measure what you cannot see;
  observability is what turns user reports into actionable diagnostics.
- **AI-typical risks** — `AI-3.7-001`, `AI-3.7-002`.
- **Signals & checks** — `OSLog` with subsystem and category, not `print`;
  MetricKit (or equivalent) integrated; consistent log levels; no PII
  in logs.
- **Operationalized by** — `planned: observability-auditor`.
- **Backing references** — Apple OSLog and MetricKit documentation.

### 3.8 Testing strategy

- **What we audit** — test pyramid balance, coverage of logic vs UI,
  mocks/fixtures, snapshot tests, CI integration, test maintainability.
- **Why it matters** — tests are the only sustainable mechanism to evolve
  the app without regressions.
- **AI-typical risks** — `AI-3.8-001`, `AI-3.8-002`.
- **Signals & checks** — meaningful unit coverage on logic-heavy code;
  UI tests use page-object or equivalent abstraction; snapshot baselines
  reviewed when changed; tests run on CI as a gate.
- **Operationalized by** — `planned: testing-strategy-auditor`.
- **Backing references** — Apple Swift Testing documentation;
  ISO/IEC 25010:2023 — Functional Suitability.

### 3.9 CI/CD & release engineering

- **What we audit** — pipelines, gates, signing, environments, rollouts,
  release notes, hotfix path, branch protection.
- **Why it matters** — release engineering is what lets a team move fast
  safely; without it, every release becomes manual heroics.
- **AI-typical risks** — `AI-3.9-001`.
- **Signals & checks** — required gates explicitly required (merge gates,
  not informational); signing and provisioning automated and documented;
  hotfix and rollback paths exist and have been exercised; release notes
  generated or curated.
- **Operationalized by** — `agent: ci-cd-auditor` (applies `skill: ci-cd-checklist`).
- **Backing references** — ISO/IEC 25010:2023 — Maintainability, Flexibility.

### 3.10 Developer experience (DX)

- **What we audit** — setup time, tooling, scripts, internal documentation,
  onboarding, friction signals reported by the team.
- **Why it matters** — bad DX is a silent quality killer; it shows up
  later as shortcuts, missing tests and inconsistent style.
- **AI-typical risks** — `AI-3.10-001`.
- **Signals & checks** — single bootstrap command; README and
  `CONTRIBUTING` accurate; pre-commit/pre-push hooks present and useful;
  generated artifacts committed or reproducible.
- **Operationalized by** — `out-of-plugin-scope (manual)`.
- **Backing references** — Swift by Sundell (codebase ergonomics); team
  retrospectives.

### 3.11 Localization & internationalization

- **What we audit** — string catalogs, plurals, locale-aware formatting,
  RTL support, missing/unused keys, mixed-language test data.
- **Why it matters** — localization is correctness, not decoration; bad
  localization is visible to every non-default-locale user.
- **AI-typical risks** — `AI-3.11-001`, `AI-3.11-002`.
- **Signals & checks** — all user-visible strings come from a string
  catalog; plural rules defined where needed; locale-aware formatters;
  lint/script reporting missing or unused keys.
- **Operationalized by** — `planned: localization-auditor`.
- **Backing references** — Apple Localization documentation.

### 3.12 UX & UI quality

- **What we audit** — navigation, layout, feedback, visual consistency,
  use of design tokens, alignment with Apple HIG.
- **Why it matters** — this is the product the user actually touches; UI
  quality is perceived quality.
- **AI-typical risks** — `AI-3.12-001`, `AI-3.12-002`.
- **Signals & checks** — HIG compliance for navigation, modality, feedback;
  documented design system in use; composition uses real subviews, not
  computed properties; modern SwiftUI APIs (`NavigationStack`,
  `foregroundStyle`, `.tab`).
- **Operationalized by** — `agent: ux-accessibility-auditor`.
- **Backing references** — Apple Human Interface Guidelines;
  Paul Hudson — *What to fix in AI-generated Swift code*.

### 3.13 Accessibility

- **What we audit** — VoiceOver, Dynamic Type, contrast, reduce motion,
  hit areas, semantic traits, alternatives to gestures.
- **Why it matters** — legal requirement, ethical baseline, and a
  measurable expansion of the audience.
- **AI-typical risks** — `AI-3.13-001`, `AI-3.13-002`.
- **Signals & checks** — VoiceOver reaches and describes every interactive
  element; Dynamic Type does not break primary flows; color contrast meets
  WCAG 2.2 AA; gestures have button or keyboard alternatives.
- **Operationalized by** — `agent: ux-accessibility-auditor`.
- **Backing references** — Apple Accessibility documentation; WCAG 2.2;
  Paul Hudson on accessibility in SwiftUI.

### 3.14 Performance & energy

- **What we audit** — launch time, scrolling smoothness, memory footprint,
  network efficiency, energy and battery impact.
- **Why it matters** — perceived quality and retention; a slow app is
  uninstalled regardless of features.
- **AI-typical risks** — `AI-3.14-001`, `AI-3.14-002`.
- **Signals & checks** — cold launch budget defined; lists profile cleanly
  under Instruments; image assets sized for device; background and energy
  modes used appropriately.
- **Operationalized by** — `agent: performance-auditor`.
- **Backing references** — Apple performance documentation; MetricKit;
  ISO/IEC 25010:2023 — Performance Efficiency.

### 3.15 API freshness & deprecations

- **What we audit** — deployment target alignment, deprecated API usage,
  adoption of modern Swift/SwiftUI patterns.
- **Why it matters** — technical debt, App Store compliance, and the
  ability to ship for new iOS versions.
- **AI-typical risks** — `AI-3.15-001`, `AI-3.15-002`, `AI-3.15-003`,
  `AI-3.15-004`.
- **Signals & checks** — no deprecation warnings in active code; modern
  SwiftUI APIs in new files; deployment target consistent across modules;
  `@Observable`, `NavigationStack`, `foregroundStyle` are the default.
- **Operationalized by** — `agent: api-freshness-auditor`.
- **Backing references** — Paul Hudson — *What to fix in AI-generated
  Swift code* and *Teach your AI to write Swift the Hacking with Swift way*.

### 3.16 Code health & SOLID

- **What we audit** — function and type sizes, naming, cohesion, coupling,
  duplication, dead code, comment quality, lint compliance.
- **Why it matters** — code health is the running cost of the codebase;
  it shows up directly in lead time and incident frequency.
- **AI-typical risks** — `AI-3.16-001`, `AI-3.16-002`.
- **Signals & checks** — SwiftLint/SwiftFormat enforced on CI; function
  and type length distributions reviewed; SOLID violations flagged;
  no commented-out code; no narrative comments duplicating the code.
- **Operationalized by** — `agent: code-health-auditor`.
- **Backing references** — Swift by Sundell (code organization);
  ISO/IEC 25010:2023 — Maintainability.

---

## 4. What this specification measures

This specification is a measurement instrument. Every audit run produces
structured data so that the specification's own assumptions can be
validated against accumulated evidence over time.

The full output contract — Markdown report and JSON schema — lives in
[`AUDIT_OUTPUT_SPEC.md`](./AUDIT_OUTPUT_SPEC.md). The summary below
states what the plugin must emit, regardless of the specific format.

### 4.1 Per-audit outputs

For each audit run the plugin emits both:

- **A human-readable Markdown report** — executive summary, per-dimension
  findings, suggested remediation tasks, severity ranking.
- **A machine-readable JSON record** — same findings in structured form,
  including stable IDs, dimension references, AI-typical risk IDs, and
  evidence locators.

Both files are written to `.claude-marketplace-audits/` inside the
audited repository.

### 4.2 Per-finding fields

Each finding carries at minimum:

- A stable finding id.
- The dimension it belongs to (3.X).
- Severity (P0–P3).
- Evidence (files, lines, metrics, or logs).
- The `ai_typical` flag and, if true, the `ai_risk_id` from the catalog.
- Remediation suggestion.
- One or more backing references from Section 6.

### 4.3 Per-audit metrics

Every audit emits at least:

- Total findings.
- Findings by severity.
- Findings by dimension.
- Count and ratio of `ai_typical: true` findings.
- Audit duration.

### 4.4 Aggregated signals (optional, off-the-shelf)

When multiple audits are accumulated for a project (or across projects,
under the team's discretion), the following signals become available
without additional infrastructure:

- Top-N AI-typical risks by occurrence.
- Recurrence of specific risks across audits.
- Dimensions that consistently produce no findings — a signal for either
  weak detection or low real-world risk.
- Trend of severity distribution per dimension over time.

These signals are the input to Section 7.3 and the basis for promoting,
demoting, or rewording entries in `AI_RISK_CATALOG.md`.

---

## 5. Recording findings

Findings are produced in two paired forms (human and machine) as defined
in `AUDIT_OUTPUT_SPEC.md`. The human-readable form follows this template:

```text
ID:           <auditor>-<short-slug>
Dimension:    3.X — <Dimension name>
Severity:     P0 | P1 | P2 | P3
Evidence:     <files, lines, screenshots, metrics, logs>
AI-typical:   yes (<AI-3.X-NNN>) | no
Remediation:  <what to do, who, by when>
References:   <backing reference(s) from Section 6>
```

Notes:

- The `AI-typical` field is mandatory. When `yes`, the AI risk ID from the
  catalog is required. This is what enables aggregation and validation.
- `References` should point to the specific source from Section 6, not to
  the dimension itself.

---

## 6. References

Grouped by what they bring to this specification.

### Apple — platform truth

- **Human Interface Guidelines** — UX, navigation, modality, motion,
  iconography, accessibility primitives.
  https://developer.apple.com/design/human-interface-guidelines/
- **App Review Guidelines** — Safety, Performance, Business, Design, Legal.
  https://developer.apple.com/app-store/review/guidelines/
- **Accessibility documentation** — VoiceOver, Dynamic Type,
  AccessibilityTraits, semantic content.
  https://developer.apple.com/accessibility/
- **Swift Concurrency, Swift Testing, OSLog, MetricKit** — official
  documentation for the modern toolset.

### Mobile security & privacy

- **OWASP MASVS v2.1** — Mobile Application Security Verification Standard.
  Eight control groups: STORAGE, CRYPTO, AUTH, NETWORK, PLATFORM, CODE,
  RESILIENCE, PRIVACY.
  https://mas.owasp.org/MASVS/

### iOS / Swift industry references

- **Paul Hudson — Hacking with Swift**
  - *What to fix in AI-generated Swift code* — direct catalog of AI
    deviations in Swift/SwiftUI.
    https://www.hackingwithswift.com/articles/281/what-to-fix-in-ai-generated-swift-code
  - *Teach your AI to write Swift the Hacking with Swift way* — recipe
    for an `AGENTS.md` to steer AI tools.
    https://www.hackingwithswift.com/articles/284/teach-your-ai-to-write-swift-the-hacking-with-swift-way
- **John Sundell — Swift by Sundell** — architecture, modularization,
  domain modeling, sustainable codebases.
  https://www.swiftbysundell.com/
- **Donny Wals** — Swift 6 concurrency, isolation, Sendable.
  https://www.donnywals.com/
- **Antoine van der Lee** — Swift 6 migration tooling, concurrency
  patterns and pitfalls.
  https://www.avanderlee.com/

### General software quality (informational)

- **ISO/IEC 25010:2023** — software product quality model. Used here as
  cross-reference, not as the primary structure.
- **WCAG 2.2** — Web Content Accessibility Guidelines, used as
  cross-platform backing for accessibility criteria.

---

## 7. Status & roadmap

### 7.1 Current status (specification v0.1)

- This specification is the operational basis of `ios-audit-agents`.
  It is not externally validated and does not claim authority beyond the
  plugin.
- Engineering scope only. Product fit (3.1) and developer experience (3.10)
  are listed as `out-of-plugin-scope (manual)` to make the boundary
  explicit but are not auditable by this plugin.
- The catalog of AI-typical risks
  ([`AI_RISK_CATALOG.md`](./AI_RISK_CATALOG.md)) starts deliberately small
  with cited entries first; heuristic entries are marked as such until
  evidence accumulates.

### 7.2 Coverage snapshot

| 3.X | Dimension | Operationalized by |
|---|---|---|
| 3.1 | Product fit & boundaries | `out-of-plugin-scope (manual)` |
| 3.2 | Architecture & modularity | `agent: architecture-auditor` |
| 3.3 | Domain model integrity | `agent: architecture-auditor` (extension) |
| 3.4 | State, concurrency & data races | `planned: concurrency-auditor`, partially `agent: code-health-auditor` |
| 3.5 | Reliability & error handling | `planned: reliability-auditor` |
| 3.6 | Security & privacy | `planned: security-privacy-auditor` |
| 3.7 | Observability & telemetry | `planned: observability-auditor` |
| 3.8 | Testing strategy | `planned: testing-strategy-auditor` |
| 3.9 | CI/CD & release engineering | `agent: ci-cd-auditor` (`skill: ci-cd-checklist`) |
| 3.10 | Developer experience | `out-of-plugin-scope (manual)` |
| 3.11 | Localization & i18n | `planned: localization-auditor` |
| 3.12 | UX & UI quality | `agent: ux-accessibility-auditor` |
| 3.13 | Accessibility | `agent: ux-accessibility-auditor` |
| 3.14 | Performance & energy | `agent: performance-auditor` |
| 3.15 | API freshness & deprecations | `agent: api-freshness-auditor` |
| 3.16 | Code health & SOLID | `agent: code-health-auditor` |

### 7.3 How evidence flows back into this specification

This specification is updated only when accumulated audit data justifies
it. A typical update cycle:

1. Aggregate the JSON outputs in `.claude-marketplace-audits/` from one
   or more projects (Section 4.4).
2. Review which AI-typical risks have been observed, how often, and at
   which severities.
3. Update `AI_RISK_CATALOG.md`:
   - Promote heuristic risks to "common knowledge" when they are observed
     consistently across projects.
   - Demote or remove risks that never appear, or reword them if their
     manifestation differs from what was hypothesized.
4. Adjust dimensions in this specification only if the data shows a
   structural gap (a recurring class of finding that does not fit any
   dimension) or structural redundancy (two dimensions that always
   co-occur).
5. Bump the specification version (Section 7.1) and record the change
   in a changelog entry.

This specification does not change with opinion. It changes with
evidence.

### 7.4 Path to a community reference (deferred)

Promoting this specification to a public reference in the future would
require:

- A citation pass on every AI-typical risk in `AI_RISK_CATALOG.md`,
  separating cited / common knowledge / framework heuristic.
- An explicit comparative analysis with ISO/IEC 25010, OWASP MASVS, Apple
  HIG and App Review Guidelines.
- A reproducible empirical protocol: running audits on a defined set of
  AI-assisted and non-AI-assisted iOS samples, then measuring whether the
  AI-typical-risk hypothesis holds.

This is deferred. This specification aims first to be a useful
instrument; any external claim follows from the data, not from this
document.
