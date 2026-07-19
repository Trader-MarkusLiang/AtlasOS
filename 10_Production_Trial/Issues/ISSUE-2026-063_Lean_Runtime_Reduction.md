# ISSUE-2026-063 — Runtime Complexity Exceeds Evidence: Lean Runtime Reduction

## Status

Accepted

## Origin

Architecture Review

## Date First Seen

2026-07-19

## Date Last Seen

2026-07-19

## Frequency

1

## Affected Area

Engineering

## Problem

The runtime cognition layer (~30 symbolic engines wired in series in
`runtime/decision_loop.py`) has grown beyond what its evidence supports: most layer
validations remain controlled-fixture evidence, while the only red-gap area (live market
data retrieval) receives less iteration. Three overlapping daemon entry points
(`atlas_daemon.py`, `atlas_runtime_daemon.py`, `atlas_host.py`) and the duplicate
`web/` dashboard add maintenance cost without user value.

## Context

User architecture review 2026-07-19 concluded: the Markdown knowledge layer is the
appreciating asset; the symbolic cognition engines duplicate reasoning a strong LLM
already performs in the Decision Brief step; complexity budget should move to the data
layer (provider rate-limit / disconnect resilience).

## Impact

High

## Evidence

- `runtime/decision_loop.py` `run_once()` hard-wires causal / world model / latent
  structure / physics / law emergence / unified intelligence chains.
- README / VERSION evidence table: Cognitive Overlay = controlled-fixture evidence;
  Live market observation = PARTIAL / EXTERNAL_BLOCKER.
- `99_Verification/Atlas_OS_Overnight_Baseline_Audit.md` already flags the three
  overlapping daemon/host concepts.

## Root Cause Hypothesis

Engine trials (v0.5-v1.2) were merged into the default pipeline instead of staying
behind an experimental flag, so experimental complexity became default complexity.

## Possible Solutions

- Add `cognition_mode` ("lean" default / "full" legacy) gate in DecisionLoop; lean keeps
  fusion + state controller + regime memory + LLM decision + forecast ledger.
- Add market data cache + stale fallback + backoff in market intelligence layer.
- Consolidate to one daemon entry; archive legacy entries under `runtime/legacy/`.
- Lighten single-user governance wording in AGENTS.md (keep Issue-first habit).

## Priority

P1

## Decision

Convert to Improvement Proposal (user-approved 2026-07-19; executed directly under the
approved lean-runtime plan; rollback = config flag / git restore)

## Linked IP

None (single-user stage: IP numbering suspended per updated AGENTS.md governance note)

## Notes

Rollback path: set `cognition_mode: "full"` in `runtime/config/user_config.json`;
legacy entry files preserved under `runtime/legacy/`, not deleted.
