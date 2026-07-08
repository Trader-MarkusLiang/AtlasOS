# Atlas OS Frontend Execution Baseline

Date: 2026-07-09 07:15 CST
Workspace: `/Users/markus/AtlasOS`
Branch: `codex/frontend-master-upgrade`
HEAD: `7d39b1c21ef18f072c92cad85d6f02dc3052f262`

## Scope Boundary

This baseline freezes the current frontend state before the Frontend Master Execution Goal repairs. It does not authorize changes to Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, CDE, Decision Contract, trading authority, broker integration, portfolio holdings, cognitive core, runtime scheduler semantics, or any v0.8-style cognition.

## Git State

Current branch: `codex/frontend-master-upgrade`

Recent local frontend commits:

- `7d39b1c docs: record frontend goal completion audit`
- `57a411a frontend: close current UX acceptance gaps`
- `62270df docs: complete frontend productization session log`
- `be2dfde frontend: establish unified product shell`
- `3f8d6e7 frontend: audit current product experience`

Remote state:

- `origin/codex/frontend-master-upgrade` was absent at baseline.
- Therefore local frontend branch work is not independently auditable at the required remote ref until pushed.

Dirty files present before this task:

- `99_Verification/artifacts/goal_07_autonomous_operations/operations_result.json`
- `99_Verification/artifacts/goal_01_user_activation/`

These are unrelated to the frontend execution task and must not be staged in the frontend commit.

## Running UI

- UI process: PID `30352`
- Port: `127.0.0.1:8765`
- Command family: Python `ui.app_server.run_server`
- Stale server risk: present as a long-running local process. Must be rechecked after code patches; if the served build diverges, restart or mark the mismatch explicitly.

Additional Python UI processes were observed on non-primary ports (`8768`, `8876`, `8891`). They are not the primary acceptance target for this baseline.

## Route Status

Baseline route smoke against `http://127.0.0.1:8765`:

| Route | HTTP | Shared shell |
|---|---:|---|
| `/` | 200 | yes |
| `/home` | 200 | yes |
| `/setup` | 200 | yes |
| `/dashboard` | 200 | yes |
| `/chat` | 200 | yes |
| `/portfolio` | 200 | yes |
| `/markets` | 200 | yes |
| `/predictions` | 200 | yes |
| `/learning` | 200 | yes |
| `/workflow` | 200 | yes |
| `/roadmap` | 200 | yes |
| `/dev-registry` | 200 | yes |
| `/settings` | 200 | yes |
| `/system-guide` | 200 | yes |
| `/control` | 200 | yes |
| `/state` | 200 | JSON endpoint |

## Current Shell Architecture

Implemented shared shell components observed:

- `ui/components/app_shell.py`
- `ui/components/global_sidebar.py`
- `ui/components/global_topbar.py`
- `ui/components/runtime_status_indicator.py`
- `ui/components/language_toggle.py`
- `ui/components/context_inspector.py`

Current gaps:

- Secondary sidebar lacks explicit System Status entry.
- Topbar lacks an explicit Settings entry.
- `/control` renders through the shell but is active as settings rather than system status.

## Current Visualization Count

Source inspection found more than 12 `atlas-viz` SVG-producing helpers in `ui/pages/product_views.py`, including portfolio exposure, risk cluster, regime trajectory, attention/liquidity, trust trend, calibration, forecast timeline, hypothesis competition, learning flow, workflow, roadmap swimlanes, capability evolution, and validation history.

Baseline gap:

- Existing visualizations render, but most do not declare a consistent `data-viz-id`, user-question metadata, tooltip target, or common interaction proof surface.
- Existing evidence therefore proves rendering more strongly than interaction.

## Current zh/en Status

`ui/i18n/i18n.py` contains EN/ZH translations and the global language toggle is wired through `/ui/language`.

Baseline gaps:

- Some product copy and chart labels remain hardcoded in English.
- Mixed-language leakage must be checked with browser evidence.
- Long-language wrapping must be included in responsive verification.

## Evidence Existing Before Task

Existing frontend reports include:

- `99_Verification/Atlas_OS_Frontend_Master_Baseline.md`
- `99_Verification/Atlas_OS_Frontend_Information_Architecture_Report.md`
- `99_Verification/Atlas_OS_Frontend_Visual_System_Report.md`
- `99_Verification/Atlas_OS_Frontend_Bilingual_Report.md`
- `99_Verification/Atlas_OS_Frontend_Accessibility_Report.md`
- `99_Verification/Atlas_OS_Frontend_Browser_E2E_Report.md`
- `99_Verification/Atlas_OS_Frontend_Final_Acceptance_Report.md`
- `99_Verification/Atlas_OS_Frontend_Master_Current_Completion_Audit.md`

Known stricter evidence gap:

- Current E2E evidence is not the exact 24-step journey required by the new execution mandate.
- Current visualization evidence must be replaced or supplemented with a real interaction matrix.
