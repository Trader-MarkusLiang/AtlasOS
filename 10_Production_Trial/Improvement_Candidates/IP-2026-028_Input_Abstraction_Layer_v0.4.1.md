# IP-2026-028 — Input Abstraction Layer v0.4.1

## Category

Engineering / Runtime / Input Abstraction / Cognitive Isolation

## Origin

ISSUE-2026-028 — EventStream Direct DSA Coupling

## Problem

Atlas OS v0.4 had partial cognitive isolation because EventStream directly imported the
source-specific DSA bridge. That violated the rule:

```text
Cognitive Layer and runtime ingestion must not depend on infrastructure-specific modules.
```

## Implemented Scope

- Added `runtime/adapter/input_router.py`.
  - Single source-neutral input abstraction layer.
  - Normalizes external inputs into:

```python
{
    "type": "market_event",
    "timestamp": 0,
    "source": "dsa | native | external",
    "intensity": 0.0,
    "payload": {}
}
```

- Updated `runtime/event_stream.py`.
  - Removed direct import of `runtime.adapter.dsa_bridge`.
  - EventStream now routes inbox and enqueue inputs through `runtime.adapter.input_router`.
  - Added neutral `market_event` support.
- Updated `runtime/adapter/dsa_bridge.py`.
  - DSA bridge is now a compatibility wrapper around Input Router.
  - EventStream does not depend on it.
- Updated `runtime/adapter/__init__.py`.
  - Exports Input Router primitives only.
- Updated `web/app.py`.
  - Dashboard infrastructure status now reads Input Router diagnostics instead of DSA bridge
    diagnostics.
- Added `99_Verification/validate_input_abstraction_layer_v0_4_1.py`.

## Architecture Diff

Before:

```text
External Systems
 -> DSA Bridge
 -> EventStream
 -> Cognitive Layer
```

After:

```text
External Systems (DSA / APIs / Native)
 -> Input Router
 -> EventStream
 -> Event Fusion Engine
 -> Regime Memory
 -> Causal Inference Layer
 -> State Controller
 -> Orchestrator
```

## Dependency Graph

```text
runtime.event_stream
 -> runtime.adapter.input_router
 -> no source-specific adapter

runtime.adapter.dsa_bridge
 -> runtime.adapter.input_router

runtime.cognition.*
 -> no runtime.adapter import
```

## Sanitization Rule

If illegal fields appear anywhere in the external input, including nested metadata, Input Router:

- strips the illegal fields
- downgrades the event to `market_event`
- sets intensity to `0.0`
- does not map it into attention, liquidity, volatility, or regime signals

Illegal fields include:

- `buy_signal`
- `sell_signal`
- `strategy`
- `alpha_score`
- `target_weight`
- `recommendation`
- MA decision-signal fields such as `ma_cross`

## Validation

Validation command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_input_abstraction_layer_v0_4_1.py
```

Regression commands:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_dsa_adapter_v0_4.py
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_cognitive_runtime_v0_3.py
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_autonomous_runtime_v0_2.py
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_runtime_kernel_v0_1.py
```

Validation result:

`99_Verification/Input_Abstraction_Layer_v0.4.1_Validation_Result.md`

## Boundary

This IP does not modify:

- Event Fusion Engine.
- Regime Memory.
- Causal Inference.
- State Controller.
- Attention vs Liquidity model.
- CDE formulas.
- Decision Brief strategy logic.
- `portfolio.local.yaml`.

It does not implement:

- trading execution
- portfolio automation
- stock picking
- DSA strategy import
- broker integration

## Status

Implemented — cognitive isolation fix.

## Final Decision

READY FOR COGNITIVE ISOLATION RE-TEST

