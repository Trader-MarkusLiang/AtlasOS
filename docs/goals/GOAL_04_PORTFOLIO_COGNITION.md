# GOAL 04 — PORTFOLIO COGNITION

## Objective

Make Atlas reasoning materially portfolio-aware without enabling trading.

## Inputs

- asset
- market
- percentage
- theme
- role
- thesis
- risk note

No exact amount required.

## Required Outputs

- asset concentration
- theme concentration
- market concentration
- liquidity sensitivity
- regime sensitivity
- correlated risk clusters
- portfolio relevance

## Required Differential Test

Same market state.

Portfolio A
Portfolio B
Portfolio C
No portfolio

Portfolio impact must differ.

## Runtime Path

UI
→ local config
→ runtime load
→ portfolio context
→ DecisionLoop
→ Decision Brief
→ UI

## Acceptance

Complete only if UI-configured portfolio changes normal runtime output.

## Deliverable

99_Verification/GOAL_04_Portfolio_Cognition_Report.md

## Transition

Proceed to:

GOAL_05_FORECAST_ACCOUNTABILITY
