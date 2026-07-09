# Atlas OS Home Intelligence Baseline

Date: 2026-07-10 CST

## Purpose

This file is the required baseline artifact for the Home Intelligence Surface Rebuild goal.
It preserves the truth-audit findings from
`99_Verification/Atlas_OS_Home_Intelligence_Surface_Baseline.md` and records the current
post-rebuild evidence used for final acceptance.

## Baseline Summary

Before the rebuild, Home was decision-first but incomplete as a decision intelligence surface.

| Capability | Baseline Classification | Evidence |
|---|---|---|
| Current State | `PRESENT_AND_CONNECTED` | Home read `/state.last_decision_packet`, `regime_state`, market state, trust, and portfolio context. |
| Expert Details | `PRESENT_BUT_RAW` | Expert information existed as raw JSON under a generic details block. |
| Expert Analysis | `MISSING_FROM_UI` | No structured causal chain, hypothesis, confidence composition, data quality, forecast evidence, or raw-evidence boundary existed. |
| Market Outlook | `MISSING_FROM_UI` | No first-class forward view existed on Home. |
| Candidate Pool | `PRESENT_BUT_DISCONNECTED` | `02_Databases/AI_Shovel_100.md` contained Priority S/A/B candidates, but Home had no candidate surface. |
| Forecast Ledger | `PRESENT_AND_CONNECTED` on `/predictions`; `PRESENT_BUT_DISCONNECTED` on Home | Ledger rows existed through `runtime/forecast_ledger.py`, but Home did not expose forecast accountability. |
| Portfolio Relevance | `PRESENT_AND_CONNECTED` | Home and `/state.portfolio_context` exposed percentage-only portfolio context. |
| Invalidation Conditions | `PRESENT_BUT_PARTIAL` | Generic invalidation existed, but forecast invalidation evidence was not first-class. |
| ZH/EN Parity | `PARTIAL` | Existing language modes worked, but required new intelligence zones were absent. |

## Current Rebuild Evidence

Current local `/state` and presentation adapter evidence:

| Item | Current Evidence |
|---|---|
| Candidate pool | `available`, 27 items from `02_Databases/AI_Shovel_100.md` |
| Candidate filters | all 27, portfolio-related 7, high-priority 20, new 0, changed-recently 6 |
| Forecast accountability | 25 open forecasts; 0 matured / verified / invalidated / inconclusive in current local sample |
| Market outlook | `available`, source `forecast_ledger + current_runtime_state` |
| Outlook / ledger boundary | `distinct_from_forecast_ledger: true` |
| Expert analysis | `available`, 9 sections |
| Data quality | 2 live channels, 2 simulated channels, 4 missing channels, 0 stale channels |
| Portfolio context | configured, 80.0% configured exposure, 20.0% unallocated buffer |
| E2E | `99_Verification/artifacts/home_intelligence/browser_e2e_results.json` status `PASS` |

## Boundary

All rebuild work is presentation-layer only:

- `ui/**`
- read-only presentation adapters
- read-only state aggregation
- verification artifacts under `99_Verification/**`

No Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, Decision Contract, CDE authority, forecast lifecycle
semantics, portfolio mutation, runtime scheduler, self-iteration semantics, broker execution, or
trading authority were modified.

