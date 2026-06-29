# Capital Deployment Engine

Version: v2.1 Alpha

## Mission

Capital Deployment Engine (CDE) upgrades Atlas from a decision system into a capital allocation
system.

Atlas should not only decide whether a thesis remains valid. Atlas should also decide:

- Whether capital deployment is allowed today.
- How much additional capital may be deployed today.
- Which deployment stage is active.
- How much Dry Powder remains.
- What conditions unlock the next deployment stage.

CDE never predicts prices.

CDE manages deployment rhythm.

## Architecture Position

```text
World Model
 ↓
Decision Engine
 ↓
Capital Deployment Engine
 ↓
Portfolio
 ↓
Execution
```

CDE does not replace Decision Engine.

CDE does not replace Portfolio.

CDE consumes the decision result and converts it into capital deployment authority.

Portfolio consumes CDE output and translates it into allocation state.

Execution consumes Portfolio action and records what happened.

## Responsibilities

CDE owns:

1. Whether capital deployment is allowed today.
2. Maximum deployment authority for today.
3. Current deployment stage.
4. Remaining Dry Powder.
5. Unlock conditions for the next deployment stage.

CDE does not own:

- World Model hierarchy.
- Seven Layer Reasoning.
- Decision Engine state machine.
- Portfolio Rules.
- Trade execution.
- Price prediction.

## Deployment Stages

| Stage | Name | Meaning | Default Authority |
|---|---|---|---|
| Stage 0 | Observe | Thesis may be valid, but deployment is not allowed today. | 0% |
| Stage 1 | Initial Deployment | First controlled capital deployment is allowed. | Small |
| Stage 2 | Deep Pullback | Additional deployment is allowed after stronger price dislocation and unchanged thesis. | Medium |
| Stage 3 | Maximum Opportunity | Highest deployment authority is allowed when world model, evidence, risk budget, and dry powder all align. | High |

Progression must depend on evidence and portfolio conditions, not price alone.

## Deployment Score

Deployment Score ranges from 0 to 100.

It explains why deployment authority is granted.

It is not a prediction of price direction.

Suggested dimensions:

| Dimension | Question | Read |
|---|---|---|
| World Model Stability | Has the relevant World Model node changed or weakened? | Stable / Strengthening / Weakening / Unknown |
| Fundamental Evidence | Is there evidence of fundamental deterioration or confirmation? | Positive / Neutral / Negative / Unknown |
| Price Dislocation | Is the price move large relative to thesis and risk? | Low / Medium / High |
| Portfolio Exposure | Is current exposure within allowed range? | Low / Balanced / High / Excessive |
| Dry Powder | Is enough dry powder available after today? | Adequate / Tight / Insufficient |
| Market Risk | Is market-wide risk blocking deployment? | Low / Medium / High |

## Score Bands

| Score | Deployment Read | Allowed Action |
|---|---|---|
| 0-39 | Deployment blocked | Observe / Hold |
| 40-59 | Limited authority | Hold / small Accumulate only if unlock rules pass |
| 60-79 | Controlled authority | Accumulate within daily authority |
| 80-100 | High authority | Accumulate up to stage authority, never automatic |

## Capital Authority

Authority is the maximum additional capital allowed today.

Authority is not a mandatory action.

Authority must be expressed as a percentage of the relevant account or bucket, not money.

Forbidden:

- Exact account value.
- Net worth.
- Currency amount.
- Balance.
- Cost.
- Market value.
- Position amount.

Required output:

```text
Capital Deployment Dashboard

Deployment Score:
Deployment Stage:
Today’s Maximum Authority:
Executed Today:
Remaining Dry Powder:
Next Unlock Stage:
Unlock Conditions:
```

## Unlock Rules

Every deployment stage must define explicit unlock conditions.

Allowed unlock conditions include:

- World Model unchanged.
- World Model strengthening.
- No fundamental deterioration.
- Evidence quality improved.
- Additional price dislocation.
- Risk budget available.
- Portfolio exposure below threshold.
- Dry Powder remains above required minimum after deployment.
- Portfolio Consistency Check passes.

Forbidden unlock logic:

- Price down alone.
- FOMO.
- Rumor.
- Unverified X post.
- Need to recover loss.
- Mandatory deployment because authority exists.

## Stage Unlock Examples

### Stage 0 -> Stage 1

Unlock only if:

- World Model is unchanged or strengthening.
- No fundamental deterioration.
- Portfolio Consistency Check passes.
- Dry Powder is adequate.
- Price dislocation exists or initial thesis deployment is planned.

### Stage 1 -> Stage 2

Unlock only if:

- Stage 1 has been executed or intentionally skipped with review.
- World Model remains unchanged or strengthening.
- No new fundamental deterioration.
- Additional price dislocation appears.
- Portfolio exposure remains below threshold.
- Remaining Dry Powder stays above minimum reserve after deployment.

### Stage 2 -> Stage 3

Unlock only if:

- Evidence quality is medium or high.
- World Model remains stable or strengthens under stress.
- Market risk does not block deployment.
- Risk budget remains available.
- Portfolio exposure remains within maximum allowed range.
- User confirms maximum opportunity authority.

## Daily CDE Decision

Every daily decision that touches capital should answer:

```text
Is deployment allowed today?
What is the maximum authority?
What stage are we in?
How much has been executed today?
How much Dry Powder remains?
What unlocks the next stage?
```

If any required input is `Unknown`, CDE should reduce authority or block deployment.

## Portfolio Consumption

Portfolio consumes CDE output.

Portfolio may not exceed CDE authority.

Portfolio may choose to deploy less than CDE authority.

Portfolio must still pass:

- Portfolio Consistency Check.
- Privacy rules.
- Account / bucket / holding allocation rules.

## Execution Boundary

CDE does not execute trades.

CDE authorizes maximum deployment rhythm.

Execution records what was actually done.

## Privacy Boundary

CDE is allocation-based.

CDE may use:

- Percentage authority.
- Deployment Stage.
- Dry Powder percentage.
- Risk budget status.
- Exposure status.

CDE must not use:

- Exact total assets.
- Account balances.
- Currency amounts.
- Net worth.
- Cost basis.
- Market value.
- Position amount.

## No Automatic Trading Rule

CDE authority is permission, not instruction.

Even when CDE grants authority, the final action must remain:

```text
Research / Observe / Build / Accumulate / Hold / Reduce / Exit
```

No `Buy` / `Sell` language.

No automatic trading.
