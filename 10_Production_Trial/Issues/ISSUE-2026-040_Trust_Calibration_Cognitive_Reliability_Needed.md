# ISSUE-2026-040 — Trust Calibration / Cognitive Reliability Needed

## Status

Implemented

## Origin

Atlas OS v0.3.2 — Trust Calibration & Cognitive Reliability Layer request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime / Trust Calibration / Cognitive Reliability / Telemetry

## Problem

Atlas Runtime has LLM feedback and observability, but does not yet compute a system-wide
meta-confidence score for LLM outputs, feedback consistency, regime stability, and causal
reliability.

## Context

The requested layer must evaluate reliability only:

- LLM trust
- cognitive trust
- regime stability trust
- feedback consistency trust
- rolling system trust state

## Impact

Medium / High

Potential effects if unresolved:

- runtime confidence drift is visible only indirectly
- repeated unstable feedback does not reduce meta-confidence
- stable repeated alignment does not increase trust state
- telemetry lacks calibrated confidence metadata

## Evidence

User request:

```text
Atlas OS v0.3.2 adds meta-confidence over cognition, NOT new cognition.
```

## Root Cause Hypothesis

Runtime v0.3.1 observes cognition but does not score the reliability of observed outputs.

## Possible Solutions

- Add `runtime/cognition/trust_score_engine.py`.
- Add `runtime/cognition/system_trust_state.py`.
- Attach trust metadata in `runtime/decision_loop.py`.
- Add trust metadata to feedback state and cognitive snapshots.
- Add calibrated confidence fields to decision traces.
- Add reliability fields to LLM traces.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement as metadata-only trust calibration.

## Linked IP

IP-2026-040 — Trust Calibration & Cognitive Reliability v0.3.2

## Notes

This issue does not authorize Event Fusion changes, CIL / LMSE / MPCE / MLE changes, Decision
Contract structure changes, LLM reasoning behavior changes, prediction logic, trading logic, or
cognitive output overrides.
