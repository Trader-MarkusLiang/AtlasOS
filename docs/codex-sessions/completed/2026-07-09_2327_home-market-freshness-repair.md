# Home Market Freshness Repair

## Metadata

- Date: 2026-07-09 23:27 CST
- Session id: current Codex desktop thread
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Repair Home data freshness showing unavailable market data and add more data-source fallbacks.
- Status: completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

The user shared a Home screenshot where data freshness reports price `0/3` available, one failed real-time channel, several unconfigured channels, and all configured portfolio holdings show no fresh data. The request is to investigate whether this is a process issue and fix it by adding more data sources.

## Constraints

- Do not modify Event Fusion, CIL, LMSE, MPCE, MLE, CDE, Decision Contract, trust, prediction, or trading logic.
- Keep the change in market-data ingestion / freshness presentation / UI visibility.
- Do not commit private portfolio values or secrets.

## Work Done

- Read Atlas architecture skill and required boundary files.
- Inspected the screenshot and confirmed the visible failure is a real data-freshness issue, not only a cosmetic UI issue.
- Audited `runtime/market_intelligence.py`, `tools/market_data/market_data_provider.py`, daemon refresh integration, and Home/UI freshness rendering.
- Found that the existing market provider path could successfully fetch live data manually, but the running daemon was still using old code and could overwrite state with failed observations.
- Added bounded fallback market data sources:
  - Eastmoney K-line history for China / Hong Kong markets.
  - Eastmoney quote fallback when history fails.
  - Tencent quote fallback when Eastmoney quote fails.
- Kept fallback quote snapshots as `Partial` when full history fields are missing, rather than pretending they are complete.
- Normalized Tencent quote volume parsing so Shenzhen A-share fallback volume is converted from board lots while Shanghai / Hong Kong remain share-count style.
- Updated market-intelligence aggregation so `Partial` counts as a usable signal while remaining visibly incomplete.
- Updated Home/topbar freshness summaries so `Available` and `Partial` are counted as price signals.
- Updated Home invalidation text so it only says live data remains unavailable when price observations truly have no signal.
- Restarted the runtime daemon so it loads the new provider code.
- Restarted the UI server on port 8765.
- Refreshed local runtime market state once so Home immediately reflects the repaired data path.

## Verification Results

- `python3 -m py_compile` passed for the changed runtime/UI modules.
- Live provider refresh for the configured holdings returned price signals for all configured assets.
- Direct quote-fallback probe returned current quote fields for all configured assets through Tencent fallback.
- `/state` reports:
  - `price_volume: LIVE`
  - `portfolio_relevance: LIVE`
  - `degraded: false`
  - all configured asset observations are `Available` in the final verification run.
- Home HTML now shows:
  - `价格 3/3 有信号`
  - all configured asset rows as `可用`
  - no stale `实时数据持续不可用` invalidation when price data is available.
- Runtime daemon restarted successfully with PID `26638`.
- UI server on port 8765 restarted successfully.

## Current State

- Home data freshness is no longer stuck at unavailable for the configured portfolio assets.
- Remaining unconfigured channels are broad market breadth, news / announcements, narrative attention, and macro policy; they are still honestly marked `NOT_CONFIGURED`.
- Existing unrelated local changes from the prior Workflow dated architecture fix are preserved and remain in the working tree.

## Resume Instructions

- Run `git status --short --branch`.
- Recheck `curl -s http://127.0.0.1:8765/state` and `/` if continuing UI validation.
- Commit together with the prior Workflow dated architecture fix if the user asks to persist all current fixes.

## Open Questions

- None yet.
