# GOAL 01 Evidence - User Activation

## Current Classification

Goal classification: `PROVEN_PARTIAL`

Evidence level: `PARTIAL`

Browser routes rendered after stale UI server restart and `/chat/send` entered the runtime inbox.
This is useful but not yet a full ordinary-user activation proof. The first GOAL 01 repair pass
removed several setup/config blockers and recorded `99_Verification/GOAL_01_User_Activation_Report.md`.

## Supporting Evidence

| Evidence | File | Classification |
|---|---|---|
| Browser product acceptance | `99_Verification/Atlas_OS_Browser_Product_Acceptance_Report.md` | `PARTIAL` |
| Runtime failure injection | `99_Verification/Atlas_OS_Live_Runtime_Failure_Injection_Report.md` | UI restart tested |
| GOAL 01 repair pass | `99_Verification/GOAL_01_User_Activation_Report.md` | `PROVEN_PARTIAL` |
| UI runtime pages | `ui/app_server.py` | implementation reference |
| Goal status | `docs/goals/status/GOAL_STATUS.json` | `PARTIAL` |

## Proven Runtime Path

- `/chat/send` writes to runtime inbox.
- Daemon consumed UI-origin user event into EventStream.
- `/control/start` and `/control/stop` operated in tested path.
- Required pages rendered after current-code server restart.
- Setup can save provider config from `active_provider`.
- Provider test path uses current saved form values.
- Setup can collect assets/percentages without requiring JSON input.
- UI start now passes current UI inbox and config path to daemon.

## Remaining Gaps

- Stale UI server/version guard.
- Full click-path acceptance for non-developer user.
- zh/en parity across Setup/Home copy.
- Provider health panel can show stale health without explanation.
- First brief visibility after fresh browser start.

## Next Evidence To Collect

1. Browser task trace for start, ask, inspect brief, inspect portfolio impact, stop.
2. Stale server detection report.
3. UX issue list with severity and fixes.
4. Fresh runtime tick -> Home Decision Brief visual proof.

## Non-Evidence

- Raw HTTP 200 alone.
- Screenshot-free claims that a route exists.
- A backend route working without proving the user can discover it.
