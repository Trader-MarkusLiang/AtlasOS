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
get_domestic_market_snapshot(ticker: str, market: str) -> dict
check_data_anomaly(snapshot: dict) -> dict
```

Missing fields are returned as `None` and listed in `missing_fields`.

Valuation data is optional. Missing valuation data does not fail provider setup.

## Domestic Snapshot v0.2

`get_domestic_market_snapshot` adds China / Hong Kong decision-input fields:

- 5D / 10D / 20D / 60D changes.
- MA5 / MA10 / MA20 / MA60.
- Price distance from MA20 / MA60 and 20D / 60D highs / lows.
- Volume ratios vs 5D / 20D averages.
- Turnover ratios when turnover is available.
- `market_structure_status`.
- `execution_readiness`.
- `data_freshness`.

`market_structure_status` is rule-based and explainable. It does not predict price.

`execution_readiness` is not Trading Authority. CDE authorization is still required before any
portfolio action.

If data is partial, stale, or unavailable, Atlas should output decision limitations such as
`CDE Precision Limited` and avoid strong execution advice.

## Data Anomaly Check

`check_data_anomaly` flags extreme market data before Domestic Market Snapshot is used for CDE,
rebalance, or execution readiness.

Outputs:

- `anomaly_status`: Normal / Warning / Severe / Unknown.
- `anomaly_flags`.
- `anomaly_reason`.
- `decision_impact`: None / CDE Precision Limited / Execution Blocked / Use Conservative Framework
  Only.

Extreme moves are not automatically wrong. They mean execution sizing should become more
conservative until Atlas has confirmation.

## Privacy

The ticker registry stores identity mapping only.

Do not store:

- Position size.
- Cost.
- Account value.
- Portfolio amount.
- Private execution data.
