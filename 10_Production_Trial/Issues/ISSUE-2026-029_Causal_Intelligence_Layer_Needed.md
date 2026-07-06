# ISSUE-2026-029 — Causal Intelligence Layer Needed

## Status

Open / Accepted / Converted to IP / Implemented

## Origin

Production Trial / Atlas OS v0.5 Causal Intelligence Layer request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime / Cognitive Layer / Causal Reasoning / Market Regime Formation

## Problem

Atlas OS v0.4.1 separates infrastructure ingestion from cognition, but the runtime cognition layer
still behaves primarily as a state-based regime system. It can fuse events, preserve memory, and
avoid state overwrite, but it does not yet express the causal structure behind regime formation.

## Context

The v0.5 request requires Atlas to reason about:

- Market causal graph structure.
- Attention as a causal symptom, not a direct signal.
- Flow propagation from attention into liquidity, price delay, and volatility.
- Regime emergence as an interaction process rather than a final label.
- Lightweight counterfactual inference without ML or stochastic simulation.

## Impact

Medium / High

Potential effects if unresolved:

- Same attention spike may be interpreted too similarly across different liquidity contexts.
- Regime output can remain too close to classification.
- Atlas can explain current state but not enough of why the regime is forming.

## Evidence

User request:

```text
Atlas OS v0.5 MUST evolve from “state classification system” to
“causal market structure reasoning system”.
```

## Root Cause Hypothesis

v0.3 / v0.4.1 cognition has event fusion, memory, and anti-overwrite control, but lacks an explicit
symbolic causal graph and counterfactual reasoning stage.

## Possible Solutions

- Add `runtime/cognition/causal_intelligence_layer.py`.
- Route DecisionLoop cognition through the Causal Intelligence Layer after Event Fusion and Regime
  Memory.
- Preserve compatibility fields consumed by State Controller.
- Add CIL-specific validation and regression coverage.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement v0.5 Causal Intelligence Layer under strict runtime
and trading boundaries.

## Linked IP

IP-2026-029 — Causal Intelligence Layer v0.5

## Notes

This issue does not authorize modification of Event Fusion Engine, Regime Memory, Input Router, DSA
adapter, CDE formulas, Decision Brief strategy logic, `portfolio.local.yaml`, trading execution,
Buy / Sell output, machine learning models, or portfolio automation.
