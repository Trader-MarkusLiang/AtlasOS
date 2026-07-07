# Atlas OS Morning Baseline State

Date: 2026-07-08 00:50 CST

## Git State

- Branch: `codex/overnight-productization-sprint`
- HEAD: `825fec024da934043c11e877adac3ffa6dc6bd2d`
- HEAD summary: `825fec0 Update productization sprint handoff status`
- Upstream: none configured for current branch
- Dirty files at freeze: none
- Recent local commits:
  - `825fec0` Update productization sprint handoff status
  - `d204ab9` Add runtime daily cycle metadata
  - `1e1d4a7` Add Keychain-first provider secret storage
  - `e15c83d` Add Atlas productization backbone
  - `be3f606` Align Atlas roadmap version tracks
  - `390d00b` Audit Atlas productization baseline

## Running Processes And Ports

No process with an Atlas daemon/UI command name was detected at freeze time.

Detected local listeners:

| PID | Port | Command | Atlas-owned |
|---|---:|---|---|
| 1831 | 18080 | `/Users/markus/autonomy_vision_action_lab/apps/console_backend/server.py` | No |
| 1864 | 8000 | `rapid-mlx serve ... qwen-rapid-local` | No |
| 1866 | 8080 | `mlx_lm.server ... Qwen3.6-35B-A3B-8bit` | No |
| 1988 | 11434 | `Ollama.app ... ollama serve` | External local LLM service |
| 1196 | 5000 | `ControlCe...` | Unknown / not identified as Atlas |

## Runtime Evidence Paths

The following runtime/private paths exist and are gitignored. Contents were not wiped.

| Path | Size | Modified | Git ignored |
|---|---:|---|---|
| `runtime/config/user_config.json` | 5157 | 2026-07-08 00:47:07 CST | YES |
| `runtime/config/user_config.json.backup-before-ccswitch-sync-20260707_0904` | 3440 | 2026-07-07 06:55:17 CST | YES |
| `runtime/state/atlas_runtime.sqlite` | 65536 | 2026-07-06 21:41:34 CST | YES |
| `runtime/logs/cognitive_snapshots.jsonl` | 1122913 | 2026-07-08 00:47:07 CST | YES |
| `runtime/logs/decision_traces.jsonl` | 124620 | 2026-07-08 00:47:07 CST | YES |
| `runtime/logs/llm_traces.jsonl` | 255810 | 2026-07-08 00:47:07 CST | YES |
| `runtime/logs/runtime_runs.jsonl` | 847369 | 2026-07-08 00:47:07 CST | YES |
| `runtime/inbox/user_event.jsonl` | 0 | 2026-07-06 13:10:26 CST | YES |

## SQLite State Summary

Current `runtime/state/atlas_runtime.sqlite` table counts:

| Table | Count / Status |
|---|---:|
| `kv_state` | 2 |
| `decision_briefs` | 6 |
| `attention_history` | 6 |
| `system_logs` | 6 |
| `events` | 0 |
| `state_transitions` | 0 |
| `forecast_ledger` | missing |

Interpretation: Forecast Ledger exists in code and was validated with temporary databases, but the
current long-lived runtime SQLite file does not yet contain forecast-ledger state.

## Roadmap State

- Roadmap file: `docs/atlas_roadmap.json`
- Version: `parallel-track productization roadmap`
- Current stage: `production validation + autonomous productization`
- Next stage: `Decision Brief-first productization, market ingestion, portfolio context, forecast accountability`
- Tracks:
  - Atlas Core / Knowledge OS
  - Atlas Runtime
  - Atlas Cognitive Overlay
  - Atlas UI / Product
  - Atlas Data / Market Intelligence

## Previous Overnight Evidence

- `99_Verification/Atlas_OS_Overnight_Baseline_Audit.md`
- `99_Verification/Atlas_OS_Overnight_Productization_Report.md`
- `99_Verification/Atlas_OS_Productization_Backbone_Validation.md`
- `99_Verification/Atlas_OS_Long_Run_Stability_Report.md`

## Freeze Notes

- No runtime evidence was deleted or reset.
- Private config/log/database files were not committed.
- This baseline does not validate claims; it only records the morning starting state for the
  independent red-team pass.
