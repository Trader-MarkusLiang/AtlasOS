# ISSUE-2026-058 — Forecast Lifecycle Runtime Closure Gap

## Status

Resolved for new runtime forecasts; legacy records remain classified

## Origin

User Feedback / Runtime Audit

## Date First Seen

2026-07-12

## Date Last Seen

2026-07-12

## Frequency

Every material or non-material DecisionLoop cycle currently attempts forecast registration.

## Affected Area

Decision Brief / Research / Engineering

## Problem

Normal runtime creates repeated structural forecasts but does not automatically deduplicate them,
mark them mature, attach later observed outcomes, or evaluate them. The live ledger therefore grows
with open forecasts while providing no ongoing calibration evidence.

## Context

The live state showed open forecasts with zero matured and zero evaluated outcomes. Controlled
verification proves lifecycle functions individually, but normal unattended runtime does not close
the lifecycle.

## Impact

High

## Evidence

- `runtime/decision_loop.py` registers a runtime forecast after each processed event batch.
- `runtime/forecast_ledger.py` exposes maturity and evaluation functions, but the normal daemon path
  does not call them before registering later equivalent forecasts.
- Live evidence is recorded in `99_Verification/Investor_Home_Truth_Baseline.md`.

## Root Cause Hypothesis

Forecast accountability was added as a persistence backbone before material-change deduplication and
automatic outcome processing were connected to the normal runtime path.

## Possible Solutions

- Define a deterministic material forecast signature.
- Reuse an equivalent open forecast instead of creating one per heartbeat.
- Mature forecasts when their supported observation horizon is reached.
- Attach the next eligible observed runtime state and evaluate through the existing ledger API.
- Keep calibration claims disabled until evaluated sample requirements are met.

## Priority

P0

## Decision

Implement as a bounded extension of the existing Forecast Ledger and DecisionLoop integration.

## Linked IP

None. This closes an existing runtime accountability path and does not introduce a prediction engine.

## Notes

Forecast outcomes must come from later runtime observations. Do not invent outcomes or use fixture
evidence as proof of normal runtime closure.

## Resolution Evidence

- Forecast creation now requires a material non-simulated event.
- Material signatures prevent repeated equivalent forecasts.
- The next eligible runtime cycle matures, attaches an observed state, and evaluates the forecast.
- Forecast misses feed bounded trust, hypothesis scoring, and structural mutation metadata.
- Historical open forecasts without a material signature remain explicitly classified as legacy
  unclassified records and are not bulk-evaluated.
- See `99_Verification/Investor_Home_Runtime_Evidence_Report.md`.
