# Public Market Source Expansion

- Date: 2026-07-13 08:10 CST
- Session id: current Codex task
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Expand bounded public market evidence sources without changing cognition semantics
- Status: Completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

Use free public databases or fixed public websites to reduce missing market evidence; allow
screenshots as a fallback where structured access is unavailable.

## Investigation

- Existing runtime already uses Tencent history, Sina breadth, PBOC policy, and SSE announcements.
- SZSE's public announcement endpoint returns structured current disclosures without credentials.
- Eastmoney's public stock-rank endpoint returns current attention ranking without credentials.
- Bing RSS redirects to the generic home page and Google News RSS times out in this environment;
  neither is suitable for the daemon path.
- Screenshots are useful for manual evidence review but are too brittle for the 60-second runtime
  path and may expose local portfolio context.

## Decisions

- Add bounded SZSE official announcement coverage for configured Shenzhen holdings.
- Add Eastmoney current-rank data only as a partial public attention proxy, never sentiment or
  trading authority.
- Keep source URL, timestamp, freshness, verification level, and coverage limitations explicit.
- Reuse `ISSUE-2026-056`; do not create a new engine or crawler.

## Current State

- Added CNInfo official disclosure coverage for Shenzhen-listed configured assets.
- Added Eastmoney Top 100 stock rank as a delayed, partial-coverage attention proxy.
- Runtime `/state` now reports `narrative_attention: DELAYED` instead of `NOT_CONFIGURED` when the
  source is reachable.
- Canonical UI and daemon are running with the new adapters.

## Work Done

- Added bounded POST JSON/form helpers using the Python standard library.
- Preserved announcement PDF URL, China-local publication date, freshness, source verification,
  affected scope, and `UNASSESSED` thesis status.
- Kept public-rank interpretation limited to attention only, without sentiment, forecast, action,
  or CDE authority.
- Rejected Bing/Google news paths after live probes showed redirect/timeout behavior.
- Updated `ISSUE-2026-056`, Goal 03 validation, and the changelog.

## Verification

- Public source validator: PASS.
- Goal 03 normal daemon/EventStream path: PASS.
- Investor Home goal: PASS.
- Home intelligence surface: PASS.
- zh/en localization: PASS.
- Production `/state`: 11 evidence items from CNInfo, Eastmoney rank, PBOC, SSE, and Sina; no source
  errors; attention and news channels both observed.
- First production tick after restart: success, 14 market events enqueued, 11.7-second duration
  within the 60-second schedule.

## Resume Instructions

1. Add HKEX coverage only after a stable structured endpoint is proven.
2. Treat user-provided screenshots as Signals with source/time provenance; do not OCR them directly
   into unattended cognition.
3. Keep broader narrative-source diversity under `ISSUE-2026-056`.

## Open Questions

- HKEX announcements still need a stable structured endpoint; do not use screenshot OCR in the
  unattended daemon until provenance and retention rules are defined.
