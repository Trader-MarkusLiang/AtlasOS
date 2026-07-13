# ISSUE-2026-060 - Task-Aware Multi-Provider Routing Needed

## Status

Converted to IP

## Origin

User Feedback / Architecture Review

## Date First Seen

2026-07-13

## Date Last Seen

2026-07-13

## Frequency

1 explicit request after multi-provider runtime activation.

## Affected Area

Research / UX / Engineering

## Problem

Atlas can configure multiple LLM providers, but normal runtime calls still use one global active
provider and one global fallback chain. Repetitive extraction, cross-source research, and final
Decision Brief synthesis cannot be assigned independent provider/model/cost policies.

## Context

The user approved a three-role design:

- Workhorse for extraction and structured Signal/Evidence preparation.
- Research for cross-source synthesis, counter-evidence, and portfolio relevance.
- Decision for the authoritative DecisionPacket and user-facing brief.

The current 60-second runtime tick also reaches the Decision adapter even when only a heartbeat is
present, which can create unnecessary premium-model calls.

## Impact

High

## Evidence

- `runtime/llm/provider_router.py` accepts one provider/model request but reads a global fallback.
- `runtime/llm_router.py` exposes one compatibility call path.
- `runtime/orchestrator.py` calls one model for every Decision Contract execution.
- `ui/pages/settings.py` configures providers but has no task-role assignment.

## Root Cause Hypothesis

Provider configuration was productized before runtime responsibilities were separated into bounded
LLM task roles.

## Possible Solutions

- Add a task-routing policy that references existing Provider Registry entries.
- Give each role its own provider, model, fallback, timeout, and output-token limit.
- Keep Workhorse/Research output non-authoritative and outside cognitive feedback.
- Skip premium calls when no meaningful input delta exists.
- Add role-specific telemetry and Settings controls.

## Priority

P1

## Decision

Convert to Improvement Proposal. The user explicitly approved the three-role architecture and
authorized implementation through the Task-Aware Multi-LLM Routing Goal.

## Linked IP

IP-2026-060 - Task-Aware Multi-LLM Routing Runtime v1.5

## Notes

This is runtime adapter and orchestration policy, not a new cognition Engine. Event Fusion, CIL,
LMSE, MPCE, MLE, UMIS, CDE, Decision Contract semantics, trust algorithms, portfolio authority,
and trading execution remain unchanged.
