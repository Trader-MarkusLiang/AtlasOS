# GOAL 01 User Activation Report

Date: 2026-07-08

Branch: `codex/overnight-productization-sprint`

Status: `PROVEN_COMPLETE`

Evidence level: `REAL_RUNTIME_PROVEN`

## Objective

Make Atlas usable by a first-time user without terminal, JSON, Python, logs, or internal acronyms.

GOAL 01 is complete for the ordinary-user activation path. This does not claim live LLM success,
live market completeness, release readiness, 2h/24h stability, broker integration, or trading
execution.

## Boundary Decision

Scope classification: UI / configuration / runtime-control usability repair.

Module boundary decision: no Event Fusion, CIL, LMSE, MPCE, MLE, CDE, Decision Contract semantics,
trading, broker, prediction, or portfolio-mutation logic was changed.

## Repairs Completed

| Requirement | Repair |
|---|---|
| API key must truly submit | Settings parser accepts `active_provider`; provider registry respects active config path; validation confirms no raw key in saved config. |
| Provider test must use current form values | Setup saves current provider/base URL/model/key before calling `/llm/provider/test`. |
| Asset setup must not require JSON | Setup uses ordinary asset, market, percentage, theme, role, thesis, and risk-note fields. |
| Runtime start must exist in user flow | Setup now includes a direct `Start Runtime` button that saves current form values and calls `/control/start`. |
| Running state must be obvious | Setup shows `Status: started`; Dashboard shows start/stop chatline feedback; `/state` exposes tick and brief. |
| Home must be Decision Brief-first | Home first viewport shows Atlas Brief, action, trust, regime, market context, portfolio impact, and risks. |
| No raw dict/JSON by default | Home, Setup, Portfolio, Markets, Predictions, and Learning avoid raw dict/JSON on default pages. JSON remains available through explicit JSON/API routes. |
| zh/en parity | Setup/Home and product-page primary labels now use the UI i18n layer and respect `ATLAS_USER_CONFIG`. |
| Stop runtime | Daemon sleep is interruptible; control PID checks treat zombie/stale processes as stopped. |

## Files Changed

- `runtime/atlas_runtime_daemon.py`
- `ui/i18n/i18n.py`
- `ui/pages/setup.py`
- `ui/pages/home.py`
- `ui/pages/portfolio.py`
- `ui/pages/markets.py`
- `ui/pages/predictions.py`
- `ui/pages/learning.py`
- `ui/system_control_panel.py`
- `99_Verification/validate_goal_01_user_activation.py`

## Browser Journey Evidence

Browser artifacts:

- `99_Verification/artifacts/goal_01_user_activation_fixed/01_setup_filled_en.png`
- `99_Verification/artifacts/goal_01_user_activation_fixed/02_setup_started.png`
- `99_Verification/artifacts/goal_01_user_activation_fixed/03_dashboard_after_ask.png`
- `99_Verification/artifacts/goal_01_user_activation_fixed/04_home_first_brief_zh.png`
- `99_Verification/artifacts/goal_01_user_activation_fixed/05_dashboard_after_stop.png`
- `99_Verification/artifacts/goal_01_user_activation_fixed/browser_journey_result.json`

Observed browser path:

| Journey Step | Evidence |
|---|---|
| Open Atlas / Setup | `/setup` rendered first-run setup. |
| Understand Atlas | Setup explains non-binding cognitive loop and no trading execution. |
| Select language | Browser selected `zh`; saved config recorded `ui.language = zh`; reloaded Setup rendered Chinese labels. |
| Configure LLM | Browser filled provider, model, base URL, and non-secret test key. |
| Test provider | Provider test used saved current values and returned visible `error` for the intentionally unreachable local endpoint. |
| Select model | Browser filled custom model `goal-01-custom-model-fixed`. |
| Add assets | Browser filled AAPL, market, theme, role, thesis, and risk note without JSON. |
| Set percentages | Browser filled `25%`; runtime portfolio context later showed exposure `25.0`. |
| Start runtime | Setup `Start Runtime` returned `Status: started`. |
| See first brief | Home displayed `今日 Atlas 简报`, `NEUTRAL`, trust, regime, market context, and portfolio impact. |
| Ask Atlas | Dashboard Chat Mode queued a `/chat/send` event. |
| Stop runtime | Dashboard Stop returned `stop_requested`; validation confirmed the runtime process stopped. |

## Automated Validation

Command:

```text
python3 -m py_compile runtime/atlas_runtime_daemon.py ui/system_control_panel.py ui/i18n/i18n.py ui/pages/setup.py ui/pages/home.py ui/pages/portfolio.py ui/pages/markets.py ui/pages/predictions.py ui/pages/learning.py 99_Verification/validate_goal_01_user_activation.py
python3 99_Verification/validate_goal_01_user_activation.py
```

Result: `PASS`

Key checks:

- Setup renders and has direct runtime start.
- Setup has no default portfolio JSON textarea.
- Settings save succeeds.
- API key is not stored in plaintext.
- Provider test returns visible status and uses `custom`.
- zh Setup labels are visible after save.
- Runtime start produces at least one tick and one Decision Brief.
- Portfolio context is configured from UI input.
- Ask Atlas writes to UI inbox.
- Home is Decision Brief-first and shows portfolio impact.
- Product pages render and do not show raw JSON by default.
- Runtime stop is visible and process exits.
- Decision Brief and Forecast Ledger rows persist in the temporary runtime DB.

## Current GOAL 01 Classification

`PROVEN_COMPLETE`

Reason:

- The complete required first-user journey succeeded through the real UI/runtime path.
- Evidence includes browser-level artifacts, persisted runtime DB/logs, and a repeatable validation
  script.
- Remaining live-provider success belongs to `GOAL_02_LIVE_LLM_ACTIVATION`, not GOAL 01.

## Transition

Proceed to `GOAL_02_LIVE_LLM_ACTIVATION`.
