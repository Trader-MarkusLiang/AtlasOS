# IP-2026-025 — Autonomous Runtime v0.2 Event-Driven macOS Runtime

## Category

Engineering / Runtime / Event Stream / Decision Brief / User Experience

## Origin

ISSUE-2026-025 — Autonomous Runtime v0.2 Request

## Problem

Runtime v0.1 provides a lightweight local host, but Atlas still needs a continuous event-driven
runtime loop with persistent state transitions and macOS daemon bootstrap.

## Implemented Scope

- `runtime/atlas_daemon.py`: launchd-compatible daemon entrypoint with heartbeat logging.
- `runtime/event_stream.py`: SQLite-backed event queue, listener, prioritization, and history.
- `runtime/state_machine.py`: runtime state machine.
- `runtime/decision_loop.py`: continuous event -> state -> orchestrator loop.
- `runtime/orchestrator.py`: state-driven autonomous route entrypoint.
- `runtime/state_store.py`: event history, system state, transition history, and time-series query
  support.
- `web/app.py`: dashboard sections for system state, live event stream, attention heat, and state
  transitions.
- `deployment/atlas_os.plist`: macOS launchd configuration.

## Runtime Flow

```text
atlas_daemon.py
 -> event_stream.py
 -> state_machine.py
 -> decision_loop.py
 -> orchestrator.py
 -> llm_router.py
 -> decision_brief.py
 -> state_store.py
 -> web dashboard
```

## States

- `NORMAL`
- `ATTENTION_EXPANSION`
- `RISK_OFF`
- `BREAKOUT`
- `DISTRIBUTION`
- `HIGH_VOLATILITY`

## Supported Event Types

- `market_anomaly`
- `attention_spike`
- `volume_price_breakout`
- `news_narrative_spike`
- `portfolio_drawdown`
- `heartbeat`
- `market_open`
- `market_close`
- `volatility_spike`
- `user_input_event`

## Safety Model

Autonomous runtime may:

- process events
- transition runtime state
- generate non-binding Decision Briefs
- update runtime state store
- display runtime status

Autonomous runtime may not:

- execute trades
- modify portfolio files
- create CDE authority
- bypass CDE
- integrate with brokers
- run full backtesting
- emit binding Buy / Sell instructions

## Validation

Validation file:

`99_Verification/validate_autonomous_runtime_v0_2.py`

Validation result:

`99_Verification/Autonomous_Runtime_v0.2_Validation_Result.md`

## Status

Implemented — autonomous local runtime trial.

## Final Decision

READY FOR AUTONOMOUS LOCAL RUNTIME TRIAL
