# IP-2026-042 — Self-Organizing Core v0.5 + UI v0.1

## Category

Engineering / Runtime Cognition / UI Observation

## Origin

ISSUE-2026-042 — Self-Organizing Core + UI Isolation Needed

## Problem

Atlas Runtime needs a self-organizing structural overlay above v0.4 structural co-evolution, plus a
minimal UI layer that observes and controls runtime boundaries without coupling to cognition.

## Implemented Scope

Core v0.5:

- Added `runtime/cognition/self_organizing_engine.py`.
- Added `runtime/cognition/trust_field_dynamics.py`.
- Added `runtime/cognition/structural_evolution_controller.py`.
- Updated `runtime/decision_loop.py` to run one self-organization cycle per processed tick and
  persist `self_organization_state`.
- Updated telemetry snapshot and daemon summary exposure.

UI v0.1:

- Added `ui/chat_interface.py`.
- Added `ui/system_control_panel.py`.
- Added `ui/state_visual_dashboard.py`.
- Added `ui/replay_console.py`.
- Added `ui/__init__.py`.

## Core Output Shape

```python
{
    "structural_shift_index": float,
    "causal_reweight_delta": dict,
    "regime_attractor_shift": float,
    "trust_field_evolution": float,
}
```

## UI Boundary

UI modules:

- do not import `runtime.cognition`
- submit user queries through runtime inbox JSON files
- read runtime state through `StateStore`
- read replay and visualization data through telemetry logs
- manage daemon process/config only

## Boundary

This IP does not modify:

- Event Fusion logic
- core CIL causal definitions
- LMSE physics
- MPCE constraints
- MLE laws
- Decision Contract schema
- CDE logic
- `portfolio.local.yaml`

It does not introduce:

- ML / DL / RL
- prediction logic
- trading execution
- buy/sell outputs
- UI-driven cognition mutation

## Status

Implemented — dual-track core/UI separation.

## Final Decision

READY FOR SELF-ORGANIZATION + UI ISOLATION REVIEW
