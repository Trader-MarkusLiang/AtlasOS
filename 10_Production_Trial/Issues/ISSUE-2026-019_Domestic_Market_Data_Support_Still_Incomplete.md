# ISSUE-2026-019 — Domestic Market Data Support Still Incomplete

## Status

Open / Accepted

## Origin

Production Trial / Market Data Provider v0.1 / User Request

## Date First Seen

2026-06-30

## Date Last Seen

2026-06-30

## Frequency

1

## Affected Area

Market Data / Strategic Candidate Dashboard / CDE / Rebalance / Decision Brief / Domestic Portfolio

## Problem

Atlas OS can now fetch basic quote and history for many China / Hong Kong tickers, but domestic
market data support is still incomplete for execution-oriented decision inputs.

Current gaps include:

- Akshare endpoints may fail under current network / proxy.
- Turnover / amount is often missing from yfinance-backed data.
- Valuation fields are optional and often missing.
- Market data freshness is not yet explicitly classified.
- Domestic data is not yet structured into execution-useful indicators.
- Atlas cannot yet produce a strong Rebalance / CDE / execution recommendation based on secondary
  market data quality alone.

## Context

Market Data Provider v0.1 established basic provider access. The next production-trial need is a
structured domestic snapshot that exposes trend, moving-average, volume, turnover, freshness, and
classification fields without changing strategy logic.

## Impact

High

This limits Atlas' ability to judge:

- Capital market confirmation.
- Price dislocation.
- Trend structure.
- Volume / turnover confirmation.
- Pullback vs breakdown.
- Breakout vs overextension.
- Candidate relative strength.
- Current holding weakness / strength.
- Staged rebalance timing.
- CDE precision for domestic account.

## Evidence

Provider validation showed China / Hong Kong quote and history can often be fetched, but turnover,
valuation, freshness, and market-structure fields remain incomplete or unstructured.

## Root Cause Hypothesis

The existing provider utility returns basic market snapshots. Atlas needs a richer domestic
decision-input layer, not a new trading engine or strategy formula.

## Possible Solutions

- Add domestic snapshot utility under `tools/market_data/`.
- Add rule-based market structure and execution readiness classifications.
- Add data freshness classification.
- Keep missing turnover / valuation as optional missing fields.
- Preserve CDE and strategy logic unchanged.

## Priority

P1

## Decision

Open / Accepted

## Linked IP

IP-2026-019 — Domestic Market Data Support v0.2

## Notes

This issue is market data support only. It does not authorize trading action, rebalance action,
automatic execution, or CDE formula changes.
