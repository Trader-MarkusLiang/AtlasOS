# ISSUE-2026-039 — Runtime Observability / Telemetry Needed

## Status

Implemented

## Origin

Atlas OS v0.3.1 — Runtime Observability & LLM Telemetry Layer request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime / Observability / LLM Traceability / Cognitive Replay

## Problem

Atlas Runtime v0.3 has cognitive feedback, but runtime execution is not fully observable. The user
requested LLM call tracing, decision trace logging, cognitive snapshots, replay capability, and a
minimal observability dashboard.

## Context

The requested change must add visibility only:

- LLM telemetry logger
- Decision trace logger
- Cognitive state snapshot engine
- Replay engine
- Minimal JSON dashboard

## Impact

Medium / High

Potential effects if unresolved:

- LLM calls cannot be audited.
- Cognitive feedback and decision packets cannot be replayed per tick.
- Runtime remains difficult to inspect during failures.

## Evidence

User request:

```text
This version does NOT change intelligence.
It adds full runtime visibility, LLM call tracing, decision replay capability, cognitive state
inspection tools, and feedback visualization data logs.
```

## Root Cause Hypothesis

Runtime v0.3 added feedback, but telemetry was not yet separated into append-only diagnostic logs.

## Possible Solutions

- Add telemetry modules under `runtime/telemetry/`.
- Add minimal JSON dashboard under `web/dashboard_observability.py`.
- Add non-blocking telemetry hooks in `runtime/llm_router.py` and `runtime/atlas_runtime_daemon.py`.
- Validate trace completeness, replay consistency, and non-intrusive behavior.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement as visibility / diagnostics infrastructure only.

## Linked IP

IP-2026-039 — Runtime Observability & LLM Telemetry v0.3.1

## Notes

This issue does not authorize Event Fusion logic changes, CIL / LMSE / MPCE / MLE logic changes,
Decision Contract semantic changes, LLM behavior changes, feedback computation changes, prediction
logic, trading logic, CDE bypass, or portfolio modification.
