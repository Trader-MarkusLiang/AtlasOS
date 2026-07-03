# ISSUE-2026-021 — Market Regime Early Warning Missing

## Status

Open / Accepted

## Origin

Production Trial / A-share Breakdown Review

## Date First Seen

2026-07-03

## Date Last Seen

2026-07-03

## Frequency

1

## Affected Area

Decision Brief / CDE / Portfolio / Rebalance / Market Data / UX

## Problem

Atlas OS can flag extreme instrument-level movement and cap rebalance migration authority, but it
does not yet produce a complete market-regime early warning when a broad domestic technology market
move becomes fragile.

During the A-share breakdown review, prior Atlas outputs already warned:

- `Severe` anomaly.
- `Execution Blocked`.
- Migration authority capped at `0-5%`.

However, the warning was execution-level only. It did not classify the broader market regime or
explain whether the market had shifted from strong risk-on to fragile uptrend, distribution warning,
risk-off, or crash stress.

## Context

Production Trial observed an extreme domestic technology rally followed by a sharp pullback. The
existing Domestic Market Snapshot, Data Anomaly Check, Rebalance Execution Plan, Portfolio Context
Injection, and CDE boundary were useful, but they operated mainly on holdings / candidates and
execution authority.

## Impact

High

This can affect:

- Decision quality.
- Capital discipline.
- Rebalance timing.
- User trust during fast market transitions.
- CDE precision when broad market conditions deteriorate.

## Evidence

Prior warning evidence:

- `99_Verification/Domestic_Market_Snapshot_Result.md` showed multiple current holdings and
  candidates in `Overextended` or `Strong Uptrend` structures with extreme 20D / 60D moves.
- `99_Verification/Rebalance_Execution_Plan_Test_Result.md` showed aggregate anomaly `Severe`,
  decision impact `Execution Blocked`, and migration authority cap `0-5%`.
- `99_Verification/Rebalance_Execution_Plan_Production_Trial_Exam.md` validated the same boundary.

Latest review evidence:

- `99_Verification/Ashare_Market_Breakdown_Early_Warning_Review.md` found current aggregate anomaly
  remains `Severe`, but Atlas lacks a market-regime warning layer.

## Root Cause Hypothesis

Atlas currently checks market data at the holding / candidate / rebalance execution level. It does
not yet aggregate those signals into a domestic market-regime state using index behavior, breadth,
sector diffusion, candidate-pool anomaly concentration, holding breakdown ratio, and sentiment
overheating.

## Possible Solutions

- Add market-regime status as a future issue-driven improvement.
- Track index-level trend and drawdown.
- Track breadth deterioration and sector diffusion.
- Track anomaly concentration across the candidate pool.
- Track current holdings structural deterioration.
- Integrate regime state into CDE precision and Rebalance Authority caps.
- Keep the output lightweight and decision-first.

## Priority

P1

## Decision

Discuss / Convert to Improvement Proposal

## Linked IP

IP-2026-021 — Market Regime Early Warning v0.1

## Notes

This issue does not implement a new Engine, does not modify CDE formulas, does not modify Decision
Brief strategy logic, does not modify portfolio allocation, and does not authorize automatic
trading.
