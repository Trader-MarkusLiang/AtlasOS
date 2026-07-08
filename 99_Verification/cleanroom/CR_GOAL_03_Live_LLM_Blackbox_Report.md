# CR_GOAL_03 — Live LLM Black-Box Report

## Verdict

Classification: `LIVE_PROVEN`

Evidence level: `LIVE_PROVEN`

Atlas OS independently used a configured LLM provider through normal runtime paths from a fresh
clone and clean runtime state. A live local Ollama provider returned real inference output, the
runtime normalized it through the Decision Contract, and safe telemetry persisted the call without
secrets.

## Fresh Evidence Scope

- Verification branch: `codex/cleanroom-verification`
- Fresh clone: `/tmp/atlas-cleanroom-cr03-20260708-161754`
- Clean runtime state: `/tmp/atlas-cleanroom-state-cr03-20260708-161754`
- Commit under test: `04b0a152f610f681df7444987e6c9f8fa7025a47`
- Evidence directory:
  `99_Verification/cleanroom/artifacts/cr_goal_03/`

Prior GOAL_02 LLM reports and previous live-provider artifacts were not used as proof.

## Successful Live Runtime Path

Observed path:

```text
UI /settings
→ runtime/config/user_config.json
→ provider registry
→ provider model list
→ provider health check
→ atlas_runtime_daemon.py --max-cycles 1
→ DecisionLoop / orchestrator
→ llm_router
→ provider_router
→ live Ollama provider
→ qwen3-coder:30b inference
→ Decision Contract validation
→ decision trace / LLM trace / runtime log
```

Evidence:

- `artifacts/cr_goal_03/live_runtime_path/ui_config_summary.json`
- `artifacts/cr_goal_03/live_runtime_path/live_runtime_telemetry_summary.json`

Live provider facts:

| Field | Value |
|---|---|
| Provider | `ollama` |
| Model | `qwen3-coder:30b` |
| Provider health | `healthy` |
| Model list | `ok`, 5 models |
| Live inference latency | `2671 ms` |
| DecisionPacket action | `observe` |
| DecisionPacket risk | `low` |
| Raw secret recorded | No |

The live LLM trace recorded provider, model, latency, prompt hash, and raw output. It did not record
API keys or bearer tokens.

## Failure Injection Matrix

Controlled local OpenAI-compatible fixture endpoints were used to attack provider failure behavior.
These failure cases prove isolation and contract failsafe behavior; they are not counted as live
provider proof.

Evidence:

- `artifacts/cr_goal_03/failure_matrix/summary.json`

| Case | Provider result | Decision Contract result |
|---|---|---|
| Valid OpenAI-compatible fixture | `ok` | Valid neutral packet |
| 401 wrong key | `failsafe`, `HTTP Error 401` | Neutral failsafe packet |
| 429 rate limit | `failsafe`, `HTTP Error 429` | Neutral failsafe packet |
| Empty response | `failsafe`, `empty_response` | Neutral failsafe packet |
| Malformed response | `failsafe`, JSON parse error | Neutral failsafe packet |
| Timeout | `failsafe`, `timed out` | Neutral failsafe packet |
| Model not found | health `model_not_found`, route `HTTP Error 404` | Neutral failsafe packet |

No failure case crashed the runtime adapter.

## Fallback Proof

Fallback was proven with a primary mock provider returning 429 and a real Ollama fallback.

Evidence:

- `artifacts/cr_goal_03/fallback_contract/summary.json`

Result:

```text
custom fixture provider
→ HTTP 429
→ fallback_chain
→ live ollama / qwen3-coder:30b
→ provider_router status ok
→ Decision Contract valid neutral packet
```

Fallback latency was `690 ms`, and the packet was not a Decision Contract failsafe.

## Active Provider Alias Repair Verification

The runtime default model alias `gpt-5.5` now uses the active provider from the provider registry
instead of forcing OpenAI.

Observed:

```json
{
  "provider": "ollama",
  "model": "qwen3-coder:30b",
  "raw_text_only": "true"
}
```

This verifies the repair in:

- `752c6eb cleanroom: repair active provider routing and model health`

## Provider Coverage

| Provider | Result |
|---|---|
| Ollama | `LIVE_PROVEN` |
| Custom/OpenAI-compatible fixture | `CONTROLLED_FIXTURE_PROVEN` for failure isolation |
| OpenAI | `NOT_CONFIGURED` in clean-room state |
| Claude / Anthropic | `NOT_CONFIGURED` in clean-room state |
| MoreCode | `NOT_CONFIGURED` in clean-room state |
| ARK / Volcano | `NOT_CONFIGURED` in clean-room state |

Only Ollama is claimed as live proven. Public or cc-switch providers were not reclassified as live
without clean-room credentials.

## Security Check

- No real API key was required for Ollama.
- Fixture keys were not persisted in committed artifacts.
- Secret-shape scan over CR_GOAL_03 artifacts found no `sk-`, bearer token, or authorization
  header leakage.
- `ATLAS_DISABLE_KEYCHAIN=1` was used for clean-room config writes.
- LLM telemetry retained output and metadata only; no provider secret values were stored.

## Boundary Check

No Event Fusion, CIL, LMSE, MPCE, MLE, CDE, Decision Contract semantics, runtime cognition,
trading execution, broker integration, or portfolio mutation were modified for this goal.

All provider work stayed inside adapter/config/runtime infrastructure.

## Remaining Risks

- Only local Ollama was live-proven in clean-room. External hosted providers remain unproven unless
  clean credentials are supplied and authorized.
- Failure injection used controlled local fixture endpoints for 401 / 429 / empty / malformed /
  timeout; this is valid adapter pressure but not evidence of specific external provider behavior.
- Long-run provider stability is not proven by a single live runtime tick. CR_GOAL_08 must test
  longer soak behavior.

## Transition

CR_GOAL_03 is complete.

Proceed to:

```text
CR_GOAL_04_LIVE_MARKET_BLACKBOX
```
