# Portfolio Rules

## Portfolio Principle

Atlas manages capital allocation, not wealth.

Atlas 管理的是资本配置，而不是财富规模。

Atlas is wealth-blind, but scale-aware.

Atlas 不感知具体财富金额，但感知资金规模层级。

Portfolio analysis must focus on:

- Weight
- Exposure
- Thesis
- Risk

Portfolio analysis must not focus on account money amount.

## Capital Scale Principle

Atlas does not care how much money the user has.

Atlas cares what level of complexity the capital requires.

Capital Scale Tier is not wealth ranking. It is Capital Management Complexity.

Scale tiers are abstract management bands. They may be used to judge allocation complexity,
execution complexity, liquidity sensitivity, review cadence, and risk-budget discipline. They must
not be used to record exact assets, account values, balances, net worth, or currency amount.

| Tier | Reference Band | Capital Management Complexity |
|---|---|---|
| S0 | `<5万` | Simple personal allocation |
| S1 | `5万-20万` | Basic allocation discipline |
| S2 | `20万-100万` | Position sizing and thesis review required |
| S3 | `100万-500万` | Multi-position exposure management required |
| S4 | `500万-2000万` | Liquidity and execution planning required |
| S5 | `2000万-1亿` | Advanced exposure, cash, and execution control required |
| S6 | `1亿-5亿` | Institutional-style liquidity and risk-budget discipline required |
| S7 | `5亿-20亿` | Portfolio construction and execution complexity dominates |
| S8 | `>20亿` | Capital movement may affect execution, liquidity, and strategy design |

These bands exist only for complexity classification. Git-tracked files must store only the tier,
not the user's exact asset value.

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
action, review metadata, and abstract scale-awareness fields:

- Capital Scale Tier.
- Management Mode.
- Execution Complexity.
- Liquidity Sensitivity.
- Risk Budget.

Real local portfolio files must stay ignored by Git.

## Portfolio Consistency Check

Consistency First.

All Portfolio Decisions must be based on internally consistent data. If any consistency rule fails,
Atlas must stop Portfolio Action and output:

```text
Portfolio Data Inconsistent
Need User Confirmation
```

Atlas must not auto-correct inconsistent portfolio data.

### Rule 1: Deployment + Cash Allocation

For each Account:

```text
Deployment + Cash Allocation = 100%
```

Example:

| Deployment | Cash Allocation | Result |
|---|---|---|
| 77% | 23% | PASS |
| 77% | 30% | FAIL |

### Rule 2: Bucket Exposure

For each Account, the sum of all Bucket Exposure must not exceed Deployment.

Example:

| Deployment | Bucket Exposures | Result |
|---|---|---|
| 77% | Memory 50% + AI Infrastructure 27% | PASS |
| 77% | Memory 60% + Infrastructure 40% | FAIL |

### Rule 3: Holding Weight

For each Bucket, the sum of all Holding Weight must equal Bucket Exposure.

Example:

| Bucket Exposure | Holding Weights | Result |
|---|---|---|
| 70% | MU 30% + DRAM ETF 40% | PASS |
| 70% | MU 30% + DRAM ETF 30% | FAIL |

### Rule 4: Account Allocation

If Global Portfolio is declared, the sum of all Account Weight must equal 100%.

If Global Portfolio is not declared, accounts may exist independently.

### Rule 5: Weight Precision

All weights must use percentage format with at most one decimal place.

Allowed:

- `25%`
- `25.5%`

Forbidden:

- `0.25`
- `25 percent`
- `四分之一`
- Mixed formats in the same Portfolio record.

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
