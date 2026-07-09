# Atlas OS Home Intelligence Surface Baseline

Date: 2026-07-10 00:22 CST

## Scope

This baseline audits the current Home / Decision Brief surface before the Home Intelligence Surface
rebuild. It is evidence-based and does not assume prior reports are correct.

## Runtime And Routes Audited

Local product UI server:

- `http://127.0.0.1:8765/`
- `http://127.0.0.1:8765/home`
- `http://127.0.0.1:8765/predictions`
- `http://127.0.0.1:8765/markets`
- `http://127.0.0.1:8765/portfolio`
- `http://127.0.0.1:8765/learning`
- `http://127.0.0.1:8765/roadmap`
- `http://127.0.0.1:8765/state`

All audited product routes returned HTTP 200 during baseline capture.

## Current Home Renderer

- Renderer: `ui/pages/product_views.py::home_content`
- Product shell route: `ui/app_server.py` routes `/` and `/home` through `_product_shell("home", _home_content_with_setup_banner(state), state)`
- State API: `ui/app_server.py::state_api`

Current Home content is decision-first and includes:

- hero summary
- current Atlas action
- confidence gauge
- proactive update card
- portfolio minimap
- regime trajectory
- data freshness
- watch-next list
- invalidation list
- trust trend
- raw expert details block

## Capability Classification

| Capability | Classification | Evidence |
|---|---|---|
| Current State | `PRESENT_AND_CONNECTED` | Home reads `last_decision_packet`, `regime_state`, `trust_index`, market state, and portfolio context from `/state`. |
| Expert Details | `PRESENT_BUT_RAW` | Home ends with `<details class="expert-details">` and a raw JSON dump from `_expert_payload(state)`. It is not structured expert analysis. |
| Expert Analysis | `MISSING_FROM_UI` | Current Home HTML contains no visible `Expert Analysis` / `专家分析` panel or causal/hypothesis/confidence/data-quality sections. |
| Market Outlook | `MISSING_FROM_UI` | Current Home HTML contains no `Market Outlook` / `市场前瞻` first-class forward view. |
| Market Data Freshness | `PRESENT_AND_CONNECTED` | `/state.market_intelligence.channels` reports live/simulated/not-configured channels, and Home renders data freshness. |
| Forecast Ledger | `PRESENT_AND_CONNECTED` on `/predictions`; `PRESENT_BUT_DISCONNECTED` on Home | `runtime/forecast_ledger.py` and `/predictions?format=json` return forecast rows and metrics; Home does not show forecast accountability. |
| Forecast Accountability | `MISSING_FROM_UI` on Home | Home does not show open/matured/verified/invalidated/inconclusive forecast counts or recent misses. |
| Candidate Pool | `PRESENT_BUT_DISCONNECTED` | `02_Databases/AI_Shovel_100.md` explicitly defines Priority S/A/B candidate pools, but Home has no candidate section. |
| Candidate Route | `MISSING_FROM_UI` | No `/candidates` or `/research-candidates` route existed during baseline. |
| Candidate Ranking Safety | `PARTIAL` | Repository rules distinguish research priority from trading authority, but Home does not surface that distinction because candidates are absent. |
| Portfolio Relevance | `PRESENT_AND_CONNECTED` | `/state.portfolio_context` is configured and Home shows portfolio minimap/exposure context. |
| Invalidation Conditions | `PRESENT_BUT_PARTIAL` | Home shows generic invalidation items; forecast-specific invalidation conditions are not visible. |
| Hypothesis State | `PRESENT_BUT_DISCONNECTED` | Forecast ledger rows include `active_hypothesis`, and runtime state contains structural overlays; Home does not structure these into an expert panel. |
| Confidence Composition | `MISSING_FROM_UI` | Home shows one confidence number but no evidence/data/hypothesis/portfolio decomposition. |
| Data Quality Explanation | `PRESENT_BUT_PARTIAL` | Data freshness exists, but it is not tied to why confidence is limited. |
| ZH/EN Parity | `PARTIAL` | Existing Home has Chinese mode and English mode text, but required new sections are absent in both languages. |

## Candidate Pool Evidence

`02_Databases/AI_Shovel_100.md` states:

- "Use this table to turn the candidate pool into a research database."
- Priority S records current/core portfolio exposure.
- Priority A records Atlas core research names.
- Priority B records watch-pool names.
- Candidate ranking is evidence-gated and does not imply trading authority.

This proves the candidate pool exists as a repository-backed research database and should be restored
to Home as a presentation-only surface.

## Forecast Ledger Evidence

`runtime/forecast_ledger.py` defines forecast statuses:

- `OPEN`
- `MATURED`
- `VERIFIED`
- `INVALIDATED`
- `INCONCLUSIVE`

`/predictions?format=json` returned ledger rows and metrics during baseline capture. Current local
ledger rows are open, non-binding structural runtime forecasts; evaluated sample remains low.

## Market Outlook Evidence

No dedicated market-outlook object exists in `/state`. Existing sources that can support a
presentation-only outlook are:

- latest forecast ledger rows
- current `regime_state`
- `last_decision_packet`
- market intelligence channel health
- portfolio context
- structural and self-organization state overlays

The rebuild must distinguish this current forward view from the Forecast Ledger accountability
record.

## Primary Defects Found

1. Home does not follow the required six-zone information architecture.
2. Expert details are raw JSON-only and buried at the bottom.
3. Candidate pool exists in the repository but is not surfaced on Home.
4. Forecast ledger exists and is connected to `/predictions` but is disconnected from Home.
5. Market Outlook is absent from Home.
6. Invalidation conditions are generic and do not include forecast invalidation evidence.
7. Confidence is shown as one number without composition.
8. Candidate ranking safety is not visible because candidate presentation is absent.

## Boundary Decision

Implementation may proceed only through:

- `ui/**`
- read-only state aggregation in `ui/app_server.py`
- presentation-only candidate parsing from existing repository files
- verification artifacts under `99_Verification/**`

No cognition semantics, Decision Contract semantics, CDE authority, forecast lifecycle semantics,
portfolio mutation, scheduler semantics, broker execution, or trading authority may be modified.
