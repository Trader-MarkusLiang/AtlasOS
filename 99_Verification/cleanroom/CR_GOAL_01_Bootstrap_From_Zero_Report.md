# CR_GOAL_01 Bootstrap From Zero Report

## Summary

CR_GOAL_01 is `BLACKBOX_PROVEN` with a documentation friction note.

From a fresh clone at the exact candidate commit, Atlas OS started the UI server, exposed empty
state honestly, started the runtime daemon through the UI control path, persisted first runtime
state, handled missing LLM credentials through failsafe output, and processed a queued UI chat event
through the daemon path. No old runtime DB, telemetry, inbox, PID file, or local portfolio state was
used.

## Environment

| Field | Value |
|---|---|
| Fresh clone | `/tmp/atlas-cleanroom-20260708-153302` |
| Runtime state root | `/tmp/atlas-cleanroom-state-20260708-153302` |
| Candidate commit | `ed63678793bdc5d10c1469433e461a6c20db7927` |
| Python | `3.9.6` |
| FastAPI | missing |
| uvicorn | missing |
| keyring | missing |
| requests | available |
| yfinance | available |
| akshare | available |

## Dependency Discovery

No top-level dependency manifest was found:

```text
requirements.txt: missing
pyproject.toml: missing
Pipfile: missing
package.json: missing
```

The scan found `ui/pages/setup.py`, but that is a UI page, not a packaging setup script.

Optional dependency behavior:

- `fastapi` / `uvicorn` were missing.
- `ui/app_server.py` fell back to its standard-library HTTP server.
- `keyring` was missing; no Keychain-dependent path was required for bootstrap.

## Startup Tests

### UI Server Fallback

Command shape:

```text
python3 -c "from ui.app_server import run_server; run_server(port=54253)"
```

Result:

| Endpoint | Result |
|---|---|
| `/` | HTTP 200 |
| `/setup` | HTTP 200 |
| `/dashboard` | HTTP 200 |
| `/state` | HTTP 200 JSON |

Observed empty state:

- `attention`: `null`
- `liquidity`: `null`
- `last_decision_brief_id`: `null`
- market intelligence status: `not_run`
- market channels: `NOT_CONFIGURED`
- provider health: `unknown`
- provider key storage: `none`

The empty state did not pretend missing market data or LLM credentials were usable signals.

### Default UI Command

Command:

```text
python3 ui/app_server.py
```

Result:

| Endpoint | Result |
|---|---|
| `/` | HTTP 200 on default port `8765` |
| `/state` | HTTP 200 JSON |

This proves the direct script entrypoint works without FastAPI or uvicorn.

### UI Control Starts Daemon

Request:

```text
POST /control/start
```

Result:

```text
status: started
pid_file: /tmp/atlas-cleanroom-state-20260708-153302/runtime/state/atlas_ui_runtime.pid
```

The generated daemon command used only clean-room paths for DB, logs, event inbox, UI inbox, and
config.

First tick result:

| Metric | Value |
|---|---|
| runtime status | `success` |
| tick counter after first tick | `1` |
| decision brief created | yes |
| runtime log written | yes |
| SQLite state written | yes |
| decision telemetry written | yes |
| cognitive snapshot written | yes |
| LLM trace written | yes |
| market refresh status | `no_configured_assets` |
| market channel status | `NOT_CONFIGURED` |
| LLM decision packet | neutral failsafe, `all_providers_failed` |
| trading execution | none |

### CLI Daemon Command

Command shape:

```text
python3 runtime/atlas_runtime_daemon.py --interval 10 --max-cycles 1 --no-sleep
```

Result:

| Metric | Value |
|---|---|
| exit code | `0` |
| runtime status | `success` |
| tick counter after CLI tick | `2` |
| UI inbox event ingested | `1` |
| `user_input_event` status | `handled` |
| UI inbox after tick | empty |
| decision briefs in DB | `2` |
| state transitions in DB | `2` |

## Required Questions

| Question | Answer |
|---|---|
| Is setup documented? | Partially. Daemon run command is documented in `runtime/atlas_runtime_daemon.py`; UI script entry exists and historical docs mention it, but no top-level setup/install quickstart exists. |
| Can UI start without hidden manual patching? | Yes. It starts through stdlib fallback without installing FastAPI/uvicorn. |
| Can daemon start without old local state? | Yes. It started through `/control/start` and direct CLI using clean DB/log/inbox paths. |
| Are missing dependencies understandable? | Partially. Missing FastAPI/uvicorn are handled transparently by fallback; missing keyring does not block bootstrap. The repository does not have a dependency manifest explaining optional dependencies. |
| Does product tell user what is missing? | Partially. `/state` reports `NOT_CONFIGURED` for market channels and provider key storage `none`; install/dependency guidance is not prominent. |

## Required Interventions

- Chose clean-room state paths via environment variables.
- Chose an unused port for the first UI server.
- Used the direct default UI script for a separate confirmation.
- No package installation was performed.
- No old runtime DB, telemetry, inbox, PID, portfolio, or local config was copied.
- No cognition core, CDE, Decision Contract, trading logic, or portfolio holdings were modified.

## Defects / Friction

| Severity | Item | Evidence | Locally fixable |
|---|---|---|---|
| P2 | No top-level bootstrap quickstart or dependency manifest | Fresh clone has no `requirements.txt`, `pyproject.toml`, or README quickstart for UI/runtime startup. | yes |
| P2 | Optional dependency expectations are implicit | FastAPI/uvicorn/keyring missing, but fallback works. | yes |

No P0/P1 bootstrap blocker was found.

## Classification

Goal status: `PROVEN_COMPLETE`

Evidence level: `BLACKBOX_PROVEN`

Rationale: The fresh clone starts and persists real runtime state with clean paths and no hidden
state reuse. Documentation gaps remain but do not block bootstrap.

## Transition

Proceed to:

```text
CR_GOAL_02_FIRST_TIME_USER_BLACKBOX
```

