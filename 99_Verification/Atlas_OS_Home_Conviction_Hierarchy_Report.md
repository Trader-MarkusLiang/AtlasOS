# Atlas OS Home Conviction Hierarchy Report

Date: 2026-07-10

## Verdict

PASS.

Home now exposes a presentation-only Conviction Hierarchy without changing forecast, hypothesis, or
cognition semantics.

## Implemented Hierarchy

| Level | Meaning | Home behavior | Limit |
|---|---|---|---|
| Level 1 | Core Judgment | Exactly one `core_judgment` appears in `#home-core-judgment`. | Exactly 1 |
| Level 2 | Key Predictions | `#home-conviction-hierarchy` lists the strongest forward view plus bounded confirmation/risk predictions. | Maximum 3 |
| Level 3 | Watch Hypotheses | Positive and negative trigger hypotheses are visible but secondary. | Expandable/supporting |
| Level 4 | Research Candidates | Home shows only 3 research priorities and links to `/candidates`. | Separate surface |

## Evidence

- Model validator: `99_Verification/artifacts/user_decision_home/validator_results.json`.
- Browser E2E: `99_Verification/artifacts/user_decision_home/browser_e2e_results.json`.
- Rendered Home artifacts:
  - `99_Verification/artifacts/user_decision_home/home_en.html`
  - `99_Verification/artifacts/user_decision_home/home_zh.html`

Validator checks passed:

- `conviction hierarchy level 1 has exactly one item`
- `conviction hierarchy level 2 has max three key predictions`
- `one core judgment exists`
- `one strongest forward view exists`
- `forward view includes confidence`
- `forward view includes falsification condition`

## Boundary Result

No Event Fusion, CIL, LMSE, MPCE, MLE, UMIS, Decision Contract, forecast lifecycle, candidate
ranking semantics, portfolio mutation, CDE authority, or trading execution code was changed.

The hierarchy is a read-only UI projection from existing runtime state.
