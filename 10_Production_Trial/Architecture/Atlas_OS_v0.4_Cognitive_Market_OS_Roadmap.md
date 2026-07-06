# Atlas OS v0.4 Roadmap -- Cognitive Market OS

Date: 2026-07-06

## Status

Roadmap proposed.

Phase 1 adapter boundary trial implemented through:

- `ISSUE-2026-027`
- `IP-2026-027`
- `runtime/adapter/dsa_bridge.py`

Full DSA infrastructure merge, causal engine, regime intelligence, trading execution, portfolio
automation, CDE bypass, and new investment authority remain not authorized.

Implementation requires:

- Issue registration.
- Architecture review.
- Acceptance tests.
- Explicit user approval.

## Phase 0 -- Current State: v0.3

Current implemented runtime cognition:

- Event Fusion Engine: working.
- Regime Memory: working.
- State Controller: working.
- Causal Inference: rule-based.
- Attention vs Liquidity separation: partial.

Known limitations:

- No true causal model.
- No reusable infrastructure extraction from external systems.
- Scheduler and runtime infrastructure are partially self-built.
- Some infrastructure responsibilities still sit too close to Atlas core cognition.

## Phase 1 -- Infrastructure Merge: DSA -> Atlas Adapter

Goal:

Reuse `daily_stock_analysis` as an infrastructure layer without making Atlas dependent on DSA
business logic.

Implementation status:

- Adapter boundary: implemented in `IP-2026-027`.
- External DSA source binding: not configured in this repository.
- Full infrastructure replacement: not implemented.

Infrastructure to extract only:

- Runtime Scheduler.
- FastAPI Web Host.
- LiteLLM Router.
- DataFetcherManager.
- Search / Social Sentiment.
- Logging system.

Atlas Adapter Layer responsibilities:

- Normalize market data.
- Transform DSA signals into Atlas events.
- Unify schema between external infrastructure and Atlas cognition.

Output:

Atlas remains an independent cognitive system above infrastructure.

Boundary:

DSA is infrastructure, not Atlas core. Atlas must not inherit DSA investment logic, portfolio
actions, trading authority, or strategy semantics.

## Phase 2 -- Cognitive System Stabilization

Goal:

Make Atlas OS deterministic under stress before adding deeper causal reasoning.

Tasks:

- Stabilize event fusion logic.
- Enforce regime memory persistence.
- Prevent state overwrite regressions.
- Unify attention vs liquidity scoring.

Output:

Stable market state machine plus memory system.

Acceptance focus:

- Same events can produce different state results when history differs.
- Crash / risk states cannot be overwritten by isolated attention events.
- Event fusion remains single-cycle and multi-factor, not independent event reactions.

## Phase 3 -- Causal Engine v0

Goal:

Introduce a causal reasoning layer without machine learning.

Scope:

- Define causal graph structure:
  - attention -> flow
  - liquidity -> volatility
  - narrative -> retail participation
- Implement counterfactual reasoning:
  - If attention were removed, would regime change?
  - If liquidity stress were removed, would volatility state persist?
  - If narrative crowding were removed, would retail flow probability still rise?

Output:

Atlas starts to explain why a regime is changing, not only what state it is in.

Boundary:

This is not a trading engine, not a predictive ML system, and not CDE authority. It can only improve
runtime context, confidence, and Decision Brief explanation.

## Phase 4 -- Regime Intelligence System

Goal:

Move from state machine control toward regime cognition.

Tasks:

- Build regime probability vector system.
- Integrate temporal decay memory.
- Add regime transition likelihood scoring.
- Enforce hysteresis control to prevent flip-flop states.

Output:

True regime-aware system.

Boundary:

Regime probability is decision context, not a direct action command. CDE authorization and user
confirmation remain mandatory for portfolio action.

## Phase 5 -- Full Atlas Cognitive OS

Goal:

Atlas OS becomes a continuous market cognition system with external infrastructure dependency kept
below Atlas core.

Final capabilities:

- Event fusion.
- Memory-based reasoning.
- Causal inference.
- Regime probability.
- Attention-flow modeling.
- Infrastructure-agnostic execution.

## Target Architecture

```text
Infra Layer (DSA)
        |
        v
Adapter Layer (Atlas Bridge)
        |
        v
Cognitive Layer (Atlas Core)
        |
        v
Decision Layer (CDE)
        |
        v
Portfolio Guidance Layer
```

## Non-Goals

v0.4 roadmap does not authorize:

- Trading execution.
- Automatic portfolio modification.
- Broker integration.
- CDE bypass.
- Strategy logic replacement.
- Heavy ML framework adoption.
- Deep learning or reinforcement learning.
- Turning Atlas into a DSA plugin.

## Roadmap Decision

`ROADMAP ACCEPTED AS PROPOSED DIRECTION / IMPLEMENTATION NOT AUTHORIZED`
