# GOAL 07 — AUTONOMOUS OPERATIONS

## Objective

Prove Atlas can run continuously and execute meaningful scheduled cycles.

## Required Cycles

Morning:

- data freshness
- overnight synthesis
- portfolio relevance
- brief

Intraday:

- market refresh
- anomaly detection
- attention/regime update

Post-market:

- close synthesis
- forecast maturity
- outcome evaluation

Overnight:

- hypothesis review
- world model delta
- next-day watch conditions

## Required Proof

Scheduler
→ phase
→ actual tasks
→ persisted artifacts

Metadata-only phase labels do not count.

## Stability

Run:

- longest feasible real-duration soak
- accelerated 500+ cycles

Collect:

- memory
- CPU
- DB growth
- queue
- errors
- provider failures
- trust drift
- hypothesis switches

## Recovery

Test:

- daemon restart
- UI restart
- stale PID
- malformed JSONL
- provider outage
- market outage

## Deliverable

99_Verification/GOAL_07_Autonomous_Operations_Report.md

## Transition

Proceed to:

GOAL_08_RELEASE_READINESS
