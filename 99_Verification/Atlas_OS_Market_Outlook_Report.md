# Atlas OS Market Outlook Report

Date: 2026-07-10 CST

## Verdict

`PRESENT_AND_CONNECTED`

Home now shows a first-class Market Outlook / 市场前瞻 section that is distinct from Forecast Ledger
accountability.

## Evidence

Current projection from `ui/presentation/home_intelligence.py`:

| Field | Evidence |
|---|---|
| Status | `available` |
| Source | `forecast_ledger + current_runtime_state` |
| Distinct from forecast ledger | `true` |
| Invalidation count | 2 |
| Horizon | from latest ledger row when available; otherwise honest insufficient evidence |
| Confidence | bounded display from forecast row or DecisionPacket |

## Home Fields

The Home section answers:

- What Atlas expects next: base case
- Over what horizon: horizon field
- With what confidence: confidence pill
- What scenarios are plausible: base / upside / downside scenario map
- What invalidates the view: invalidation conditions card

## Boundary Between Outlook And Ledger

The UI explicitly states:

```text
Market Outlook is the current forward view.
Forecast Ledger is the accountability record.
```

Chinese mode states the same distinction:

```text
市场前瞻是当前对未来的判断；预测账本是已记录、可验证的责任链。
```

## Honesty Constraints

- The outlook is a presentation projection from existing runtime and ledger evidence.
- It does not create a prediction model.
- It does not mutate forecast lifecycle state.
- It does not produce trading execution or Buy/Sell output.
- If no usable evidence exists, the adapter renders insufficient-evidence states.

## Browser Evidence

`99_Verification/artifacts/home_intelligence/browser_e2e_results.json`:

- Step 5: Open Outlook `PASS`
- Step 6: Confirm base case `PASS`
- Step 7: Confirm horizon `PASS`
- Step 8: Confirm invalidation `PASS`

