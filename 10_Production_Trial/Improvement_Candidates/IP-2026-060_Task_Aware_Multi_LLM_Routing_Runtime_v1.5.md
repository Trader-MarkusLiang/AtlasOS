# IP-2026-060 - Task-Aware Multi-LLM Routing Runtime v1.5

Date: 2026-07-13
Status: Accepted for implementation
Category: Engineering

## Linked Issue

ISSUE-2026-060 - Task-Aware Multi-Provider Routing Needed

## Objective

Add Workhorse, Research, and Decision task routes over the existing Provider Registry and Provider
Router so Atlas can use cost-appropriate models without weakening decision integrity.

## Implementation Boundary

Allowed:

- Provider type metadata and adapter normalization.
- Task-route configuration and validation.
- Role-specific provider/model/fallback routing.
- Runtime orchestration outside cognition implementations.
- No-delta call suppression and bounded result caching.
- LLM telemetry, Settings UI, APIs, i18n, and verification.

Forbidden:

- Event Fusion semantic changes.
- CIL, LMSE, MPCE, MLE, UMIS, or CDE changes.
- Decision Contract semantic changes.
- Workhorse/Research direct cognition or portfolio mutation.
- Broker integration, trading execution, ML, DL, RL, or agent swarms.
- API key or private local configuration commits.

## Required Result

- Three independently configurable roles.
- Provider-model discovery remains API-backed.
- Role-specific fallback and failure isolation.
- Workhorse/Research outputs use strict non-authoritative contracts.
- Decision remains the only role whose validated packet enters existing feedback.
- Heartbeat-only ticks do not call premium models.
- Two-hour proactive updates and user queries exercise legitimate task responsibilities.
- Role, latency, usage, cost status, fallback, and trigger telemetry are visible.
- Full zh/en Settings parity and browser validation.

## Release Position

Runtime/UI minor track only. Atlas Core remains v2.1 RC Production Trial.
