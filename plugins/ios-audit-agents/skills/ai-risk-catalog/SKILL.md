---
name: ai-risk-catalog
description: The ios-audit-agents AI Risk Catalog v0.1 — stable identifiers (AI-3.X-NNN) for AI-typical risks observed in AI-assisted iOS code, grouped by quality model dimension and tagged with a maturity status (cited / common knowledge / framework heuristic / retired). Use when an audit needs to attach an `ai_risk_id` to a finding flagged as `ai_typical: true`, decide whether a candidate risk already exists in the catalog, or interpret the maturity of a risk entry. Always paired with the quality-model skill (to map the risk to its 3.X dimension) and the audit-output-format skill (to emit the finding).
---

# AI Risk Catalog — v0.1

This skill is the consultative lens over the plugin's catalog of AI-typical risks. It tells an agent **which stable ID** to attach to a finding, **what status** that ID carries, and **how to look up entries**. It does not duplicate the catalog — the canonical source is `../../docs/AI_RISK_CATALOG.md` (English) and `../../docs/AI_RISK_CATALOG.es.md` (Spanish).

## Operating rules

- Read the canonical document **once per audit run** and reuse the loaded context for every finding in that run.
- The `ai_risk_id` field is required only when the finding has `ai_typical: true`. When `ai_typical: false`, the field is omitted.
- Always reuse an existing ID. Never invent a new ID inline in a finding.
- If a candidate finding clearly is AI-typical but no existing entry matches, set `ai_typical: true`, omit `ai_risk_id`, and surface the gap in the audit report's notes section so the catalog can be extended later. Do not block the audit on this.
- IDs from dimensions explicitly **out-of-plugin-scope** in `QUALITY_FRAMEWORK.md` Section 7.2 (today: `AI-3.1-001`, `AI-3.10-001`) MUST NOT be attached to findings. Those entries exist in the catalog for completeness but the plugin does not audit those dimensions.
- Retired IDs (`status: retired`) MUST NOT be attached to new findings. They are kept in the document for traceability only.
- The catalog's version is independent from both the quality model and the plugin. The catalog version (`v0.1`) is declared in the banner of `AI_RISK_CATALOG.md` and reaffirmed in its Changelog section.

## Topic router

| You need to know… | Section in `AI_RISK_CATALOG.md` |
|---|---|
| What the catalog is and how it relates to the quality model | Top banner + "How to read this catalog" |
| The identifier format `AI-3.X-NNN` and the rule that IDs are never reused | "Identifier scheme" |
| The four status values and what each one means | "Status values" |
| The fields every entry contains (Description, AI manifestation, Example, Sources) | "Entry shape" |
| All risks attached to a specific quality dimension | "Dimension 3.X — ..." |
| The current version of the catalog and what changed | "Changelog" |

## Identifier scheme (mirrors "Identifier scheme")

```text
AI-3.X-NNN
```

- `3.X` — quality dimension from the quality model (`3.1` through `3.16`).
- `NNN` — zero-padded sequential index inside that dimension.
- IDs are **stable forever**. A retired ID is kept with `status: retired`; the next new entry in that dimension takes the next number, never the retired one.

## Status quick reference (mirrors "Status values")

- **`cited`** — at least one explicit, public source describes this pattern as a recurring AI deviation.
- **`common knowledge`** — broadly agreed in the iOS community, no single canonical source, but consistently observed.
- **`framework heuristic`** — introduced by this catalog as a testable hypothesis. Will be promoted, reworded, or retired based on accumulated audit data.
- **`retired`** — no longer used. ID kept for traceability.

A finding does not need to filter by status. Status is metadata used by Section 7.3 of the quality model when evidence accumulates and the catalog is reviewed.

## Resolving a risk ID for a finding

1. Identify the dimension first (use the `quality-model` skill). The catalog is grouped by dimension, so this narrows the search to one section.
2. Skim the entries under `Dimension 3.X — …` and match by **AI manifestation** and **Example**, not by title alone — titles are short and several risks can sound similar.
3. If exactly one entry matches, attach its ID to the finding (`ai_risk_id: "AI-3.X-NNN"`).
4. If two entries plausibly match, prefer the more specific one (e.g. `AI-3.6-002 — App Transport Security relaxations` over `AI-3.6-001 — Hardcoded secrets or unsafe storage`).
5. If no entry matches and the finding still looks AI-typical, leave `ai_risk_id` out and add a note for catalog extension (see "Operating rules").

## Versioning

The catalog uses its own version (currently `v0.1`), declared in the banner of `AI_RISK_CATALOG.md` and in the "Changelog" section. Catalog updates are driven by accumulated audit evidence as described in `QUALITY_FRAMEWORK.md` Section 7.3 — promote heuristic risks to `common knowledge` when they are observed consistently, demote or rework risks that never appear, and add new entries when a recurring class of finding does not fit any existing one.

## Bilingual note

Both the English document (`AI_RISK_CATALOG.md`) and the Spanish document (`AI_RISK_CATALOG.es.md`) are authoritative and kept in sync. IDs are language-agnostic, so a finding that cites `AI-3.15-001` is valid against either file.
