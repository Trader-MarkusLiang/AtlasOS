# ATLAS CLEANROOM MASTER GOAL

## Objective

Independently verify Atlas OS from a fresh clone and clean runtime state.

This clean-room program exists because prior Master Goal evidence was produced by the same
implementation process. Prior reports may guide test targeting, but they are not accepted as
independent proof.

Primary question:

```text
Can Atlas OS, from a fresh clone and clean runtime state, actually behave like a usable,
continuously runnable, market-aware, portfolio-aware, forecast-accountable, bounded
self-iterating asset cognition system?
```

## Candidate Source

- Candidate branch: `codex/overnight-productization-sprint`
- Candidate commit: `ed63678793bdc5d10c1469433e461a6c20db7927`

The exact remote commit must be verified before runtime testing begins. If remote HEAD differs,
record both values and test the explicit candidate commit unless the user authorizes a newer
candidate.

## Absolute Boundaries

Do not:

- implement broker integration;
- execute trades;
- auto-modify portfolio holdings;
- bypass CDE;
- expose or commit API keys;
- store exact private wealth or account balances;
- add Buy/Sell as Atlas action vocabulary;
- implement v0.8;
- add speculative cognitive engines;
- introduce unrestricted self-modification;
- replace Atlas cognition with LLM-only reasoning;
- weaken trust or safety gates.

Allowed Atlas action vocabulary:

- Observe
- Hold
- Reduce
- Build
- Accumulate

## Execution Order

1. `CR_GOAL_00_FRESH_CLONE_BASELINE`
2. `CR_GOAL_01_BOOTSTRAP_FROM_ZERO`
3. `CR_GOAL_02_FIRST_TIME_USER_BLACKBOX`
4. `CR_GOAL_03_LIVE_LLM_BLACKBOX`
5. `CR_GOAL_04_LIVE_MARKET_BLACKBOX`
6. `CR_GOAL_05_PORTFOLIO_COGNITION_BLACKBOX`
7. `CR_GOAL_06_FORECAST_ACCOUNTABILITY_BLACKBOX`
8. `CR_GOAL_07_SELF_ITERATION_BLACKBOX`
9. `CR_GOAL_08_RECOVERY_AND_SOAK`
10. `CR_GOAL_09_FINAL_TRIBUNAL_AND_MERGE_GATE`

For each goal:

```text
AUDIT -> EXECUTE -> OBSERVE -> ATTACK -> REPAIR LOCALLY FIXABLE DEFECTS
-> RE-RUN -> REGRESS -> RECORD EVIDENCE -> UPDATE STATUS -> CONTINUE
```

## Prior Evidence Non-Reuse Rule

The following previous artifacts are not independent proof:

- GOAL_00 through GOAL_08 reports;
- previous tribunal result;
- previous browser screenshots;
- previous runtime databases;
- previous telemetry logs;
- previous treatment/control artifacts;
- previous soak artifacts.

They may identify expected behavior or likely test targets only.

## Evidence Levels

- `LIVE_PROVEN`
- `REAL_RUNTIME_PROVEN`
- `BLACKBOX_PROVEN`
- `CONTROLLED_FIXTURE_PROVEN`
- `ACCELERATED_ONLY`
- `PARTIAL`
- `DISCONNECTED`
- `FAILED`
- `EXTERNAL_BLOCKER`

Do not use vague PASS without an evidence level.

## Stop Conditions

The clean-room master goal may stop only when:

- `CR_GOAL_00` through `CR_GOAL_09` have final classifications;
- all locally fixable P0/P1 defects are closed;
- the independent tribunal is complete;
- clean-room regression is complete;
- merge readiness is classified;
- or remaining gaps are genuine external blockers with reproducible evidence.

