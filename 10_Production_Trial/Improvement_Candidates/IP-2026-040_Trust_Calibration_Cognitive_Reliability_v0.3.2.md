# IP-2026-040 — Trust Calibration & Cognitive Reliability v0.3.2

## Category

Engineering / Runtime Infrastructure / Trust Calibration

## Origin

ISSUE-2026-040 — Trust Calibration / Cognitive Reliability Needed

## Problem

Atlas Runtime has cognitive feedback and observability, but needs a meta-confidence layer that
scores reliability of LLM outputs, cognitive feedback, regime stability, and causal reasoning
without changing cognition.

## Implemented Scope

- Added `runtime/cognition/trust_score_engine.py`.
- Added `runtime/cognition/system_trust_state.py`.
- Updated `runtime/decision_loop.py` to compute and persist trust metadata.
- Updated `runtime/cognition/llm_cognitive_feedback_engine.py` to attach trust weighting metadata
  without modifying feedback deltas.
- Updated `runtime/telemetry/decision_trace_logger.py` with:
  - `calibrated_confidence`
  - `confidence_adjustment_factor`
- Updated `runtime/telemetry/llm_trace_logger.py` with:
  - `output_stability_score`
  - `hallucination_risk_proxy`
  - `response_consistency_index`
- Updated `runtime/telemetry/state_snapshot.py` to include `trust_state`.
- Added `99_Verification/validate_trust_calibration_v0_3_2.py`.

## Trust Score

```python
trust_score = {
    "llm_trust": float,
    "cognitive_trust": float,
    "regime_stability_trust": float,
    "feedback_consistency_trust": float,
    "global_trust_index": float,
}
```

## System Trust State

```python
{
    "rolling_trust_index": float,
    "llm_provider_trust": dict,
    "regime_trust_decay": float,
    "feedback_stability_index": float,
}
```

## Boundary

This IP does not modify:

- Event Fusion logic
- CIL / LMSE / MPCE / MLE logic
- Decision Contract structure
- LLM reasoning behavior
- cognitive outputs
- CDE logic
- `portfolio.local.yaml`

It does not introduce:

- prediction logic
- trading logic
- broker connectivity
- portfolio automation

## Status

Implemented — metadata-only trust calibration.

## Final Decision

READY FOR TRUST CALIBRATION REVIEW
