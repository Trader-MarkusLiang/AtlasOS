# ISSUE-2026-017 — Market Data Provider Not Configured

## Status

Open / Accepted

## Origin

Production Trial / Market Data Fetch Gate Acceptance Test

## Date First Seen

2026-06-30

## Date Last Seen

2026-06-30

## Frequency

1

## Affected Area

Market Data / Strategic Candidate Dashboard / CDE / Rebalance / Decision Brief / Execution

## Problem

Atlas OS can detect when market data is required, but local providers for A-share and Hong Kong
stock data may not be installed or configured.

This limits Atlas's ability to evaluate:

- Latest price.
- Daily change.
- Volume / turnover.
- K-line status.
- Valuation risk.
- Price dislocation.
- Market confirmation.
- Rebalance timing.
- CDE precision.

## Context

Market Data Fetch Gate v0.1 is implemented as a safety gate. It prevents Atlas from inventing
market-sensitive fields when data is unavailable. Production Trial now needs to verify whether the
local environment has a real provider that can satisfy the gate.

## Impact

High

If market data providers are unavailable, Atlas must repeatedly output:

```text
Market Data Missing or Unavailable — Decision Limited
```

This is safe, but weakens real trading usefulness.

## Evidence

Local package audit on 2026-06-30 found:

- `pandas`: installed.
- `numpy`: installed.
- `requests`: installed.
- `yfinance`: missing.
- `akshare`: missing.
- `beautifulsoup4`: missing.
- `lxml`: missing.
- `pandas_market_calendars`: missing.

Repository search found no existing Atlas market data provider, adapter, or cached market data
layer.

## Root Cause Hypothesis

Atlas added the Market Data Fetch Gate before a local provider was configured. The gate correctly
limits decisions, but current provider capability is not yet sufficient for A-share / Hong Kong
market data retrieval.

## Possible Solutions

- Install and configure `akshare` as the minimum viable A-share / Hong Kong data provider.
- Add `yfinance` as a fallback, especially for Hong Kong tickers where Yahoo symbols are reliable.
- Treat valuation fields as optional and source-dependent.
- Keep real-time / intraday fast rebalance limited until provider freshness and reliability are
  validated.

## Priority

P1

## Decision

Accepted

## Linked IP

None

## Notes

This issue records provider availability only. It does not request a new Engine, provider adapter,
market data cache, crawler, API, strategy change, CDE change, or portfolio modification.
