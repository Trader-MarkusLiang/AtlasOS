# ISSUE-2026-023 — Runtime System v0.1 Request

## Status

Open / Accepted / Converted to IP / Step 1 Implemented

## Origin

Production Trial / User Architecture Request

## Date First Seen

2026-07-05

## Date Last Seen

2026-07-05

## Frequency

2

## Affected Area

Engineering / Daily Operating Cycle / Decision Brief / Repository / Market Data / Portfolio

## Problem

Atlas OS is currently chat-driven and cannot run independently as a scheduled or event-triggered
runtime system.

The user proposed:

- Scheduler Layer.
- Event Trigger Engine.
- Runtime Orchestrator.
- State Store.
- Output Generator.

The target direction is a human-in-the-loop market runtime OS that can generate daily reports,
weekly simulations, event-based risk alerts, and regime transition updates.

## Context

Requested runtime deliverables included:

- `/runtime/scheduler.py`
- `/runtime/orchestrator.py`
- `/runtime/event_engine.py`
- `/runtime/state_store.py`
- `/runtime/output_generator.py`
- AGENTS update.
- Architecture documentation update.
- Runtime-enabled Decision Brief Template.

However, Atlas is currently in Production Trial. Current stage rules forbid direct full runtime
automation or new investment-engine implementation without Issue discussion, priority review,
Architecture Review, Acceptance Test definition, and explicit user approval.

On 2026-07-05, the user explicitly narrowed and approved Step 1:

- Minimal scheduler.
- Minimal orchestrator.
- Pipeline routing skeleton.
- Runtime-generated Decision Brief stub.
- Runtime execution logging.

The user explicitly excluded full simulation, state machine, trading logic, portfolio weight
changes, CDE logic changes, backtesting, regime prediction, and automatic trading.

## Impact

Medium / High

Potential benefit:

- reduce reliance on manual chat prompts
- improve daily decision discipline
- preserve state across runs
- support event-based risk review

Potential risk:

- premature automation
- false sense of autonomy
- accidental bypass of CDE
- confusion between advisory runtime and trading system

## Evidence

User request on 2026-07-05:

`Atlas OS Upgrade — Runtime System v0.1 (From Chat System -> Operating System)`

## Root Cause Hypothesis

Atlas has accumulated process, market data utilities, issue governance, and Decision Brief
templates, but it still lacks a runtime boundary design for scheduled / event-triggered execution.

## Possible Solutions

- Keep Runtime System v0.1 in Roadmap Ideas until repeated Production Trial evidence justifies it.
- Define an Architecture Review before any runtime code.
- Define a safety model for human-in-the-loop operation.
- Require Acceptance Tests proving:
  - no automatic trading
  - CDE remains mandatory
  - portfolio privacy remains intact
  - state store is Git-friendly and non-sensitive

## Priority

P1

## Decision

Accepted for Step 1 only.

Full Runtime System v0.1 remains unimplemented and requires separate approval.

## Linked IP

IP-2026-023 — Runtime v0.1 Step 1 Minimal Scheduler + Orchestrator Backbone

## Notes

Step 1 implementation evidence:

- `runtime/scheduler.py`
- `runtime/orchestrator.py`
- `runtime/logging.py`
- `99_Verification/validate_runtime_step1.py`
- `99_Verification/Runtime_v0.1_Step1_Validation_Result.md`

Step 1 does not approve:

- automatic trading
- state store
- event trigger engine beyond manual event trigger entrypoint
- simulation engine
- regime prediction
- CDE formula changes
- portfolio allocation changes
- Decision Brief strategy logic changes
