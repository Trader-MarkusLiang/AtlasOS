# CR_GOAL_06 - FORECAST ACCOUNTABILITY BLACK-BOX

## Objective

Prove Atlas records expectations before outcomes and later evaluates them.

## Required Lifecycle

```text
CREATE -> OPEN -> MATURED -> OUTCOME ATTACHED -> ERROR COMPUTED
-> CALIBRATION COMPUTED -> VERIFIED / INVALIDATED / INCONCLUSIVE
```

## Required Cases

- hit;
- miss;
- inconclusive;
- high-confidence miss;
- low-confidence hit.

Use normal supported runtime/UI paths wherever possible. Controlled clock advancement is allowed.
Direct database fabrication is not accepted.

## Deliverable

`99_Verification/cleanroom/CR_GOAL_06_Forecast_Accountability_Blackbox_Report.md`

