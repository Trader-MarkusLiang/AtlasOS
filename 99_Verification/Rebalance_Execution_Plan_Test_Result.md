# Rebalance Execution Plan Test Result

Generated: 2026-06-30T23:56:19

## Scenario

User asks whether the domestic account can migrate 20%-40% exposure during a morning rebalance window, using current holdings, domestic snapshots, candidate ranking, and CDE boundary.

## Required Boundary

Execution Plan is not Trading Authority. CDE authorization and user confirmation are still required.

## Precheck Result

| Check | Result |
|---|---|
| Portfolio Context required | PASS |
| Domestic Market Snapshot required | PASS |
| Data Anomaly Check required | PASS |
| CDE boundary required | PASS |
| Strategic Candidate Ranking is not Trading Authority | PASS |
| Execution Readiness is not Trading Authority | PASS |

## Data Anomaly Check

- Aggregate anomaly status: Severe
- Decision impact: Execution Blocked
- Migration Authority cap from anomaly / CDE precision: 0-5%

| Name | Structure | 20D | 60D | MA20 Gap | Anomaly | Impact | Flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 雅克科技 | Overextended | 113.83 | 185.94 | 52.96 | Warning | CDE Precision Limited | abs_20d_change_pct; abs_60d_change_pct; price_vs_ma20_pct; price_vs_ma60_pct |
| 建滔集团 | Strong Uptrend | 96.86 | 253.86 | 17.26 | Severe | Execution Blocked | abs_60d_change_pct; abs_20d_change_pct; price_vs_ma60_pct |
| 东山精密 | Strong Uptrend | 36.82 | 153.97 | 8.83 | Warning | CDE Precision Limited | abs_60d_change_pct |
| 泰金新能 | Strong Uptrend | 29.01 | 324.50 | 14.19 | Severe | Execution Blocked | abs_60d_change_pct |
| 赛腾股份 | Overextended | 68.01 | 153.35 | 36.97 | Warning | CDE Precision Limited | abs_60d_change_pct |
| 澜起科技 | Strong Uptrend | 33.41 | 147.37 | 21.45 | Normal | None | None |
| 江丰电子 | Overextended | 96.00 | 165.30 | 31.53 | Warning | CDE Precision Limited | abs_20d_change_pct; abs_60d_change_pct |
| 太极实业 | Overextended | 115.36 | 227.13 | 48.11 | Warning | CDE Precision Limited | abs_20d_change_pct; abs_60d_change_pct; price_vs_ma20_pct; price_vs_ma60_pct |
| 广钢气体 | Overextended | 94.62 | 134.51 | 54.12 | Warning | CDE Precision Limited | abs_20d_change_pct; price_vs_ma20_pct |
| 昊华科技 | Overextended | 85.53 | 149.57 | 28.15 | Warning | CDE Precision Limited | abs_20d_change_pct |

## Current Holding Assessment

| Holding | Role | Current Structure | Execution Readiness | Anomaly Status | Portfolio Role | Suggested Treatment |
| --- | --- | --- | --- | --- | --- | --- |
| 雅克科技 | Current Holding | Overextended | Wait for Pullback | Warning | Existing exposure | Trim if Extended |
| 建滔集团 | Current Holding | Strong Uptrend | Wait for Pullback | Severe | Existing exposure | Data Limited |
| 东山精密 | Current Holding | Strong Uptrend | Wait for Breakout Confirmation | Warning | Existing exposure | Hold Core |
| 泰金新能 | Current Holding | Strong Uptrend | Wait for Pullback | Severe | Existing exposure | Data Limited |

## Candidate Receiving Assessment

| Candidate | Research Tier | Market Structure | Execution Readiness | Anomaly Status | Portfolio Fit | Receiving Priority |
| --- | --- | --- | --- | --- | --- | --- |
| 赛腾股份 | Needs Strategic Candidate Dashboard | Overextended | Wait for Pullback | Warning | Needs portfolio fit review | Pullback Candidate |
| 澜起科技 | Needs Strategic Candidate Dashboard | Strong Uptrend | Wait for Pullback | Normal | Needs portfolio fit review | Pullback Candidate |
| 江丰电子 | Needs Strategic Candidate Dashboard | Overextended | Wait for Pullback | Warning | Needs portfolio fit review | Pullback Candidate |
| 太极实业 | Needs Strategic Candidate Dashboard | Overextended | Wait for Pullback | Warning | Needs portfolio fit review | Pullback Candidate |
| 广钢气体 | Needs Strategic Candidate Dashboard | Overextended | Wait for Pullback | Warning | Needs portfolio fit review | Pullback Candidate |
| 昊华科技 | Needs Strategic Candidate Dashboard | Overextended | Wait for Pullback | Warning | Needs portfolio fit review | Pullback Candidate |

## Migration Authority

- Requested band: 20-40%
- Allowed validation band: 0-5%
- Reason: Data anomaly check detected extreme 20D / 60D moves and CDE Precision Limited applies.
- Migration Authority is not CDE Authority and not mandatory action.

## Execution Tiers

| Tier | Condition | Action Vocabulary | Max Scope | Stop Condition |
| --- | --- | --- | --- | --- |
| Tier 0 | Severe anomaly or no CDE | Observe / Hold | 0-5% | Execution blocked |
| Tier 1 | Warning anomaly or extended structure | Observe / Hold / Reduce | 5-10% | Anomaly worsens |
| Tier 2 | CDE and market confirmation align | Build / Accumulate / Reduce | 10-20% | Confirmation fails |
| Tier 3 | Strong evidence + CDE + user confirmation | Build / Accumulate / Reduce | 20-40% | User does not confirm |

## Stop Conditions

- Data anomaly severe.
- Market structure deterioration.
- Price gap too extended.
- Volume confirmation failure.
- CDE not authorized.
- Portfolio exposure conflict.
- Thesis evidence weakens.
- User does not confirm execution.

## Follow-up Triggers

- Pullback to MA20 / MA60.
- Breakout confirmation.
- Volume confirmation.
- Candidate relative strength improves.
- Current holding overextension eases.
- CDE authority improves.
- New fundamental evidence.
- Market risk declines.

## Post-Action Review

If the user executes a rebalance, Atlas should later request intended action, actual action, reason, market context, execution quality, missed opportunity / avoided risk, and whether World Model / CDE / Portfolio rules need update. Do not store private amounts.

## Acceptance Result

PASS
