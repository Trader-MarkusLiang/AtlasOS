# GOAL 01 User Activation Report

Date: 2026-07-08

Branch: `codex/overnight-productization-sprint`

Status: `PROVEN_PARTIAL`

## Objective

Make Atlas usable by a first-time user without terminal, JSON, Python, logs, or internal acronyms.

This report records the first GOAL 01 repair pass after GOAL 00. It does not claim full ordinary-user
activation because browser-level click-path acceptance is still pending.

## Audit Findings

| Requirement | Before Repair | Action |
|---|---|---|
| API key must truly submit | Setup submitted `active_provider`, but legacy config parser only read `provider` | Parser now accepts `active_provider` |
| Provider test must use current form values | Setup test called `/llm/provider/test` without saving current API key/base URL/model | Setup test now saves current values before testing |
| Asset setup must not require JSON | Setup required a portfolio JSON textarea | Setup now provides ordinary asset, market, percentage, theme, role, thesis, and risk-note fields |
| Runtime start must exist in user flow | UI control existed, but daemon start did not pass UI inbox/config path | Start command now passes `--ui-inbox-path` and `--market-config-path` |
| No raw dict/JSON by default | Setup result used raw JSON; Home printed raw market channel dict | Setup shows human-readable status; Home shows market channel summary |
| Config isolation | Provider endpoints ignored `ATLAS_USER_CONFIG` in some paths | Provider endpoints and registry now honor the active UI config path |

## Files Changed

- `runtime/llm/provider_registry.py`
- `ui/app_server.py`
- `ui/system_control_panel.py`
- `ui/pages/setup.py`
- `ui/pages/home.py`
- `ui/pages/settings.py`

No cognition, Event Fusion, CDE, broker, trading, prediction, or portfolio-mutation logic was
changed.

## Validation

### Static Checks

- `python3 -m py_compile runtime/llm/provider_registry.py ui/system_control_panel.py ui/app_server.py ui/pages/setup.py ui/pages/home.py ui/pages/settings.py`: PASS
- Render assertions:
  - Setup has normal asset fields.
  - Setup has base URL field.
  - Setup provider test references current payload.
  - Setup no longer uses a raw `<pre>` result.
  - Home no longer renders raw Python dict channel output.

### Temporary HTTP Flow

The HTTP validation used temporary:

- `ATLAS_USER_CONFIG`
- `ATLAS_RUNTIME_DB`
- `ATLAS_UI_INBOX`
- `ATLAS_UI_PID_FILE`
- telemetry/log paths

Validated endpoints:

| Step | Result |
|---|---|
| `GET /setup` | 200 |
| setup asset fields visible | PASS |
| setup JSON textarea absent | PASS |
| `POST /settings` with `active_provider=custom` | `saved` |
| API key in response | not present |
| saved custom provider base URL | current form value preserved |
| saved API key | encrypted local value; no raw key in file |
| `GET /llm/providers` | reads temporary active config; active provider `custom` |
| `POST /llm/provider/test` | used saved current provider values; returned honest `error` for unreachable endpoint |
| `POST /chat/send` | queued event and wrote UI inbox |
| `POST /control/start` | started daemon |
| start command includes `--ui-inbox-path` | PASS |
| start command includes `--market-config-path` | PASS |
| `POST /control/stop` | stop requested |

Provider test returned an error for the intentionally unreachable temporary endpoint. That is
expected and proves failure visibility, not provider live readiness.

## Current GOAL 01 Classification

`PROVEN_PARTIAL`

Reasons:

- Several locally fixable ordinary-user blockers were repaired.
- API/config/UI control path is materially better and validated through real HTTP endpoints.
- Full browser-level first-user journey has not yet been executed.
- zh/en parity is not fully proven across every page.
- Seeing the first brief after a fresh browser start still needs end-to-end visual validation.

## Remaining Work

1. Run browser-level click path:
   - open Atlas
   - understand Atlas
   - select language
   - configure LLM
   - test provider
   - select model
   - add assets
   - set percentages
   - start runtime
   - see first brief
   - ask Atlas
   - stop runtime
2. Add stale-server/version guard if browser testing shows old assets can remain served.
3. Improve zh/en parity in Setup and Home copy.
4. Verify Home is Decision Brief-first after a fresh runtime tick, not just route-rendered.

## Transition

Do not advance to GOAL 02 yet. Continue GOAL 01 until the full ordinary-user journey succeeds
through the real UI/runtime path.
