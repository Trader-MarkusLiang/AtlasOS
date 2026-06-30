# Audit Report — Domestic Market Data Support v0.2

Date: 2026-06-30

## Executive Summary

What was added:

- `ISSUE-2026-019` for incomplete domestic market data support.
- `IP-2026-019` for Domestic Market Data Support v0.2.
- `tools/market_data/domestic_market_snapshot.py`.
- `99_Verification/validate_domestic_market_snapshot.py`.
- `99_Verification/Domestic_Market_Snapshot_Result.md`.
- Ticker registry entries for 太极实业, 广钢气体, and 昊华科技.
- Regression Case 15.

Current domestic market data status:

```text
DOMESTIC READY
```

China / Hong Kong account data readiness:

- Current domestic holdings have quote, 60D history-derived fields, volume, MA20 / MA60, market
  structure, execution readiness, and data freshness.
- A-share candidates and Hong Kong candidates tested in this upgrade have domestic snapshots.
- Missing turnover and valuation fields are marked optional and do not block readiness.

Remaining limitations:

- Current provider source is yfinance in this environment.
- Akshare endpoints remain subject to network / proxy availability.
- Turnover / amount and valuation fields remain optional when unavailable.
- Execution Readiness is not Trading Authority; CDE authorization is still required.
- DRAM ETF ticker mapping remains outside domestic readiness.

## Provider Result

Akshare status:

- Installed.
- Attempted first by the underlying provider for A-share / Hong Kong.
- Current validation fell back to yfinance, indicating akshare endpoint access is not the active
  successful source in this run.

Yfinance fallback status:

- Available for all tested current domestic holdings.
- Available for all tested A-share candidates.
- Available for all tested Hong Kong candidates.

Missing fields:

- Turnover / amount: optional missing for yfinance-backed snapshots.
- Valuation: optional and not part of domestic readiness gate.

## Domestic Holdings Result

| Holding | Market | Source | Quote / History / Volume / MA | Structure | Readiness | Freshness | Status |
|---|---|---|---|---|---|---|---|
| 雅克科技 | A-share | yfinance | Available | Overextended | Wait for Pullback | Fresh | Available |
| 建滔集团 | HK | yfinance | Available | Strong Uptrend | Wait for Pullback | Fresh | Available |
| 东山精密 | A-share | yfinance | Available | Strong Uptrend | Wait for Breakout Confirmation | Fresh | Available |
| 泰金新能 | A-share | yfinance | Available | Strong Uptrend | Wait for Pullback | Fresh | Available |

## Candidate Result

### A-share Candidates

| Candidate | Market | Source | Quote / History / Volume / MA | Structure | Readiness | Freshness | Status |
|---|---|---|---|---|---|---|---|
| 赛腾股份 | A-share | yfinance | Available | Overextended | Wait for Pullback | Fresh | Available |
| 澜起科技 | A-share | yfinance | Available | Strong Uptrend | Wait for Pullback | Fresh | Available |
| 江丰电子 | A-share | yfinance | Available | Overextended | Wait for Pullback | Fresh | Available |
| 太极实业 | A-share | yfinance | Available | Overextended | Wait for Pullback | Fresh | Available |
| 广钢气体 | A-share | yfinance | Available | Overextended | Wait for Pullback | Fresh | Available |
| 昊华科技 | A-share | yfinance | Available | Overextended | Wait for Pullback | Fresh | Available |

### Hong Kong Candidates

| Candidate | Market | Source | Quote / History / Volume / MA | Structure | Readiness | Freshness | Status |
|---|---|---|---|---|---|---|---|
| 中芯国际 | HK | yfinance | Available | Strong Uptrend | Wait for Pullback | Fresh | Available |
| 长飞光纤光缆 | HK | yfinance | Available | Strong Uptrend | Wait for Breakout Confirmation | Fresh | Available |

## Rule Explanation

### `market_structure_status`

Allowed values:

- Strong Uptrend.
- Mild Uptrend.
- Range / Consolidation.
- Pullback.
- Breakdown Risk.
- Overextended.
- Data Insufficient.

Rule basis:

- Price vs MA20 / MA60.
- 20D / 60D change.
- Distance from 20D / 60D highs and lows.
- Volume ratio vs 20D average when available.

This classification is not price prediction and must not be presented as a buy / sell signal.

### `execution_readiness`

Allowed values:

- No Action.
- Watch.
- Wait for Pullback.
- Wait for Breakout Confirmation.
- Pilot Deployment Candidate.
- Reduce Risk Candidate.
- Data Insufficient.

Rule basis:

- Uses market structure, data status, freshness, and price gap from MA20.
- It is only an input to Decision Brief / Strategic Candidate Dashboard / CDE / Rebalance review.
- It is not Trading Authority.
- CDE authorization is still required.

### `data_freshness`

Allowed values:

- Fresh.
- Delayed.
- Stale.
- Unknown.

Rule basis:

- Current local date timestamp: Fresh.
- Recent prior timestamp: Delayed.
- Older timestamp: Stale.
- Missing or ambiguous timestamp: Unknown.

The rule is conservative and avoids overclaiming exchange-calendar precision.

## Decision Integration Guidance

Decision Brief, Strategic Candidate Dashboard, CDE, and Rebalance review may use Domestic Market
Snapshot as input for:

- Market Confirmation.
- Technical Status.
- Price Dislocation.
- Execution Risk.
- Waiting Triggers.
- Rebalance Readiness.

They must still obey:

- Research Priority is not Trading Authority.
- Market Structure is not price prediction.
- Execution Readiness is not Trading Authority.
- CDE authorization is still required.
- If data is Partial, output `CDE Precision Limited`.
- If data is stale or unavailable, avoid strong execution advice.

## Safety Verification

| Rule | Result |
|---|---|
| No CDE modification | PASS |
| No Decision Brief strategy logic modification | PASS |
| No `portfolio.local.yaml` modification | PASS |
| No allocation percentage modification | PASS |
| No private amount / cost / net worth / account balance stored | PASS |
| No new Engine created | PASS |
| No automatic trading | PASS |
| Missing turnover / valuation does not fail snapshot | PASS |

## Final Decision

```text
DOMESTIC READY
```
