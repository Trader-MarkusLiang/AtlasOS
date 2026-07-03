# IP-2026-021 — Market Regime Early Warning v0.1

## Category

Market Regime / CDE Support / Rebalance Support / User Experience

## Origin

ISSUE-2026-021 — Market Regime Early Warning Missing

## Problem

Atlas can identify instrument-level overextension and execution anomaly, but it does not yet
summarize whether the broader domestic technology market is in a healthy risk-on state, fragile
uptrend, distribution warning, risk-off state, or crash-stress state.

This creates a gap between:

- Execution warning: Atlas can cap migration authority.
- Market-regime warning: Atlas cannot yet explain whether the whole market environment has changed.

## Root Cause

Domestic Market Snapshot and Data Anomaly Check operate at the holding / candidate level. Rebalance
Execution Plan uses those checks to cap migration, but Atlas does not yet aggregate them into a
market-regime layer using breadth, sector diffusion, anomaly concentration, holding deterioration,
and sentiment overheating.

## Expected Improvement

Future implementation should add a lightweight market-regime early warning output that helps Atlas
answer:

- What is the current domestic technology market regime?
- Is the market merely extended, or has it entered distribution / risk-off?
- Should CDE precision be limited?
- Should Rebalance Authority be capped?
- Should the user prioritize capital preservation over new deployment?

## Proposed Future Fields

- Market Regime.
- Risk-On / Extended Risk-On / Fragile Uptrend / Distribution Warning / Risk-Off / Crash Stress.
- Breadth Status.
- Sector Diffusion.
- Candidate Pool Overheat Ratio.
- Holding Breakdown Ratio.
- Decision Impact.
- CDE Precision Status.
- Rebalance Authority Cap.

## Affected Modules

Potential future affected modules, subject to Architecture Review:

- `tools/market_data/domestic_market_snapshot.py`
- `tools/market_data/data_anomaly_check.py`
- `06_Portfolio/Rebalance_Execution_Plan_v0.1.md`
- `10_Capital_Deployment_Engine/Capital_Deployment_Engine.md`
- `08_Daily_Operating_Cycle/Decision_Brief_Template.md`
- `.agents/skills/atlas-portfolio/SKILL.md`
- `.agents/skills/atlas-daily/SKILL.md`
- `.agents/skills/atlas-research/SKILL.md`
- `99_Verification/Regression_Tests.md`

## Priority

P1

## Status

Proposed

## Compatibility

This proposal is not implemented in this task. It does not create a new Engine, modify CDE
formulas, modify Decision Brief strategy logic, modify portfolio allocation, store private amounts,
or enable automatic trading.

## Approval

Requires user discussion, Architecture Review, Acceptance Test definition, and explicit approval
before implementation.
