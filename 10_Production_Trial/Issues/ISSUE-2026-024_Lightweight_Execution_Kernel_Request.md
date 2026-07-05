# ISSUE-2026-024 — Lightweight Execution Kernel Request

## Status

Open / Accepted / Converted to IP / Implemented

## Origin

Production Trial / User Runtime Host Request

## Date First Seen

2026-07-05

## Date Last Seen

2026-07-05

## Frequency

1

## Affected Area

Engineering / Runtime / Daily Operating Cycle / Decision Brief / Portfolio Read-only Context

## Problem

Atlas OS is still primarily chat-driven. Runtime v0.1 Step 1 added scheduler and orchestrator
backbone, but it did not yet provide a continuously running macOS host, state persistence,
LLM provider abstraction, or dashboard surface.

## User Request

The user requested:

- macOS runtime host.
- lightweight scheduler.
- event-driven runtime loop.
- LLM API routing for GPT / Claude / Kimi / GLM.
- SQLite state persistence.
- non-binding Decision Brief generation.
- minimal web dashboard.

## Constraints

The user explicitly forbade:

- OpenClaw.
- CrewAI.
- Conductor.
- heavy agent frameworks.
- trading execution.
- automatic portfolio modification.
- CDE bypass.
- full backtesting engine.

## Impact

High

Potential benefit:

- Atlas can run scheduled local cycles.
- Runtime state becomes persistent.
- Decision Briefs can be generated without a new manual chat prompt.
- User can inspect runtime state through a local dashboard.

Potential risk:

- false perception of trading automation
- CDE bypass
- private portfolio data leakage
- overbuilt agent framework

## Decision

Accept as a lightweight runtime host only.

This Issue does not authorize trading, automatic portfolio modification, CDE bypass, backtesting,
or regime prediction.

## Linked IP

IP-2026-024 — Lightweight Execution Kernel v0.1 macOS Runtime Host
