# Atlas OS Strongest Prediction Report

Date: 2026-07-10

## Requirement

Home must show maximum 3 strongest predictions. Each prediction must include judgment, confidence,
horizon, evidence, and invalidation. Atlas must not fabricate conviction.

## Implementation Evidence

- View model: `_strongest_predictions`
- DOM anchor: `#home-strongest-predictions`
- Validator checks: `C_strongest_predictions_max_3`, `D_prediction_required_fields`

## Current Projection

Home shows the strongest available runtime forecast from Forecast Ledger as low conviction. It is
explicitly labeled as the strongest available runtime forecast, not a high-conviction call.

## Current Fields

- Confidence: derived from Forecast Ledger / DecisionPacket.
- Horizon: Forecast Ledger horizon.
- Evidence: causal drivers plus fresh portfolio price/volume observations when present.
- Invalidation: Forecast Ledger invalidation conditions.

## Result

PASS.
