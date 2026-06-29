# Allocation Playbook

Allocation Playbook records how capital moves under different market states. Every action must be
traceable to Trading OS.

## Allocation First Principle

Every Portfolio Decision must proceed in this order:

```text
Allocation
 ↓
Exposure
 ↓
Thesis
 ↓
Holding
```

1. Judge Allocation first.
2. Judge Exposure second.
3. Judge Thesis third.
4. Judge Holding last.

Do not change Capital Thesis directly because a single holding moved up or down.

Decision Engine should judge exposure and capital mission, not account amount.

## Pullback

```text
Cash
 ↓
Memory
 ↓
Equipment
 ↓
Materials
```

| Market State | Source | Destination | Action | Trading OS Trace |
|---|---|---|---|---|
| Thesis intact, price pulls back | Cash | Memory | Accumulate | Daily Dashboard + Trading Decision Table |
| Memory crowded, Equipment confirms orders | Memory / Cash | Equipment | Build / Accumulate | Capital Rotation Table + Order Book |
| Equipment matures, Materials evidence improves | Equipment / Cash | Materials | Build | Capital Rotation Table + Price Transmission |

## Acceleration

```text
Reduce
 ↓
Rotate
 ↓
Build
```

| Market State | Source | Destination | Action | Trading OS Trace |
|---|---|---|---|---|
| Position accelerates without new evidence | Extended position | Cash / next relay | Reduce | Risk Radar + Trading Decision Table |
| Thesis remains but valuation is crowded | Extended winner | Next confirmed bottleneck | Rotate | Capital Rotation Table |
| New relay confirms evidence | Cash / reduced source | Confirmed destination | Build | Order Book + Price Transmission |

## Risk Release

```text
Exit
 ↓
Cash
 ↓
Wait
```

| Market State | Source | Destination | Action | Trading OS Trace |
|---|---|---|---|---|
| Thesis breaks | Affected position | Cash | Exit | Seven Layer Reasoning + Risk Radar |
| High-severity risk triggers | Affected theme | Cash | Reduce / Exit | Risk Radar |
| Evidence is incomplete | Cash | Wait | Observe | Alpha Radar + Trading Decision Table |

## Rule

No allocation action is valid unless it can be traced to:

1. Trading OS.
2. Living Database evidence.
3. Portfolio position state.
4. Execution Log review plan.
