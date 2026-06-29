# Memory Equipment ETF Methodology Session

## Metadata

- Date: 2026-06-29
- Session id: 2026-06-29_2151_memory-equipment-etf-methodology
- Project: Atlas OS
- Workspace: `/Users/markus/AtlasOS`
- Task: Evaluate a memory-expansion semiconductor equipment ETF opinion using Atlas OS.
- Status: completed
- Branch: main

## User Request Summary

The user provided an investment blogger's proposed 10-stock global semiconductor equipment ETF
focused on memory expansion paths and asked Atlas to judge whether it contains high-quality
information that should be distilled into reusable methodology.

## Constraints

- Use Atlas OS reasoning.
- Do not turn a social-media opinion directly into trade action.
- If evidence is not verified, mark it `Unverified`.
- No repository update was requested.

## Work Done

- Read atlas-research and atlas-portfolio skills.
- Read local portfolio context from `06_Portfolio/portfolio.local.yaml`.
- Read Seven Layer Reasoning, Atlas Principles, Trading Discipline, Bottleneck Map, AI Capital Map,
  and AI Shovel 100.
- Classified the signal as a medium-quality methodology candidate rather than direct evidence.

## Decisions

- Treat the core reusable method as: memory expansion equipment exposure should be mapped by process
  procurement order and bottleneck intensity, not by generic semiconductor beta.
- Keep the proposed ETF weights as a research hypothesis until company role, order evidence, and
  capex sensitivity are verified.
- No portfolio action authorized because China account is already highly deployed and the signal has
  no direct current-holding mapping except indirect support for Equipment / Materials thesis.

## Current State

- Final research response prepared.
- The signal is judged as a valid Pattern candidate:
  - Memory Expansion Equipment Procurement Sequence.
  - World Model node: Equipment, linked to Memory.
  - Not enough verified evidence for direct portfolio action or repository merge.

## Resume Instructions

1. If the user asks to persist this methodology, create a Knowledge / Pattern proposal under the
   appropriate Atlas knowledge area, not a direct database merge.
2. Verify each ticker and equipment role from primary sources before scoring candidates.
3. Preserve portfolio context injection.

## Open Questions

- Whether the user wants this method added to Atlas repository as a formal Pattern candidate.
