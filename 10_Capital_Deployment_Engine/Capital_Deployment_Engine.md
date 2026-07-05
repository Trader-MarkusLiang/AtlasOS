# Capital Deployment Engine

Version: v2.1 RC

## Mission

Capital Deployment Engine (CDE) upgrades Atlas from a decision system into a capital allocation
system.

Atlas should not only decide whether a thesis remains valid. Atlas should also decide:

- Whether capital deployment is allowed today.
- How much additional capital may be deployed today.
- Which deployment lifecycle stage is active.
- How much Dry Powder remains.
- What conditions unlock the next deployment stage.

CDE never predicts prices.

CDE manages deployment rhythm.

## Run First Principle

Atlas evolves from real investment decisions, not imagined features.

Atlas 的成长来自真实投资决策，而不是不断增加功能。

v2.1 RC freezes major architecture expansion. CDE should become more usable every trading day
before Atlas adds any new engine.

## Explainability Standard

CDE explanations should be concise and decision-first.

Every Deployment Score, Authority, and Deployment Lifecycle output should answer:

1. What is the current decision?
2. Why is this the decision?
3. What limits this decision?
4. What could change this decision?

Do not expose unnecessary implementation detail in the default Decision Brief.

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
3. Current deployment lifecycle stage.
4. Remaining Dry Powder.
5. Unlock conditions for the next deployment stage.

CDE does not own:

- World Model hierarchy.
- Seven Layer Reasoning.
- Decision Engine state machine.
- Portfolio Rules.
- Trade execution.
- Price prediction.

## Deployment Lifecycle

CDE uses lifecycle stages instead of simple numbered stages.

```text
Observe
 ↓
Pilot Deployment
 ↓
Initial Deployment
 ↓
Scaling
 ↓
Maximum Opportunity
 ↓
Capital Preservation
```

| Lifecycle Stage | Meaning | Default Authority |
|---|---|---|
| Observe | Thesis may be valid, but deployment is not allowed today. | 0% |
| Pilot Deployment | Small test deployment is allowed to start exposure or verify execution quality. | Very Small |
| Initial Deployment | First controlled deployment is allowed after thesis, evidence, consistency, and dry powder pass. | Small |
| Scaling | Additional deployment is allowed after evidence quality, price dislocation, and portfolio room improve. | Medium |
| Maximum Opportunity | Highest deployment authority is allowed only when world model, evidence, risk, exposure, and dry powder all align. | High |
| Capital Preservation | Deployment slows or stops because exposure, dry powder, liquidity, or market risk requires preservation. | 0% / Reduce only if needed |

Progression must depend on evidence and portfolio conditions, not price alone. Regression to
Observe or Capital Preservation is allowed whenever evidence weakens, portfolio consistency fails,
or strategic cash needs protection.

## Deployment Score

Deployment Score ranges from 0 to 100.

It must explain why deployment authority is granted.

It is not a prediction of price direction.

Every Deployment Score must expose its composition.

| Component | Max Score | Question | Read |
|---|---:|---|---|
| World Model Stability | 25 | Has the relevant World Model node changed or weakened? | Stable / Strengthening / Weakening / Unknown |
| Evidence Quality | 20 | Is evidence confirming the thesis or showing deterioration? | High / Medium / Low / Unknown |
| Price Dislocation | 20 | Is the price move large relative to thesis and risk? | Low / Medium / High |
| Portfolio Exposure | 15 | Is current exposure within allowed range? | Low / Balanced / High / Excessive |
| Dry Powder | 10 | Is enough dry powder available after today? | Adequate / Tight / Insufficient |
| Market Risk | 10 | Is market-wide risk blocking deployment? | Low / Medium / High |

Required format:

```text
Deployment Score
68 / 100

World Model Stability
24 / 25

Evidence Quality
16 / 20

Price Dislocation
15 / 20

Portfolio Exposure
8 / 15

Dry Powder
3 / 10

Market Risk
2 / 10

Reason:
- World Model stable.
- Large price dislocation.
- Portfolio already highly deployed.
- Preserve strategic cash.

Limits:
- Dry Powder is limited.
- Portfolio exposure is already high.

Could Change:
- Evidence quality improves.
- Market risk falls.
- Portfolio exposure is reduced.
```

The score is invalid if it is only a single number.

## Score Bands

| Score | Deployment Read | Allowed Action |
|---|---|---|
| 0-39 | Deployment blocked | Observe / Hold |
| 40-59 | Limited authority | Hold / small Accumulate only if unlock rules pass |
| 60-79 | Controlled authority | Accumulate within daily authority |
| 80-100 | High authority | Accumulate up to lifecycle authority, never automatic |

## Capital Authority

Authority is the maximum additional capital allowed today.

Authority is not a mandatory action.

Authority must be expressed as a percentage of the relevant account or bucket, not money.

Authority must always explain its origin.

Required format:

```text
Today’s Authority
6%

Derived From

Deployment Score
68

Deployment Lifecycle
Initial Deployment

Dry Powder
24%

Execution Risk
Medium

Reason:
Deployment authority is limited by portfolio exposure and remaining strategic cash.

Could Change:
Authority may increase if evidence quality improves, market risk falls, or exposure room improves.
```

Authority is invalid if it does not show the score, lifecycle stage, dry powder, execution risk,
and reason.

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
Deployment Lifecycle:
Today’s Authority:
Derived From:
  Deployment Score:
  Deployment Lifecycle:
  Dry Powder:
  Execution Risk:
Executed Today:
Remaining Dry Powder:
Next Lifecycle Stage:
Unlock Conditions:
```

## Unlock Rules

Every deployment lifecycle stage must define explicit unlock conditions.

Allowed unlock conditions include:

- World Model unchanged.
- World Model strengthening.
- No fundamental deterioration.
- Evidence quality improved.
- Additional price dislocation.
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

## Lifecycle Unlock Examples

### Observe -> Pilot Deployment

Unlock only if:

- World Model is unchanged or strengthening.
- No fundamental deterioration.
- Portfolio Consistency Check passes.
- Dry Powder is adequate.
- Price dislocation exists or initial thesis deployment is planned.

### Pilot Deployment -> Initial Deployment

Unlock only if:

- Pilot Deployment has been executed or intentionally skipped with review.
- World Model remains unchanged or strengthening.
- No new fundamental deterioration.
- Additional price dislocation appears.
- Portfolio exposure remains below threshold.
- Remaining Dry Powder stays above minimum reserve after deployment.

### Initial Deployment -> Scaling

Unlock only if:

- Evidence quality is medium or high.
- World Model remains stable or strengthens under stress.
- Portfolio exposure remains within allowed range.
- Dry Powder remains available after the proposed action.
- Execution risk is not high.

### Scaling -> Maximum Opportunity

Unlock only if:

- Evidence quality is medium or high.
- World Model remains stable or strengthens under stress.
- Market risk does not block deployment.
- Portfolio exposure remains within maximum allowed range.
- User confirms maximum opportunity authority.

### Any Stage -> Capital Preservation

Move to Capital Preservation if:

- Portfolio exposure becomes excessive.
- Remaining Dry Powder falls below required strategic reserve.
- Liquidity or execution risk becomes high.
- Market risk blocks deployment.
- Evidence quality deteriorates.
- Portfolio Consistency Check fails.

## Daily CDE Decision

Every daily decision that touches capital should answer:

```text
Is deployment allowed today?
What is the maximum authority?
What lifecycle stage are we in?
How much has been executed today?
How much Dry Powder remains?
What unlocks the next lifecycle stage?
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
- Deployment Lifecycle.
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

## Improvement Proposal Standard

Improvement Proposal IDs must be globally unique.

Use:

```text
IP-YYYY-NNN
```

Example:

```text
IP-2026-001
Category: Capital Deployment
```

Do not encode module names in the ID. Use `Category` as an independent field.

Supported categories:

- Knowledge
- World Model
- Decision Engine
- Portfolio
- Capital Deployment
- User Experience
- Engineering

## Roadmap

Atlas roadmap stages:

| Stage | Meaning |
|---|---|
| Released | Production-ready capability. |
| Current | Actively under refinement. |
| Planned | Architecture approved but intentionally not implemented. |
| Ideas | Interesting concepts or proposed architectures waiting for validation / approval. |
| Deprecated | Historical capability retained only for traceability. |

Current roadmap:

### Released

- Seven Layer Reasoning.
- Decision Engine.
- World Model.
- Portfolio OS.
- Daily Operating Cycle.
- Decision First user experience.

### Current

- Run First v2.1 RC.
- Explainable Capital Deployment Engine.
- Deployment Lifecycle.
- Authority Explainability.
- Market Data Fetch Gate.
- Market Data Provider v0.1 / Domestic Market Data Support v0.2.
- Data Anomaly Check.
- Rebalance Execution Plan v0.1.

### Planned

The following modules are planned future milestones only.

They are not implemented in v2.1 RC:

| Future Milestone | Status | Rule |
|---|---|---|
| Risk Budget Engine | Planned | Do not implement before real CDE operation exposes the need. |
| Execution Governance Engine | Planned | Do not implement before repeated execution problems are observed. |
| Performance Attribution | Planned | Do not implement before enough completed decisions exist for review. |
| Meta Learning Engine | Planned | Do not implement before long-term case history exists. |

Future engines must come from observed operating problems, not imagined architecture gaps.

### Ideas

| Idea / Proposed Architecture | Status | Boundary |
|---|---|---|
| Market Regime Early Warning v0.1 | Proposed Architecture | `IP-2026-021`; not implemented. |
| Attention-Flow Market Transition System v0.1 | Proposed Architecture | `IP-2026-022`; no runtime code. |
| Runtime System v0.1 | Issue Recorded / Watching | `ISSUE-2026-023`; no runtime scheduler, orchestrator, event engine, state store, or output generator. |

Ideas are not implementation approval.

Runtime or engine-like work requires Issue discussion, Architecture Review, Acceptance Test
definition, and explicit user approval before coding.

### Deprecated

| Deprecated Concept | Replaced By | Reason |
|---|---|---|
| Old Stage Model | Deployment Lifecycle | Lower explainability and weaker daily operating clarity. |
