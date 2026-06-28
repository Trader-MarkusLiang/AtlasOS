# Decision Lifecycle

Decision Lifecycle assigns each decision state to one Atlas module so responsibility does not
overlap.

## Module Ownership

| Module | Owns | Does Not Own |
|---|---|---|
| Research | Market Signal, Signal Classification, Evidence Collection, Seven Layer Reasoning, Confidence Scoring, Research Conclusion | Git release, capital execution, framework changes |
| Trading OS | Trading Decision | Raw research intake, real portfolio storage, post-trade learning |
| Portfolio | Portfolio Action, Execution Review | Core reasoning rules, public database schema, release tags |
| Repository | Knowledge Update, Archive, Markdown maintenance, audit files, commit/tag when requested | Investment judgment, capital action |
| Daily | Status Report across active signals, risks, waiting triggers, and open decisions | New framework design, database structure changes, trade execution |
| Architecture | Framework Evolution review when Decision Review marks `Framework Change?` as Yes | Routine signal processing, routine portfolio action, Git-only maintenance |

## Lifecycle by State

| State | Primary Owner | Supporting Module | Output Location |
|---|---|---|---|
| Market Signal | Research | Daily | Alpha Radar or session note |
| Signal Classification | Research | Daily | Alpha Radar / Risk Radar / session note |
| Evidence Collection | Research | Repository | Order Book / Price Transmission / source note |
| Seven Layer Reasoning | Research | Architecture if boundary issue appears | Research output or case note |
| Confidence Scoring | Research | Portfolio for position context | Research output / AI Shovel 100 |
| Research Conclusion | Research | Trading OS | Research output / Alpha Radar |
| Trading Decision | Trading OS | Portfolio | Trading Decision Table format |
| Portfolio Action | Portfolio | Trading OS | Portfolio note / Execution Log |
| Execution Review | Portfolio | Research | Execution Log / Decision Review |
| Knowledge Update | Repository | Research / Portfolio | Database, case, current-state, or verification file |
| Archive | Repository | Daily | Session log, completed note, or archive record |

## Daily Status Role

Daily does not own the decision. Daily reports state:

- Which decisions are open.
- Which gates are blocked.
- Which risks changed.
- Which waiting triggers matter.
- Whether action is allowed today.

## Architecture Role

Architecture enters only when:

- A Decision Review marks `Framework Change?` as Yes.
- A module boundary is unclear.
- A proposed change would alter Core, Framework, Trading OS, Portfolio Rules, or database structure.
- A release gate or audit package must be redesigned.

Architecture does not modify files unless the user explicitly asks for implementation.

## End-to-End Loop

```text
Research captures and reasons.
Trading OS translates research into decision fields.
Portfolio translates valid decisions into capital behavior.
Review compares thesis with reality.
Repository updates durable knowledge and archives the loop.
Daily reports current status.
Architecture handles framework evolution only when review demands it.
```

## Non-Overlap Rule

If a task crosses modules, route each step to its owner. Do not let one module perform another
module's responsibility merely for speed.
