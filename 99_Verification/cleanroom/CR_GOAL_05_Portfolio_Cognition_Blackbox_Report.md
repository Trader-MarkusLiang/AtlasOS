# CR_GOAL_05 — Portfolio Cognition Black-Box Report

## Verdict

Classification: `REAL_RUNTIME_PROVEN`

Evidence level: `REAL_RUNTIME_PROVEN`

Atlas OS normal runtime output changes when the portfolio is configured differently through the UI
settings path. The proof used the same market input for all cases and compared four isolated
runtime runs.

## Fresh Evidence Scope

- Verification branch: `codex/cleanroom-verification`
- Fresh clone: `/tmp/atlas-cleanroom-cr05-rerun-20260708-163116`
- Clean runtime state root: `/tmp/atlas-cleanroom-state-cr05-ui-20260708-163116`
- Commit under test: `1a812b120bece456f144d2aa8d165ac7208ea309`
- Evidence directory:
  `99_Verification/cleanroom/artifacts/cr_goal_05/ui_runtime_differential/`

Prior portfolio differential artifacts were not used as proof.

## Runtime Path

Observed path for each case:

```text
/settings HTTP
→ runtime/config/user_config.json
→ runtime.portfolio_context.build_portfolio_context()
→ atlas_runtime_daemon.py --max-cycles 1
→ DecisionLoop / orchestrator
→ Decision Brief
→ persisted runtime state
```

All cases used the same market input:

```text
daemon first simulated attention tick
market refresh disabled
```

This isolates portfolio context as the changed variable.

## Differential Cases

Evidence:

- `summary.json`
- `portfolio_a_ai_hardware_concentrated.json`
- `portfolio_b_high_cash_low_exposure.json`
- `portfolio_c_single_theme_concentration.json`
- `portfolio_d_no_portfolio.json`

| Case | Exposure | Cash / Unassigned | Theme | Market | Relevance |
|---|---:|---:|---|---|---:|
| Portfolio A — AI hardware concentrated | `95%` | `5%` | AI hardware `95%` | US `70%`, TW `25%` | `91.25` |
| Portfolio B — high cash / low exposure | `25%` | `75%` | platform quality `15%`, AI software `10%` | US `25%` | `22.0` |
| Portfolio C — single theme concentration | `90%` | `10%` | semiconductor manufacturing `90%` | TW `35%`, EU `30%`, US `25%` | `81.75` |
| Portfolio D — no portfolio | `0%` | `null` | none | none | `0.0` |

Distinct portfolio outputs: `4`.

## Required Output Coverage

| Required Output | Result |
|---|---|
| Asset concentration | Proven in each configured case |
| Theme concentration | Proven and differs across A/B/C/D |
| Market concentration | Proven and differs across A/B/C/D |
| Liquidity sensitivity | Present; unchanged for these diversified public-market examples |
| Regime sensitivity | Differs: single-theme sensitive vs broad/unclassified |
| Correlated risk clusters | Proven and differs by theme concentration |
| Portfolio relevance | Proven: `91.25`, `22.0`, `81.75`, `0.0` |

## Defect Found And Repaired

### P1 — Detailed portfolio context overwritten by asset list

During the first CR_GOAL_05 differential run, detailed `portfolio_json` entries were overwritten by
simple `asset_list` entries for the same asset. That collapsed theme and market information into
`Unspecified` / guessed defaults.

Repair:

- `1a812b1 cleanroom: preserve detailed portfolio asset context`

Final rerun proved that detailed fields are preserved:

- AI hardware concentration remains `AI hardware: 95%`.
- Single-theme semiconductor concentration remains `semiconductor manufacturing: 90%`.
- Regional markets remain US / TW / EU instead of collapsing to US.

## Safety And Privacy

- No exact account value, cost basis, broker data, position amount, or private wealth was used.
- Portfolio input used percentages only.
- Runtime output remained non-binding.
- No trading execution was created.
- Decision Briefs retained `CDE Authority: Not created by runtime`.

## Boundary Check

No Event Fusion, CIL, LMSE, MPCE, MLE, CDE, Decision Contract semantics, broker integration,
trading execution, portfolio mutation, or prediction logic was modified.

The only repair was in the read-only portfolio context merge logic.

## Remaining Risks

- Liquidity sensitivity did not vary materially across these public-market examples; a separate
  regional A-share/HK-heavy case may be useful later.
- LLM wording may vary across runs, but the deterministic portfolio context and Decision Brief
  exposure fields changed as required.
- This proves portfolio-aware runtime context, not trading authority or allocation execution.

## Transition

CR_GOAL_05 is complete.

Proceed to:

```text
CR_GOAL_06_FORECAST_ACCOUNTABILITY_BLACKBOX
```
