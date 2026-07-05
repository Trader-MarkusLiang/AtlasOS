# IP-2026-024 — Lightweight Execution Kernel v0.1 macOS Runtime Host

## Category

Engineering / Runtime / Decision Brief / User Experience

## Origin

ISSUE-2026-024 — Lightweight Execution Kernel Request

## Problem

Atlas OS needs a minimal local runtime host so it can run scheduled decision cycles and persist
runtime state without requiring a new chat prompt for every cycle.

## Implemented Scope

- `runtime/atlas_host.py`: macOS-friendly daemon-style runtime host.
- `runtime/scheduler.py`: daily, intraday, weekly compatibility, and event trigger entrypoints.
- `runtime/orchestrator.py`: pipeline routing and aggregation.
- `runtime/llm_router.py`: multi-provider LLM abstraction using standard-library HTTP calls.
- `runtime/state_store.py`: SQLite runtime memory.
- `runtime/decision_brief.py`: non-binding runtime Decision Brief generator.
- `web/app.py`: minimal local web dashboard with optional FastAPI support and stdlib fallback.

## Runtime Flow

```text
atlas_host.py
 -> scheduler trigger
 -> orchestrator
 -> llm_router
 -> Atlas skill boundaries / placeholders
 -> decision_brief generator
 -> state_store update
 -> web dashboard read
```

## Supported Events

- `market_open`
- `market_close`
- `market_anomaly`
- `attention_spike`
- `volatility_spike`
- `user_input_event`

## LLM Provider Support

Supported provider aliases:

- `gpt-5.5`
- `claude-sonnet`
- `kimi`
- `glm`

If credentials are missing, runtime returns `offline_no_api_key` and continues with a deterministic
non-binding Decision Brief.

## State Store

SQLite stores:

- redacted portfolio snapshot metadata
- regime state
- attention history
- latest and historical runtime Decision Briefs
- system logs

The state store must not store private portfolio amounts, costs, balances, account values, net
worth, or position amounts.

## Boundary

This is not a new investment engine. It is a local execution host and runtime kernel.

It does not implement:

- trading execution
- automatic portfolio modification
- CDE bypass
- full backtesting
- heavy agent frameworks
- distributed systems
- regime prediction model

## Validation

Validation file:

`99_Verification/validate_runtime_kernel_v0_1.py`

Validation result:

`99_Verification/Runtime_Kernel_v0.1_Validation_Result.md`

## Status

Implemented — Lightweight local runtime trial.

## Final Decision

READY FOR LIGHTWEIGHT LOCAL RUNTIME TRIAL
