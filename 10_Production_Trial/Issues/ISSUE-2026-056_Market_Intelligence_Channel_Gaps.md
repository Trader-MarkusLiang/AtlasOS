# ISSUE-2026-056 — Market Intelligence Channel Gaps

Date: 2026-07-08
Date Last Seen: 2026-07-13
Status: Accepted
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

P0

## Decision

Implement incrementally under the Portfolio-First Investor Decision Brief Goal. Start with existing
provider capabilities and explicit degradation; do not build a broad crawler or fabricate channel
coverage.

## Linked IP

None

## 2026-07-12 Progress

- Portfolio quotes now fall back to Tencent and retain provider timestamps.
- A-share breadth uses a bounded Sina sample and is labeled partial/delayed rather than full-market.
- PBOC policy releases and SSE portfolio-related announcements enter the normal EventStream path.
- Narrative / public-attention coverage remains `NOT_CONFIGURED`; this Issue stays open.

## 2026-07-13 Progress

- A bounded Tencent daily K-line fallback now supplies 5/20/60-day history for configured A-share
  and Hong Kong holdings when earlier providers fail.
- Browser and runtime validation confirmed all three configured holdings expose usable current and
  multi-period observations without replacing stale weekend data with false `LIVE` status.
- Current channel state includes real, delayed, cached, and explicitly not-configured channels;
  narrative / public-attention coverage remains the open gap.

## 2026-07-13 Public Source Expansion

- Added CNInfo's public disclosure endpoints for configured Shenzhen-listed assets. Records retain
  official PDF URLs, source timestamps, freshness, affected assets, and `UNASSESSED` thesis state.
- Added Eastmoney's public Top 100 stock-rank endpoint as a delayed, partial-coverage attention
  proxy. It does not infer sentiment, thesis change, price direction, or trading authority.
- Bing RSS redirected to a generic home page and Google News RSS timed out in the current network;
  neither was accepted into the runtime path.
- Automated screenshot/OCR ingestion remains out of the daemon because it is brittle and can expose
  local portfolio context. Screenshots remain suitable as manually supplied Signals with source
  and timestamp provenance.
- HKEX structured announcement coverage and broader narrative-source diversity remain open.
