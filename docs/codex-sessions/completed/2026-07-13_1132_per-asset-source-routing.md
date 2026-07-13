# Per-Asset Market Source Routing

- Date: 2026-07-13 11:32 CST
- Session id: current Codex task
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Add fixed reliable source plans and runtime source status for each configured asset
- Status: Completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

Clarify and implement stock-specific reliable public database or website routing so every triggered
update fetches each asset from its corresponding fixed sources.

## Investigation

- Price/history and official evidence are fetched per configured position, but `/state` does not
  expose a per-asset source plan or source health map.
- SSE, CNInfo, Tencent, Eastmoney, Sina, PBOC, and Eastmoney rank are live-proven in the current
  environment.
- HKEX issuer lookup is reachable and resolves stock code to issuer identity; the title-search
  result endpoint still requires a stable automated contract.
- Source routing must be market-derived, not a Git-tracked copy of private holdings.

## Decisions

- Create a small market/source registry with reliability and automation metadata.
- Generate source plans dynamically from each local configured asset's market and ticker suffix.
- Attach actual source use, freshness, latest timestamp, and errors after every market refresh.
- Keep manual website/screenshot sources explicit and separate from automated ingestion.

## Current State

- Every locally configured asset now receives a market-derived source plan on each scheduled market
  refresh.
- `/state` exposes actual source use, standby fallbacks, failures, checked-no-record results, and
  manual-review sources under `market_intelligence.asset_source_map`.
- The Markets page displays source status per asset in Chinese and English.
- Canonical UI and the 60-second daemon are running with the new routing.

## Work Done

- Added `runtime/market_source_registry.py` with SH, SZ, HK, and US source policies.
- Integrated the source map into normal market refresh state.
- Added one bounded retry for transient public-site transport failures; HTTP errors remain final.
- Added source transparency table and bilingual labels to `/markets`.
- Added pure routing and live runtime-path validation.

## Verification

- Asset source routing validator: PASS for neutral SH/SZ/HK/US fixtures.
- Public source validator: PASS, including explicit external failure handling.
- Goal 03 daemon/EventStream/UI path: PASS with source plan visible.
- Investor Home and zh/en localization regressions: PASS.
- Production `/state`: 3 local assets, 6 used sources, 0 failed sources, 1 manual-review source,
  and no source errors after daemon restart.
- Desktop browser source table: 3 rows, no horizontal overflow.
- Mobile browser exposed an initial table overflow; global table containment and internal scrolling
  were added, and the updated CSS is present on the live route.

## Resume Instructions

1. Automate HKEX/SEC disclosures only after stable structured endpoints are proven.
2. Add provider cadence/backoff only if production logs show repeated source throttling.
3. Keep real portfolio render artifacts local-only.

## Open Questions

- HKEX announcement retrieval remains manual until a stable structured result endpoint is proven.
