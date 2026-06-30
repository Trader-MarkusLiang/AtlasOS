# ISSUE-2026-020 — Rebalance Execution Plan Missing

## Status

Open / Accepted

## Origin

Production Trial / Real Trading Feedback / Domestic Market Data Ready

## Date First Seen

2026-06-30

## Date Last Seen

2026-06-30

## Frequency

1

## Affected Area

Portfolio / CDE / Rebalance / Execution / Domestic Market Snapshot / Decision Brief

## Problem

Atlas OS can now produce portfolio context, strategic candidate ranking, CDE boundary, and domestic
market snapshots. However, it still lacks a structured rebalance execution plan when the user asks
about fast rebalance, position migration, cash redeployment, or switching from old holdings to new
candidates.

Without this layer, Atlas may:

- Stay too conservative and only say Observe / Hold.
- Produce research rankings without execution staging.
- Fail to distinguish strategic preference from actual execution readiness.
- Fail to explain how much position migration is allowed today.
- Fail to define stop conditions and follow-up triggers.

## Context

Domestic Market Data Support v0.2 reached `DOMESTIC READY`, so Atlas can now use domestic snapshot
data as a decision input. A rebalance plan still needs anomaly checks and CDE boundary language
before any migration guidance.

## Impact

High

This limits Atlas' usefulness in real trading windows, especially when:

- Cash has been released.
- Current holdings are overextended.
- New candidates are strong but extended.
- Domestic market data is available.
- The user needs staged execution guidance, not just research commentary.

## Evidence

Production Trial repeatedly involved domestic account rebalance, candidate receiving pool, and
cash redeployment questions after market data became available.

## Root Cause Hypothesis

Atlas has portfolio context, market data, and CDE boundary rules, but no optional output layer that
combines them into staged, non-automatic rebalance execution guidance.

## Possible Solutions

- Add Data Anomaly Check before execution sizing.
- Add Rebalance Execution Plan template.
- Add migration authority bands that are not CDE authority.
- Require CDE boundary and user confirmation.
- Add validation and regression coverage.

## Priority

P1

## Decision

Open / Accepted

## Linked IP

IP-2026-020 — Rebalance Execution Plan v0.1

## Notes

This issue does not authorize trades, change CDE formulas, or modify portfolio allocation files.
