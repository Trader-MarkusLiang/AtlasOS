# CR_GOAL_08 — Recovery and Soak Report

Date: 2026-07-08

Branch: `codex/cleanroom-verification`

Current repair commit tested: `08574039784047357a82da3d4b5475d03f790576`

Fresh rerun clone: `/tmp/atlas-cleanroom-cr08-rerun-20260708-173210`

Fresh rerun state root: `/tmp/atlas-cleanroom-state-cr08-rerun-20260708-173210`

Fresh rerun artifacts:
`99_Verification/cleanroom/artifacts/cr_goal_08/rerun_20260708-173210/`

Classification: `PROVEN_COMPLETE`

Evidence level: `REAL_RUNTIME_PROVEN`

## Objective

Test clean-room operational resilience and soak behavior without reusing prior soak artifacts.

## Original Finding

The first CR08 pass proved recovery injections and 505 accelerated cycles, but remained
`ACCELERATED_ONLY` because no 2-hour clean-room real-duration soak was completed. It also found
that provider failure paths could stretch runtime ticks.

## Repair

Commit `0857403 cleanroom: bound provider outage latency` added bounded provider outage behavior:

- LLM provider calls now use configurable bounded HTTP timeouts.
- Market data provider attempts now use configurable timeout boundaries.
- `akshare` and `yfinance` calls are isolated in a subprocess so stuck provider code can be
  terminated without hanging the daemon tick.

This is runtime resilience only. It does not modify Event Fusion, CIL, LMSE, MPCE, MLE, CDE,
Decision Contract semantics, trading execution, broker integration, portfolio mutation, or
prediction behavior.

## Fresh Evidence

### Fresh Clone Context

```json
{
  "clone_path": "/tmp/atlas-cleanroom-cr08-rerun-20260708-173210",
  "commit": "08574039784047357a82da3d4b5475d03f790576",
  "prior_runtime_state_reused": false,
  "prior_telemetry_reused": false,
  "prior_browser_artifacts_reused": false
}
```

### Recovery and Accelerated Regression

Fresh clone recovery regression passed:

```json
{
  "status": "PASS",
  "accelerated_cycles": 500,
  "accelerated_tick_errors": 0,
  "accelerated_elapsed_seconds": 14.8991,
  "checks_all_true": true,
  "no_trading_execution": true,
  "recovery_statuses": {
    "daemon_restart": "passed",
    "malformed_jsonl": "passed",
    "market_outage": "passed",
    "provider_outage": "passed",
    "stale_pid": "passed",
    "ui_restart": "passed"
  }
}
```

The repaired invalid-market one-tick path completed in bounded time and preserved explicit channel
status:

```json
{
  "market_refresh_status": "ok",
  "price_volume": "FAILED",
  "duration_ms": 486,
  "status": "success"
}
```

### Real-Duration Soak

The fresh clone completed a scheduler-sleep real-duration soak:

```json
{
  "status": "PASS",
  "classification": "REAL_DURATION_2H_PROVEN",
  "elapsed_seconds": 16533.5355,
  "target_cycles": 721,
  "runtime_log_lines": 721,
  "tick_errors": 0,
  "returncode": 0,
  "provider_failures": 721,
  "market_failure_ticks": 0,
  "pending_queue_depth": 0,
  "db_size_bytes": 12099584,
  "max_rss_kb": 33312,
  "max_cpu_pct": 15.4,
  "hypothesis_switches": 0,
  "no_trading_execution": true
}
```

The runtime intentionally used degraded provider state during the soak. This produced 721 provider
failsafe events, but every tick stayed successful and no trading execution was produced.

## Acceptance Assessment

Passed:

- daemon restart recovery;
- UI restart recovery;
- stale PID cleanup;
- malformed inbox isolation;
- provider outage isolation;
- market outage isolation with explicit `FAILED` channel status;
- 500-cycle accelerated fresh-clone regression;
- 721-cycle scheduler-sleep real-duration soak;
- 2-hour minimum exceeded;
- SQLite remained usable with bounded queue depth;
- no trading execution.

Still not claimed:

- 24-hour unattended stability;
- complete live market coverage;
- full external-provider reliability under real paid API traffic.

## Evidence Artifacts

Fresh rerun artifacts:

- `00_fresh_clone_context.json`
- `01_goal07_recovery_accelerated_result.json`
- `01_goal07_recovery_accelerated_summary.json`
- `02_long_soak_smoke_result.json`
- `02_long_soak_smoke_summary.json`
- `03_long_soak_2h_result.json`
- `03_long_soak_2h_summary.json`
- `04_secret_shape_scan.json`

Secret-shaped token scan over the fresh rerun artifacts returned no matches.

## Classification

CR_GOAL_08 classification: `PROVEN_COMPLETE`

Evidence level: `REAL_RUNTIME_PROVEN`

Reason: recovery injections, accelerated regression, and a fresh clone real-duration soak exceeding
the 2-hour target completed with zero tick errors and no trading execution.

## Boundary

No Event Fusion, CIL, LMSE, MPCE, MLE, CDE, Decision Contract semantics, trading execution, broker
integration, portfolio mutation, or prediction-engine behavior was modified.
