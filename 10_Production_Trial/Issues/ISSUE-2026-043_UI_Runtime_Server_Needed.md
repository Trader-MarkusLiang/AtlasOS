# ISSUE-2026-043 — UI Runtime Server Needed

## Status

Implemented

## Origin

Atlas OS UI Runtime Server v0.1 request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime UI / Web Interaction / Safe Control Gateway

## Problem

Atlas UI v0.1 modules exist as Python helpers, but they are not exposed as a real browser-facing
interaction layer. Users need a lightweight web server for chat submission, state dashboard,
replay, and safe runtime controls.

## Context

The UI server must be a thin orchestration and visualization gateway:

- User browser -> UI server
- UI server -> UI modules and telemetry
- UI modules -> Atlas runtime via inbox/state/log boundaries

It must not import cognitive-core modules or mutate cognitive state directly.

## Impact

Medium / High

Potential effects if unresolved:

- UI modules remain non-interactive helpers
- chat input cannot be submitted from browser to runtime
- state and replay data remain buried in logs
- controls lack a safe HTTP boundary

## Evidence

User request:

```text
UI Server is a thin orchestration + visualization gateway, NOT a cognition layer.
```

## Root Cause Hypothesis

UI v0.1 added module-level helpers but not an HTTP server or daemon-compatible JSONL user event
inbox.

## Possible Solutions

- Add `ui/app_server.py`.
- Add `/chat/send`, `/state`, `/dashboard`, `/replay`, and `/control` endpoints.
- Patch `runtime/atlas_runtime_daemon.py` to poll `runtime/inbox/user_event.jsonl`.
- Add validation for chat flow, isolation, state consistency, replay accuracy, and daemon
  integration.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement a safe UI Runtime Server.

## Linked IP

IP-2026-043 — UI Runtime Server v0.1

## Notes

This issue does not authorize cognition module changes, Decision Contract changes, trading logic,
prediction logic, CDE bypass, broker integration, or direct UI mutation of runtime cognition.
