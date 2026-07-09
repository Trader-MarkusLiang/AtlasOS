# Atlas OS Getting Started User Flow Report

Date: 2026-07-09
Branch: `codex/frontend-master-upgrade`

## Scope

Validated the new Guided Start Center through real UI/server paths without modifying cognitive semantics.

Primary route:

- `GET /getting-started`
- `GET /getting-started/status`

## Environment

Main UI:

- `http://127.0.0.1:8765/getting-started`

Isolated E2E UI:

- `http://127.0.0.1:8770/getting-started`
- Temp config/db/pid/logs under `/tmp/atlas_getting_started_e2e/`
- Isolated runtime daemon was started and stopped during test.

## 24-Step Flow Result

| Step | Result | Evidence |
| --- | --- | --- |
| 1. Open `/getting-started` | PASS | HTTP 200, page rendered through App Shell |
| 2. Read Atlas explanation | PASS | Understand Atlas section visible |
| 3. Select Chinese | PASS | `/ui/language` POST succeeded, page reloaded in zh |
| 4. Continue | PASS | Mark-understood action persisted in localStorage |
| 5. Inspect provider state | PASS | Provider summary/status visible |
| 6. Configure provider | PASS | Current form values saved through `/settings` |
| 7. Test provider | PASS | `/llm/provider/test` executed against current form values |
| 8. Discover/select model | PASS DEGRADED | `/llm/provider/models` executed; custom model retained when list unavailable |
| 9. Inspect market readiness | PASS | Channel matrix visible |
| 10. Add first asset | PASS | AAPL percentage row saved |
| 11. Add second asset | PASS | MSFT percentage row saved |
| 12. Confirm percentages | PASS | Status reported 2 assets and 20% exposure |
| 13. Review runtime interval | PASS | 10s interval selected |
| 14. Save runtime settings | PASS | `/control/set_interval` returned success |
| 15. Click Start Atlas | PASS | `/control/start` executed |
| 16. Observe boot sequence | PASS | Boot log updated during save/start/poll |
| 17. Confirm runtime Running | PASS | Status showed `running: true` with isolated PID |
| 18. Confirm first tick | PASS | Status showed `tick_counter: 2`, later `3` |
| 19. Confirm first brief | PASS | `first_brief.status: READY` |
| 20. Open Home | PASS | Browser opened `/` successfully |
| 21. Return to `/getting-started` | PASS | Browser returned to route |
| 22. Confirm completed steps persist | PASS | Progress displayed `7 / 8 步已完成` before stop |
| 23. Stop runtime | PASS | `/control/stop` executed |
| 24. Confirm Stopped | PASS | UI summary displayed `已停止`; status showed `running: false` |

## Key Runtime Evidence

After start:

```json
{
  "runtime": {"running": true, "tick_counter": 2, "tick_interval": 10},
  "first_brief": {"status": "READY", "decision": "neutral"},
  "portfolio": {"position_count": 2, "exposure_sum_pct": 20.0},
  "market_data": {"status": "READY"}
}
```

After stop:

```json
{
  "runtime": {"running": false, "tick_counter": 3},
  "first_brief": {"status": "READY"}
}
```

## Artifact

- `99_Verification/artifacts/getting_started/getting_started_e2e.png`

## Notes

- Provider model discovery was intentionally tested against an isolated local fake endpoint. The UI correctly preserved a custom model name and displayed the degraded path instead of blocking runtime startup.
- No raw API key or encrypted key material appeared in rendered HTML.
