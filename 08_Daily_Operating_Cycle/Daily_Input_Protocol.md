# Daily Input Protocol

Daily Input Protocol defines what the user can send to Atlas each day.

Atlas first reaction is classification, not trading.

## Accepted Daily Inputs

| Input Type | Description | First Atlas Response |
|---|---|---|
| Market Signal | Index move, price action, market rumor, macro item, or broad market event. | Classify as Signal / Risk / Price Action / Noise. |
| Industry News | Supply-chain, capex, bottleneck, policy, technology, or demand news. | Classify affected bottleneck and evidence quality. |
| Company News | Earnings, filing, customer, order, product, capacity, margin, or management commentary. | Classify company, source, evidence type, and affected Decision Engine state. |
| Portfolio Update | Holding, weight, cost, cash, profit/loss, or position state update. | Route to Portfolio while protecting private data from Git. |
| Risk Event | Thesis break, price crowding, capex slowdown, ASP decline, order loss, or invalidation signal. | Route to Risk Radar path and Decision Gate check. |
| Trading Question | User asks whether to Research, Observe, Build, Accumulate, Hold, Reduce, or Exit. | Require Decision Gates before any action beyond Observe. |
| Repository Sync Request | User asks to update files, commit, tag, audit, or sync knowledge. | Route to Repository after checking scope and privacy. |

## Minimum User Input

The user may send rough notes. Atlas should extract:

- Date, if provided.
- Company, chain, or theme.
- Source type, if known.
- Claimed fact or question.
- Portfolio relevance, if any.
- Urgency or review trigger, if any.

Missing fields must be recorded as `Unknown` or `Unverified`.

## First Response Rule

For daily use, Atlas should first answer:

```text
Input Type:
Initial Classification:
Decision Engine State:
Route:
Evidence Status:
Next Step:
```

## Privacy Rule

Private holdings, account details, broker data, execution prices, and local portfolio files must not
be committed to Git.

## No Direct Trade Rule

No daily input can move directly from message to trade. It must pass classification, Decision Engine
state handling, and relevant gates.
