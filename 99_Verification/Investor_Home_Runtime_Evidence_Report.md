# Investor Home Runtime Evidence Report

Date: 2026-07-12
Runtime: daemon tick every 60 seconds; proactive research review every 7200 seconds.

## Live Path

Normal runtime evidence path:

`public source -> market normalization -> EventStream -> DecisionLoop -> persisted state -> Home`

Observed Goal validation state:

- market observations: 3;
- usable observations: 3;
- channel states: 2 `LIVE`, 1 `CACHED`, 4 `DELAYED`, 1 `NOT_CONFIGURED`;
- configured LLM provider present;
- latest inference status: `succeeded`;
- unavailable observations excluded from usable counts.

Active evidence adapters include Tencent portfolio quotes, a bounded Sina A-share breadth sample,
PBOC official policy releases, and SSE official announcements. Partial coverage is labeled delayed
or cached; it is not promoted to full-market live coverage.

## Forecast Accountability

The five-case lifecycle validator passes hit, miss, inconclusive, high-confidence miss, and
low-confidence hit. New runtime forecasts:

- require a material non-simulated event;
- use a deterministic material signature;
- skip equivalent repeated creation;
- mature on the next eligible runtime observation;
- attach the later observed state and evaluate;
- expose error, calibration error, lineage, and bounded trust update.

The control/treatment experiment is classified `REAL_RUNTIME_BEHAVIORAL_LOOP`. A verified outcome
produced positive calibration; an invalidated outcome produced `-0.12` feedback. Treatment trust was
`0.1587` below control, while hypothesis distribution and bounded structural mutation also changed.
Action bias remained neutral and no trading execution was created.

Historical `OPEN` records without a material signature are classified as legacy unclassified. They
are not bulk-evaluated from one current observation.

## Failure Paths

Provider validation passes valid response, 401, 429, timeout, empty response, malformed response,
model-not-found, fallback, Decision Contract parsing, telemetry, and secret masking. The older strict
market validator could obtain partial Tencent A-share quotes but not a full `Available` history
snapshot; this is retained as external-provider evidence, not rewritten as a pass.

Machine-readable evidence:

- `99_Verification/artifacts/investor_home/goal_validation_result.json`
- `99_Verification/artifacts/goal_05_forecast_accountability/lifecycle_result.json`
- `99_Verification/artifacts/goal_06_self_iteration_reality/treatment_control_result.json`
