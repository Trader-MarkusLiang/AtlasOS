# Codex Session Log: Causal Self-Discovery v0.7

## Metadata

- Date: 2026-07-06
- Session id: 2026-07-06_1530_causal-self-discovery-v07
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Implement Causal Self-Discovery Layer for Atlas OS
- Status: Completed
- Branch: main

## User Request Summary

Upgrade Atlas OS from explanation-driven correction to causal hypothesis generation and selection.
Required modules include causal hypothesis generation, hypothesis scoring, active structure
selection, multi-explanation competition, and hypothesis memory. The implementation must not modify
Event Fusion core logic, LMSE / MPCE / MLE definitions, Decision Contract schema, ML/DL/RL training
loops, trading or prediction logic, or the trust calibration system.

## Work Done

- Read Atlas architecture and repository skill instructions.
- Read required Atlas core, release, changelog, audit, and release gate files.
- Inspected v0.6 explanation self-correction modules, `runtime/decision_loop.py`, and `StateStore`.
- Created Production Trial records:
  - `10_Production_Trial/Issues/ISSUE-2026-047_Causal_Self_Discovery_Needed.md`.
  - `10_Production_Trial/Improvement_Candidates/IP-2026-047_Causal_Self_Discovery_v0.7.md`.
- Added v0.7 causal self-discovery modules:
  - `runtime/cognition/causal_hypothesis_engine.py`.
  - `runtime/cognition/hypothesis_scoring_engine.py`.
  - `runtime/cognition/causal_structure_selector.py`.
  - `runtime/cognition/hypothesis_memory.py`.
- Extended `runtime/cognition/explanation_error_engine.py` with
  `compute_multi_explanation_competition()`.
- Integrated v0.7 hypothesis generation, scoring, selection, competition metrics, and memory
  persistence into `runtime/decision_loop.py`.
- Added validation script:
  - `99_Verification/validate_causal_self_discovery_v0_7.py`.
- Added validation result:
  - `99_Verification/Causal_Self_Discovery_v0.7_Validation_Result.md`.
- Added Regression Test Case 31 to `99_Verification/Regression_Tests.md`.

## Decisions

- Treat causal explanations as competing hypotheses, not truth claims.
- Store hypothesis memory in `StateStore` key/value state instead of adding a database table.
- Keep selection non-permanent with switch cooldown and trust-gated switching.
- Keep hypotheses as metadata overlays; no core graph rewrite, no prediction/trading output.
- Use deterministic scoring and selection gates instead of ML / RL / stochastic optimization.
- Persist hypothesis memory in existing key/value state to avoid adding new database schema.
- Keep low-trust behavior conservative by reducing switching frequency rather than changing trust
  calibration.

## Current State

- Completed.
- Validation passed:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile runtime/cognition/causal_hypothesis_engine.py runtime/cognition/hypothesis_scoring_engine.py runtime/cognition/causal_structure_selector.py runtime/cognition/hypothesis_memory.py runtime/cognition/explanation_error_engine.py runtime/decision_loop.py 99_Verification/validate_causal_self_discovery_v0_7.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_causal_self_discovery_v0_7.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_explanation_self_correction_v0_6.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_structural_coevolution_v0_4.py`
  - `PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_runtime_daemon_v0_1.py`
- Boundary checks passed:
  - no diff in Event Fusion, LMSE, MPCE, MLE, Decision Contract, or `portfolio.local.yaml`.
  - no forbidden v0.7 imports in those core files.
  - no `__pycache__` directories left under `runtime`, `ui`, or `99_Verification`.

## Resume Instructions

1. Read `99_Verification/Causal_Self_Discovery_v0.7_Validation_Result.md` for scope and test
   results.
2. Read `runtime/decision_loop.py` around the explanation error and hypothesis selection block if
   continuing runtime integration.
3. Re-run `PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_causal_self_discovery_v0_7.py`
   after any future v0.7 edits.

## Open Questions

- None.
