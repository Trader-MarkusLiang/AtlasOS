# ISSUE-2026-022 — Attention-Flow Regime Transition Request

## Status

Open / Accepted for Architecture Review

## Origin

Production Trial / User Architecture Request / Market Regime Early Warning Review

## Date First Seen

2026-07-05

## Date Last Seen

2026-07-05

## Frequency

1

## Affected Area

Decision Brief / CDE / Rebalance / Strategic Candidate Dashboard / Market Regime / Research /
Engineering

## Problem

Atlas currently has a proposed Market Regime Early Warning architecture centered on Attention
Momentum, Narrative Crowding, Attention Exhaustion, and Attention-Price Divergence. The user now
identified a deeper requirement:

Atlas should not stop at regime classification or rule-based warning.

Atlas should reason about market regime transitions probabilistically through:

```text
Attention -> Capital Flow -> Price Acceleration -> Regime Transition Probability
```

The requested system would estimate:

- Attention Score.
- Attention Velocity.
- Attention Acceleration.
- Narrative Concentration.
- Expected Retail Flow Probability.
- Expected Institutional Follow-through.
- Liquidity Inflow Strength.
- Price Acceleration.
- Trend Sustainability.
- Regime Probability Vector.

## Context

The request was framed as:

`Atlas OS Upgrade — Regime Engine v3: Attention-Flow Market Transition System`

Requested runtime deliverables included:

- `regime_engine_v3.py`
- `attention_flow_model.py`
- `market_regime_transition.py`
- AGENTS updates.
- Decision Brief Template updates.
- Regression Tests.

However, Atlas is currently in Production Trial. Current rules prohibit direct runtime engine
implementation without Issue discussion, priority review, Architecture Review, Acceptance Test, and
explicit approval.

## Impact

High

If validated, this could materially improve Atlas by:

- detecting regime change before price breakdown
- distinguishing attention surge from real capital inflow
- identifying narrative-driven bubbles earlier
- reducing lagging technical-indicator dependency
- improving Decision Brief and Strategic Candidate Dashboard risk context

## Evidence

- `ISSUE-2026-021` showed Atlas had execution-level warnings but lacked full market-regime warning.
- `IP-2026-021` proposed Market Regime Early Warning v0.1 with Attention Momentum and Narrative
  Crowding.
- The current user request extends that architecture from static warning labels toward transition
  probability vectors.

## Root Cause Hypothesis

The current proposed architecture still risks behaving like a classification system unless Atlas
explicitly models the transition chain:

```text
attention change -> flow probability -> price feedback -> regime transition probability
```

## Possible Solutions

- Preserve this as a Proposed IP, not runtime code.
- Add an architecture review for Attention-Flow Market Transition.
- Define output schema for regime probability vector.
- Define validation cases before implementation.
- Decide later whether this belongs as:
  - an extension of Market Regime Early Warning
  - an enhancement to Decision Brief risk context
  - a lightweight model layer
  - or a future engine, if Production Trial stage changes

## Priority

P1

## Decision

Discuss / Convert to Improvement Proposal

## Linked IP

IP-2026-022 — Attention-Flow Market Transition System v0.1

## Notes

No runtime code is authorized by this issue.

This issue records the production problem and architecture direction only.

Implementation requires separate user approval after Architecture Review and Acceptance Test design.
