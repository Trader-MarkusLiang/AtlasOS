# CR_GOAL_08 - RECOVERY AND SOAK

## Objective

Test clean-room operational resilience.

## Required Failure Injections

1. daemon kill;
2. daemon restart;
3. UI restart;
4. stale PID;
5. malformed inbox JSONL;
6. corrupt telemetry final line;
7. provider failure;
8. market provider failure;
9. missing optional dependency;
10. stale UI process.

## Soak

Run independently:

- accelerated 500+ cycles minimum;
- longest practical real-duration soak;
- target 2h minimum if execution environment allows;
- preferred 4h+.

Measure tick count, tick errors, RSS, CPU, DB growth, log growth, queue depth, provider failures,
market failures, trust drift, hypothesis switches, forecast growth, and structural updates.

## Deliverable

`99_Verification/cleanroom/CR_GOAL_08_Recovery_And_Soak_Report.md`

