# Atlas OS Forecast Ledger E2E Report

Date: 2026-07-08

## Method

Five controlled forecasts:

- Directional/state forecast.
- Regime risk forecast.
- Attention expansion forecast.
- Liquidity stress persistence forecast.
- Deliberately wrong forecast.

Lifecycle tested:

```text
OPEN -> MATURED -> VERIFIED / INVALIDATED
```

## Evidence

`validate_morning_red_team.py` created 5 forecasts, matured them, evaluated them, and persisted:

- `prediction_error`
- `forecast_error`
- `calibration_error`
- `lineage`
- `trust_update`
- `hypothesis_evaluation`

Statuses:

```text
VERIFIED, VERIFIED, VERIFIED, VERIFIED, INVALIDATED
```

## Verdict

PASS for ledger lifecycle and metadata calibration. Statistical calibration remains LOW SAMPLE.
