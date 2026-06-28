# Daily Routing Rules

Daily Routing Rules map user input to the smallest Atlas workflow that can handle it.

## Routing Map

| User Input | Route |
|---|---|
| Market information | `atlas-research` |
| Industry information | `atlas-research` |
| Company information | `atlas-research` |
| Holding, position, cost, cash, or allocation question | `atlas-portfolio` |
| Daily report or daily dashboard request | `atlas-daily` |
| Git, commit, audit, tag, changelog, version, or repository sync | `atlas-repository` |
| Framework boundary, state machine, core rule, or architecture question | `atlas-architecture` |

## Mixed Task Order

If a daily user message mixes tasks, split and process in this order:

```text
Research
 ↓
Decision Engine
 ↓
Portfolio
 ↓
Daily
 ↓
Repository
```

## Routing Rules

- Market / Industry / Company information routes to `atlas-research`.
- Portfolio / position / cost / allocation information routes to `atlas-portfolio`.
- Daily report requests route to `atlas-daily`.
- Git / commit / audit / tag requests route to `atlas-repository`.
- Framework boundary / state machine / core rule questions route to `atlas-architecture`.
- If routing is unclear, default to `atlas-research` and mark uncertainty as `Unknown` or
  `Unverified`.
- If the task touches real holdings, keep private data local and out of Git.

## Decision Engine Bridge

After Research classification, place the item into the appropriate Decision Engine state:

| Condition | Decision Engine State |
|---|---|
| New unprocessed item | Market Signal |
| Source is identified but type is unclear | Signal Classification |
| Source and claim exist but evidence is incomplete | Evidence Collection |
| Evidence is sufficient for reasoning | Seven Layer Reasoning |
| Reasoning is complete but action is unclear | Confidence Scoring / Research Conclusion |
| Action is proposed | Trading Decision / Decision Gate |
| Portfolio impact exists | Portfolio Action |
| Outcome or review trigger appears | Execution Review |
| Durable learning appears | Knowledge Update |

## Repository Sync Rule

Repository sync happens only after Research, Decision Engine, Portfolio, and Daily outputs identify
what should become durable knowledge.
