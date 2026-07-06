# Causal Self-Discovery v0.7 Validation Result

Date: 2026-07-06
Status: Pass

## Scope

Atlas OS v0.7 adds a causal self-discovery layer above the explanation-driven correction system.
The layer treats explanations as competing hypotheses, not final truth.

## Implemented Components

- `runtime/cognition/causal_hypothesis_engine.py`
  - Generates multiple structural causal graph variants per event window.
  - Marks each hypothesis as a non-truth claim.
- `runtime/cognition/hypothesis_scoring_engine.py`
  - Scores hypotheses with deterministic factors:
    - historical consistency,
    - explanation error reduction proxy,
    - regime stability,
    - trust alignment,
    - simplicity versus accuracy tradeoff.
- `runtime/cognition/causal_structure_selector.py`
  - Selects one active causal structure.
  - Retains shadow hypotheses.
  - Applies switching cooldown and low-trust reduced switching.
- `runtime/cognition/hypothesis_memory.py`
  - Stores selected and rejected hypotheses with regime context and selection rationale.
- `runtime/cognition/explanation_error_engine.py`
  - Adds `compute_multi_explanation_competition()` for:
    - explanation divergence,
    - structural divergence,
    - causal conflict,
    - model instability pressure.
- `runtime/decision_loop.py`
  - Integrates hypothesis generation, scoring, active selection, competition metrics, and memory
    persistence after explanation-error computation and before structural co-evolution.

## Boundary Result

No intended changes were made to:

- Event Fusion Engine.
- LMSE definitions.
- MPCE definitions.
- MLE definitions.
- Decision Contract schema.
- CDE rules.
- Portfolio files.

The v0.7 layer is metadata-only and does not introduce trading execution, prediction output,
portfolio mutation, ML training, deep learning, reinforcement learning, or broker integration.

## Validation Coverage

`99_Verification/validate_causal_self_discovery_v0_7.py` checks:

1. Multi-hypothesis generation produces at least three causal models.
2. Hypotheses differ structurally by graph signatures and edge sets.
3. Hypothesis scoring ranks all models and emits a score distribution.
4. High-trust regime shift can switch active hypothesis.
5. One-tick oscillation is blocked by selection stability rules.
6. Low trust blocks hypothesis switching.
7. Multi-explanation competition emits divergence and conflict metrics.
8. Hypothesis memory records selected and rejected structures.
9. Three runtime ticks persist:
   - `cognition_state.causal_hypotheses`,
   - `cognition_state.hypothesis_scoring`,
   - `cognition_state.active_causal_structure`,
   - `cognition_state.multi_explanation_competition`,
   - `causal_hypothesis_memory`.
10. Forbidden core files do not import v0.7 hypothesis modules.

## Three-Cycle Demonstration

Expected behavior under the validation daemon:

| Cycle | Expected Causal Discovery Behavior |
| --- | --- |
| 1 | Generate plural hypotheses and initialize an active causal structure. |
| 2 | Preserve shadow hypotheses and update memory without forced truth collapse. |
| 3 | Continue scoring under memory context; switch only if trust and stability gates allow it. |

## Risk Analysis

- Overfitting risk: reduced by deterministic scoring, structural simplicity scoring, and shadow
  model retention.
- Model plurality risk: mitigated by one active structure plus shadow hypotheses rather than
  multiple simultaneous control outputs.
- Oscillation risk: mitigated by minimum active age, switch margin, and low-trust reduced switching.
- Architecture coupling risk: controlled by keeping v0.7 imports out of Event Fusion, LMSE, MPCE,
  MLE, and Decision Contract.

## Command Verification

To be filled after execution:

```text
py_compile: PASS
validate_causal_self_discovery_v0_7.py: PASS
validate_explanation_self_correction_v0_6.py: PASS
validate_structural_coevolution_v0_4.py: PASS
validate_runtime_daemon_v0_1.py: PASS
boundary scan: PASS
```
