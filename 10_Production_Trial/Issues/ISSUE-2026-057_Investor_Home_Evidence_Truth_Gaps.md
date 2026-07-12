# ISSUE-2026-057 — Investor Home Evidence Truth Gaps

## Status

Resolved

## Origin

User Feedback / Runtime Audit

## Date First Seen

2026-07-12

## Date Last Seen

2026-07-12

## Frequency

Repeated on every Home render while providers are degraded.

## Affected Area

Decision Brief / UX / Engineering

## Problem

The investor Home surface can describe unavailable price observations as refreshed or usable,
display a configured provider without distinguishing whether the latest inference succeeded, and
present static framework snapshots beside runtime evidence without a sufficiently strong truth label.

## Context

The live `/state` response reported `price_volume: FAILED`, three unavailable observation records,
and a latest DecisionPacket with `all_providers_failed`. Home still described the observation records
as available because presentation logic tested list presence instead of observation quality.

## Impact

Critical

## Evidence

- `ui/presentation/home_intelligence.py` counts a non-empty observation list as fresh.
- Live `/state` evidence captured in `99_Verification/Investor_Home_Truth_Baseline.md`.
- Configured provider identity and successful inference are currently separate facts but are not
  clearly separated in the Home header.

## Root Cause Hypothesis

Presentation helpers were optimized around fixture-backed observations and did not centralize
quality, freshness, and provenance checks before producing investor-facing claims.

## Possible Solutions

- Normalize Home evidence into usable, degraded, unavailable, and stale collections.
- Derive every freshness and availability claim from observation quality and source fields.
- Display configured provider separately from latest inference outcome.
- Add explicit runtime truth classes for live observation, verified evidence, framework snapshot,
  inference, hypothesis, unverified, and data missing.

## Priority

P0

## Decision

Implement under the Portfolio-First Investor Decision Brief Goal.

## Linked IP

None. This is a production-trial correctness repair, not a new engine.

## Notes

Do not change cognition semantics or create synthetic evidence to make the Home surface appear complete.

## Resolution Evidence

- Unavailable observations are excluded from usable/fresh counts.
- Missing multi-day changes render as data missing rather than `0.0%`.
- Configured provider and latest inference status are displayed separately.
- Runtime observations, provider evidence, framework snapshots, inference, hypotheses, and missing
  data have distinct presentation labels.
- See `99_Verification/Investor_Home_Runtime_Evidence_Report.md`.
