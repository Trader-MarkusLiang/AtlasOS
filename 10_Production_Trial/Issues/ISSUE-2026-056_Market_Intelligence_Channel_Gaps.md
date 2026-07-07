# ISSUE-2026-056 — Market Intelligence Channel Gaps

Date: 2026-07-08
Status: Open
Category: Engineering

## Source

Overnight productization sprint market ingestion audit.

## Problem

Atlas has market-data utilities and now has a scheduled price/volume ingestion backbone, but the
full normalized channel set remains incomplete. Market breadth, news/announcement, narrative,
macro/policy, and deeper liquidity channels are still reported as missing or partial rather than
pretending to be live.

## Constraints

- Do not build a giant crawler.
- Do not hardcode unsupported providers.
- Do not route news directly to decisions; news remains Signal.
- All observations must pass Input Router -> EventStream -> cognition.
- If credentials/providers are missing, degrade gracefully and report exact missing capability.

## Impact

Medium.

## Evidence

`runtime/market_intelligence.py` reports price/volume when configured assets are available, with
volatility and liquidity proxy marked partial. Other mandated channels are intentionally reported
as `not_implemented`.

## Root Cause Hypothesis

The repository previously had provider utilities but not a productized, scheduled, normalized
multi-channel ingestion cycle.

## Possible Solutions

- Add optional provider-backed breadth, macro, and narrative adapters incrementally.
- Keep channel status explicit in UI.
- Add validation fixtures for stale, malformed, and contradictory observations.

## Priority

P2

## Decision

Watch / Discuss after backbone stabilizes.

## Linked IP

None

