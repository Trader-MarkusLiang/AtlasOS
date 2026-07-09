# Atlas OS Expert Analysis Report

Date: 2026-07-10 CST

## Verdict

`PRESENT_AND_CONNECTED`

Home now has a structured Expert Analysis / 专家分析 panel. It is collapsed by default, discoverable
from the Home view switch, and no longer raw JSON-only.

## Required Sections

| Section | Status |
|---|---|
| A. Causal Chain / 因果链 | `PASS` |
| B. Hypothesis State / 假设状态 | `PASS` |
| C. Regime State / 市场状态 | `PASS` |
| D. Confidence Composition / 置信度构成 | `PASS` |
| E. Data Quality / 数据质量 | `PASS` |
| F. Portfolio Sensitivity / 组合敏感性 | `PASS` |
| G. Forecast Evidence / 预测证据 | `PASS` |
| H. Invalidation Conditions / 失效条件 | `PASS` |
| I. Raw Evidence / 原始证据 | `PASS` |

## Evidence Sources

The expert panel is built from existing evidence only:

- `/state.regime_state`
- `/state.last_decision_packet`
- `/state.market_intelligence`
- `/state.portfolio_context`
- `/state.structural_coevolution_state`
- `/state.self_organization_state`
- `/state.forecast_ledger`

## Data Quality Link To Confidence

Current data-quality projection:

- Live channels: 2
- Simulated channels: 2
- Missing channels: 4
- Stale channels: 0
- Limitation: confidence is limited by missing, stale, or unconfigured market channels

The confidence composition breaks out:

- evidence quality
- market data completeness
- hypothesis stability
- portfolio relevance
- forecast history

## Raw Evidence Boundary

Raw JSON is only under the nested Raw Evidence / 原始证据 disclosure. The primary expert panel is
structured text and compact metrics.

## Browser Evidence

`99_Verification/artifacts/home_intelligence/browser_e2e_results.json`:

- Step 20: Expand Expert Analysis `PASS`
- Step 21: Inspect Causal Chain `PASS`
- Step 22: Inspect Hypothesis State `PASS`
- Step 23: Inspect Confidence Composition `PASS`
- Step 24: Inspect Data Quality `PASS`
- Step 25: Inspect Forecast Evidence `PASS`
- Step 26: Inspect Invalidation `PASS`
- Step 27: Expand Raw Evidence `PASS`
- Step 28: Collapse Raw Evidence `PASS`

