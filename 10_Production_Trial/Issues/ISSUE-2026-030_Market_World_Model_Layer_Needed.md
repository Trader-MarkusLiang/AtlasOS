# ISSUE-2026-030 — Market World Model Layer Needed

## Status

Open / Accepted / Converted to IP / Implemented

## Origin

Production Trial / Atlas OS v0.6 Market World Model Layer request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime / Cognitive Layer / Market World Model / Structural Dynamics

## Problem

Atlas OS v0.5 can explain causal structure behind regime formation, but it does not yet model how
market structure evolves over time as a continuous state. The system needs an interpretable world
model layer that can simulate structural evolution without becoming a price forecast or trading
model.

## Context

The v0.6 request requires:

- Market state space model.
- State transition function.
- Attention -> liquidity transformation model.
- Regime emergence dynamics.
- Counterfactual market simulation.

## Impact

Medium / High

Potential effects if unresolved:

- Atlas can explain why market moved but not how the structure evolves.
- Counterfactual reasoning remains node-local instead of trajectory-based.
- Market state remains too close to event classification.

## Evidence

User request:

```text
Atlas OS v0.6 MUST evolve from “Why did market move?” to
“How does market structure evolve over time?”
```

## Root Cause Hypothesis

v0.5 CIL defines causal structure, but it does not maintain an explicit MarketState(t) vector or
simulate state transitions across time.

## Possible Solutions

- Add `runtime/cognition/world_model_engine.py`.
- Build a deterministic MarketState(t) vector.
- Add state transition and scenario trajectory functions.
- Integrate output into DecisionLoop cognition state after CIL and before State Controller.
- Validate with state evolution, attention-liquidity transformation, regime emergence, and
  counterfactual trajectory tests.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement v0.6 as a bounded, interpretable runtime cognition
layer.

## Linked IP

IP-2026-030 — Market World Model Layer v0.6

## Notes

This issue does not authorize ML, deep learning, reinforcement learning, Event Fusion modification,
Regime Memory modification, direct CIL modification, CDE bypass, trading execution, Buy / Sell
recommendations, portfolio automation, or forecast-model behavior.
