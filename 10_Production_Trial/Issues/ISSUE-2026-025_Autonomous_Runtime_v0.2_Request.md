# ISSUE-2026-025 — Autonomous Runtime v0.2 Request

## Status

Open / Accepted / Converted to IP / Implemented

## Origin

Production Trial / User Autonomous Runtime Request

## Date First Seen

2026-07-05

## Date Last Seen

2026-07-05

## Frequency

1

## Affected Area

Engineering / Runtime / Event Stream / State Machine / Decision Brief / Dashboard

## Problem

Atlas OS Lightweight Execution Kernel v0.1 still behaves as a semi-runtime: it can run locally but
does not yet provide a true event-driven autonomous loop with state transitions and macOS daemon
bootstrap.

## User Request

The user requested:

- macOS daemon layer.
- real event stream system.
- runtime state machine.
- enhanced orchestrator consuming state and events.
- launchd plist bootstrap.
- continuous decision loop.
- enhanced state store and dashboard.

## Constraints

The user explicitly forbade:

- OpenClaw.
- CrewAI.
- Conductor.
- heavy frameworks.
- trading execution.
- automatic portfolio modification.
- CDE bypass.
- full backtesting engine.
- batch script runner behavior.

## Impact

High

Potential benefit:

- Atlas can run continuously in the background.
- Events can trigger state transitions.
- Decision Briefs can be generated automatically from event context.
- Runtime state becomes inspectable through dashboard and SQLite state.

Potential risk:

- false perception of autonomous trading
- portfolio privacy leakage
- CDE bypass
- excessive runtime complexity

## Decision

Accept as autonomous market cognition runtime only.

This Issue does not authorize trading execution, automatic portfolio modification, CDE bypass,
broker integration, or full backtesting.

## Linked IP

IP-2026-025 — Autonomous Runtime v0.2 Event-Driven macOS Runtime
