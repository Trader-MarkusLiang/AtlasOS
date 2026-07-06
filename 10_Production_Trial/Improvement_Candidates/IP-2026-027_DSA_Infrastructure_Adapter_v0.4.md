# IP-2026-027 — DSA Infrastructure Adapter v0.4

## Category

Engineering / Runtime / Infrastructure Adapter / Market Cognition

## Origin

ISSUE-2026-027 — DSA Infrastructure Adapter Needed

## Problem

Atlas OS needs to consume infrastructure outputs from DSA-style systems while keeping Atlas Core as
the cognitive layer above infrastructure.

The integration must not import stock-picking logic, MA strategy, buy / sell rules, scoring
systems, single-stock pipeline behavior, CDE authority, or portfolio automation.

## Implemented Scope

- `runtime/adapter/dsa_bridge.py`
  - Compatibility wrapper for DSA-style infrastructure signals.
  - In v0.4.1, source-neutral validation moved to `runtime/adapter/input_router.py`.
  - EventStream no longer imports this module directly.
- `runtime/adapter/data_fetch.py`
  - Adds optional DSA data-fetch boundary through `ATLAS_DSA_DATAFETCHER`.
  - Fails safely when DSA is not configured.
- `runtime/event_stream.py`
  - Allows inbox JSON / JSONL files to use native Atlas event schema or unified DSA-style schema.
- `runtime/llm_router.py`
  - Adds optional `ATLAS_LLM_BACKEND=litellm` backend selection.
  - Keeps native provider behavior as default.
- `web/app.py`
  - Adds infrastructure status to dashboard payload.
- `99_Verification/validate_dsa_adapter_v0_4.py`
  - Validates DSA adapter schema, ingestion, cognition consistency, business-logic neutralization, and
    dashboard infrastructure status.

## v0.4.1 Follow-up

`IP-2026-028 — Input Abstraction Layer v0.4.1` fixed the direct EventStream -> DSA bridge coupling
found during Cognitive Isolation Verification.

Current dependency:

```text
EventStream -> Input Router
DSA Bridge -> Input Router
Cognitive Layer -> no adapter import
```

## Architecture Diff

Before:

```text
Atlas runtime -> EventStream -> Cognitive Layer -> Orchestrator -> Decision Brief
```

After:

```text
DSA / external infrastructure
 -> Atlas Adapter Layer
 -> EventStream
 -> Cognitive Layer
 -> Orchestrator
 -> Decision Brief
```

## Module Mapping

| DSA / Infrastructure Area | Atlas Integration | Status |
|---|---|---|
| Runtime Scheduler | Existing Atlas scheduler / daemon remains active | Not imported |
| FastAPI Web Host | Existing `web/app.py` displays infrastructure status | Adapter-aware |
| LiteLLM Router | `runtime/llm_router.py` optional `ATLAS_LLM_BACKEND=litellm` | Optional |
| DataFetcherManager | `runtime/adapter/data_fetch.py` optional callable boundary | Optional |
| Search / Social Sentiment | `runtime/adapter/input_router.py` -> `attention_spike` / `news_narrative_spike` | Implemented |
| Logging / Diagnostics | Existing runtime logging plus dashboard infrastructure status | Adapter-aware |
| Stock Picking Logic | Excluded | Not imported |
| MA Strategy | Excluded | Not imported |
| Buy / Sell Rules | Excluded | Rejected |
| Scoring Systems | Excluded | Rejected |
| Single-stock Pipeline | Excluded | Not imported |

## Integration Points

- Event input:
  - inbox JSON / JSONL now accepts native Atlas events and DSA-style unified events through Input Router.
- LLM backend:
  - default native router unchanged.
  - optional LiteLLM backend selected only through `ATLAS_LLM_BACKEND=litellm`.
- Data fetch:
  - optional DSA callable selected through `ATLAS_DSA_DATAFETCHER`.
- Dashboard:
  - exposes DSA adapter, data source, and LLM backend status.

## Cognitive Core Integrity

Unchanged:

- `runtime/cognition/event_fusion_engine.py`
- `runtime/cognition/regime_memory.py`
- `runtime/cognition/causal_inference.py`
- `runtime/cognition/state_controller.py`
- `runtime/cognition/attention_liquidity_model.py`

## Validation

Validation command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_dsa_adapter_v0_4.py
```

Regression commands:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_cognitive_runtime_v0_3.py
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_autonomous_runtime_v0_2.py
PYTHONDONTWRITEBYTECODE=1 python3 99_Verification/validate_runtime_kernel_v0_1.py
```

Validation result:

`99_Verification/DSA_Adapter_v0.4_Validation_Result.md`

## Boundary

This IP does not implement:

- trading execution
- portfolio auto-rebalance
- broker integration
- CDE bypass
- DSA business logic import
- stock-picking logic
- MA strategy
- buy / sell rules
- scoring systems
- single-stock analyzer behavior
- cognitive core logic changes

## Status

Implemented — adapter boundary trial.

## Final Decision

READY FOR INFRASTRUCTURE ADAPTER TRIAL
