# CR_GOAL_04 - LIVE MARKET BLACK-BOX

## Objective

Prove actual market data reaches the real runtime from the fresh clone.

## Required Path

```text
real source -> normalization -> Input Router -> EventStream -> DecisionLoop
-> persistence -> UI freshness
```

## Channels

Attempt price, volume, volatility, breadth, liquidity, news, announcements, macro, narrative, and
attention.

Every channel must classify as one of:

- `LIVE`
- `DELAYED`
- `CACHED`
- `SIMULATED`
- `NOT_CONFIGURED`
- `RATE_LIMITED`
- `FAILED`

No missing source may become zero signal. No fixture may be labeled live.

## Deliverable

`99_Verification/cleanroom/CR_GOAL_04_Live_Market_Blackbox_Report.md`

