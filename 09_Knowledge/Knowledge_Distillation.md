# Knowledge Distillation

Knowledge Distillation defines how Atlas turns daily information into durable knowledge.

From v2.0 Alpha, durable knowledge ultimately updates Atlas World Model.

## Distillation Flow

```text
Signal
 ↓
Evidence
 ↓
Reasoning
 ↓
Pattern Extraction
 ↓
Case Generation
 ↓
Pattern Validation
 ↓
World Model Update
 ↓
Knowledge Merge
 ↓
Repository
```

## Meaning

| Step | Meaning | Output |
|---|---|---|
| Signal | A market item enters Atlas. | Classified signal or archive. |
| Evidence | Signal is tested against verifiable records. | Evidence packet with `Unknown` / `Unverified` fields. |
| Reasoning | Evidence passes through Seven Layer Reasoning. | Layer change, bottleneck change, ROI path, capital flow, trading implication. |
| Pattern Extraction | Atlas asks whether the reasoning can repeat elsewhere. | Candidate Pattern or no pattern. |
| Case Generation | Atlas preserves a reusable decision episode. | Candidate Case if upgrade criteria are met. |
| Pattern Validation | Atlas checks whether the Case validates, refutes, or modifies a Pattern. | Pattern confidence update, counter example, or no validation. |
| World Model Update | Atlas checks which World Model Node changed. | World Model Delta or No World Model Change Today. |
| Knowledge Merge | Reviewed knowledge is merged into the repository. | World Model, Pattern, Case, database update, or archive note. |
| Repository | Git records the merge. | Commit as Knowledge Merge. |

## Distillation Rules

- Do not write Signal directly into a database as durable knowledge.
- Do not treat news volume as conviction.
- Evidence can validate, reject, or modify a Signal.
- Reasoning must come before Pattern Extraction.
- Pattern Extraction must ask whether logic is reusable across companies, industries, or cycles.
- Pattern must belong to a World Model Node.
- Case Generation must include outcome and lessons, not just thesis.
- Case is the validator of Pattern.
- Pattern is a component of World Model.
- World Model is the highest active knowledge structure.
- Knowledge Merge requires review.
- Theory does not participate in daily flow.
- Theory comes only from long-term operation.

## Daily Cycle Integration

Daily Operating Cycle should become:

```text
User Input
 ↓
Classification
 ↓
Research
 ↓
Decision Engine
 ↓
Knowledge Proposal
 ↓
Review
 ↓
World Model Delta
 ↓
Knowledge Merge
 ↓
Daily Report
 ↓
Repository Sync
```

## AI Shovel 100 Rule

AI Shovel 100 is a company instance map, not Atlas's highest knowledge layer.

Company records should point to Patterns when possible. If no reusable Pattern exists, the company
remains research evidence or watchlist material.

## World Model Rule

Database, Pattern, Case, Evidence, and Signal are components of Atlas World Model.

World Model is the true knowledge object. Markdown is persistent storage.

Signal does not change World Model by default. Only Evidence + Reasoning + Review can change World
Model.

## Theory Boundary

Theory is not created in daily operation.

Theory can emerge only after multiple Patterns survive multi-year, cross-industry, and cross-cycle
validation with predictive value.
