# IP-2026-023 — Runtime v0.1 Step 1 Minimal Scheduler + Orchestrator Backbone

## Category

Engineering / Daily Operating Cycle / Runtime

## Origin

ISSUE-2026-023 — Runtime System v0.1 Request

## Problem

Atlas OS is still mostly chat-driven. The user approved a narrowly scoped first runtime step so
Atlas can be triggered manually or by a future scheduler without requiring a fresh chat prompt.

## Scope

Step 1 implements only:

- Scheduler entrypoints.
- Orchestrator routing skeleton.
- Read-only portfolio availability check.
- Runtime-generated Decision Brief stub.
- Runtime execution metadata logging.

## Implemented Files

- `runtime/scheduler.py`
- `runtime/orchestrator.py`
- `runtime/logging.py`
- `runtime/__init__.py`
- `runtime/logs/.gitignore`
- `99_Verification/validate_runtime_step1.py`
- `99_Verification/Runtime_v0.1_Step1_Validation_Result.md`

## Runtime Flow

```text
scheduler -> orchestrator -> Atlas skill boundary names -> decision brief stub -> JSONL log
```

## Trigger Routes

| Trigger | Pipeline | Runtime Behavior |
|---|---|---|
| `daily_run` | Live Analysis | Routes to `atlas-daily` boundary |
| `weekly_run` | Simulation Placeholder | Routes to `atlas-research`, `atlas-portfolio`, and placeholder only |
| `event_trigger` | Risk Check | Routes to `atlas-research`, `atlas-portfolio`, and attention placeholder only |

## Explicit Non-Scope

This IP does not implement:

- automatic trading
- portfolio weight modification
- CDE logic changes
- Decision Brief strategy logic changes
- backtesting
- simulation engine
- regime prediction
- state store
- full event trigger engine
- new investment engine

## Safety Model

Runtime Step 1 can produce only a non-binding runtime-generated Decision Brief stub.

Allowed Action Bias:

```text
Observe / Hold only; non-binding; CDE authority still required.
```

The runtime log stores execution metadata only and does not store private portfolio values,
execution prices, costs, balances, account values, or position amounts.

## Acceptance Test

Validation file:

`99_Verification/validate_runtime_step1.py`

Expected:

1. `daily_run()` triggers orchestrator and routes to `Live Analysis`.
2. `weekly_run()` triggers orchestrator and routes to `Simulation Placeholder`.
3. `event_trigger("market_anomaly")` triggers orchestrator and routes to `Risk Check`.
4. Every route generates `Atlas Decision Brief (Runtime Generated)`.
5. Every route writes one JSONL metadata log record.
6. Logs do not store full Decision Brief content or private portfolio content.
7. No trading, portfolio modification, CDE change, prediction, or simulation is implemented.

## Status

Implemented — Step 1 only.

Full Runtime System v0.1 remains unimplemented.

## Boundary Confirmation

| Boundary | Result |
|---|---|
| No automatic trading | PASS |
| No portfolio.local.yaml modification | PASS |
| No portfolio weight modification | PASS |
| No CDE logic change | PASS |
| No Decision Brief strategy logic change | PASS |
| No backtesting system | PASS |
| No regime prediction implementation | PASS |
| No simulation engine implementation | PASS |
| No new investment engine | PASS |
