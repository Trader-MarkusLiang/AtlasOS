# IP-2026-047 — Causal Self-Discovery v0.7

## Category

Engineering / Runtime Cognition / Causal Hypothesis Selection

## Origin

ISSUE-2026-047 — Causal Self-Discovery Needed

## Problem

Atlas needs to represent explanations as competing causal hypotheses rather than one true
explanation. The system should generate multiple structural variants, score them, select an active
causal structure, keep shadow hypotheses, and remember selection context.

## Implemented Scope

- Added `runtime/cognition/causal_hypothesis_engine.py`.
- Added `runtime/cognition/hypothesis_scoring_engine.py`.
- Added `runtime/cognition/causal_structure_selector.py`.
- Added `runtime/cognition/hypothesis_memory.py`.
- Extended `runtime/cognition/explanation_error_engine.py` with multi-explanation competition
  metrics:
  - `explanation_divergence_index`
  - `causal_conflict_score`
  - `model_instability_pressure`
- Updated `runtime/decision_loop.py` to generate, score, select, and persist causal hypotheses.
- Added validation:
  - `99_Verification/validate_causal_self_discovery_v0_7.py`
  - `99_Verification/Causal_Self_Discovery_v0.7_Validation_Result.md`

## Boundary

This IP does not modify:

- Event Fusion core logic
- LMSE / MPCE / MLE definitions
- Decision Contract schema
- Trust calibration formulas
- CDE logic
- `portfolio.local.yaml`

It does not introduce:

- ML/DL/RL training loops
- trading logic
- prediction logic
- broker connectivity
- portfolio automation

## Status

Implemented — bounded causal self-discovery metadata layer with active/shadow hypotheses.

## Final Decision

READY FOR CAUSAL SELF-DISCOVERY REVIEW

