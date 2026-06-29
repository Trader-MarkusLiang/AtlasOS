# Proposal Template

Every durable knowledge update must begin as a Knowledge Proposal.

Proposal is generated first. Merge happens only after review.

## Proposal Schema

| Field | Content |
|---|---|
| Proposal ID | KP-YYYY-NNN |
| Target Database | Pattern / Case / Alpha Radar / Order Book / Risk Radar / Price Transmission / AI Shovel 100 / Current State / Other |
| Reason | Why should Atlas update knowledge? |
| Evidence | Evidence packet, source, or internal note |
| Confidence | Low / Medium / High / Very High |
| Pattern | Existing Pattern, candidate Pattern, or `Unknown` |
| Case | Existing Case, candidate Case, or `Unknown` |
| Need Review | YES / NO |
| Suggested Action | Research / Observe / Merge / Reject / Archive |
| Review Result | Pending / Approved / Rejected / Needs more evidence |
| Merge Result | Not merged / Merged / Archived |

## Proposal Rules

- Crawler output cannot modify databases directly.
- Daily notes cannot become durable knowledge without Proposal.
- If Pattern is unknown, mark `Unknown`.
- If Evidence is unverified, mark `Unverified`.
- Proposal must identify whether the target is Signal, Evidence, Case, or Pattern.
- Repository sync can merge only reviewed proposals.

## Proposal Outcome

| Outcome | Meaning |
|---|---|
| Merge | Knowledge is durable enough to enter repository. |
| Reject | Evidence or reasoning failed. |
| Archive | Signal did not become reusable knowledge. |
| Needs more evidence | Keep in research workflow. |
