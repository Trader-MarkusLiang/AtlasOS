# CR_GOAL_03 - LIVE LLM BLACK-BOX

## Objective

Prove a real provider inference through actual product/runtime paths.

## Required Path

```text
UI/config -> secret store -> provider registry -> provider router -> real provider
-> response normalization -> Decision Contract -> safe telemetry -> visible product result
```

## Required Tests

- primary provider;
- fallback provider;
- wrong key;
- timeout;
- 401;
- 429;
- malformed response;
- empty response;
- model not found.

At least one actual inference is required. A model-list call or HEAD request is not enough.

Never record secret values.

## Deliverable

`99_Verification/cleanroom/CR_GOAL_03_Live_LLM_Blackbox_Report.md`

## Classification

- `LIVE_PROVEN`
- `PARTIAL`
- `EXTERNAL_BLOCKER`
- `FAILED`

