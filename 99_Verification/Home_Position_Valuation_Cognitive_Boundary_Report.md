# Home Position Valuation Cognitive Boundary Report

Date: 2026-07-14

Linked Issue: `ISSUE-2026-061`

## Classification

`PRESENTATION_AND_LOCAL_PORTFOLIO_INFRASTRUCTURE_ONLY`

## Protected Semantics

No implementation diff exists in:

- `runtime/cognition/`
- `runtime/decision_loop.py`
- Event Fusion
- CIL / LMSE / MPCE / MLE / UMIS
- Decision Contract
- trust computation
- forecast accountability
- hypothesis selection
- CDE authority
- broker or trading execution

Task-aware Workhorse, Research, and Decision routing regression validation remains PASS.

## Safe Path

```text
ignored local config
-> runtime.portfolio_valuation
-> normalized public market observation
-> Decimal calculation
-> visibility filtering
-> server-rendered localhost Home
```

## Unchanged Cognition Path

```text
ignored local config
-> runtime.portfolio_context.build_portfolio_context
-> percentage-only exposure context
-> EventStream / DecisionLoop / cognition / LLM
```

The second path still drops average cost, quantity, total cost, market value, and PnL fields.

## Decision Semantics

Cost and PnL are shown beside existing Atlas posture, thesis context, risk trigger, and review
priority. They do not compute or override posture. Profit is not thesis validation; loss is not
thesis invalidation. Configured allocation is labeled separately from unavailable estimated current
weight. CDE authority remains unchanged and no action is generated from cost alone.

## Result

`PASS`
