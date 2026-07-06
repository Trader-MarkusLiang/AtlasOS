# ISSUE-2026-037 — Decision Contract / LLM Router Runtime Boundary Needed

## Status

Implemented

## Origin

Atlas OS v0.2 — Decision Contract + LLM Router Runtime Layer request

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime / Decision Contract / LLM Router / Logging Boundary

## Problem

Atlas runtime needs a strict bridge between deterministic cognitive output and probabilistic LLM
reasoning. Without a contract, runtime reasoning can drift into unstructured text, malformed
fields, or unsafe action semantics.

## Context

The requested runtime upgrade requires:

- strict `DecisionPacket` schema
- no direct LLM call from `DecisionLoop`
- raw LLM text routed through a validator
- provider-swappable LLM router
- failsafe neutral packet when LLM output is malformed or unavailable

## Impact

High

Potential effects if unresolved:

- unstructured LLM text can leak into runtime state
- malformed fields can enter logs or Decision Brief metadata
- provider failures can crash runtime
- deterministic cognition and probabilistic reasoning remain weakly separated

## Evidence

User request:

```text
Upgrade Atlas OS runtime by introducing:
1. Decision Contract Layer (STRICT STRUCTURE)
2. LLM Router Layer (pluggable reasoning engine)
```

## Root Cause Hypothesis

Previous runtime routes had a lightweight LLM abstraction, but no strict DecisionPacket contract
between LLM raw output and runtime logging / Decision Brief metadata.

## Possible Solutions

- Add `runtime/cognition/decision_contract.py`.
- Add `runtime/cognition/decision_validator.py`.
- Extend `runtime/llm_router.py` with raw-text provider routing.
- Route orchestrator LLM output through the contract before persistence.
- Add validation coverage for schema stability, provider swap, failure isolation, and cognitive
  integrity.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement as runtime boundary infrastructure only.

## Linked IP

IP-2026-037 — Decision Contract + LLM Router Runtime v0.2

## Notes

This issue does not authorize trading execution, broker connectivity, CDE bypass, portfolio
modification, prediction-engine behavior, or changes to cognitive modules v0.5-v1.0.
