# Atlas OS Live LLM Activation Report

Date: 2026-07-08

## Verdict

Classification: `LIVE_PROVEN` for local cc-switch ARK-compatible inference through Atlas provider
router.

## Baseline Failure

Before repair, `route_llm_request()` returned failsafe:

```text
morecode -> api_key_missing
ark -> api_key_missing
volcano -> api_key_missing
ollama -> HTTP 404
openai -> api_key_missing
claude -> api_key_missing
custom -> base_url_missing
```

## Repair

`runtime/llm/provider_router.py` now allows OpenAI-compatible loopback URLs to omit
`Authorization`. Public providers still require credentials. `runtime/llm/provider_registry.py`
health/model discovery also recognizes loopback endpoints.

## Live Smoke Result

| Field | Evidence |
|---|---|
| Active provider | `morecode` |
| Fallback provider used | `ark` |
| Fallback reason | MoreCode local shim returned HTTP 401 |
| Live provider endpoint | local cc-switch ARK shim |
| Model | `kimi-k2.6` |
| Latency | 6078 ms in first successful smoke; 10051 ms in failure-injection smoke |
| Decision Contract | Valid DecisionPacket parsed |
| Recommended action vocabulary | `neutral` |
| Secrets exposed | none |

Live provider model discovery:

```text
ark: 125 models discovered
volcano: 125 models discovered
morecode: HTTP 401
```

## Remaining Provider Limits

- MoreCode local shim is reachable but requires auth not present in Atlas config.
- OpenAI and Claude public providers remain `not_configured` because no Atlas-stored API key is
  present.
- Ollama endpoint was health-checkable but the configured model path was not proven for inference.
