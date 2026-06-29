# Knowledge Distillation

Knowledge Distillation defines how Atlas turns daily information into durable knowledge.

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
| Knowledge Merge | Reviewed knowledge is merged into the repository. | Pattern, Case, database update, or archive note. |
| Repository | Git records the merge. | Commit as Knowledge Merge. |

## Distillation Rules

- Do not write Signal directly into a database as durable knowledge.
- Do not treat news volume as conviction.
- Evidence can validate, reject, or modify a Signal.
- Reasoning must come before Pattern Extraction.
- Pattern Extraction must ask whether logic is reusable across companies, industries, or cycles.
- Case Generation must include outcome and lessons, not just thesis.
- Case is the validator of Pattern.
- Pattern is the main subject of Knowledge.
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

## Theory Boundary

Theory is not created in daily operation.

Theory can emerge only after multiple Patterns survive multi-year, cross-industry, and cross-cycle
validation with predictive value.
