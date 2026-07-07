# ISSUE-2026-054 — Productization Backbone Needed

Date: 2026-07-08
Status: Accepted for implementation
Category: User Experience / Engineering

## Source

Overnight autonomous productization sprint baseline audit.

## Problem

Atlas Runtime had advanced EventStream, cognition overlays, provider routing, telemetry, and UI
surfaces, but ordinary-user product surfaces were incomplete. The default entry was not
Decision Brief-first, portfolio percentages were mostly UI configuration, market refresh was not
scheduled into the runtime loop, and there was no persistent Forecast Ledger for accountability.

## Constraints

- Do not modify Event Fusion, CIL, LMSE, MPCE, MLE, CDE, or core decision/trust algorithms.
- Do not add broker integration or trading execution.
- Do not store account value, cost basis, balance, broker data, or net worth.
- External observations must pass Input Router -> EventStream -> cognition.
- Forecasts must be non-binding and must not default to price targets.

## Acceptance Criteria

- Home defaults to a Decision Brief-first view.
- UI exposes Home, Ask Atlas, Portfolio, Markets, Predictions, Learning, Workflow, Roadmap, and
  Settings.
- Runtime can refresh normalized market observations and enqueue them through EventStream.
- Portfolio context produces a read-only percentage exposure map.
- Forecast Ledger records expected state, actual outcome, forecast error, calibration error, and
  low-sample warnings.
- Validation covers no-private-config mode.

## Linked Improvement Candidate

None yet.

