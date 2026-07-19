# Market Provider Spawn Fix

- Date: 2026-07-18 13:06 CST
- Session id: 019e958e-8f65-72f2-bf8e-1ef552f8ef7d
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Fix macOS Codex UI crash caused by market data hard-timeout subprocess fork.
- Status: completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

User asked to fix the previously diagnosed AtlasOS crash. The crash report showed a macOS multi-threaded Python process forking before `exec`, with the child initializing `curl_cffi`/libcurl/SystemConfiguration and crashing with `EXC_GUARD`.

## Work Done

- Continuing from `/Users/markus/AtlasOS/docs/codex-sessions/completed/2026-07-18_1251_market-provider-fork-curl-crash.md`.
- Inspected `/Users/markus/AtlasOS/tools/market_data/market_data_provider.py`.
- Confirmed `_load_history_in_process()` currently chooses `fork` whenever available.
- Added `_market_provider_process_context()` so macOS uses multiprocessing `spawn`, while non-macOS keeps the previous `fork` preference.
- Updated `_load_history_in_process()` to use that helper.
- Ran `python3 -m py_compile tools/market_data/market_data_provider.py`: passed.
- Ran focused market snapshot smoke with `ATLAS_MARKET_PROVIDER_TIMEOUT_SECONDS=8`: `AAPL` returned `Available yahoo_chart`; `000001` returned `Available tencent_kline`.
- Directly confirmed `_market_provider_process_context().get_start_method()` returns `spawn` on this machine.
- Direct direct `yfinance` hard-timeout test reached the spawned worker and returned a controlled `YFRateLimitError` due to upstream rate limiting, with no macOS process crash.
- Restarted the live UI server on port 8765 so the patched module is loaded.
- Verified the live server is running from `/Users/markus/AtlasOS` as PID 16232 and `/` plus `/state` return HTTP 200.

## Decisions

- Use the smallest platform-specific fix: `spawn` on macOS, keep existing `fork` preference elsewhere.
- Do not add dependencies or broaden market provider behavior.

## Current State

- Completed. The macOS crash-prone fork path is no longer used by market data hard-timeout workers.

## Resume Instructions

1. Read `/Users/markus/AtlasOS/tools/market_data/market_data_provider.py`.
2. If related crashes recur, verify the running UI server has reloaded this file and confirm `_market_provider_process_context().get_start_method()` prints `spawn`.
3. Treat future `YFRateLimitError` from yfinance as provider throttling, not the original macOS fork crash.

## Open Questions

- None.
