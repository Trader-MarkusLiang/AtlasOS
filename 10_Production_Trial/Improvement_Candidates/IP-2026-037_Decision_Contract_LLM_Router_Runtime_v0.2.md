# IP-2026-037 — Decision Contract + LLM Router Runtime v0.2

## Category

Engineering / Runtime Infrastructure / LLM Boundary

## Origin

ISSUE-2026-037 — Decision Contract / LLM Router Runtime Boundary Needed

## Problem

Atlas runtime needs a strict bridge between deterministic cognitive output and probabilistic LLM
reasoning. The bridge must prevent unstructured LLM text, malformed schema, provider-specific
drift, and unsafe action semantics from entering runtime state.

## Implemented Scope

- Added `runtime/cognition/decision_contract.py`.
- Added `runtime/cognition/decision_validator.py`.
- Updated `runtime/llm_router.py` with raw-text provider routing for:
  - OpenAI-compatible providers
  - Claude / Anthropic
  - Ollama local LLM
  - optional proxy adapter
- Updated `runtime/orchestrator.py` so LLM raw text is parsed into a validated `DecisionPacket`
  before logs or Decision Brief metadata are written.
- Updated `runtime/decision_loop.py` to surface validated packet status in tick results without
  importing or calling the LLM router.
- Updated `runtime/atlas_runtime_daemon.py` to include DecisionPacket metadata in runtime tick
  summaries.
- Added `99_Verification/validate_decision_contract_llm_router_v0_2.py`.

## DecisionPacket Contract

```python
DecisionPacket = {
    "regime_state": str,
    "confidence": float,
    "risk_level": str,
    "attention_state": str,
    "liquidity_state": str,
    "causal_summary": str,
    "recommended_action": "observe | reduce | neutral",
    "reasoning_trace": str,
}
```

## Runtime Flow

```text
Cognitive Output
 -> Decision Contract Formatter
 -> LLM Router raw text
 -> Decision Contract Parser / Validator
 -> Validated DecisionPacket
 -> Logger / Decision Brief metadata
```

`DecisionLoop` does not import or call the LLM router directly.

## Failsafe

If LLM output is unavailable, malformed, has extra fields, has invalid field types, contains
unsafe directive language, or violates allowed risk/action bounds, runtime returns:

```json
{
  "regime_state": "unknown",
  "confidence": 0.0,
  "risk_level": "unknown",
  "attention_state": "unknown",
  "liquidity_state": "unknown",
  "causal_summary": "LLM reasoning unavailable or invalid.",
  "recommended_action": "neutral",
  "reasoning_trace": "failsafe reason"
}
```

## Boundary

This IP does not modify:

- cognitive layers v0.5-v1.0
- Event Fusion Engine
- Regime Memory
- CIL / World Model / LMSE / MPCE / MLE / UMIS core logic
- CDE logic
- `portfolio.local.yaml`

It does not introduce:

- trading execution
- broker connectivity
- prediction-engine behavior
- ML / DL / RL training
- portfolio automation
- Buy / Sell runtime actions

## Status

Implemented — runtime boundary infrastructure only.

## Final Decision

READY FOR DECISION CONTRACT RUNTIME REVIEW
