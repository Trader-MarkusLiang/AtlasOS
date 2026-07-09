# Atlas OS Getting Started Baseline

Date: 2026-07-09
Branch: `codex/frontend-master-upgrade`

## Scope

This baseline supports the Guided Start Center implementation. The change is limited to UI/product integration, readiness reporting, and verification assets.

Out of scope:

- Event Fusion semantics
- CIL / LMSE / MPCE / MLE / UMIS behavior
- Decision Contract semantics
- Capital Deployment Engine or trading authority
- Broker execution or portfolio mutation
- New cognitive engines

## Existing Execution Paths Audited

| Area | Current path | Baseline finding |
| --- | --- | --- |
| App Shell | `ui/components/app_shell.py` | Active product shell renders sidebar, topbar, content, inspector, and timeline. New page should use this shell. |
| Product routes | `ui/app_server.py` | FastAPI routes already exist for Home, Setup, Settings, Portfolio, Markets, Predictions, Learning, Workflow, Roadmap, Dev Registry, System Guide, Control, State. |
| Runtime state | `GET /state` via `state_api()` | Returns runtime status, tick counter, provider registry, market intelligence, portfolio context, latest decision packet, and brief id. |
| Runtime control | `POST /control/start`, `/control/stop`, `/control/set_interval` | Starts/stops daemon and stores allowed intervals. Does not import cognition modules. |
| Provider registry | `runtime/llm/provider_registry.py` | Supports safe registry views, masked secrets, health checks, latency tracking, and provider model discovery. |
| Provider UI APIs | `/llm/providers`, `/llm/provider/test`, `/llm/provider/models`, `/llm/providers/test_all` | Existing endpoints can configure/test/discover models without exposing raw secrets. |
| User config | `ui/pages/settings.py`, `runtime/config/user_config.json` | Settings save language, providers, runtime params, and asset metadata. API keys are masked in responses. |
| Portfolio context | `runtime/portfolio_context.py` | Builds read-only percentage-only exposure context. It does not store account value or execute trades. |
| Market readiness | `_market_intelligence_state()` and `/markets?format=json` | Reports channel status explicitly, including `NOT_CONFIGURED`; does not pretend missing data is zero signal. |
| First brief | `StateStore.get_latest_decision_brief()` through `/state` | `last_decision_brief_id` and `last_decision_packet` are available for first-brief readiness. |
| i18n | `ui/i18n/i18n.py` | Existing EN/ZH dictionary and language persistence are available. Guided Start needs new keys. |

## Gaps To Close

- No `/getting-started` route exists.
- No unified guided readiness page exists.
- Existing `/setup` is useful but too linear and not resume-aware enough for the requested 8-step journey.
- No single readiness endpoint aggregates language, provider, market, portfolio, runtime, and first brief status.
- Sidebar/topbar do not expose `Get Started / 开始使用`.
- Guided Start verification reports and validator do not yet exist.

## Implementation Boundary Decision

Accept the requested change as UI/product integration. Add a thin readiness aggregation endpoint only if implemented as read-only projection over existing state/config APIs. Do not add cognition, prediction, trading, or broker behavior.

## Baseline Dirty Worktree

Pre-existing unrelated dirty artifacts were observed and must be preserved:

- `99_Verification/artifacts/goal_07_autonomous_operations/operations_result.json`
- `99_Verification/artifacts/goal_01_user_activation/`
