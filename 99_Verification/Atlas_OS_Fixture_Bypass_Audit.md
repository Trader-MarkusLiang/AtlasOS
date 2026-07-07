# Atlas OS Fixture Bypass Audit

Date: 2026-07-08 07:25 CST

## Scope

Prompt D Phase A audits `99_Verification/validate_prompt_c_completion.py` and Prompt C reports for
fixture/runtime bypass. This audit does not invalidate Prompt C as a controlled internal-alpha
validation. It reclassifies each Prompt C success by whether it used the real daemon, real
scheduler, real EventStream, real DecisionLoop, real StateStore, real config path, real persistent
runtime DB, UI-to-runtime path, and non-manual state transitions.

Required Prompt D classifications:

- `REAL_RUNTIME_PATH`
- `REAL_MODULE_BUT_BYPASSED_RUNTIME`
- `CONTROLLED_FIXTURE_PATH`
- `TEMP_DB_ONLY`
- `MANUAL_STATE_INJECTION`
- `MOCK_ONLY`
- `DISCONNECTED`
- `UNKNOWN`

## Script-Level Finding

The Prompt C validation script explicitly states:

```text
This script uses only temporary fixtures/state.
```

It wraps all checks in `tempfile.TemporaryDirectory(prefix="atlas-prompt-c-")`, writes temporary
provider/config/database files, and intentionally disables Keychain with `ATLAS_DISABLE_KEYCHAIN=1`.
That is appropriate for Prompt C controlled validation, but it means Prompt C cannot be used as
Prompt D live/runtime proof without independent real-path execution.

## Prompt C PASS Reclassification

| Prompt C capability | Prompt C evidence | Real daemon | Real scheduler | Real EventStream | Real DecisionLoop | Real StateStore | Real config path | Real runtime DB | UI-to-runtime | Manual injection | Prompt D classification |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LLM E2E routing | Local HTTP fixture with `bad500 -> empty -> malformed -> good`, provider router, Decision Contract, temp telemetry | no | no | no | no | no | no | no | no | fixture provider | `CONTROLLED_FIXTURE_PATH` |
| Provider failover | Temporary registry with encrypted fixture secret and local fixture server | no | no | no | no | no | no | no | no | fixture endpoints | `CONTROLLED_FIXTURE_PATH` |
| Market ingestion | Temp config with `market_intelligence.fixtures`, `refresh_market_intelligence(..., enqueue=True)` | no | no | yes, temp DB | no | yes, temp DB | no | no | no | controlled fixture quote | `CONTROLLED_FIXTURE_PATH` |
| Portfolio cognition | `AtlasRuntimeDaemon.run_tick(0)` consumed temp config via `ATLAS_USER_CONFIG`; LLM patched | yes, single tick object | no | yes, temp DB | yes | yes, temp DB | no, temp config | no | no | patched LLM | `REAL_MODULE_BUT_BYPASSED_RUNTIME` |
| Forecast ledger lifecycle | Direct calls to `create_forecast`, `mark_forecast_matured`, `evaluate_forecast` in temp DB | no | no | no | no | yes, temp DB | no | no | no | direct lifecycle calls | `TEMP_DB_ONLY` |
| Self-iteration | Direct forecast miss inserted/evaluated in treatment temp DB, then equivalent input through `DecisionLoop` | no | no | yes, temp DB | yes | yes, temp DB | no | no | no | direct forecast miss setup | `MANUAL_STATE_INJECTION` |
| Daily cycle | Direct calls to all phase functions, plus direct `dispatch_current_daily_cycle` in temp DB | no | partial dispatch only | no | no | yes, temp DB | no | no | no | direct phase invocation | `REAL_MODULE_BUT_BYPASSED_RUNTIME` |
| Recovery | Corrupt inbox, telemetry, malformed forecast, stale PID against temp files | no | no | yes, temp DB for event case | no | yes, temp DB | no | no | no | direct fixtures | `CONTROLLED_FIXTURE_PATH` |
| Accelerated soak | `AtlasRuntimeDaemon(max_cycles=500, no_sleep=True)` with temp DB/config and patched LLM | yes, object path | no real sleep | yes, temp DB | yes | yes, temp DB | no | no | no | patched LLM + fixture config | `CONTROLLED_FIXTURE_PATH` |
| Security scan | `git grep` tracked secret-shape scan | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | no | `REAL_MODULE_BUT_BYPASSED_RUNTIME` |
| Live market probe | Direct `get_market_snapshot` for `000001` and `AAPL` | no | no | no | no | no | no | no | no | no | `DISCONNECTED` from runtime path |

## Prompt C Report Reclassification

| Report | Original wording | Prompt D reading |
|---|---|---|
| `Atlas_OS_Prompt_C_LLM_E2E_Report.md` | `CONTROLLED_FIXTURE_PROOF`; no live provider claim | Correctly scoped. Still not live provider proof. |
| `Atlas_OS_Prompt_C_Market_Ingestion_Report.md` | Fixture ingestion complete; live probe unavailable | Correctly scoped. Needs real observation through daemon/EventStream/UI freshness. |
| `Atlas_OS_Prompt_C_Portfolio_Differential_Report.md` | UI-style temp config -> runtime daemon -> brief | Strong module evidence, but not actual UI-config file or browser UI-to-runtime proof. |
| `Atlas_OS_Prompt_C_Forecast_Lifecycle_Report.md` | Fixture lifecycle complete | Not real runtime forecast lineage; direct ledger function calls only. |
| `Atlas_OS_Prompt_C_Self_Iteration_Proof.md` | `REAL_BEHAVIORAL_LOOP` | Overstated for Prompt D. It proves DecisionLoop consumes manually persisted forecast calibration state, not that daemon/UI path creates/evaluates forecasts. |
| `Atlas_OS_Prompt_C_Daily_Cycle_Report.md` | Phase functions and dispatch completed | Module execution proof, not wall-clock scheduler proof. |
| `Atlas_OS_Prompt_C_Soak_Report.md` | 500 accelerated cycles | Accelerated-only; no real-duration proof. |
| `Atlas_OS_Completion_Tribunal.md` | `PROVEN_COMPLETE` labels | Needs Prompt D evidence-level rewrite; many items are fixture complete, not runtime/live complete. |

## Bypass Patterns Found

1. **Temporary DB only:** Prompt C uses `/tmp/atlas-prompt-c-*/*.sqlite` for forecast, self-iteration,
   daily, recovery, and soak tests. Baseline real DB `runtime/state/atlas_runtime.sqlite` had no
   `forecast_ledger` table.
2. **Temporary config only:** Provider, market, portfolio, daily, and soak tests use generated temp
   config files rather than actual ignored `runtime/config/user_config.json`.
3. **Fixture provider only:** LLM E2E uses a local `ThreadingHTTPServer` fixture that always returns
   a valid DecisionPacket at the final fallback provider.
4. **Patched LLM path:** Portfolio, self-iteration, and soak call `_patch_orchestrator_llm()`,
   replacing `runtime.orchestrator.call_llm_raw` with a deterministic lambda.
5. **Manual forecast lifecycle:** Forecast lifecycle and self-iteration directly call ledger APIs
   rather than proving forecast creation/evaluation through daemon/UI normal cycles.
6. **Direct daily phase calls:** Daily-cycle validation invokes `run_morning_cycle`,
   `run_intraday_cycle`, `run_post_market_cycle`, and `run_overnight_cycle` directly.
7. **No UI browser path:** Prompt C does not prove browser actions write real UI config, submit
   runtime inbox events, or observe fresh persisted state.
8. **No real-duration scheduler:** The soak uses `no_sleep=True`; scheduler cadence and wall-clock
   survival remain unproven.

## Locally Fixable Runtime Gaps To Test Or Repair

| Gap | Baseline status | Local repair/test path |
|---|---|---|
| Provider router blocks local OpenAI-compatible shims with `api_key_missing` | likely `DISCONNECTED` for cc-switch local shims | Test real local provider path. If localhost shim accepts no key, allow local-loopback OpenAI-compatible calls without storing fake secrets. |
| Forecast ledger not created by normal daemon cycle | `DISCONNECTED` from real runtime path | Add or prove a supported non-binding forecast registration path from DecisionLoop/daemon without changing cognition semantics. |
| Self-iteration depends on manually inserted forecast miss | `MANUAL_STATE_INJECTION` | Run control/treatment through normal forecast lifecycle. Repair only if normal forecast registration is safely integrated. |
| Daily cycle is dispatched each tick but not proven by all phase times | `PARTIAL` | Use controlled `now=` dispatch through daemon-supported path or run phase dispatch with persistent DB evidence and classify exact scope. |
| Portfolio proof used temp config rather than actual UI-config path | `PARTIAL` | Backup/restore ignored `runtime/config/user_config.json`, run daemon cycle with config A/B, compare briefs. |
| Browser UX not proven | `PARTIAL` | Start/attach UI server and test rendered pages with browser automation if available. |
| Real market provider unavailable in Prompt C | `EXTERNAL_BLOCKER` until retried | Attempt configured assets through `refresh_market_intelligence` and daemon path. Do not convert failure into zero signal. |

## Prompt D Immediate Downgrades

| Capability | Prompt D evidence level before repair |
|---|---|
| Background runtime | `ACCELERATED_ONLY` |
| LLM routing/failover | `CONTROLLED_FIXTURE_PROVEN` |
| Live provider inference | `DISCONNECTED` pending real router smoke |
| Market ingestion | `CONTROLLED_FIXTURE_PROVEN` |
| Live market observation | `EXTERNAL_BLOCKER` pending retry |
| Portfolio cognition | `PARTIAL` |
| Forecast lifecycle | `CONTROLLED_FIXTURE_PROVEN` |
| Runtime forecast lineage | `DISCONNECTED` |
| Self-iteration | `PARTIAL` with `MANUAL_STATE_INJECTION` |
| Daily cycle | `PARTIAL` |
| Recovery | `CONTROLLED_FIXTURE_PROVEN` |
| Real-duration stability | `ACCELERATED_ONLY` |
| Browser usability | `PARTIAL` |
| Security tracked-file scan | `REAL_RUNTIME_PROVEN` for tracked repository files only |

## Phase A Verdict

Fixture bypass audit is complete. Prompt C closed controlled validation gaps, but Prompt D must not
carry forward Prompt C `PROVEN_COMPLETE` labels as live/runtime proof. At least seven disconnects
or partial paths require real-path testing or safe repair before any real-world activation closure:

1. live provider inference,
2. live market observation through daemon/EventStream,
3. actual UI-config portfolio differential,
4. real runtime forecast lineage,
5. true self-iteration without manual state injection,
6. true daily-cycle scheduler/dispatch proof,
7. real-duration soak and actual daemon failure injection.
