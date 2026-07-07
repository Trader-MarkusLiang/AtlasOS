# Atlas OS Overnight Baseline Audit

Generated: 2026-07-08 00:20 CST

Branch: `codex/overnight-productization-sprint`

## Executive Verdict

Atlas OS is a real local runtime + UI + symbolic cognition prototype, but it is not yet a
production-grade autonomous asset cognition product.

The repository contains substantial implemented runtime infrastructure: EventStream, Input Router,
DecisionLoop, cognitive overlays, LLM provider routing, telemetry, UI server, market-data utilities,
and local daemon control. However, several user-facing product claims remain ahead of execution
evidence:

- Market ingestion is mostly simulated inside the daemon.
- Market data utilities exist but are not scheduled into EventStream.
- Portfolio UI configuration is mostly UI/local-config metadata and is not yet a real cognition
  context layer.
- Forecast / prediction accountability does not have a persistent ledger.
- Outcome evaluation and calibration exist for explanation/trust, but not for explicit forecasts.
- The default UI is still a control interface, not a Decision Brief-first home product.
- Roadmap/version metadata is stale and linearizes tracks that are actually parallel.

## Audit Method

Inspected actual files and execution paths, not completion labels:

- `README.md`
- `AGENTS.md`
- `VERSION.md`
- `CHANGELOG.md`
- `docs/atlas_roadmap.json`
- `runtime/`
- `runtime/cognition/`
- `runtime/llm/`
- `runtime/telemetry/`
- `runtime/config/`
- `ui/`
- `ui/components/`
- `ui/pages/`
- `tools/market_data/`
- `07_Decision_Engine/`
- `09_World_Model/`
- `10_Capital_Deployment_Engine/`
- `10_Production_Trial/`
- `99_Verification/`

Also executed lightweight checks:

- Provider registry safe view: 7 providers, active provider `morecode`, raw encrypted keys not
  exposed through `/llm/providers`.
- Market sample: `000001` A-share via `akshare` returned `Available`; `AAPL` via `yfinance`
  returned `Unavailable` because of provider rate limiting.
- Runtime private files are ignored by Git: `runtime/config/user_config.json`, runtime logs,
  runtime inbox, and sqlite state.

## Capability Truth Table

| Capability | Classification | Evidence | Notes / Gap |
|---|---:|---|---|
| Core Atlas knowledge OS | REAL | `00_Core/`, `07_Decision_Engine/`, `09_World_Model/`, `10_Capital_Deployment_Engine/` | Mature Markdown governance and reasoning framework. |
| Runtime daemon loop | PARTIAL | `runtime/atlas_runtime_daemon.py` | Runs ticks and isolates exceptions, but default event source is simulated. |
| EventStream queue | REAL | `runtime/event_stream.py`, `runtime/state_store.py` | SQLite-backed queue, file inbox, append-only event history. |
| Input Router isolation | REAL | `runtime/adapter/input_router.py` | Strips illegal trading/strategy fields before cognition. |
| DSA bridge | PARTIAL | `runtime/adapter/dsa_bridge.py`, `runtime/adapter/data_fetch.py` | Compatibility wrapper and optional data fetch hook only; external DSA source not bundled. |
| Event Fusion / Regime Memory | REAL | `runtime/cognition/event_fusion_engine.py`, `runtime/cognition/regime_memory.py` | Used by `runtime/decision_loop.py`. |
| CIL / World Model / LMSE / MPCE / MLE / UMIS overlays | REAL | `runtime/decision_loop.py` imports and executes them | Symbolic/deterministic overlays exist and are wired into the loop. |
| LLM Decision Contract | REAL | `runtime/cognition/decision_contract.py`, `decision_validator.py` | Strict schema, failsafe packet, forbidden trading language checks. |
| LLM provider runtime | REAL | `runtime/llm/provider_registry.py`, `provider_router.py` | Real adapter calls and fallback chain. |
| LLM key storage | PARTIAL | `runtime/llm/provider_registry.py` | Custom local obfuscation/encryption beside config; not production-grade secret storage. |
| Provider health/model UI | REAL | `/llm/providers`, `/llm/provider/test`, `/llm/provider/models`, `ui/pages/settings.py` | Local provider visibility works; model discovery is best-effort. |
| Telemetry logs | REAL | `runtime/telemetry/*` | JSONL traces, snapshots, replay reconstruction. |
| UI server | REAL | `ui/app_server.py` | FastAPI with stdlib fallback. |
| UI server cognition boundary | REAL | `ui/app_server.py` imports state/telemetry/provider modules, not cognition modules | UI is read/control gateway, not direct cognition mutator. |
| Runtime start/stop controls | PARTIAL | `ui/system_control_panel.py` | Starts/stops a background Python daemon; provider/interval changes are mostly next-start config. |
| Product home page | NOT_IMPLEMENTED | `/` returns `_system_interface_page()` | Default page is control interface, not Decision Brief-first Home. |
| First-run setup wizard | NOT_IMPLEMENTED | no `/setup` route | Settings page exists, but no guided wizard. |
| Market data provider | PARTIAL | `tools/market_data/market_data_provider.py` | Real akshare/yfinance utility, but not integrated into daemon ingestion. |
| Domestic market snapshot | REAL as utility | `tools/market_data/domestic_market_snapshot.py` | Produces structured snapshots and execution-readiness input labels. |
| Scheduled market refresh | NOT_IMPLEMENTED | daemon uses `SimulatedMarketEventSource` | No configured market refresh cadence into EventStream. |
| News / narrative ingestion | MOCK | simulated narrative event in `runtime/event_source.py` | No real news/source adapter. |
| Portfolio context storage | PARTIAL | `StateStore.save_portfolio_snapshot()`, settings asset config | Store redacts private fields, but runtime only checks for `06_Portfolio/portfolio.local.yaml`. |
| Portfolio exposure map | NOT_IMPLEMENTED | no parser/context layer | No concentration/theme/market/liquidity/regime sensitivity map. |
| Decision Brief portfolio impact | PARTIAL | `runtime/decision_brief.py`, `runtime/orchestrator.py` | Brief notes portfolio presence only; no holding-level exposure reasoning. |
| Forecast ledger | NOT_IMPLEMENTED | no forecast table/module/page | No persistent forecast schema or maturity lifecycle. |
| Prediction error | NOT_IMPLEMENTED | no explicit forecast/outcome comparison | Existing explanation error is not prediction error. |
| Explanation error | REAL | `runtime/cognition/explanation_error_engine.py` | Wired into `DecisionLoop`. |
| Trust calibration | REAL for cognition metadata | `runtime/cognition/trust_score_engine.py`, `system_trust_state.py` | Does not yet consume forecast outcome error. |
| Hypothesis memory/scoring | REAL | `runtime/cognition/hypothesis_memory.py`, `hypothesis_scoring_engine.py` | Works on explanation history, not explicit forecasts. |
| Self-iteration loop | PARTIAL | `DecisionLoop` routes feedback/trust/structural updates | Lacks forecast/outcome ledger and minimum-sample gating from prediction history. |
| Autonomous daily operating cycle | PARTIAL | `runtime/atlas_host.py`, `runtime/scheduler.py` | Daily/intraday functions exist, but content remains placeholder and not market-ingestion driven. |
| Long-run stability evidence | PARTIAL | daemon supports `max_cycles`, validation scripts exist | No current 24h proof; only short/accelerated tests are credible. |
| Roadmap / version truth | STALE_DOC | `docs/atlas_roadmap.json`, README/VERSION | Linear v0.1-v0.8 roadmap conflicts with actual parallel Core/Runtime/UI/Product tracks. |
| UI ordinary-user language | PARTIAL | i18n exists; many UI labels still internal | Default page exposes Control/Workflow/System terms rather than plain Decision Brief language. |

## Stale Roadmap / Documentation Findings

1. `README.md` and `VERSION.md` still describe the current stage as not building dashboard, API,
   automation, crawler, or database program. That is historically true for the knowledge repository
   but stale for the current runtime/UI product layer.
2. `docs/atlas_roadmap.json` describes a single sequence `v0.1 - v0.8`, current stage `v0.7`, next
   stage `v0.8 preparation`. Actual repo state now includes runtime/UI/product/provider versions
   beyond that sequence.
3. The roadmap does not distinguish:
   - Atlas Core / Knowledge OS
   - Atlas Runtime
   - Atlas Cognitive Overlay
   - Atlas UI / Product
   - Atlas Data / Market Intelligence
4. The roadmap can mislead a normal user into thinking `v0.8 Causal Interaction Layer` must be the
   next implementation. The sprint mandate correctly redirects current focus to production
   validation and autonomous productization.

## Duplicate / Overlapping Layers

- `runtime/atlas_host.py`, `runtime/atlas_daemon.py`, and `runtime/atlas_runtime_daemon.py` all
  represent daemon/host concepts. `atlas_runtime_daemon.py` is the current UI-started tick daemon;
  `atlas_host.py` is older schedule host infrastructure.
- `web/app.py`, `web/dashboard_observability.py`, and `ui/app_server.py` overlap dashboard roles.
  `ui/app_server.py` is the current product UI server.
- UI has both older component files and newer v2 control center rendering embedded in
  `ui/app_server.py`, creating visual and maintenance duplication.

## Dead Code / Placeholder Findings

- `runtime/orchestrator.py` still routes multiple placeholders:
  `regime_check_placeholder`, `attention_update_placeholder`, `simulation_placeholder`,
  `risk_evaluation_placeholder`, `anomaly_detection_placeholder`, `portfolio_risk_scan_placeholder`,
  and related state placeholders.
- `runtime/event_source.py` default source is deterministic simulated events.
- `ExternalEventSourceHook` is an extension point, not a configured real ingestion source.

## UI-Only Configs That Appear Runtime-Active

- Settings page stores `assets.portfolio_json`, `asset_list`, and `weights`, but runtime brief
  generation reads only whether `06_Portfolio/portfolio.local.yaml` exists.
- `switch_llm_provider()` stores next-start preference in `runtime/state/ui_runtime_config.json`;
  it does not rewire a running daemon.
- Control-panel asset editor links to settings; it does not currently persist a cognition-ready
  Portfolio Context Layer.

## Provider Config Reality

- Real provider registry exists with safe UI masking.
- Real route calls exist for OpenAI-compatible, Anthropic, Ollama, and custom proxy protocols.
- MoreCode / ARK / Volcano are represented as OpenAI-compatible providers.
- Current local active provider: `morecode`.
- Missing credentials degrade to `not_configured` / failsafe behavior.
- API keys are not committed because `runtime/config/user_config.json` is ignored.
- Security caveat: current key storage is custom local obfuscation/encryption. It is better than
  plaintext display, but not equivalent to macOS Keychain or production secret management.

## Market Data Capability Reality

- `tools/market_data/market_data_provider.py` can fetch via `akshare` and `yfinance`.
- A-share sample `000001` returned `Available` via `akshare` during audit.
- US sample `AAPL` returned `Unavailable` due to `yfinance` rate limit during audit.
- Market data is not yet normalized into the runtime event schema or scheduled into EventStream.
- News/social/macro ingestion is not implemented beyond simulated narrative events and user inbox.

## Portfolio Context Reality

- Portfolio governance documents are robust and privacy-preserving.
- Local `06_Portfolio/portfolio.local.yaml` exists but is ignored/private.
- Runtime currently records only a redacted portfolio availability snapshot.
- No Portfolio Exposure Map exists.
- UI asset percentages are not validated for consistency or mapped into cognition.

## Forecast / Accountability Reality

- No persistent Forecast Ledger exists.
- No `/predictions` page exists.
- No forecast maturity/outcome schema exists.
- No prediction-error calculation exists.
- Existing explanation error and trust calibration should be reused, but they do not satisfy
  prediction accountability by themselves.

## True Autonomous Runtime Status

- Real local daemon can run continuously and safely isolate tick exceptions.
- Default daemon behavior is simulated-event driven.
- UI start/stop can spawn/terminate the runtime daemon.
- Long-run stability has not been proven. The repo has validation scripts, but no current 24h
  evidence.

## Current Blockers

| Blocker | Severity | Required Action |
|---|---:|---|
| No Forecast Ledger | High | Add persistent ledger schema, APIs, and UI page before claiming prediction accountability. |
| Market data not wired into EventStream | High | Add normalized market intelligence refresh cycle using existing market-data utilities. |
| Portfolio context is not cognition-ready | High | Add read-only Portfolio Context Layer from percent-only config. |
| Default UI is not Decision Brief-first | Medium | Add Home / Ask Atlas / Portfolio / Markets / Predictions / Learning navigation and Home view. |
| Key storage is custom local obfuscation | Medium | Add Issue and either Keychain-backed storage or honest UI/security labeling. |
| Roadmap version model stale | Medium | Replace linear runtime roadmap with parallel track model. |
| No long-run evidence | Medium | Add accelerated soak test and label it honestly. |

## Boundary Check

This audit found no need to modify Event Fusion, CIL, LMSE, MPCE, MLE, Decision Contract semantics,
CDE formulas, trading execution, broker integration, or private portfolio files for the next safe
productization steps.

