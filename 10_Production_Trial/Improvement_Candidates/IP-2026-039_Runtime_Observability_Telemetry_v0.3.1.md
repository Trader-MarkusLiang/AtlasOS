# IP-2026-039 — Runtime Observability & LLM Telemetry v0.3.1

## Category

Engineering / Runtime Infrastructure / Observability

## Origin

ISSUE-2026-039 — Runtime Observability / Telemetry Needed

## Problem

Atlas Runtime v0.3 supports LLM cognitive feedback, but needs transparent telemetry for LLM calls,
DecisionPacket path reconstruction, cognitive snapshots, replay, and lightweight inspection.

## Implemented Scope

- Added `runtime/telemetry/llm_trace_logger.py`.
- Added `runtime/telemetry/decision_trace_logger.py`.
- Added `runtime/telemetry/state_snapshot.py`.
- Added `runtime/telemetry/replay_engine.py`.
- Added `web/dashboard_observability.py`.
- Updated `runtime/llm_router.py` with a non-blocking LLM trace hook.
- Updated `runtime/decision_loop.py` to expose telemetry-ready feedback risk delta.
- Updated `runtime/atlas_runtime_daemon.py` with per-tick decision trace and cognitive snapshot
  hooks.
- Added `99_Verification/validate_runtime_observability_v0_3_1.py`.

## Telemetry Logs

```text
runtime/logs/llm_traces.jsonl
runtime/logs/decision_traces.jsonl
runtime/logs/cognitive_snapshots.jsonl
```

Each log is append-only JSONL and best-effort. Logging failures do not block the runtime tick loop.

## Replay

`runtime/telemetry/replay_engine.py` reconstructs recorded decision paths from telemetry logs. It
does not re-run cognition and does not mutate runtime state.

## Dashboard

`web/dashboard_observability.py` exposes JSON views for:

- tick timeline
- regime state evolution
- attention / liquidity / volatility trend fields
- LLM call counts
- feedback delta heatmap
- replay endpoint

## Boundary

This IP does not modify:

- Event Fusion logic
- CIL / LMSE / MPCE / MLE logic
- Decision Contract semantics
- LLM reasoning behavior
- feedback computation logic
- CDE logic
- `portfolio.local.yaml`

It does not introduce:

- prediction logic
- trading logic
- broker connectivity
- portfolio automation

## Status

Implemented — observability / diagnostics only.

## Final Decision

READY FOR OBSERVABILITY REVIEW
