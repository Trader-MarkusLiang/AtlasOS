# ISSUE-2026-042 — Self-Organizing Core + UI Isolation Needed

## Status

Implemented

## Origin

Atlas OS v0.5 + UI v0.1 — Dual Track Evolution System request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime / Cognitive Structural Metadata / UI Observation and Control

## Problem

Atlas Runtime has trust-gated structural co-evolution, but lacks a higher-level
self-organization cycle and a separated user-facing observation/control layer.

## Context

The requested dual-track system must keep two systems strictly separated:

- Core system: cognition, structure, evolution
- UI system: interaction, visualization, control

UI must not import or mutate cognition modules.

## Impact

High

Potential effects if unresolved:

- structural drift remains externally computed rather than endogenous
- trust remains scalar or state-local rather than component-field based
- users cannot observe runtime trust/structure evolution without reading raw logs
- unsafe UI coupling could accidentally bypass core constraints

## Evidence

User request:

```text
CORE SYSTEM (v0.5) -> cognition, structure, evolution
UI SYSTEM (v0.1) -> interaction, visualization, control
NO direct coupling allowed.
```

## Root Cause Hypothesis

Runtime v0.4 stores structural overlays, but does not yet run a separate self-organization cycle
that governs causal reweighting, regime sensitivity, and trust-field propagation. The repo also has
telemetry, but no isolated UI modules over that telemetry.

## Possible Solutions

- Add `runtime/cognition/self_organizing_engine.py`.
- Add `runtime/cognition/trust_field_dynamics.py`.
- Add `runtime/cognition/structural_evolution_controller.py`.
- Integrate v0.5 in `runtime/decision_loop.py`.
- Add UI modules under `ui/` that only use telemetry, `StateStore`, process control, and inbox
  events.
- Add isolation validation.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement as strictly separated core/UI tracks.

## Linked IP

IP-2026-042 — Self-Organizing Core v0.5 + UI v0.1

## Notes

This issue does not authorize ML/DL/RL, prediction logic, trading execution, Decision Contract
schema changes, core CIL / LMSE / MPCE / MLE rewrites, CDE bypass, or UI-driven cognition mutation.
