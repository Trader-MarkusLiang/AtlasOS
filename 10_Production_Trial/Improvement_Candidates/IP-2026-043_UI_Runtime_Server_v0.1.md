# IP-2026-043 — UI Runtime Server v0.1

## Category

Engineering / Runtime UI / Safe Control Gateway

## Origin

ISSUE-2026-043 — UI Runtime Server Needed

## Problem

Atlas UI v0.1 modules need a lightweight browser-facing runtime server that exposes chat,
dashboard, replay, and safe controls without coupling UI to cognition.

## Implemented Scope

- Added `ui/app_server.py`.
- Added HTTP routes:
  - `GET /`
  - `GET /chat`
  - `POST /chat/send`
  - `GET /dashboard`
  - `GET /replay`
  - `GET /control`
  - `GET /state`
  - `POST /control/start`
  - `POST /control/stop`
  - `POST /control/set_interval`
  - `POST /control/set_llm_provider`
- Added FastAPI app construction when FastAPI is available.
- Added standard-library HTTP fallback runner for environments without FastAPI/Flask.
- Updated `runtime/atlas_runtime_daemon.py` to poll `runtime/inbox/user_event.jsonl`.
- Added `99_Verification/validate_ui_runtime_server_v0_1.py`.

## Runtime Inbox Format

```json
{
  "timestamp": "",
  "type": "user_query",
  "content": "",
  "source": "ui_chat"
}
```

## Boundary

This IP does not modify:

- Event Fusion
- CIL / LMSE / MPCE / MLE / UMIS
- v0.5 self-organizing engine
- Decision Contract logic
- CDE logic
- `portfolio.local.yaml`

It does not introduce:

- trading logic
- prediction logic
- broker connectivity
- UI-driven cognitive mutation

## Status

Implemented — thin UI web gateway with daemon JSONL inbox integration.

## Final Decision

READY FOR UI RUNTIME SERVER REVIEW
