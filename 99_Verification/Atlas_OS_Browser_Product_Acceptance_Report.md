# Atlas OS Browser Product Acceptance Report

Date: 2026-07-08

## Verdict

Classification: `PARTIAL`.

Browser-level validation was performed with the in-app browser against `http://127.0.0.1:8768`.

## Initial Failure

The running UI server was stale. Before restart:

| Route | Status |
|---|---|
| `/` | rendered |
| `/settings` | rendered |
| `/setup` | 404 |
| `/portfolio` | 404 |
| `/markets` | 404 |
| `/predictions` | 404 |
| `/learning` | 404 |

## Repair

Old UI server processes on ports `8767` and `8768` were stopped and a fresh current-code server was
started on `8768`.

After restart, all required routes returned rendered HTML:

```text
/
/setup
/portfolio
/markets
/predictions
/learning
/workflow
/roadmap
/settings
```

## Rendered Page Checks

| Page | Browser result |
|---|---|
| Home/dashboard | rendered cognitive control center with state, trust, decision, inspector |
| Setup | rendered setup flow |
| Portfolio | rendered privacy-preserving portfolio context |
| Markets | rendered degraded channel state |
| Predictions | rendered Forecast Ledger and creation form |
| Learning | rendered accountability metrics |
| Workflow | rendered guided pipeline page |
| Roadmap | rendered lifecycle/validation page |
| Settings | rendered provider/settings controls |

No horizontal overflow or server traceback was detected on these pages.

## Interaction Checks

| Task | Result |
|---|---|
| Language endpoint | `/ui/language` saved `zh` and `en` |
| Chat send | `/chat/send` queued local user query |
| Runtime inbox | daemon consumed chat event into EventStream |
| Provider test | `ark` reachable |
| Provider models | 125 models discovered |
| Runtime start | `/control/start` started daemon process |
| Runtime stop | `/control/stop` requested stop |

## UX Issues Found

1. Existing running server can become stale relative to repo code, causing route-level 404s until
   restarted.
2. The dashboard mode button for chat was visible, but browser inspection did not show a clear
   switched chat workspace after clicking.
3. Some navigation checks are bilingual; English-only route keyword checks can misread Chinese UI
   labels.
4. Provider health in the left panel may show stale `error` while settings page shows ARK/Volcano
   healthy after fresh checks.
