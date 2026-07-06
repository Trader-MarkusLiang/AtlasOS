# ISSUE-2026-027 — DSA Infrastructure Adapter Needed

## Status

Open / Accepted / Converted to IP / Implemented

## Origin

Production Trial / v0.4 Cognitive Market OS Roadmap

## Date First Seen

2026-07-06

## Date Last Seen

2026-07-06

## Frequency

1

## Affected Area

Runtime / Infrastructure / Adapter Layer / Event Stream / LLM Router / Dashboard

## Problem

Atlas OS v0.3 has working cognition modules, but runtime infrastructure remains partly duplicated
inside Atlas. The v0.4 roadmap requires Atlas to sit above an infrastructure layer such as DSA
without inheriting stock-picking, strategy, or trading logic.

## Context

The user requested a v0.4 infrastructure merge and cognitive stabilization step:

- identify reusable DSA infrastructure
- exclude DSA business logic
- create `runtime/adapter/dsa_bridge.py`
- unify DSA signal schema into Atlas event schema
- keep Event Fusion, Regime Memory, Causal Inference, and State Controller unchanged

The local DSA source repository was not available in the current workspace during implementation,
so the adapter must be configurable and safe when DSA is not installed.

## Impact

Medium

Without a DSA adapter boundary, Atlas risks either duplicating infrastructure or being flattened
into a stock-analysis pipeline.

## Evidence

- v0.4 roadmap recorded DSA infrastructure reuse as Phase 1.
- No local DSA repository was found under `/Users/markus` during the implementation scan.
- Existing Atlas cognition modules can consume EventStream events if external signals are normalized.

## Root Cause Hypothesis

Atlas runtime evolved quickly from local scheduler to event-driven cognition before the
infrastructure boundary was separated from Atlas core cognition.

## Possible Solutions

- Add a DSA bridge adapter that normalizes external infrastructure signals into Atlas event schema.
- Add optional DSA data-fetch and LiteLLM backend hooks.
- Keep DSA business logic out of Atlas.
- Validate that cognition output remains stable for native and DSA-adapted events.

## Priority

P1

## Decision

Convert to Improvement Proposal and implement minimal adapter boundary.

## Linked IP

IP-2026-027 — DSA Infrastructure Adapter v0.4

## Notes

This issue does not authorize trading execution, CDE bypass, portfolio automation, stock-picking
logic, MA strategy, buy / sell rules, or DSA scoring-system import.

