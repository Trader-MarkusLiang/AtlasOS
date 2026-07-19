# ISSUE-2026-062 - Real-Time Brief Closure and Runtime Efficiency

## Status

Converted to IP

## Origin

Real Usage / User Feedback / Architecture Review

## Date First Seen

2026-07-19

## Date Last Seen

2026-07-19

## Frequency

Repeated continuously during the audited overnight runtime.

## Affected Area

Decision Brief / Research / User Experience / Engineering

## Problem

Atlas completes scheduler ticks, market refreshes, and Decision-provider calls, but the two-hour
proactive path stops at a plan event, Workhorse and Research are disabled, Daily Cycle creates
per-tick artifact churn, and Home can contradict the latest DecisionPacket through fixed
presentation posture and static headline behavior. Telemetry readers and unbounded state payloads
also cause severe memory and storage growth.

## Context

The user reviewed Home after an overnight run and correctly observed no meaningful visible change.
Runtime evidence showed successful ticks and current evidence collection, but not an effective
research-to-Brief product loop. The user approved replacing phase-gated Brief production with
continuous material-event-driven section updates.

## Impact

Critical

## Evidence

- Current daemon audit: 408 consecutive successful ticks, 81 market refreshes, four proactive
  plans, and 164 successful Decision calls.
- Proactive state remained `planned`; Workhorse and Research runtime timestamps were stale.
- Current DecisionPackets reported `RISK_OFF`, high risk, and Reduce while Home showed Observe / no
  review needed.
- Daily Cycle produced one unique artifact per tick.
- Runtime logs/state exceeded 750 MB and repeated `/state` reads drove UI RSS above 9 GB.
- Current market evidence remained `thesis_changed=UNASSESSED`.

## Root Cause Hypothesis

Runtime productization joined several independently validated components without a single
material-delta publication contract. Scheduling, research planning, Decision routing, persistence,
and Home projection therefore advance independently rather than publishing one coherent current
Brief revision.

## Possible Solutions

- Add deterministic material-delta gating before role routing.
- Execute Workhorse and Research during due/material proactive updates.
- Make Daily Cycle maintenance-only and idempotent.
- Publish atomic, section-versioned current Brief state.
- Align Home posture and headline with the validated DecisionPacket and assessed evidence.
- Add bounded telemetry reads, lightweight state summary, and retention/rotation.

## Priority

P0

## Decision

Convert to Improvement Proposal. The user explicitly approved full implementation of the temporary
real-time Brief repair plan.

## Linked IP

IP-2026-062 - Real-Time Brief Closure and Runtime Efficiency

## Notes

This issue does not authorize cognition changes, broker integration, trading execution, or direct
mutation of Git-tracked World Model/candidate knowledge.
