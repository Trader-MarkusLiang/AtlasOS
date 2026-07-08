# GOAL 02 — LIVE LLM ACTIVATION

## Objective

Prove Atlas OS can independently use configured LLM providers through normal runtime paths.

## Providers

Attempt configured:

- MoreCode
- ARK
- Volcano
- OpenAI-compatible
- Anthropic
- Ollama
- Custom

## Required Proof

At least one actual inference request:

secret store
→ provider registry
→ router
→ provider
→ normalized response
→ Decision Contract
→ safe telemetry

## Required Tests

- valid provider
- 401
- 429
- timeout
- empty response
- malformed response
- fallback
- model not found

## Security

- no secret in logs
- no secret in UI response
- Keychain-first where available

## Acceptance

Complete when:

- one provider is LIVE_PROVEN
- fallback is REAL_RUNTIME_PROVEN
- failure states are visible

## Deliverable

99_Verification/GOAL_02_Live_LLM_Report.md

## Transition

Proceed to:

GOAL_03_MARKET_INTELLIGENCE
