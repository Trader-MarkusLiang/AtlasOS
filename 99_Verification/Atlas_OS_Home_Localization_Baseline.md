# Atlas OS Home Localization Baseline

Date: 2026-07-09 21:43 CST

## Scope

Baseline audit for the Home Localization & Decision Brief UX Rebuild Goal.

This audit inspected:

- `/`
- `/home`
- `ui/pages/product_views.py::home_content`
- `ui/app_server.py::_product_shell` runtime refresh JavaScript
- current `/state` DecisionPacket projection
- causal summary rendering
- recommended action rendering
- regime/state labels
- causal factor labels
- freshness channels
- timestamps
- right inspector
- i18n dictionary

No runtime, cognition, Decision Contract, CDE, portfolio, forecast, or trading logic was modified
for this baseline.

## Current Runtime Evidence

Current `/state` contains a DecisionPacket with dynamic English cognitive output:

- `recommended_action`: `reduce`
- `risk_level`: `high`
- `regime_state`: `RISK_OFF / Runtime State Context`
- `causal_summary`: long English paragraph beginning `The fused runtime state indicates high stress...`
- `reasoning_trace`: long English paragraph beginning `RISK_OFF remains the active...`
- `attention_state`: `attention not dominant; attention pressure low relative to liquidity stress`
- `liquidity_state`: `Liquidity Shock; liquidity stress is the primary driver`

Current market intelligence includes raw backend channel/status values:

- `liquidity_proxy`: `SIMULATED`
- `macro_policy`: `NOT_CONFIGURED`
- `market_breadth`: `NOT_CONFIGURED`
- `narrative_attention`: `NOT_CONFIGURED`
- `news_announcement`: `NOT_CONFIGURED`
- `portfolio_relevance`: `LIVE`
- `price_volume`: `LIVE`
- `volatility`: `SIMULATED`

Current proactive update state includes raw English research focus items such as:

- `[portfolio asset redacted] (A-share) price, volume, liquidity, and announcement freshness`
- `Refresh degraded channels: market_breadth, news_announcement, narrative_attention, macro_policy`

Current timestamps are ISO strings such as:

- `2026-07-09T13:41:21.166468+00:00`
- `2026-07-09T13:54:55.187838+00:00`

## Defects Found

| Defect | Evidence | Status |
|---|---|---|
| `HERO_ENGLISH_LEAK` | `home_content()` derives hero text from English `causal_summary` via `_headline_from_summary()`; Chinese HTML contains `Liquidity Stress`. | Present |
| `LONG_ENGLISH_PARAGRAPH` | `home_content()` renders `packet.causal_summary` directly as primary hero copy. | Present |
| `ACTION_NOT_LOCALIZED` | `home_content()` renders `_safe_action(packet.get("recommended_action"))`, producing `Reduce` instead of `降低暴露 / Reduce`. | Present |
| `FACTOR_LABEL_NOT_LOCALIZED` | `ui/app_server.py::dominantFactors()` emits `risk:high`, `attention:...`, `liquidity:...`; causal graph factors remain English. | Present |
| `INSPECTOR_MIXED_LANGUAGE` | `updateState()` writes `packet.causal_summary`, `packet.reasoning_trace`, and English factor text directly into the right inspector. | Present |
| `RAW_ISO_TIMESTAMP` | Home/proactive card and expert-near primary areas can show raw ISO timestamps such as `2026-07-09T...`. | Present |
| `DYNAMIC_OUTPUT_BYPASSES_I18N` | The dynamic Home and inspector paths do not pass DecisionPacket, market channels, status labels, or timestamps through a locale-aware presentation adapter. | Present |

## Boundary Classification

- Scope classification: UI presentation/localization.
- Module boundary decision: allowed in `ui/**`, `ui/i18n/**`, locale-aware presentation adapters,
  formatting helpers, and verification artifacts.
- Project-stage risk: acceptable Production Trial usability repair; no new cognition engine.
- Runtime/cognition semantics: unchanged in baseline.

## Required Repair Direction

Implement a UI-only cognitive presentation adapter that:

- canonicalizes dynamic concept text into locale labels;
- renders Chinese-dominant Home with secondary English technical labels;
- creates concise Chinese causal summaries from structured state;
- keeps raw English model output collapsed under expert details;
- localizes action/risk/regime/factor/channel/status/asset freshness labels;
- formats timestamps as human-readable local time;
- provides the same localized payload to browser-side polling updates.
