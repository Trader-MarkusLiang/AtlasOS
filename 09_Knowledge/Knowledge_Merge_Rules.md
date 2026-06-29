# Knowledge Merge Rules

Knowledge Merge is the repository act of accepting reusable reasoning into Atlas.

Commit represents Knowledge Merge, not News Archive.

From v2.0 Alpha, Knowledge Merge should ultimately update or preserve Atlas World Model.

Markdown is persistence. World Model is the knowledge object.

## Merge Requirements

Before merge, a Knowledge Proposal must include:

1. Proposal ID.
2. Target Database.
3. Reason.
4. Evidence.
5. Confidence.
6. Pattern or `Unknown`.
7. Case or `Unknown`.
8. Affected World Model Node or `Unknown`.
9. World Model Delta or `No World Model Change Today`.
10. Review Result.
11. Merge Result.

## Merge Targets

| Target | Merge Condition |
|---|---|
| World Model | Evidence, reasoning, and review show a node weight, confidence, trend, counter evidence, or waiting trigger changed. |
| Pattern | Reusable across companies, industries, or cycles and reviewed. |
| Case | Meets at least one Case upgrade criterion and includes outcome or review plan. |
| Alpha Radar | Signal remains useful but has not become Case or Pattern. |
| Order Book | Order, capacity, backlog, shipment, utilization, or qualification evidence is confirmed. |
| Risk Radar | Risk threshold, severity, or invalidation logic changed. |
| Price Transmission | Revenue, margin, ASP, FCF, capex, or pricing transmission changed. |
| AI Shovel 100 | Company instance mapping changed. |
| Current State | Bottleneck rank, capital map, or strategy state changed. |

## No Direct Write Rule

```text
Crawler / News / Signal
  cannot directly modify
Atlas Database
```

Required path:

```text
Signal -> Evidence -> Reasoning -> Proposal -> Review -> Merge
```

From v2.0 Alpha, durable merge path is:

```text
Signal -> Evidence -> Reasoning -> Review -> World Model Delta -> Knowledge Merge -> Repository
```

## Repository Responsibility

Repository owns:

- Knowledge Merge.
- Commit.
- Tag.
- Changelog.
- Audit records.

Repository does not own:

- Investment judgment.
- Pattern creation without review.
- Portfolio action.
- News archiving for its own sake.

Repository records World Model Merge. It does not replace World Model.

## Merge Decision

| Decision | Meaning |
|---|---|
| Merge | Durable knowledge accepted. |
| Defer | Evidence or review incomplete. |
| Reject | Reasoning failed or signal was noise. |
| Archive | Signal was useful temporarily but not reusable knowledge. |
