# Atlas OS Frontend Browser E2E Report

Date: 2026-07-08

## Environment

- UI server: `127.0.0.1:8765`
- Branch: `codex/frontend-master-upgrade`
- Browser evidence directory: `99_Verification/artifacts/frontend_master/`

## Route E2E

All required HTML routes returned HTTP 200 and rendered the shared shell:

- `/`
- `/setup`
- `/dashboard`
- `/portfolio`
- `/markets`
- `/predictions`
- `/learning`
- `/workflow`
- `/roadmap`
- `/dev-registry`
- `/settings`
- `/system-guide`

All checked JSON routes returned HTTP 200:

- `/state`
- `/roadmap?format=json`
- `/predictions?format=json`
- `/markets?format=json`

## Product Journey Validation

| Step | Result | Evidence |
|---|---|---|
| Open Atlas | PASS | `/` rendered shared shell |
| Understand Home | PASS | Home no longer uses `NEUTRAL` hero |
| Switch to Chinese | PASS | `/ui/language` zh returned saved |
| Switch to English | PASS | `/ui/language` en returned saved |
| Open Setup | PASS | `/setup` rendered shared shell |
| Configure provider surface | PASS | Settings/Setup provider controls visible |
| Test provider | PASS | active provider `morecode` returned `reachable`, `http_501`, `5ms` latency |
| Add assets surface | PASS | ordinary asset rows visible; no JSON primary |
| Start Runtime | PASS | `/control/start` returned `started`, pid `5928` |
| Stop Runtime | PASS | `/control/stop` returned `stop_requested`; PID file removed afterward |
| Return Home | PASS | `/` rendered after runtime control |
| Ask Atlas | PASS | `/chat/send` queued `user_query` event |
| Open Markets | PASS | `/markets` visual-first page rendered |
| Open Portfolio | PASS | `/portfolio` visual-first page rendered with no-asset SVG empty state |
| Open Predictions | PASS | `/predictions` accountability page rendered |
| Open Learning | PASS | `/learning` belief-change page rendered |
| Open Workflow | PASS | `/workflow` global system map rendered |
| Open Roadmap | PASS | `/roadmap` swimlane page rendered |
| Open Settings | PASS | `/settings` provider/assets/runtime page rendered |

## Browser Metrics

After screenshot metrics:

- shell failures: none
- horizontal overflow: none
- `NEUTRAL` hero: none
- visible `Unknown`: none
- primary table count: zero in the after screenshot set
- after SVG count: 12

## Runtime Cleanup

After start/stop smoke:

- `runtime/state/atlas_ui_runtime.pid` was removed.
- No daemon PID remained from the UI start smoke.

Result: `PASS`
