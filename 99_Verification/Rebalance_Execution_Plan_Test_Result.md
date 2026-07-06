# Rebalance Execution Plan Test Result

Generated: 2026-07-06T23:41:34

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
| 雅克科技 | Data Insufficient | Data Missing | Data Missing | Data Missing | Severe | Execution Blocked | latest_price_missing_or_non_positive; history_too_short_for_ma60; timestamp_freshness_unknown |
| 建滔集团 | Data Insufficient | Data Missing | Data Missing | Data Missing | Severe | Execution Blocked | latest_price_missing_or_non_positive; history_too_short_for_ma60; timestamp_freshness_unknown |
| 东山精密 | Mild Uptrend | 1.38 | 105.91 | -7.49 | Normal | None | None |
| 泰金新能 | Mild Uptrend | -5.07 | 312.10 | -7.07 | Severe | Execution Blocked | abs_60d_change_pct |
| 赛腾股份 | Strong Uptrend | 38.61 | 110.80 | 6.49 | Normal | None | None |
| 澜起科技 | Strong Uptrend | 12.24 | 110.07 | 2.67 | Normal | None | None |
| 江丰电子 | Strong Uptrend | 62.46 | 119.06 | 5.92 | Normal | None | None |
| 太极实业 | Overextended | 70.10 | 211.82 | 21.77 | Warning | CDE Precision Limited | abs_60d_change_pct |
| 广钢气体 | Strong Uptrend | 60.57 | 92.07 | 18.90 | Normal | None | None |
| 昊华科技 | Strong Uptrend | 47.71 | 106.52 | 4.45 | Normal | None | None |

## Current Holding Assessment

| Holding | Role | Current Structure | Execution Readiness | Anomaly Status | Portfolio Role | Suggested Treatment |
| --- | --- | --- | --- | --- | --- | --- |
| 雅克科技 | Current Holding | Data Insufficient | Data Insufficient | Severe | Existing exposure | Data Limited |
| 建滔集团 | Current Holding | Data Insufficient | Data Insufficient | Severe | Existing exposure | Data Limited |
| 东山精密 | Current Holding | Mild Uptrend | Watch | Normal | Existing exposure | Hold Core |
| 泰金新能 | Current Holding | Mild Uptrend | Watch | Severe | Existing exposure | Data Limited |

## Candidate Receiving Assessment

| Candidate | Research Tier | Market Structure | Execution Readiness | Anomaly Status | Portfolio Fit | Receiving Priority |
| --- | --- | --- | --- | --- | --- | --- |
| 赛腾股份 | Needs Strategic Candidate Dashboard | Strong Uptrend | Wait for Breakout Confirmation | Normal | Needs portfolio fit review | Breakout Confirmation Candidate |
| 澜起科技 | Needs Strategic Candidate Dashboard | Strong Uptrend | Wait for Breakout Confirmation | Normal | Needs portfolio fit review | Breakout Confirmation Candidate |
| 江丰电子 | Needs Strategic Candidate Dashboard | Strong Uptrend | Wait for Breakout Confirmation | Normal | Needs portfolio fit review | Breakout Confirmation Candidate |
| 太极实业 | Needs Strategic Candidate Dashboard | Overextended | Wait for Pullback | Warning | Needs portfolio fit review | Pullback Candidate |
| 广钢气体 | Needs Strategic Candidate Dashboard | Strong Uptrend | Wait for Pullback | Normal | Needs portfolio fit review | Pullback Candidate |
| 昊华科技 | Needs Strategic Candidate Dashboard | Strong Uptrend | Wait for Breakout Confirmation | Normal | Needs portfolio fit review | Breakout Confirmation Candidate |

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
