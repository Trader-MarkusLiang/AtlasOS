# Regime Engine v3 Boundary Review

Date: 2026-07-05

## Result

PARTIAL / BLOCKED FOR IMPLEMENTATION

## Scope Classification

The user request contains two different layers:

| Layer | Decision |
|---|---|
| Investment logic upgrade: Attention -> Flow -> Price -> Transition Probability | ACCEPT as architecture direction |
| Runtime deliverables: `regime_engine_v3.py`, `attention_flow_model.py`, `market_regime_transition.py` | BLOCK under current Production Trial rules |

## Module Boundary Decision

This request should first enter Atlas Issue System and Proposed IP flow.

It should not directly modify:

- CDE formulas.
- Decision Brief strategy logic.
- Portfolio files.
- Runtime market-data code.
- AGENTS rules.

## Project-Stage Risk

Atlas is in Production Trial.

Production Trial permits:

- bug fixes
- usability polish
- issue recording
- architecture review
- acceptance test planning

Production Trial does not permit direct creation of a new runtime regime engine without approved
Issue -> IP -> Architecture Review -> Acceptance Test -> Implementation.

## Why Runtime Files Were Not Created

The requested files:

- `regime_engine_v3.py`
- `attention_flow_model.py`
- `market_regime_transition.py`

would introduce executable regime logic and therefore cross the current boundary from architecture
proposal into runtime implementation.

They were not created.

## What Was Preserved

The core method was preserved as proposed architecture:

```text
Attention -> Flow Inference -> Price Feedback -> Regime Transition Probability
```

The proposal records:

- Attention Score.
- Attention Velocity.
- Attention Acceleration.
- Narrative Concentration Index.
- Expected Retail Flow Probability.
- Expected Institutional Follow-through.
- Liquidity Inflow Strength.
- Price Acceleration Index.
- Trend Sustainability Score.
- Regime Probability Vector.
- Attention Lifecycle Model.
- Low-data inference mode.

## Boundary Verification

| Boundary | Result |
|---|---|
| No runtime implementation | PASS |
| No `regime_engine_v3.py` | PASS |
| No `attention_flow_model.py` | PASS |
| No `market_regime_transition.py` | PASS |
| No new Engine | PASS |
| No AGENTS modification | PASS |
| No Decision Brief strategy logic modification | PASS |
| No CDE formula modification | PASS |
| No `portfolio.local.yaml` modification | PASS |
| No private amount stored | PASS |
| No automatic trading | PASS |
| No Buy / Sell language as Atlas action | PASS |

## Final Decision

`READY FOR DISCUSSION / NOT READY FOR IMPLEMENTATION`

Implementation requires explicit approval after Architecture Review and Acceptance Test definition.
