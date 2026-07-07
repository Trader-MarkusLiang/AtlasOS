# Atlas OS Live Market Activation Report

Date: 2026-07-08

## Verdict

Classification: `PARTIAL` / `EXTERNAL_BLOCKER`.

Atlas proved that market refresh failures enter the real daemon/EventStream path as degraded state
without fake freshness. It did **not** obtain a stable live price/volume observation through the
daemon path during Prompt D closure.

## Local Repair

Prompt D found a runtime import-path bug: executing `python3 runtime/atlas_runtime_daemon.py`
placed `runtime/` ahead of the standard library, so third-party providers imported Atlas
`runtime/logging.py` instead of Python `logging`.

Repair:

- `runtime/atlas_runtime_daemon.py` removes its script directory from `sys.path` and inserts repo
  root before runtime imports.

## Direct Provider Probe

After repair, direct provider probe showed:

| Asset | Market | Status | Source | Price/Volume |
|---|---|---|---|---|
| `000001` | A-share | Available once | akshare | present |
| `AAPL` | US | Unavailable | yfinance | rate limited |

## Daemon Path Attempts

Daemon attempts used UI-configured non-private assets and real daemon CLI:

```text
UI /settings
→ runtime/config/user_config.json
→ python3 runtime/atlas_runtime_daemon.py
→ refresh_market_intelligence()
→ EventStream market_event
→ DecisionLoop
→ persisted Decision Brief
```

Observed daemon result:

| Channel | Status |
|---|---|
| `price_volume` | `FAILED` |
| `portfolio_relevance` | `LIVE` |
| `market_breadth` | `NOT_CONFIGURED` |
| `volatility` | `NOT_CONFIGURED` |
| `liquidity_proxy` | `NOT_CONFIGURED` |
| `news_announcement` | `NOT_CONFIGURED` |
| `narrative_attention` | `NOT_CONFIGURED` |
| `macro_policy` | `NOT_CONFIGURED` |

Degraded evidence:

- `000001`: Eastmoney proxy disconnected during daemon attempts.
- `AAPL`: yfinance rate limited.
- Daemon stayed `success`.
- Market events were enqueued and handled as `market_event`.
- UI `/markets` displayed degraded status and channel labels.

## Classification By Channel

| Channel | Classification |
|---|---|
| Price / volume | `EXTERNAL_BLOCKER` during daemon path |
| Portfolio relevance | `LIVE_PROVEN` metadata path |
| Breadth/news/macro/narrative | `NOT_CONFIGURED` |
| Runtime degraded handling | `REAL_RUNTIME_PROVEN` |
