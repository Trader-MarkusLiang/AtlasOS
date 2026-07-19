---
Date: 2026-07-18 12:51 CST
Session id: 019e958e-8f65-72f2-bf8e-1ef552f8ef7d
Project: atlas-os
Workspace: /Users/markus/AtlasOS
Task: Diagnose macOS Python crash report from AtlasOS UI/runtime market data process.
Status: complete
Branch: current working tree
---

# Market Provider Fork Curl Crash

## User Request Summary

User provided a macOS crash report and asked to inspect the issue. The report shows a Python process crash under `com.atlasos.ui.8765`.

## Work Done

- Read `/Users/markus/.codex/attachments/da970d20-709c-48d9-a297-a1a099498516/pasted-text.txt`.
- Identified crash signature:
  - `EXC_GUARD`
  - `GUARD_TYPE_MACH_PORT`
  - `*** multi-threaded process forked ***`
  - `crashed on child side of fork pre-exec`
  - crash stack enters `SCDynamicStoreCopyProxiesWithOptions`, `Curl_macos_init`, `curl_easy_init`, and `curl_cffi/_wrapper.abi3.so`.
- Confirmed running process tree:
  - UI server: `from ui.app_server import run_server; run_server(port=8765)`
  - child daemon: `runtime/atlas_runtime_daemon.py --interval 60 ...`
- Searched AtlasOS for `curl_cffi`, multiprocessing, fork, and subprocess usage.
- Found high-probability local trigger in `/Users/markus/AtlasOS/tools/market_data/market_data_provider.py`.

## Findings

- The crash is not a Python exception in Atlas business logic; it is a macOS process-level crash caused by unsafe fork behavior in a multi-threaded process.
- `tools/market_data/market_data_provider.py` uses:
  `ctx = mp.get_context("fork") if "fork" in mp.get_all_start_methods() else mp.get_context()`
- That code runs hard-timeout isolation for `akshare` and `yfinance` sources.
- The crash report shows the child process loading `curl_cffi`/`libcurl-impersonate`, then libcurl asks macOS SystemConfiguration for proxy settings through `SCDynamicStoreCopyProxiesWithOptions`.
- macOS reports the child was forked from a multi-threaded process and crashed before exec. This matches the known class of unsafe operations after `fork` in a multi-threaded macOS process.
- The direct symptom is likely a market-data subprocess crash during quote/history refresh, not necessarily a full UI server crash.

## Decisions

- Do not modify code in this diagnostic turn.
- Preferred repair is to avoid `fork` for the market data isolation process on macOS. Use `spawn` by default, or at least use `spawn` when `sys.platform == "darwin"`.
- A temporary operational workaround is to set `ATLAS_MARKET_PROVIDER_HARD_TIMEOUT=0`, which avoids the multiprocessing hard-timeout path, but this may reintroduce hanging provider calls.

## Current State

- Diagnosis complete.
- No files changed except this session log and session indexes.

## Resume Instructions

If implementing a fix:

1. Open `/Users/markus/AtlasOS/tools/market_data/market_data_provider.py`.
2. Change `_load_history_in_process` so macOS uses `mp.get_context("spawn")` instead of `fork`.
3. Consider preserving `fork` only for non-macOS platforms if needed.
4. Test market snapshots from the running AtlasOS environment.
5. Check macOS crash reports and Atlas runtime logs after refresh.

## Open Questions

- Should the repair prefer `spawn` globally for reliability, or only on macOS to preserve Linux performance?
- Should Atlas disable yfinance/akshare hard-timeout subprocess isolation when running inside the UI daemon?
