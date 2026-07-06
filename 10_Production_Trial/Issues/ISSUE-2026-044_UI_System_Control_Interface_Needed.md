# ISSUE-2026-044 — UI System Control Interface Needed

## Status

Implemented

## Origin

Atlas OS UI v1.0 system-level control interface redesign request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime UI / System Control Surface / Observability Presentation

## Problem

The UI Runtime Server exists, but the browser surface is still a simple page shell. Atlas needs a
system-level operating interface that shows runtime state, cognitive output, decision flow,
telemetry, user input, and stream updates without requiring page reloads.

## Context

The interface must remain a thin UI gateway:

- Use existing HTTP endpoints.
- Do not import cognitive-core modules into UI components.
- Do not allow UI code to mutate cognitive state directly.
- Do not add prediction, trading, or portfolio execution behavior.

## Impact

Medium / High

Potential effects if unresolved:

- The UI does not communicate Atlas runtime status clearly.
- Users cannot inspect decision flow and telemetry in one operating surface.
- Chat input and runtime state remain disconnected in the browser experience.

## Evidence

User request:

```text
Current UI is a blank shell.
Transform it into Atlas OS System Control Interface.
```

## Root Cause Hypothesis

UI Runtime Server v0.1 exposed safe endpoints, but its HTML routes remained minimal instead of a
real-time system layout.

## Possible Solutions

- Add componentized UI render helpers for the top bar, system state panel, inspector, and event
  stream.
- Enhance the chat interface view to show DecisionPacket output.
- Update `ui/app_server.py` HTML routes to serve a real-time flexbox interface.
- Add validation for UI layout, polling, chat endpoint flow, and cognition isolation.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement UI v1.0 as a presentation-only redesign.

## Linked IP

IP-2026-044 — UI System Control Interface v1.0

## Notes

This issue does not authorize cognitive-core changes, runtime daemon changes, Decision Contract
changes, trading logic, prediction logic, CDE bypass, broker integration, or direct UI mutation of
runtime cognition.

