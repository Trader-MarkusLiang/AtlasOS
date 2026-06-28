# Decision Review

Decision Review closes the loop after an action, a rejected action, or a deliberate no-action
decision reaches its review trigger.

Review is mandatory because Atlas improves by comparing thesis with reality.

## Review Trigger

Review begins when one of the following occurs:

- A planned review date arrives.
- Earnings, order, pricing, margin, backlog, or capex evidence appears.
- A risk threshold is triggered.
- A position action is executed.
- A decision is invalidated.
- A signal is rejected and archived.

## Review Template

| Field | Required Question |
|---|---|
| Decision ID / Topic | What decision is being reviewed? |
| Original Thesis | What did Atlas believe at the time? |
| Original Evidence | What evidence supported the thesis? |
| Original Action | Research / Observe / Build / Accumulate / Hold / Reduce / Exit |
| Reality | What actually happened? |
| Wrong | What did Atlas get wrong? |
| Right | What did Atlas get right? |
| Unexpected | What happened that Atlas did not model? |
| Lessons | What should future decisions remember? |
| Database Update | Which database, case, current-state, or risk file should change? |
| Framework Change? | Yes / No |
| Framework Change Reason | If Yes, what evidence justifies architecture review? |
| Next Review | What date or event forces the next review? |

## Review Rules

- A profitable result does not prove the thesis was correct.
- A losing result does not prove the thesis was wrong.
- Review must compare the original thesis to reality, not rewrite the thesis after the fact.
- If facts changed, update the relevant Atlas record.
- If the framework appears wrong, mark `Framework Change?` as Yes and route to Architecture.
- If no durable learning exists, archive the decision without forcing a database change.

## Database Update Rule

Database updates must specify the target:

| Target | Use When |
|---|---|
| `02_Databases/Alpha_Radar.md` | Signal quality or promotion status changed. |
| `02_Databases/Risk_Radar.md` | A risk appeared, changed severity, or invalidated a thesis. |
| `02_Databases/Order_Book.md` | Order, capacity, backlog, shipment, utilization, or qualification evidence changed. |
| `02_Databases/Price_Transmission.md` | Revenue, margin, FCF, capex, or pricing transmission changed. |
| `02_Databases/AI_Shovel_100.md` | Company priority, thesis, confidence, or review trigger changed. |
| `04_Current_State/` | Bottleneck rank, capital map, or current strategy changed. |
| `05_Cases/` | A reusable case study should be preserved. |

## Archive Rule

A decision can be archived only after:

1. Review is complete.
2. Database update need is resolved or marked unnecessary.
3. Next review is recorded or explicitly not needed.
