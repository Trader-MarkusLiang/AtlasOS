# IP-2026-062 - Real-Time Brief Closure and Runtime Efficiency

Date: 2026-07-19
Status: Accepted for implementation
Category: User Experience / Research / Engineering

## Linked Issue

ISSUE-2026-062 - Real-Time Brief Closure and Runtime Efficiency

## Objective

Turn the existing daemon, market refresh, role routing, DecisionLoop, state store, telemetry, and
Home projection into a continuous material-event-driven Brief loop. New verified evidence should
update only affected Home sections at any time; heartbeat-only ticks should create no LLM calls or
Brief revisions.

## Implementation Boundary

Allowed:

- Deterministic material hashes and section revision metadata.
- Real execution lifecycle for existing Workhorse / Research / Decision roles.
- Maintenance-only, idempotent Daily Cycle behavior.
- Runtime-only evidence assessment and candidate overlays.
- Atomic current-Brief publication through existing state storage.
- Bounded telemetry reads, state-summary endpoints, retention, and log rotation.
- Home semantic/freshness presentation changes and focused validators.

Forbidden:

- Changes to Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, CDE, trust, or Decision Contract semantics.
- Direct mutation of Git-tracked World Model or candidate knowledge from runtime output.
- Broker connectivity, trading execution, prediction-system expansion, ML, DL, or RL.
- Private portfolio amounts or provider secrets in cognition, telemetry, or Git.

## Required Result

- Brief updates are material-event-driven rather than phase-gated.
- Proactive cycles terminate as `COMPLETED`, `DEGRADED`, or `FAILED` with evidence.
- Workhorse, Research, and Decision roles advance on a completed material research cycle.
- Heartbeat-only and duplicate-evidence ticks produce zero LLM calls and zero Brief revisions.
- Home is consistent with the latest validated DecisionPacket and explains reviewed-but-unchanged
  evidence.
- Closed-market freshness is explicit.
- UI polling memory and persisted telemetry growth are bounded.
- Desktop/mobile behavior and runtime recovery are verified.

## Release Position

Runtime/UI Production Trial repair only. Atlas Core remains v2.1 RC; cognition and capital
authority remain unchanged.
