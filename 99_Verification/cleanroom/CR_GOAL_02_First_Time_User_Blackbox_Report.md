# CR_GOAL_02 — First-Time User Black-Box Report

## Verdict

Classification: `BLACKBOX_PROVEN`

Evidence level: `BLACKBOX_PROVEN`

Atlas OS can be configured and operated through the user-facing UI path from a fresh clone and
clean runtime state. The final rerun proved language switching, LLM configuration, model listing,
provider test, runtime start, first brief generation, product pages, chat event ingestion, and
runtime stop. Earlier fresh CR_GOAL_02 browser artifacts also verified that the setup page exposes
asset rows for adding assets without editing a raw JSON textarea.

## Fresh Evidence Scope

- Verification branch: `codex/cleanroom-verification`
- Final rerun commit: `f15370019467e28d1f78df765598de718e25efd0`
- Final fresh clone: `/tmp/atlas-cleanroom-cr02-final-20260708-161259`
- Final clean runtime state: `/tmp/atlas-cleanroom-state-cr02-final-20260708-161259`
- Final evidence directory:
  `99_Verification/cleanroom/artifacts/cr_goal_02/rerun_final/`
- Summary artifact:
  `99_Verification/cleanroom/artifacts/cr_goal_02/rerun_final/summary.json`

Prior GOAL artifacts were not used as proof. Earlier CR_GOAL_02 screenshots and reruns were used
only to identify defects and verify repairs.

## User Journey Result

| Step | Result | Evidence |
|---|---:|---|
| Open Atlas | PASS | `01_home_initial.html` |
| Understand Atlas | PASS | Home and onboarding copy rendered without raw state leakage |
| Select Chinese | PASS | `/ui/language` returned `{"language": "zh", "status": "saved"}` |
| Switch back to English | PASS | `/ui/language` returned `{"language": "en", "status": "saved"}` |
| Configure LLM | PASS | `/settings` saved active provider `ollama` |
| Test provider | PASS | `/llm/provider/test` returned `healthy`, latency `2 ms` |
| Select model | PASS | `/llm/provider/models` returned 5 models and included `qwen3-coder:30b` |
| Add 3 assets | PASS | Browser artifact `screenshots/04_setup_assets_configured.png`; final settings endpoint saved NVDA / TSM / MSFT context |
| Set percentages | PASS | 35 / 30 / 20 percentages persisted in clean user config |
| Save | PASS | `/settings` returned `status: saved` |
| Start Atlas | PASS | `/control/start` returned `started`, PID `76922` |
| Confirm running | PASS | Runtime generated tick telemetry and state |
| See first brief | PASS | Runtime log and state showed DecisionPacket / brief output |
| Open Markets | PASS | `/markets` rendered |
| See freshness/degraded state | PASS | Market state was explicit; missing channels were not treated as zero signal |
| Open Portfolio | PASS | `/portfolio` rendered configured portfolio context |
| Open Predictions | PASS | `/predictions` rendered Forecast Ledger |
| Open Learning | PASS | `/learning` rendered |
| Ask Atlas | PASS | `/chat/send` queued a `user_query`; next tick processed user input |
| Stop Atlas | PASS | `/control/stop` returned `stopped`; PID file removed |

## Runtime Evidence

Final rerun generated fresh runtime artifacts under the clean state root:

| Artifact | Result |
|---|---:|
| Runtime DB | Created at `/tmp/atlas-cleanroom-state-cr02-final-20260708-161259/runtime/atlas_runtime.sqlite3` |
| Runtime log | 6 lines, 20,461 bytes |
| Decision trace | 2 lines, 2,522 bytes |
| LLM trace | 2 lines, 2,995 bytes |
| Cognitive snapshot | 2 lines, 27,556 bytes |
| UI inbox after processing | Chat event cleared after daemon ingestion |

The final `/state` after stop reported:

```json
{
  "runtime": {
    "running": false,
    "pid": null,
    "rolling_trust_index": 0.4836,
    "feedback_stability_index": 0.8944
  }
}
```

## LLM Path Observed During User Journey

The final first-user run used the normal UI/runtime path:

```text
UI settings
→ provider registry
→ /llm/provider/models
→ /llm/provider/test
→ /control/start
→ runtime daemon
→ DecisionLoop / orchestrator
→ llm_router
→ provider_router
→ Ollama qwen3-coder:30b
→ Decision Contract
→ persisted telemetry
→ visible /state and UI output
```

The final LLM trace recorded:

- Provider: `ollama`
- Model: `qwen3-coder:30b`
- Call count: 2
- Latest latency: approximately 2.3 seconds
- DecisionPacket status: validated by runtime and persisted in telemetry

CR_GOAL_03 will independently attack the same path with malformed response, invalid model,
timeout, fallback, and provider failure cases.

## Defects Found And Repaired

### P1 — Home raw boolean leakage

Initial first-user run exposed raw `True` / `False` style state. Fixed in:

- `e5c8fa6 cleanroom: repair first-user UI trace leakage`

### P1 — Dashboard raw trace / JSON leakage

Initial dashboard exposed raw structural trace blocks. Fixed in:

- `e5c8fa6 cleanroom: repair first-user UI trace leakage`

### P1 — Active provider ignored by runtime default model

The runtime default `llm_model=gpt-5.5` forced OpenAI routing even when the UI active provider was
Ollama. Fixed in:

- `752c6eb cleanroom: repair active provider routing and model health`

### P1 — Provider health did not validate selected Ollama model

Ollama health checked `/api/tags` reachability only and marked a missing selected model healthy.
Fixed in:

- `752c6eb cleanroom: repair active provider routing and model health`

### P1 — Stop left stale PID after daemon exit

The UI stop action returned immediately while the daemon became a zombie and the PID file stayed.
Fixed in:

- `f153700 cleanroom: cleanly report runtime stop state`

Final rerun proved `stop_status: stopped`, `running: false`, no process status, and no PID file
remaining.

## Non-Issues / False Positives

- `/setup` contained JavaScript object literals such as `const providerMeta = {...}`. This is not
  visible raw dict leakage to the user.
- `/predictions` contained JavaScript `JSON.stringify(...)` for the forecast form result target.
  This is not a default raw JSON panel.
- `UNKNOWN` appeared inside onboarding explanatory text that teaches the user what UNKNOWN means,
  not as an unexplained runtime state leak.

## Security Check

- No API key was configured or stored for Ollama.
- `ATLAS_DISABLE_KEYCHAIN=1` was used in the clean-room state to avoid touching local Keychain.
- No `sk-` secret-shaped value appeared in the saved settings response.
- LLM trace stored provider/model/latency/output, not provider secrets.

## Remaining Risks

- The UI server script still listens on default port `8765`; positional host/port arguments are
  ignored. This is not a first-user blocker for the documented default command, but it is
  documentation/operability friction for future cleanup.
- CR_GOAL_02 proves the first-user path, not long-run provider stability or all LLM failure modes.
  Those remain CR_GOAL_03 scope.
- Market freshness remains a separate CR_GOAL_04 question; CR_GOAL_02 only verified the page and
  honest degraded rendering.

## Transition

CR_GOAL_02 is complete.

Proceed to:

```text
CR_GOAL_03_LIVE_LLM_BLACKBOX
```
