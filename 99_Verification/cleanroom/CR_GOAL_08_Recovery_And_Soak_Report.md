# CR_GOAL_08 — Recovery and Soak Report

Date: 2026-07-08

Branch: `codex/cleanroom-verification`

Commit tested: `f9a24ec857d0867b6b0a5dc6b617f9f53431fad6`

Clean-room clone: `/tmp/atlas-cleanroom-cr08-20260708-165652`

Primary state root: `/tmp/atlas-cleanroom-state-cr08-20260708-165652`

Accelerated no-market soak state root:
`/tmp/atlas-cleanroom-state-cr08-accelerated-nomarket-20260708-170130`

Classification: `ACCELERATED_ONLY`

## Objective

Test clean-room operational resilience and soak behavior without reusing prior soak artifacts.

## Failure Injection Results

| Injection | Result |
|---|---|
| Daemon kill | Terminated daemon process; SQLite integrity remained `ok`. |
| Daemon restart | Next one-cycle daemon run exited `0`; SQLite integrity remained `ok`. |
| UI restart | `/state` returned 200 before restart and 200 after restart. |
| Stale UI process | After UI termination, `/state` became unavailable; restart recovered on same port. |
| Stale PID | PID file existed before `/state`; `/state` reported `running: false` and removed stale PID. |
| Malformed inbox JSONL | Bad line skipped, valid event processed, file renamed `.processed`, daemon exited `0`. |
| Corrupt telemetry final line | `/replay?format=json` still returned 200. |
| Provider failure | Missing provider credentials degraded to neutral DecisionPacket; daemon tick stayed success. |
| Market provider failure | Invalid asset produced explicit `price_volume: FAILED`, not zero signal. |
| Missing optional dependency mode | UI served `/state` with `python3 -S`, using stdlib fallback. |

## Accelerated Soak

The clean no-market accelerated soak completed:

```json
{
  "tick_entries_counted": 505,
  "first_tick": 0,
  "last_tick": 504,
  "tick_errors": 0,
  "duration_sec": 16.4445,
  "peak_rss_kb": 34640,
  "sqlite_integrity": "ok",
  "db_size_bytes": 7917568,
  "log_size_bytes": 4621055
}
```

This proves accelerated daemon/scheduler/DecisionLoop stability with market refresh disabled.

## Market Failure Soak Finding

An attempted market-enabled accelerated soak against an invalid configured asset was intentionally
terminated after `131.1733` seconds because the invalid market provider path averaged multiple
seconds per tick.

Observed:

- corrected daemon tick entries before termination: `18`;
- market failed tick entries: `11`;
- market channel status was explicit: `price_volume: FAILED`;
- stderr included provider timeout messages from the market data path;
- this did not corrupt SQLite.

This is not a crash, but it means market-provider failures can materially slow accelerated runtime
cycles. It should be treated as an operational risk before any long-running live market soak.

## Real-Duration Soak

A short scheduler-sleep run completed:

```json
{
  "cycles": 2,
  "wall_duration_sec": 18.643,
  "returncode": 0
}
```

The 2-hour clean-room target was not run in this pass. Therefore CR_GOAL_08 is not a full
real-duration stability proof.

## Acceptance Assessment

Passed:

- daemon kill recovery;
- daemon restart;
- UI restart;
- stale PID cleanup;
- malformed inbox isolation;
- corrupt telemetry replay tolerance;
- provider failure isolation;
- explicit market failure status;
- missing optional dependency fallback;
- 505-cycle accelerated no-market soak.

Not fully proven:

- 2-hour or longer clean-room real-duration soak;
- market-enabled 500-cycle accelerated soak under provider timeouts;
- bounded long-run forecast ledger growth beyond 505 accelerated cycles.

## Evidence Artifacts

Artifacts are stored under:

```text
99_Verification/cleanroom/artifacts/cr_goal_08/
```

Key files:

- `cr08_final_recovery_soak_assessment.json`
- `cr08_accelerated_505_nomarket_summary.json`
- `cr08_recovery_soak_summary.json`
- `cr08_stale_pid_precise.json`
- `cr08_market_provider_failure_tick.json`
- `cr08_provider_failure_tick.json`
- `cr08_malformed_inbox_tick.json`
- `cr08_short_real_duration_soak_2_cycles.json`

Artifact JSON validation passed. Secret-shaped token scan over CR08 artifacts returned no matches.

## Classification

CR_GOAL_08 classification: `PROVEN_PARTIAL`

Evidence level: `ACCELERATED_ONLY`

Reason: recovery injections and accelerated daemon stability were proven, but the required
real-duration 2-hour soak was not completed from clean-room evidence.

## Boundary

No Event Fusion, CIL, LMSE, MPCE, MLE, CDE, Decision Contract semantics, trading execution, broker
integration, portfolio mutation, or prediction-engine behavior was modified.
