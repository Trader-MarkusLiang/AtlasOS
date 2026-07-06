# ISSUE-2026-046 — Explanation Self-Correction Needed

## Status

Implemented

## Origin

Atlas OS v0.6 Explanation-Driven Self-Correction Layer request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime Cognition / Explanation Feedback / Structural Adaptation

## Problem

Atlas can explain decisions and visualize cognitive state, but explanation quality does not yet
feed back into bounded causal correction. A wrong or incomplete explanation should be able to
produce a trust-gated, reversible adjustment signal without rewriting the cognitive core.

## Context

The layer must be self-correcting but not self-training:

- Do not modify Event Fusion core logic.
- Do not modify LMSE / MPCE / MLE definitions.
- Do not modify Decision Contract structure.
- Do not introduce ML/RL training.
- Do not introduce trading or prediction logic.

## Impact

High

Potential effects if unresolved:

- Explanations remain telemetry-only.
- Repeated explanatory mismatch cannot reduce overestimated causal factors.
- Causal drift remains detached from explanation errors.

## Evidence

User request:

```text
explanation becomes a feedback signal NOT just telemetry output.
```

## Root Cause Hypothesis

Previous layers compute explanations, trust, and structural drift separately, but the decision loop
does not yet compute explanation error or convert it into bounded causal edge correction metadata.

## Possible Solutions

- Add an explanation error engine.
- Add a trust-gated causal self-correction engine.
- Add regime explanation alignment.
- Integrate explanation feedback after DecisionPacket generation and trust scoring.
- Pass correction metadata into structural drift as bounded reversible edge deltas.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement bounded explanation-driven self-correction.

## Linked IP

IP-2026-046 — Explanation Self-Correction v0.6

## Notes

This issue does not authorize trading logic, prediction logic, ML/RL, broker integration, direct
portfolio changes, Decision Contract changes, or core cognition definition rewrites.

