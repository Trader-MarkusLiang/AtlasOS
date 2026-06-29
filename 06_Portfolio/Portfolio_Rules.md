# Portfolio Rules

## Portfolio Principle

Atlas manages capital allocation, not wealth.

Atlas 管理的是资本配置，而不是财富规模。

Portfolio analysis must focus on:

- Weight
- Exposure
- Thesis
- Risk

Portfolio analysis must not focus on account money amount.

## Privacy Rule

Atlas never knows:

- Total assets.
- RMB amount.
- USD amount.
- Account balance.
- Net worth.
- Market value.
- Position amount.
- Cost basis.
- Currency balance.

Atlas only knows Allocation.

Git-tracked portfolio files may store only percentage weights, exposure, thesis, conviction, capital
action, and review metadata. Real local portfolio files must stay ignored by Git.

## Position Lifecycle

```text
Research
 ↓
Watch
 ↓
Build Position
 ↓
Increase
 ↓
Hold
 ↓
Reduce
 ↓
Exit
 ↓
Review
```

## Capital Action Vocabulary

Use only:

- Research
- Observe
- Build
- Accumulate
- Hold
- Reduce
- Exit

Do not use:

- Buy
- Sell

Reason:

> Action must be tied to position state and capital allocation, not treated as an isolated order.

## Conviction

- Low
- Medium
- High
- Very High

## Priority

- S
- A
- B

## Review Frequency

- Daily
- Weekly
- Monthly
- Quarterly

## Traceability Rule

Every portfolio action must trace back to:

1. Living Database evidence.
2. Trading OS reasoning.
3. Portfolio allocation and exposure state.
4. Execution Log review when a trade occurs.
