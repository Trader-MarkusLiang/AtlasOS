# IP-2026-017 — Market Data Provider Setup v0.1

## Category

Market Data / Research / Strategic Candidate Dashboard / CDE Support

## Origin

ISSUE-2026-017 — Market Data Provider Not Configured

## Problem

Market Data Fetch Gate v0.1 can determine when market data is required, but Atlas could not use
real local market data because providers were not installed or configured.

## Root Cause

Atlas had a gate and limitation language, but no minimum local provider setup for A-share, Hong
Kong, or US / ETF symbols.

## Expected Improvement

Install and validate minimum local market data providers so Atlas can fetch current and historical
market data for:

- A-share.
- Hong Kong stocks.
- US / ETF symbols where ticker mapping exists.

## Affected Modules

- `tools/market_data/`
- `99_Verification/validate_market_data_provider.py`
- `99_Verification/Market_Data_Provider_Validation_Result.md`
- `99_Verification/Audit_Report_Market_Data_Provider_Setup.md`
- `99_Verification/Regression_Tests.md`

## Provider Priority

| Market | Primary Provider | Fallback |
|---|---|---|
| A-share | akshare | yfinance if available |
| Hong Kong | akshare | yfinance |
| US / ETF | yfinance | None |

## Minimum Interface

```python
get_latest_quote(ticker: str, market: str) -> dict
get_history(ticker: str, market: str, period: str = "60d") -> pandas.DataFrame
get_market_snapshot(ticker: str, market: str) -> dict
```

The returned snapshot includes:

- Ticker.
- Market.
- Source.
- Timestamp.
- Latest price.
- Daily change %.
- Volume.
- Turnover when available.
- 5D / 20D / 60D change.
- 20D / 60D moving average.
- Optional valuation fields.
- Data status.
- Missing fields.

## Priority

P1

## Status

Implemented

## Validation Result

`99_Verification/Market_Data_Provider_Validation_Result.md`

Final decision:

```text
PARTIAL
```

## Compatibility

This setup adds a provider utility only. It does not modify strategy logic, CDE logic, Decision
Brief strategy logic, Strategic Candidate Dashboard logic, Portfolio Rules, private portfolio data,
or trading execution.
