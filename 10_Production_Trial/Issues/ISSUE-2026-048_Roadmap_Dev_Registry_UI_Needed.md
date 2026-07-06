# ISSUE-2026-048 — Roadmap Dev Registry UI Needed

Date: 2026-07-06
Status: Accepted for implementation
Category: User Experience

## Source

User request: Atlas OS Roadmap + Development Registry UI Page.

## Problem

Atlas runtime and UI layers have evolved quickly, but the system does not yet expose a single
machine-readable lifecycle registry for:

- version progression,
- modules added per version,
- validation status,
- active stage,
- next planned stage.

Without this, the UI can show runtime state but cannot show development traceability.

## Constraints

- Do not modify cognitive core logic.
- Do not modify decision logic or trust system.
- Do not introduce ML / RL or trading logic.
- Do not change runtime daemon execution semantics.
- Limit implementation to UI, documentation, and registry tracking.

## Acceptance Criteria

- `docs/atlas_roadmap.json` exists and is machine-readable.
- `/roadmap` returns current version, completed layers, active stage, and next planned stage.
- `/dev-registry` renders version history, module evolution, validation status, and current system
  state.
- Dashboard navigation exposes System, Chat, Inspector, Graph, Roadmap, and Dev Registry.
- Boundary scan confirms no cognitive layer or runtime daemon semantic changes.

## Linked Improvement Candidate

IP-2026-048 — Roadmap Dev Registry UI
