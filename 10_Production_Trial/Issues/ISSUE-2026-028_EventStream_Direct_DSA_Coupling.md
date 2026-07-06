# ISSUE-2026-028 — EventStream Direct DSA Coupling

## Status

Open / Accepted / Converted to IP / Implemented

## Origin

Production Trial / Cognitive Isolation Verification Test

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime / Event Stream / Infrastructure Adapter / Cognitive Isolation

## Problem

Atlas OS v0.4 introduced a DSA adapter boundary, but `runtime/event_stream.py` imported
`runtime.adapter.dsa_bridge` directly. This meant removing `dsa_bridge.py` broke the full runtime
DecisionLoop even though the cognitive modules themselves were source-agnostic.

## Context

Cognitive isolation verification found:

- Direct cognition modules could run without `dsa_bridge.py`.
- Full runtime ingestion failed when `dsa_bridge.py` was removed.
- Nested malicious metadata such as `buy_signal`, `sell_pressure`, and `alpha_score` could survive
  the v0.4 adapter payload.

## Impact

High

Potential effects:

- EventStream becomes source-system aware.
- DSA adapter becomes a runtime dependency.
- Strategy / trading fields can leak into runtime payload.
- Atlas cognitive isolation is only partial.

## Evidence

Test failure from Cognitive Isolation Verification:

```text
ModuleNotFoundError: No module named 'runtime.adapter.dsa_bridge'
```

when `dsa_bridge.py` was removed and DecisionLoop attempted to import EventStream.

## Root Cause Hypothesis

v0.4 placed normalization in a source-specific DSA adapter instead of a source-neutral Input
Abstraction Layer.

## Possible Solutions

- Introduce `runtime/adapter/input_router.py`.
- Make EventStream depend only on the input router.
- Treat DSA bridge as compatibility wrapper, not runtime ingestion dependency.
- Strip illegal fields recursively and neutralize poisoned events to `market_event`.

## Priority

P0

## Decision

Convert to Improvement Proposal and implement v0.4.1 decoupling fix.

## Linked IP

IP-2026-028 — Input Abstraction Layer v0.4.1

## Notes

This issue does not authorize cognitive logic changes, trading execution, CDE bypass, stock-picking
functionality, DSA business logic import, or portfolio automation.

