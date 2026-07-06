# IP-2026-036 — Runtime Daemon Background Execution v0.1

## Category

Engineering / Runtime Infrastructure / macOS Background Execution

## Origin

ISSUE-2026-036 — Runtime Daemon Background Execution Needed

## Problem

Atlas OS has cognitive runtime components, but needs a minimal daemon wrapper that can run
continuously on macOS, generate or receive events, call the existing cognitive pipeline, persist
runtime output, and recover from single-cycle failures.

## Implemented Scope

- Added `runtime/atlas_runtime_daemon.py`.
- Added `runtime/event_source.py`.
- Added `runtime/output_logger.py`.
- Extended `runtime/scheduler.py` with:
  - `RuntimeScheduleConfig`
  - allowed intervals: `10`, `30`, `60`, `300`
  - `next_run_time()`
- Added `99_Verification/validate_runtime_daemon_v0_1.py`.

## Runtime Flow

```text
AtlasRuntimeDaemon
 -> EventSource
 -> EventStream
 -> DecisionLoop
 -> existing cognitive pipeline
 -> StateStore
 -> OutputLogger
```

Existing cognitive pipeline called by `DecisionLoop`:

```text
Event Stream
 -> Fusion Engine
 -> Regime Memory
 -> CIL
 -> World Model
 -> LMSE
 -> MPCE
 -> MLE
 -> UMIS
```

## Run Instructions

Foreground:

```bash
python3 runtime/atlas_runtime_daemon.py
```

Background:

```bash
nohup python3 runtime/atlas_runtime_daemon.py &
```

Test / smoke mode:

```bash
python3 runtime/atlas_runtime_daemon.py --interval 10 --max-cycles 3 --no-sleep
```

## Output Log

Default log:

```text
runtime/logs/atlas_runtime.log
```

Each JSONL entry includes:

- timestamp
- event
- cognition summary
- regime state
- decision brief metadata
- system metrics

## Failure Handling

`AtlasRuntimeDaemon.run_tick()` catches exceptions per tick, writes a failure record, and allows
the loop to continue. Safe shutdown is handled through `SIGINT` and `SIGTERM`.

## Boundary

This IP does not modify:

- cognitive architecture v0.5-v1.2
- Event Fusion core logic
- CIL / LMSE / MPCE / MLE / UMIS logic
- CDE logic
- Decision Brief strategy logic
- `portfolio.local.yaml`

It does not introduce:

- ML training
- trading execution
- broker connectivity
- Buy / Sell output
- prediction systems
- portfolio automation

## Status

Implemented — runtime infrastructure only.

## Final Decision

READY FOR RUNTIME DAEMON VALIDATION REVIEW
