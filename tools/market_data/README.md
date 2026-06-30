# Market Data Provider Utility

Minimal market data utility for Atlas OS Production Trial.

This is a provider utility, not an Engine, trading system, crawler, cache, or automatic execution
layer.

## Providers

Provider priority:

| Market | Primary | Fallback |
|---|---|---|
| A-share | akshare | yfinance if available |
| Hong Kong | akshare | yfinance |
| US / ETF | yfinance | None |

## Install

```bash
python3 -m pip install --user akshare yfinance beautifulsoup4 lxml 'pandas_market_calendars<5'
```

`pandas_market_calendars<5` is used for compatibility with the system Python 3.9 runtime.

## Interface

```python
get_latest_quote(ticker: str, market: str) -> dict
get_history(ticker: str, market: str, period: str = "60d") -> pandas.DataFrame
get_market_snapshot(ticker: str, market: str) -> dict
```

Missing fields are returned as `None` and listed in `missing_fields`.

Valuation data is optional. Missing valuation data does not fail provider setup.

## Privacy

The ticker registry stores identity mapping only.

Do not store:

- Position size.
- Cost.
- Account value.
- Portfolio amount.
- Private execution data.
