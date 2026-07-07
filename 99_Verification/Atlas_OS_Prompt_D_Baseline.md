# Atlas OS Prompt D Baseline

Date: 2026-07-08 07:06 CST

## Scope

Prompt D begins after Prompt A/B/C on branch `codex/overnight-productization-sprint`. This
baseline freezes the Prompt C state before real-world activation work. It records runtime evidence
without exposing provider secrets, private portfolio contents, API keys, or exact private wealth.

## Git State

| Item | Value |
|---|---|
| Branch | `codex/overnight-productization-sprint` |
| HEAD | `44debaa791acf535a40ef81ceab94cce712337ca` |
| HEAD short | `44debaa` |
| Upstream | `origin/codex/overnight-productization-sprint` |
| Ahead/behind | ahead by 4 commits |
| Prompt C local commits | `4c58743`, `4774449`, `16daf57`, `44debaa` |
| Origin branch head | `de19343 Morning red-team repair and internal alpha closure` |
| Main/origin head | `6968821 Add provider model picker` |
| Dirty files at Prompt D logging start | session-log/index updates only |

Recent history:

```text
44debaa Close Prompt C session log
16daf57 Fix Prompt C secret scan self-reference
4774449 Close Prompt C completion gaps
4c58743 Establish Prompt C completion backlog
de19343 Morning red-team repair and internal alpha closure
825fec0 Update productization sprint handoff status
d204ab9 Add runtime daily cycle metadata
1e1d4a7 Add Keychain-first provider secret storage
e15c83d Add Atlas productization backbone
be3f606 Align Atlas roadmap version tracks
390d00b Audit Atlas productization baseline
6968821 Add provider model picker
```

## Runtime And UI Processes

Atlas-related local processes were present before Prompt D activation work:

| Process | Evidence |
|---|---|
| UI server | Python `from ui.app_server import run_server; run_server(port=8767)` listening on `127.0.0.1:8767` |
| UI server | Python `from ui.app_server import run_server; run_server(port=8768)` listening on `127.0.0.1:8768` |
| Local LLM/OpenAI-compatible shim | `rapid-mlx` listening on `127.0.0.1:8000` |
| MLX OpenAI server | `mlx_lm.server` listening on `127.0.0.1:8080` |
| MoreCode cc-switch shims | listening on `127.0.0.1:15722` and `127.0.0.1:15723` |
| ARK/Volcano cc-switch shim | listening on `127.0.0.1:15732` |
| Ollama/Anthropic bridge | listening on `127.0.0.1:15731` |
| Open WebUI | listening on `*:8081` |

No active `runtime/atlas_runtime_daemon.py` process was observed at baseline.

## Runtime Evidence Files

| Path | Baseline state |
|---|---|
| `runtime/config/user_config.json` | exists, 5.0 KB, ignored local config |
| `runtime/inbox/user_event.jsonl` | exists, 0 B |
| `runtime/logs/cognitive_snapshots.jsonl` | exists, 102 MB, 5,237 valid JSONL lines |
| `runtime/logs/decision_traces.jsonl` | exists, 4.2 MB, 5,267 valid JSONL lines |
| `runtime/logs/llm_traces.jsonl` | exists, 407 KB, 429 valid JSONL lines |
| `runtime/logs/runtime_runs.jsonl` | exists, 23 MB, 10,836 valid JSONL lines |
| `runtime/state/atlas_runtime.sqlite` | exists, 64 KB |

Latest observed runtime log timestamp at baseline: `2026-07-07T17:32:35Z`.

## Runtime SQLite State

Database path: `runtime/state/atlas_runtime.sqlite`.

| Table | Row count |
|---|---:|
| `attention_history` | 6 |
| `decision_briefs` | 6 |
| `events` | 0 |
| `kv_state` | 2 |
| `state_transitions` | 0 |
| `system_logs` | 6 |

Important Prompt D finding: the baseline runtime DB did **not** contain `forecast_ledger`. Prompt C
forecast proof therefore requires special scrutiny for temporary DB usage or runtime-path
disconnect.

## Provider Registry Safe View

Configured active provider: `morecode`.

Fallback chain:

```text
morecode -> ark -> volcano -> ollama -> openai -> claude -> custom
```

Safe provider status, with no secret values exposed:

| Provider | Enabled | Base URL type | Model | Secret storage | Health | Latency |
|---|---:|---|---|---|---|---:|
| `morecode` | true | local cc-switch shim | `gpt-5.5` | none | error | 0 ms |
| `ark` | true | local cc-switch shim | `kimi-k2.6` | none | error | 0 ms |
| `volcano` | true | local cc-switch shim | `kimi-k2.6` | none | error | 0 ms |
| `ollama` | true | localhost Ollama API | `llama3.1` | none | error | 3 ms |
| `openai` | true | public OpenAI API | `gpt-5.5` | none | error | 0 ms |
| `claude` | true | public Anthropic API | `claude-sonnet-4-20250514` | none | error | 0 ms |
| `custom` | true | empty | `custom-default` | none | error | 0 ms |

Baseline interpretation: local shims exist and may support real inference without Atlas-stored API
keys, but registry health state was stale/error at baseline. Prompt D live LLM activation must use
an actual inference request through the provider router, not a health check alone.

## Local Config And Portfolio State

Safe local config metadata:

| Item | State |
|---|---|
| `assets.asset_list` | 0 configured entries |
| `assets.weights` | 0 configured entries |
| `assets.portfolio_json` | present but empty object payload |
| `system.tick_interval` | configured |
| `system.runtime_mode` | configured |
| `system.trust_threshold` | configured |
| `system.hypothesis_switching_sensitivity` | configured |
| UI language | configured |

No private holdings, account values, broker data, or exact wealth fields were printed or committed.

## Roadmap State

| Item | Value |
|---|---|
| Roadmap version | `parallel-track productization roadmap` |
| Current stage | `productization internal alpha after Prompt C completion enforcement` |
| Next stage | `live market channels, real Keychain smoke, real-duration soak, forecast accountability live sample growth` |
| v0.8 Causal Interaction Layer | planned, not implemented |

## Prompt C Tribunal Baseline

Prompt C local reports classify the branch as stronger internal alpha hardening, not Release
Candidate and not 24-hour stable. The Prompt C tribunal used `PROVEN_COMPLETE` style labels for
fixture-backed areas; Prompt D will reclassify all capabilities with explicit evidence levels:

- `LIVE_PROVEN`
- `REAL_RUNTIME_PROVEN`
- `CONTROLLED_FIXTURE_PROVEN`
- `ACCELERATED_ONLY`
- `PARTIAL`
- `DISCONNECTED`
- `FAILED`
- `EXTERNAL_BLOCKER`

## Baseline Risk Flags

1. `forecast_ledger` is absent from the baseline runtime SQLite DB, so Prompt C forecast lifecycle
   proof is not yet proven on the real runtime DB path.
2. No active Atlas daemon process was observed at baseline; subsequent daemon-path proof must start
   or attach to the real daemon.
3. UI server processes are present, but baseline UI evidence is process/port-level only; browser UX
   proof remains pending.
4. Provider registry health is stale/error despite local shims being present; live inference must be
   attempted through the intended router.
5. Local portfolio config is effectively empty; real portfolio runtime differential proof will need
   a safe temporary UI-config path with restore discipline.
