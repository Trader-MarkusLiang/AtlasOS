# ISSUE-2026-018 — Current Holding Ticker Mapping Incomplete

## Status

Open / Accepted

## Origin

Production Trial / Market Data Provider Setup

## Date First Seen

2026-06-30

## Date Last Seen

2026-06-30

## Frequency

1

## Affected Area

Market Data / Portfolio / Strategic Candidate Dashboard / CDE / Rebalance / Decision Brief

## Problem

Some current holdings do not have executable ticker mappings, preventing Atlas from fetching market
data for current portfolio holdings.

Known unresolved mappings:

- DRAM ETF.

Potential naming normalization issue:

- 建韬集团 / 建滔集团.

## Context

Market Data Provider v0.1 can fetch quotes and history for mapped A-share and Hong Kong symbols.
However, Market Data Fetch Gate cannot fully support Current Holdings Market Data Status until
every current holding either has a validated ticker mapping or an explicit `Needs Manual Mapping`
status.

## Impact

High

Incomplete ticker mapping limits:

- Current Holdings Market Data Status.
- Strategic Candidate Dashboard.
- CDE precision.
- Rebalance decisions.
- Market confirmation.
- K-line / technical status.

## Evidence

Provider smoke test on 2026-06-30 found:

- 雅克科技: mapped and fetchable.
- 建滔集团: mapped and fetchable; `建韬集团` retained as alias.
- 东山精密: mapped and fetchable.
- 泰金新能: ticker mapping confirmed by user on 2026-06-30 as `688813`, A-share, SH /
  科创板, with `akshare: 688813` and `yfinance: 688813.SS`.
- DRAM ETF: `Needs Manual Mapping`.

## Root Cause Hypothesis

Portfolio records can use human-readable holding names while provider calls require executable
tickers. Some current holdings were originally recorded as thematic descriptions or with uncertain
legacy mapping.

## Possible Solutions

- Confirm exact executable ticker for DRAM ETF.
- Keep registry aliases for naming variants such as 建韬集团 / 建滔集团.
- Do not force-map uncertain symbols.

## Priority

P1

## Decision

Open / Accepted

## Linked IP

None

## Notes

This issue is data infrastructure only. It does not modify portfolio allocation, strategy logic,
CDE, Decision Brief strategy logic, or execution.
