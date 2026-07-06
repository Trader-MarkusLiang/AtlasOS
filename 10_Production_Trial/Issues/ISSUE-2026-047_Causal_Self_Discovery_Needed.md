# ISSUE-2026-047 — Causal Self-Discovery Needed

## Status

Implemented

## Origin

Atlas OS v0.7 Causal Self-Discovery Layer request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime Cognition / Causal Hypothesis Selection / Explanation Feedback

## Problem

Atlas v0.6 can correct explanations, but it still treats the current explanation path as the main
causal model. Atlas needs multiple competing causal hypotheses, scoring, active model selection,
shadow hypotheses, and memory of why hypotheses were selected or rejected.

## Context

The layer must preserve strict boundaries:

- Do not modify Event Fusion core logic.
- Do not modify LMSE / MPCE / MLE definitions.
- Do not modify Decision Contract schema.
- Do not introduce ML/DL/RL training loops.
- Do not introduce trading or prediction logic.
- Do not override trust calibration.

## Impact

High

Potential effects if unresolved:

- Explanations can become over-anchored to one causal structure.
- Corrective feedback lacks model plurality.
- Regime shifts cannot rotate causal interpretation without manual model assumptions.

## Evidence

User request:

```text
explanations are no longer truth; they are hypotheses
```

## Root Cause Hypothesis

v0.6 computes explanation error and edge correction, but does not generate structurally distinct
causal graph variants or choose among them over time.

## Possible Solutions

- Add causal hypothesis generation.
- Add deterministic hypothesis scoring.
- Add non-permanent active causal structure selection.
- Add hypothesis memory in StateStore.
- Extend explanation error with multi-explanation competition metrics.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement bounded causal self-discovery.

## Linked IP

IP-2026-047 — Causal Self-Discovery v0.7

## Notes

This issue does not authorize trading logic, prediction logic, ML/DL/RL training, broker
integration, portfolio automation, trust calibration override, Decision Contract schema changes, or
core cognition definition rewrites.

