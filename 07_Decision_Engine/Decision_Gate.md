# Decision Gate

Decision Gate defines the minimum checks required before Atlas can turn research into a portfolio
action.

Signal must never move directly to Buy or Sell. Atlas portfolio vocabulary is limited to:

```text
Research
Observe
Build
Accumulate
Hold
Reduce
Exit
```

## Portfolio Validation Flow

Before Portfolio Action, Atlas must validate Portfolio data consistency:

```text
Research
 ↓
Decision
 ↓
Portfolio Validation
 ↓
Consistency Check
 ↓
Portfolio Action
 ↓
Execution
```

If Consistency Check fails, Atlas must stop and output:

```text
Portfolio Data Inconsistent
Need User Confirmation
```

No Portfolio Action may be generated until the user confirms corrected data.

## Required Gates

| Gate | Name | Question | Required Pass Condition | Blocks If |
|---|---|---|---|---|
| Gate 1 | Evidence | Is the signal supported by usable evidence? | Source, date, affected company/theme, and evidence quality are recorded. Missing data is marked `Unknown` or `Unverified`. | Evidence is only rumor, unsupported opinion, or unclear price action. |
| Gate 2 | Seven Layer | Which Atlas reasoning layer changed? | Fact, Physics, Engineering, Economics, Finance, Capital, and Trading have been checked. | No layer changed or the changed layer is not identified. |
| Gate 3 | Counter Argument | What is the strongest reason this could be wrong? | Counter argument is explicit and not cosmetic. | The decision only records the bullish or bearish case. |
| Gate 4 | Risk / Reward | Is the current risk/reward acceptable? | Upside driver, downside risk, invalidation trigger, and price/valuation context are recorded. | Price already reflects thesis or invalidation is undefined. |
| Gate 5 | Portfolio Impact | What happens to capital and position state? | Portfolio Validation and Consistency Check pass; position lifecycle, source of funds, sizing implication, and concentration risk are reviewed. | Portfolio data is inconsistent, real portfolio impact is unknown, or private data would need to enter Git. |
| Gate 6 | Execution | How will the action be reviewed? | Execution or no-action review plan is recorded with date or event trigger. | No review plan exists. |

## Gate Outcomes

| Result | Meaning | Allowed Action |
|---|---|---|
| All gates pass | Research can become a trading and portfolio decision. | Build / Accumulate / Hold / Reduce / Exit |
| Some gates pass | Signal is useful but incomplete. | Research / Observe |
| Evidence gate fails | Signal cannot enter decision path. | Reject / Archive |
| Portfolio gate fails | Research may be valid, but capital action is blocked. | Observe |
| Consistency check fails | Portfolio data is internally inconsistent. | Stop and request user confirmation |
| Execution gate fails | No action can be taken because learning loop is incomplete. | Observe |

## Trading Decision Completion

Before any action beyond Observe, Atlas must complete:

| Field | Required |
|---|---|
| Action | Yes |
| Confidence | Yes |
| Logic Chain | Yes |
| Evidence | Yes |
| Risk / Reward | Yes |
| Trigger | Yes |
| Counter Argument | Yes |
| Review Plan | Yes |

If any field is missing, the default action is Observe.

## Action Progression

```text
Observe
 ↓
Build
 ↓
Accumulate
 ↓
Hold
 ↓
Reduce
 ↓
Exit
```

Progression is not automatic. Each transition must pass the gates again using the newest evidence.
