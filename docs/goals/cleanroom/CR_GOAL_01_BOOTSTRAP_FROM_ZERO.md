# CR_GOAL_01 - BOOTSTRAP FROM ZERO

## Objective

Determine whether a new machine-like environment can start Atlas OS from the repository.

## Required Tests

1. Dependency discovery.
2. Documented install path.
3. First UI start.
4. First daemon start.
5. Missing optional dependency behavior.
6. Missing config behavior.
7. Empty state behavior.
8. First runtime state persistence.

## Required Questions

- Is setup documented?
- Can UI start without hidden manual patching?
- Can daemon start without old local state?
- Are missing dependencies understandable?
- Does the product tell the user what is missing?

Do not silently install random dependencies merely to force PASS. Record all required
interventions.

## Deliverable

`99_Verification/cleanroom/CR_GOAL_01_Bootstrap_From_Zero_Report.md`

## Classification

- `BLACKBOX_PROVEN`
- `PARTIAL`
- `FAILED`

