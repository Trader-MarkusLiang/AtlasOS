# CR_GOAL_06 — Forecast Accountability Black-Box Report

Date: 2026-07-08

Branch: `codex/cleanroom-verification`

Final repair commit tested: `4280a5ad583c57a29075e5a6a3533adba6b3888d`

Final clean-room clone: `/tmp/atlas-cleanroom-cr06-rerun-20260708-163952`

Final clean runtime state: `/tmp/atlas-cleanroom-state-cr06-rerun-20260708-163952`

Evidence level: `REAL_RUNTIME_PROVEN`

## Objective

Prove Atlas records expectations before outcomes and later evaluates them through the normal
supported product path. The test did not directly insert final evaluated rows into SQLite.

## Runtime Path Tested

```text
HTTP /predictions
-> runtime.forecast_ledger.create_forecast()
-> SQLite forecast_ledger OPEN row
-> HTTP /predictions/mature
-> MATURED row with maturity evidence
-> HTTP /predictions/evaluate
-> outcome, forecast error, calibration error, trust calibration state
-> HTTP /predictions?format=json and /predictions HTML page
```

## Required Case Results

| Case | Forecast ID | Create | Mature | Final status | Forecast error | Calibration error |
|---|---|---:|---:|---:|---:|---:|
| Hit | `cr06-rerun-hit-001` | OPEN | MATURED | VERIFIED | 0.0 | 0.28 |
| Miss | `cr06-rerun-miss-001` | OPEN | MATURED | INVALIDATED | 1.0 | 0.68 |
| Inconclusive | `cr06-rerun-inconclusive-001` | OPEN | MATURED | INCONCLUSIVE | 0.5 | 0.01 |
| High-confidence miss | `cr06-rerun-high-confidence-miss-001` | OPEN | MATURED | INVALIDATED | 1.0 | 0.95 |
| Low-confidence hit | `cr06-rerun-low-confidence-hit-001` | OPEN | MATURED | VERIFIED | 0.0 | 0.75 |

Ledger metrics before attack regression:

```json
{
  "total": 5,
  "open": 0,
  "matured": 0,
  "evaluated": 5,
  "verified": 2,
  "accuracy": 0.4,
  "mean_forecast_error": 0.5,
  "mean_calibration_error": 0.534,
  "minimum_sample_size_met": false
}
```

## Persistence Evidence

The rerun persistence check confirmed:

- all five required cases persisted in `forecast_ledger`;
- each required case lineage was exactly `created -> matured -> evaluated`;
- each required case had `actual_outcome`, `prediction_error`, `forecast_error`, and
  `calibration_error`;
- `forecast_calibration_state.evaluated_count` was `5`;
- `forecast_calibration_state.mean_forecast_error` was `0.5`;
- `system_trust_state.latest_forecast_calibration` was updated by the final evaluated forecast.

## Attack Findings

Initial black-box attack against the pre-repair CR06 clone found two lifecycle defects:

1. OPEN forecasts could be evaluated directly through `POST /predictions/evaluate`.
2. Existing `forecast_id` values could be overwritten through `POST /predictions`.

These defects weakened the strict lifecycle because a caller could bypass `MATURED` or destroy an
existing accountability record.

## Repair

Repair commit:

```text
4280a5a cleanroom: enforce forecast lifecycle boundaries
```

Repair scope:

- `create_forecast()` now rejects duplicate `forecast_id` with `forecast_already_exists`.
- `evaluate_forecast()` now rejects any forecast whose current status is not `MATURED` with
  `forecast_not_matured`.

No Event Fusion, CIL, LMSE, MPCE, MLE, CDE, Decision Contract semantics, trading execution,
broker integration, portfolio mutation, or prediction behavior was modified.

## Rerun Attack Regression

After the repair, a new clean-room clone and empty runtime state were used.

Attack regression results:

- missing forecast maturity request returned `forecast_not_found`;
- missing forecast evaluate request returned `forecast_not_found`;
- direct evaluation of an OPEN forecast returned `forecast_not_matured`;
- duplicate creation of an existing forecast returned `forecast_already_exists`;
- direct-evaluation attack row remained `OPEN` in persistence after the rejected evaluate call.

## Evidence Artifacts

Artifacts are stored under:

```text
99_Verification/cleanroom/artifacts/cr_goal_06/
```

Key files:

- `cr06_rerun_forecast_lifecycle_summary.json`
- `cr06_rerun_persistence_check.json`
- `cr06_rerun_attack_lifecycle_boundaries.json`
- `cr06_rerun_case_hit.json`
- `cr06_rerun_case_miss.json`
- `cr06_rerun_case_inconclusive.json`
- `cr06_rerun_case_high_confidence_miss.json`
- `cr06_rerun_case_low_confidence_hit.json`

The repository artifact copies were sanitized to remove secret-shaped fields. Secret-shape scan
over `99_Verification/cleanroom/artifacts/cr_goal_06/` returned no matches.

## Classification

CR_GOAL_06 classification: `PROVEN_COMPLETE`

Evidence level: `REAL_RUNTIME_PROVEN`

Reason: the complete lifecycle executed through the supported UI/API route, persisted real ledger
rows, computed forecast and calibration errors, updated runtime calibration state, and passed
post-repair lifecycle-bypass regression from a fresh clone.

## Remaining Risks

- Outcomes were controlled test outcomes, not live market outcomes. This is acceptable for
  CR_GOAL_06 because controlled advancement is allowed, but CR_GOAL_07 must prove whether realized
  forecast error changes later equivalent behavior.
- The HTTP fallback server returns JSON errors with HTTP 200 for lifecycle rejection. Product UX may
  later improve status codes, but the runtime boundary is enforced.
