# 2026-07-09 13:40 CST — Home Freshness UI Audit

## Metadata

- Date: 2026-07-09 13:40 CST
- Session id: current Codex thread
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Investigate and repair Home/Decision Brief typography imbalance and poor market freshness display
- Status: active
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

User reported the Home/Decision Brief page has visually inconsistent font sizes and poor-looking data freshness. They asked whether this is a workflow/process issue and requested investigation.

## Work Done

- Inspected current git state and relevant UI/runtime files.
- Reviewed:
  - `ui/pages/product_views.py`
  - `ui/design/tokens.py`
  - `ui/components/global_topbar.py`
  - `ui/components/app_shell.py`
  - `runtime/market_intelligence.py`
  - `tools/market_data/market_data_provider.py`
  - `/state` runtime response on `127.0.0.1:8765`
- Verified daemon/UI API is running and ticking.
- Found Home hero title uses `_main_change()` which returns the first 120 chars of `DecisionPacket.causal_summary`, causing long English LLM text to render as a huge hero heading.
- Found freshness display exposes raw market timestamp in the top bar rather than a user-readable channel health summary.
- Found market data provider normalization did not consistently adapt Hong Kong padded tickers and
  Shanghai A-share suffixes to Yahoo-compatible symbols.
- Found current market config has no separate `market_intelligence` channel config; only portfolio and LLM config exist. Therefore news, breadth, macro, narrative channels honestly show `NOT_CONFIGURED`.
- Patched `tools/market_data/market_data_provider.py`:
  - Yahoo-compatible HK tickers now normalize to four-digit `.HK`.
  - Yahoo-compatible Shanghai A-share tickers now normalize from `.SH` to `.SS`.
  - akshare calls now receive suffix-free local symbols.
- Patched Home/UI display:
  - `ui/pages/product_views.py` now extracts short hero headlines instead of rendering long `causal_summary` text as the H1.
  - `ui/design/tokens.py` reduces hero H1 scale and adds safer wrapping.
  - `ui/components/global_topbar.py` and `ui/components/app_shell.py` now show freshness as channel/asset health instead of raw ISO timestamps.
  - Data freshness card now shows price coverage and per-asset availability rows.
- Patched runtime status reliability:
  - `ui/components/runtime_status_indicator.py` now reads `runtime.running`.
  - `ui/components/app_shell.py` updates the visible status label during polling.
  - `ui/system_control_panel.py` starts daemon child processes with `start_new_session=True` and can recover the PID file by discovering an already-running daemon.
- Restarted UI LaunchAgent and verified runtime daemon PID consistency.

## Decisions

- Keep cognition/runtime semantics unchanged.
- Fix display logic in UI only for typography and freshness wording.
- Fix ticker normalization in the market data utility because it is ingestion support, not cognition logic.
- Continue to report unavailable channels honestly instead of hiding degraded data.
- Treat unconfigured macro/news/breadth/narrative channels as honest product state, not a bug.

## Current State

- Completed.
- Runtime daemon is running from PID file with 60-second interval.
- Home shows short hero title, readable freshness summary, and per-asset market availability.
- Current validated market observations:
  - all three locally configured portfolio assets returned `Available` in the runtime state
- Remaining degraded context is expected because several non-price channels are not configured.

## Verification

- `python3 -m py_compile ui/pages/product_views.py ui/components/global_topbar.py ui/components/app_shell.py ui/components/runtime_status_indicator.py ui/design/tokens.py ui/system_control_panel.py tools/market_data/market_data_provider.py`
- `get_market_snapshot()` smoke test:
  - locally configured Hong Kong, Shenzhen, and Shanghai symbols normalized successfully
  - all three local portfolio assets returned `Available`
- `/state` verification:
  - runtime running: `true`
  - PID file repaired to active daemon PID
  - price observations: `3/3 Available`
- Browser verification:
  - hero title: short localized state headline
  - topbar freshness: `价格 3/3 · 4 未配置`
  - topbar runtime status: `运行中`

## Resume Instructions

If this work needs to continue, inspect:

- `ui/pages/product_views.py`
- `ui/design/tokens.py`
- `ui/components/global_topbar.py`
- `ui/components/app_shell.py`
- `ui/components/runtime_status_indicator.py`
- `ui/system_control_panel.py`
- `tools/market_data/market_data_provider.py`

Next steps:

1. Configure additional real channels if desired: news, macro, breadth, narrative attention, and liquidity proxy.
2. Consider a dedicated runtime LaunchAgent for the daemon if Atlas should survive logout/reboot independently of UI control.

## Open Questions

- Whether to configure additional real market intelligence channels later, such as news, macro, market breadth, and narrative attention providers.
