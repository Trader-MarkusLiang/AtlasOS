# Atlas OS Prompt C Market Ingestion Report

Date: 2026-07-08

## Command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_prompt_c_completion.py
```

## Controlled Fixture Evidence

- Market refresh status: `ok`.
- Proof mode: `CONTROLLED_FIXTURE_PROOF`.
- Events enqueued: 1.
- Routed event type: `volume_price_breakout`.

## Channel State Matrix

| Channel | Status |
|---|---|
| price_volume | SIMULATED |
| volatility | SIMULATED |
| liquidity_proxy | SIMULATED |
| portfolio_relevance | SIMULATED |
| market_breadth | NOT_CONFIGURED |
| news_announcement | NOT_CONFIGURED |
| macro_policy | NOT_CONFIGURED |
| narrative_attention | NOT_CONFIGURED |

All channel states now use the required vocabulary:

```text
LIVE / DELAYED / CACHED / SIMULATED / NOT_CONFIGURED / FAILED
```

## Live Probe

- `000001` A-share: unavailable. Provider errors included Eastmoney proxy failure and yfinance
  rate limit.
- `AAPL` US: unavailable due yfinance rate limit.
- Live price/volume count: 0.

## Verdict

PROVEN_COMPLETE for normalized fixture ingestion and honest channel labeling. Live market freshness
is EXTERNAL_BLOCKER under the current provider/network state.
