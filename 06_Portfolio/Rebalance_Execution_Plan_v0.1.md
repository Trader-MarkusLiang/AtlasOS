# Rebalance Execution Plan v0.1

Rebalance Execution Plan is an optional Atlas output layer for rebalance, switching, migration,
cash redeployment, and domestic account repositioning questions.

It is not automatic trading.

It is not a new Engine.

It does not modify CDE formulas.

Execution Plan is not Trading Authority. CDE authorization and user confirmation are still
required.

## Trigger Conditions

Use this template only when the user asks about:

- 调仓.
- 换仓.
- 快速调仓.
- 仓位迁移.
- 现金部署.
- 重新部署.
- Old holdings vs new candidates.
- Whether to migrate 30%-40% position.
- What to receive after reducing a position.
- 国内账户怎么重新布局.
- 当前哪些该减，哪些该接.

## Required Prechecks

1. Portfolio Context Injection.
2. Market Data Fetch Gate.
3. Domestic Market Snapshot for China / Hong Kong names.
4. Data Anomaly Check before execution sizing.
5. CDE boundary.
6. Research Priority is not Trading Authority.
7. Execution Readiness is not Trading Authority.
8. Migration Authority is not mandatory action.
9. User confirmation is required for any actual trade.

## Compact Decision Brief Block

```text
Rebalance Plan Required: YES / NO
Migration Authority: 0-5% / 5-10% / 10-20% / 20-40% / 40%+
Reason:
Limits:
Next Trigger:
```

## 1. Rebalance Context

Required fields:

| Field | Content |
|---|---|
| User Intent | Rebalance / switch / cash redeployment / position migration |
| Account Scope | Account involved |
| Current Deployment / Cash | If available and consistent |
| Current Holdings Involved | Holdings under review |
| Candidate Pool Involved | Candidate receiving pool |
| Domestic Market Snapshot Status | Available / Partial / Missing |
| Data Anomaly Check Status | Normal / Warning / Severe / Unknown |
| CDE Boundary | CDE authorized / CDE Precision Limited / CDE not authorized |

## 2. Current Holding Assessment

| Holding | Role | Current Structure | Execution Readiness | Anomaly Status | Portfolio Role | Suggested Treatment |
|---|---|---|---|---|---|---|

Allowed Suggested Treatment:

- Hold Core.
- Hold / Watch.
- Reduce Risk.
- Trim if Extended.
- No Action.
- Data Limited.

Do not use Buy / Sell language.

## 3. Candidate Receiving Assessment

| Candidate | Research Tier | Market Structure | Execution Readiness | Anomaly Status | Portfolio Fit | Receiving Priority |
|---|---|---|---|---|---|---|

Allowed Receiving Priority:

- Not Ready.
- Watch.
- Pullback Candidate.
- Breakout Confirmation Candidate.
- Pilot Deployment Candidate.
- Data Limited.

Receiving Priority is not trade authority.

## 4. Migration Authority

Migration Authority describes whether capital can be migrated from current holdings / cash into
candidates if CDE allows.

Migration Authority is not CDE Authority.

Migration Authority is not mandatory action.

| Band | Meaning |
|---|---|
| 0-5% | No meaningful rebalance; watch only |
| 5-10% | Light adjustment |
| 10-20% | Controlled rebalance |
| 20-40% | Active rebalance |
| 40%+ | Major reconstruction; requires explicit user confirmation |

Rules:

- If Domestic Snapshot is Available and no severe anomaly, Atlas may suggest a migration band.
- If anomaly Warning exists, max migration band should usually be capped at 10-20%.
- If anomaly Severe exists, migration authority must be 0-5% or blocked.
- If CDE Precision Limited, do not give aggressive migration band.
- If portfolio context is stale / inconsistent, migration authority must be blocked.

## 5. Execution Tiers

| Tier | Condition | Action Vocabulary | Max Scope | Stop Condition |
|---|---|---|---|---|
| Tier 0 | No CDE, severe anomaly, stale data, or portfolio conflict | Observe / Hold | 0-5% | Any severe stop condition |
| Tier 1 | Warning anomaly or extended structure | Observe / Hold / Reduce | 5-10% | Anomaly worsens or CDE not authorized |
| Tier 2 | CDE and market confirmation align | Build / Accumulate / Reduce | 10-20% | Confirmation fails |
| Tier 3 | Strong evidence + CDE + user confirmation | Build / Accumulate / Reduce | 20-40% | User does not confirm or risk rises |

Allowed action vocabulary:

- Observe.
- Hold.
- Reduce.
- Build.
- Accumulate.

Do not use Buy / Sell.

## 6. Stop Conditions

- Data anomaly severe.
- Market structure deterioration.
- Price gap too extended.
- Volume confirmation failure.
- CDE not authorized.
- Portfolio exposure conflict.
- Thesis evidence weakens.
- User does not confirm execution.

## 7. Follow-up Triggers

- Pullback to MA20 / MA60.
- Breakout confirmation.
- Volume confirmation.
- Candidate relative strength improves.
- Current holding overextension eases.
- CDE authority improves.
- New fundamental evidence.
- Market risk declines.

## 8. Post-Action Review

If the user executes a rebalance, Atlas should later request or record:

- Intended action.
- Actual action.
- Reason.
- Market context.
- Execution quality.
- Missed opportunity / avoided risk.
- Whether World Model / CDE / Portfolio rules need update.

Do not store private amounts.
