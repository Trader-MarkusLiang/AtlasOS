# IP-2026-019 — Domestic Market Data Support v0.2

## Category

Market Data / Domestic Portfolio / CDE Support / Rebalance Support

## Origin

ISSUE-2026-019 — Domestic Market Data Support Still Incomplete

## Problem

Atlas can fetch basic China / Hong Kong quote and history data for many tickers, but the data is
not yet structured enough to support domestic market confirmation, technical status, price
dislocation, execution risk, or rebalance readiness.

## Root Cause

Market Data Provider v0.1 exposes basic snapshots. Domestic decision inputs need derived trend,
moving-average, high / low, volume, turnover, freshness, market structure, and execution-readiness
fields while keeping strategy logic unchanged.

## Expected Improvement

Upgrade domestic market data support from basic quote / history retrieval to a structured
secondary-market snapshot for China / Hong Kong holdings and candidates.

## Affected Modules

- `tools/market_data/domestic_market_snapshot.py`
- `tools/market_data/README.md`
- `tools/market_data/ticker_registry.yaml`
- `99_Verification/validate_domestic_market_snapshot.py`
- `99_Verification/Domestic_Market_Snapshot_Result.md`
- `99_Verification/Audit_Report_Domestic_Market_Data_Support_v0.2.md`
- `99_Verification/Regression_Tests.md`

## Scope

- Add `get_domestic_market_snapshot(ticker: str, market: str) -> dict`.
- Add rule-based market structure classification.
- Add execution readiness classification as decision input only.
- Add data freshness classification.
- Add validation report for domestic holdings and candidates.

## Out of Scope

- No strategy logic change.
- No CDE formula change.
- No Decision Brief strategy logic change.
- No automatic trading.
- No dashboard.
- No new Engine.
- No private portfolio data.

## Priority

P1

## Status

Implemented

## Compatibility

This IP adds a market data utility only. Research Priority remains different from Trading
Authority. Market Structure is not price prediction. Execution Readiness is not Trading Authority.
CDE authorization is still required.
