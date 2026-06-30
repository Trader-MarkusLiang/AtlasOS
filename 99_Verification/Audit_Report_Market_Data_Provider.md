# Audit Report — Market Data Provider Availability

Date: 2026-06-30

## Executive Summary

Current provider status:

- `pandas`, `numpy`, and `requests` are installed.
- `yfinance`, `akshare`, `beautifulsoup4`, `lxml`, and `pandas_market_calendars` are not installed.
- No existing Atlas market data provider, adapter, or cached market data layer was found.
- `requests` is an HTTP transport package, not a market data provider by itself.

Whether Atlas can currently fetch A-share data:

- No. No configured local provider can retrieve A-share latest price, history, volume, turnover,
  valuation, or K-line fields.

Whether Atlas can currently fetch Hong Kong data:

- No. No configured local provider can retrieve Hong Kong latest price, history, volume, turnover,
  valuation, or K-line fields.

Whether Market Data Fetch Gate can operate with real data now:

- Gate behavior can operate.
- Real data retrieval is blocked by missing provider configuration.
- Atlas should continue outputting `Market Data Missing or Unavailable — Decision Limited` or
  `Market Data Provider Missing — Configure data source` when market data is required.

Main blockers:

- `akshare` is not installed.
- `yfinance` is not installed.
- `beautifulsoup4` and `lxml` are not installed, so even a manual HTML fallback would lack parsing
  dependencies.
- No local Atlas provider or cache exists.

Decision:

```text
BLOCKED — no useful market data provider available
```

Next Step:

```text
Install / configure provider
```

## Package Audit

| Package | Installed | Version | Notes |
|---|---|---|---|
| pandas | YES | 2.3.3 | Data manipulation available |
| numpy | YES | 2.0.2 | Numeric support available |
| yfinance | NO | Data Missing | Missing provider |
| akshare | NO | Data Missing | Missing provider |
| requests | YES | 2.32.5 | Transport only; not a data provider |
| beautifulsoup4 | NO | Data Missing | HTML parsing unavailable |
| lxml | NO | Data Missing | XML / HTML parser unavailable |
| pandas_market_calendars | NO | Data Missing | Market calendar support unavailable |

Package audit note:

- Importing `requests` surfaced an environment warning: urllib3 v2 expects OpenSSL 1.1.1+, while
  this Python SSL module is compiled with LibreSSL 2.8.3. This did not block import, but may matter
  for future provider reliability.

## A-share Test Result

No installed provider could retrieve A-share market data during this audit.

| Candidate | Ticker | Ticker Resolution | Latest Price | Daily Change % | Volume | Turnover | 5D History | 20D History | 60D History | Market Cap | PE / PB | Timestamp | Source | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 雅克科技 | 002409.SZ | Provided by task | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | Provider Missing |
| 东山精密 | 002384.SZ | Provided by task | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | Provider Missing |
| 泰金新能 | 688813.SH? | Local registry shows `688813`; suffix requires manual confirmation | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | Ticker Resolution Needs Manual Mapping |
| 赛腾股份 | 603283.SH | Provided by task | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | Provider Missing |
| 澜起科技 | 688008.SH | Provided by task | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | Provider Missing |
| 江丰电子 | 300666.SZ | Provided by task | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | Provider Missing |

## Hong Kong Test Result

No installed provider could retrieve Hong Kong market data during this audit.

| Candidate | Ticker | Ticker Resolution | Latest Price | Daily Change % | Volume | Turnover | 5D History | 20D History | 60D History | Market Cap | PE / PB | Timestamp | Source | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 建滔集团 | 00148.HK | Provided by task | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | HK Market Data Unavailable |
| 长飞光纤光缆 | 06869.HK | Provided by task | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | HK Market Data Unavailable |
| 中芯国际 | 00981.HK | Provided by task | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | Data Missing | No configured provider | HK Market Data Unavailable |

## Provider Capability Matrix

| Provider | Installed | A-share Latest | A-share Historical | HK Latest | HK Historical | Valuation Data | Notes |
|---|---|---|---|---|---|---|---|
| akshare | NO | NO | NO | NO | NO | NO | Best minimum provider candidate, but not installed |
| yfinance | NO | NO | NO | NO | NO | NO | Useful fallback for some HK tickers, but not installed |
| direct web fallback | NO | NO | NO | NO | NO | NO | No implemented local Atlas web fallback provider was found |
| existing local Atlas provider | NO | NO | NO | NO | NO | NO | Repository search found no provider / adapter |
| cached data layer | NO | NO | NO | NO | NO | NO | Repository search found no cache layer |
| requests | YES | NO | NO | NO | NO | NO | Transport package only; not sufficient without provider logic |

## Recommended Minimum Setup

1. Best provider for A-share:

   `akshare`, because it commonly supports China A-share quote, history, turnover, and some
   valuation-style fields.

2. Best provider for Hong Kong stocks:

   `akshare` as the primary provider, with `yfinance` as fallback where Hong Kong Yahoo symbols are
   reliable.

3. Whether akshare is sufficient:

   Likely sufficient for Production Trial daily / candidate / rebalance checks if installed and
   validated, but it should not be assumed reliable for every valuation field.

4. Whether yfinance is useful as fallback:

   Yes, especially for Hong Kong symbols, broad historical prices, and fallback latest quote data.
   For A-share it may be less reliable depending on symbol format and data availability.

5. Reliable fields:

   Latest price, daily change, historical close, and volume are likely the most reliable fields
   once provider access is configured.

6. Unreliable fields:

   Turnover, PE / PB, market cap, and real-time freshness may vary by provider and should be treated
   as optional / source-dependent.

7. Valuation data:

   Treat valuation data as optional. Atlas should never block all research because PE / PB is
   missing, but must not invent valuation risk.

8. Real-time versus delayed:

   Assume delayed unless the provider explicitly reports real-time freshness. Intraday Fast
   Rebalance should remain limited until timestamp and freshness are validated.

9. Enough for Strategic Candidate Dashboard:

   Not currently. After `akshare` / `yfinance` are installed and validated, likely sufficient for
   research-priority ranking with source-tagged market confirmation.

10. Enough for CDE:

    Not currently. After provider setup, likely sufficient for non-intraday CDE precision if price
    history and timestamp are available.

11. Enough for Rebalance Plan:

    Not currently. After provider setup, may support staged rebalance planning, but not fast
    intraday execution unless freshness is proven.

12. Enough for Intraday Fast Rebalance:

    Not currently. Keep `Fast Rebalance Decision Limited — Market Data Required` until real-time or
    reliably fresh data is configured and validated.

## Decision

```text
BLOCKED — no useful market data provider available
```

## Next Step

```text
Install / configure provider
```

## Safety Verification

| Rule | Result |
|---|---|
| Did not modify `portfolio.local.yaml` | PASS |
| Did not modify Decision Brief logic | PASS |
| Did not modify CDE logic | PASS |
| Did not modify Strategic Candidate Dashboard logic | PASS |
| Did not create a new Engine | PASS |
| Did not install packages | PASS |
| Did not commit secrets or API keys | PASS |
| Did not store sensitive portfolio amounts | PASS |

## Known Limitations

- This is an availability audit, not a provider implementation.
- No package installation was performed.
- No paid or credentialed API was used.
- No aggressive scraping was performed.
- `泰金新能` ticker mapping should be manually confirmed before any market-data-dependent output.
