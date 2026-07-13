# Restore Canonical Atlas UI Service

- Date: 2026-07-13 14:27 CST
- Session id: current Codex task
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Restore unreachable canonical UI and runtime services
- Status: Completed
- Branch: `codex/frontend-master-upgrade`

## User Request Summary

The canonical Atlas URL at `http://127.0.0.1:8765` refused connections. Restore access and verify
the backend runtime is active.

## Investigation

- No process was listening on port `8765`.
- The existing `com.atlasos.ui.8765` LaunchAgent was loaded with `RunAtLoad` and `KeepAlive`, but
  remained stopped after receiving signal 15.
- The runtime daemon was also stopped, so restoring only the UI would have produced a stale shell.
- The plist syntax, working directory, Python command, and log paths were valid.

## Work Done

- Restarted the canonical UI with:
  `launchctl kickstart -k gui/$(id -u)/com.atlasos.ui.8765`.
- Started the runtime through Atlas's `/control/start` endpoint with the configured 60-second tick,
  local user config, MoreCode model setting, and two-hour proactive update cadence.
- Did not modify cognition, decision, market, provider, or portfolio semantics.

## Verification

- LaunchAgent state: running.
- Port `8765`: listening on `127.0.0.1`.
- `/`, `/state`, and `/markets`: HTTP 200 after a delayed recheck.
- Runtime PID exists and `/state` reports `runtime.running: true` and mode `live`.

## Decisions

- Keep `8765` as the canonical UI address.
- Use the LaunchAgent for UI persistence instead of a Codex terminal session.
- Use Atlas's supported control endpoint for the runtime daemon.

## Resume Instructions

1. If only the UI is unreachable, run
   `launchctl kickstart -k gui/$(id -u)/com.atlasos.ui.8765`.
2. If UI works but runtime is stopped, use `POST /control/start`.
3. Do not create another temporary frontend port unless `8765` cannot be repaired.

## Open Questions

- None.
